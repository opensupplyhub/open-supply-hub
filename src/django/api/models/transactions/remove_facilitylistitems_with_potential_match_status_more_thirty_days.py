import os
from django.db import transaction, connection


@transaction.atomic
def remove_facilitylistitems_with_potential_match_status_more_thirty_days():
    with connection.cursor() as c:
        try:
            print('Stripping all triggers...')
            c.execute("call strip_all_triggers();")
            print('All triggers stripped.')

            print('Removing facilitylistitems where facility_id is null and related data...')
            file_path = os.path.join('./sqls/', 'remove_facilitylistitems_where_facility_id_is_null_and_related_data.sql')
            sql_statement = open(file_path).read()
            with connection.cursor() as c:
                c.execute(sql_statement)
            print('Facilitylistitems where facility_id is null and related data removed.')
            # c.callproc("remove_facilitylistitems_with_potential_match_status_more_thirty_days")
            # c.execute("0135")

        except Exception as error:
            print(error)
        finally:
            c.close()
