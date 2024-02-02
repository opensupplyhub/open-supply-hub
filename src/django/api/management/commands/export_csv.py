import csv
from datetime import datetime

from django.core.management.base import BaseCommand

from api.models.transactions.index_facilities_new import index_facilities_new
from api.serializers.facility.facility_index_download_serializer import (
    FacilityIndexDownloadSerializer
)
from api.models.facility.facility_index import FacilityIndex


def count_with_percent(i: int, count: int) -> str:
    return f"{i} out of {count} ({i / count * 100})%"


def print_with_time(text: str) -> None:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- {text}")


class Command(BaseCommand):
    help = 'Export all facilities to a CSV file.'

    def add_arguments(self, parser):
        return
        print("add_arguments")

    def handle(self, *args, **options):
        print_with_time("Started indexing facilities")
        index_facilities_new()
        facilities = FacilityIndex.objects.order_by("id").all()
        count = facilities.count()
        print_with_time(f"Finished indexing {count} facilities")

        serializer = FacilityIndexDownloadSerializer()

        now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        with open(f"./facilities-command-{now}.csv", 'w+') as f:
            writer = csv.writer(f)
            print_with_time("Opened file")

            writer.writerow(serializer.get_headers())
            print_with_time("Written headers")

            print_with_time("Fetching data from DB")
            i = 0
            for facility in facilities:
                if i == 0:
                    print_with_time(f"Started exporting {count} facilities")

                i += 1

                row = serializer.get_row(facility)
                writer.writerow(row)

                if i % 100 == 0:
                    print_with_time(f"Wrote {count_with_percent(i, count)}")

            print_with_time(f"Finished {count_with_percent(i, count)}")
