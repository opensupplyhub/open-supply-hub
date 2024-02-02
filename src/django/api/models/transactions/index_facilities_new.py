
from django.db import transaction, connection


@transaction.atomic
def index_facilities_new(facility_ids=list):
    with connection.cursor() as c:
        try:
            # If passed an empty array, create or
            # update all existing facilities
            if len(facility_ids) == 0:
                c.execute("call index_facilities();")
            else:
                c.execute(
                    "call index_facilities_by(%(ids)s);",
                    {'ids': facility_ids}
                )
        except Exception as error:
            print(error)
        finally:
            c.close()
