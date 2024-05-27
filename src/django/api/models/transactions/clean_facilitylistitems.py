import os
from django.db import transaction, connection


@transaction.atomic
def clean_facilitylistitems():
    def execute_sql_file(cursor, file_name):
        file_path = os.path.join('./sqls/', file_name)
        with open(file_path, 'r') as sql_file:
            sql_statement = sql_file.read()
            cursor.execute(sql_statement)

    def call_procedure(cursor, procedure_name):
        cursor.execute(f"CALL {procedure_name}();")

    with connection.cursor() as cursor:
        try:
            print('Dropping table triggers...')
            execute_sql_file(cursor, 'drop_table_triggers.sql')
            print('Table triggers dropped.')

            print('Removing facilitylistitems where facility_id is null...')
            call_procedure(cursor, 'remove_items_where_facility_id_is_null')
            print('Facilitylistitems where facility_id is null removed.')

            print(
                'Removing facilitylistitems with potential match status more '
                'than thirty days...'
            )
            call_procedure(cursor, 'remove_old_pending_matches')
            print(
                'Facilitylistitems with potential match status more than '
                'thirty days removed.'
            )

            print(
                'Removing facilitylistitems without matches and related '
                'facilities...'
            )
            call_procedure(
                cursor, 'remove_items_without_matches_and_related_facilities'
            )
            print(
                'Facilitylistitems without matches and related facilities '
                'removed.'
            )

            print('Creating table triggers...')
            execute_sql_file(cursor, 'create_table_triggers.sql')
            print('Table triggers created.')

            print('Start indexing facilities...')
            call_procedure(cursor, 'index_facilities')
            print('Facilities indexed.')

        except Exception as error:
            print(f"An error occurred: {error}")

        finally:
            cursor.close()
