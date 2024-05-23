from django.core.management.base import BaseCommand

from api.models.transactions.clean_facilitylistitems import (
    clean_facilitylistitems,
)


class Command(BaseCommand):
    help = 'Removes facilitylistitems where facility_id is null, '
    'removes matches with PENDING status more than thirty days, '
    'removes facilitylistitems without matches and related facilities.'

    def handle(self, *args, **options):
        clean_facilitylistitems()
