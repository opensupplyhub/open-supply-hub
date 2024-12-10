import os
import logging
from django.db import transaction, connection

logger = logging.getLogger(__name__)


@transaction.atomic
def clean_facilitylistitems():
    def execute_sql_file(cursor, file_name):
        file_path = os.path.join('./sqls/table_triggers', file_name)
        with open(file_path, 'r') as sql_file:
            sql_statement = sql_file.read()
            cursor.execute(sql_statement)

    def call_procedure(cursor, procedure_name):
        cursor.execute(f"CALL {procedure_name}();")

    with connection.cursor() as cursor:
        try:
            logger.info('Dropping table triggers...')
            execute_sql_file(cursor, 'drop_table_triggers.sql')
            logger.info('Table triggers dropped.')

            logger.info(
                'Removing facilitylistitems where facility_id is null...'
            )
            call_procedure(cursor, 'remove_items_where_facility_id_is_null')
            logger.info(
                'Facilitylistitems where facility_id is null removed.'
            )

            logger.info(
                'Removing facilitylistitems with potential match status more '
                'than thirty days...'
            )
            call_procedure(cursor, 'remove_old_pending_matches')
            logger.info(
                'Facilitylistitems with potential match status more than '
                'thirty days removed.'
            )

            logger.info(
                'Removing facilitylistitems without matches and related '
                'facilities...'
            )
            call_procedure(
                cursor, 'remove_items_without_matches_and_related_facilities'
            )
            logger.info(
                'Facilitylistitems without matches and related facilities '
                'removed.'
            )

            logger.info('Creating table triggers...')
            execute_sql_file(cursor, 'create_table_triggers.sql')
            logger.info('Table triggers created.')

            logger.info('Start indexing facilities...')
            call_procedure(cursor, 'index_facilities')
            logger.info('Facilities indexed.')

        except Exception as error:
            print(f"An error occurred: {error}")

        finally:
            cursor.close()
