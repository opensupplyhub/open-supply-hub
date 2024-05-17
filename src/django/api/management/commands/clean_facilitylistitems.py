from django.core.management.base import BaseCommand

from api.models.transactions.remove_facilitylistitems_with_potential_match_status_more_thirty_days import remove_facilitylistitems_with_potential_match_status_more_thirty_days


class Command(BaseCommand):
    help = 'Removes facilitylistitems with potential match status more than thirty days.'

    def handle(self, *args, **options):
        print("Start removing facilitylistitems with potential match status more than thirty days...")
        remove_facilitylistitems_with_potential_match_status_more_thirty_days()
