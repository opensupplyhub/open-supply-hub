import csv
import math
from datetime import datetime

from django.core.management.base import BaseCommand

from api.serializers.facility.facility_download_serializer import (
    FacilityDownloadSerializer
)
from api.models.facility.facility_index import FacilityIndex


def count_with_percent(i: int, count: int) -> str:
    return f"{i} out of {count} ({i / count * 100})%"


def print_with_time(text: str) -> None:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- {text}")


def create_chunk(list, size, last_id):
    return list[last_id:last_id + size]


class Command(BaseCommand):
    help = 'Export all facilities to a CSV file.'

    def add_arguments(self, parser):
        return

    def handle(self, *args, **options):
        facilities = FacilityIndex.objects.order_by("id").all()
        count = facilities.count()
        print_with_time(f"Amount of indexed facilities: {count}")

        serializer = FacilityDownloadSerializer()

        now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        with open(f"./facilities-command-{now}.csv", 'w+') as f:
            writer = csv.writer(f)
            print_with_time("Opened file")

            headers = serializer.get_headers()
            writer.writerow(headers)

        print_with_time("Written headers")

        print_with_time("Fetching data from DB")

        last_id = 0
        size_of_chunk = 1000
        while last_id != count - 1:
            facility_chunk = create_chunk(facilities, size_of_chunk, last_id)
            last_id = len(facility_chunk) - 1
            with open(f"./facilities-command-{now}.csv", 'a') as f:
                writer = csv.writer(f)
                i = 0
                for facility in facility_chunk:
                    if i == 0:
                        print_with_time(
                            f"Started exporting {count} facilities"
                        )
                    i += 1

                    row = serializer.get_row(facility)
                    writer.writerow(row)

                    if i % 100 == 0:
                        print_with_time(
                            f"Wrote {count_with_percent(i, count)}"
                        )

        print_with_time(
            f"Finished {count_with_percent(i, count)}"
        )
