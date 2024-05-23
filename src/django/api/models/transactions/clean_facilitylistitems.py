from django.db import transaction, connection


@transaction.atomic
def clean_facilitylistitems():
    with connection.cursor() as c:
        try:
            print('Stripping all triggers...')
            c.execute("call strip_all_triggers();")
            print('All triggers stripped.')

            print('Removing facilitylistitems where facility_id is null...')
            c.execute("call remove_items_where_facility_id_is_null();")
            print('Facilitylistitems where facility_id is null and removed.')

            print(
                'Removing facilitylistitems with potential match status more '
                'than thirty days...'
            )
            c.execute("call remove_old_pending_matches();")
            print(
                'Facilitylistitems with potential match status more than '
                'thirty days removed.'
            )

            print(
                'Removing facilitylistitems without matches and related '
                'facilities...'
            )
            c.execute(
                "call remove_items_without_matches_and_related_facilities();"
            )
            print(
                'Facilitylistitems without matches and related facilities '
                'removed.'
            )

            print('Start indexing facilities...')
            c.execute("call index_facilities();")
            print('Facilities indexed.')

            print('Creating all triggers...')
            c.execute("call perform_contributor_indexing();")
            print('All triggers created.')

        except Exception as error:
            print(error)
        finally:
            c.close()
