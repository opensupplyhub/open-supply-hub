from django.core.management.base import BaseCommand

from api.models.transactions.index_facilities_new import index_facilities_new


class Command(BaseCommand):
    help = 'Adds facilities to the index new table.'

    def handle(self, *args, **options):
        # index all facilities
        print("Start index_facilities_new...")
        index_facilities_new([])
