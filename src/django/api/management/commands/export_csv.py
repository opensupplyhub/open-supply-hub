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


def divide_chunks(list, size, amount):
    chunks = []
    last_index = size
    first_index = 0
    for i in range(1, amount + 1):
        if i == amount:
            chunks.append(list[first_index:])
        else:
            chunks.append(list[first_index:last_index])
            first_index = last_index
            last_index = last_index + size
    return chunks


class Command(BaseCommand):
    help = 'Export all facilities to a CSV file.'

    def add_arguments(self, parser):
        return

    def handle(self, *args, **options):
        facilities = FacilityIndex.objects.order_by("id").all()
        count = facilities.count()
        size_of_chunk = 1000
        amount_of_chunks = math.ceil(count / size_of_chunk)
        print_with_time(f"Amount of indexed facilities: {count}")
        print_with_time(f"Amount of chunks: {amount_of_chunks}")

        facilities_pool = divide_chunks(
            facilities,
            size_of_chunk,
            amount_of_chunks
        )

        serializer = FacilityDownloadSerializer()

        now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        with open(f"./facilities-command-{now}.csv", 'w+') as f:
            writer = csv.writer(f)
            print_with_time("Opened file")

            headers = serializer.get_headers()
            writer.writerow(headers)

            print_with_time("Written headers")

            print_with_time("Fetching data from DB")
            i = 0
            for facilities_chunk in facilities_pool:
                for facility in facilities_chunk:
                    print(i)
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
