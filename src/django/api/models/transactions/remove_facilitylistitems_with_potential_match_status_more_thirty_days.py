from django.db import transaction, connection


@transaction.atomic
def remove_facilitylistitems_with_potential_match_status_more_thirty_days():
    with connection.cursor() as c:
        try:
            c.execute("call strip_all_triggers();")
            # c.execute("call remove_facilitylistitems_with_potential_match_status_more_thirty_days();")
        except Exception as error:
            print(error)
        finally:
            c.close()
