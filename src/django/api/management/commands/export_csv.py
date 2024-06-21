import csv
from datetime import datetime

from django.core.management.base import BaseCommand

from api.serializers.facility.facility_download_serializer import (
    FacilityDownloadSerializer
)
from api.models.facility.facility_index import FacilityIndex

serializer = FacilityDownloadSerializer()


def count_with_percent(i: int, count: int) -> str:
    return f"{i} out of {count} ({i / count * 100})%"


def print_with_time(text: str) -> None:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- {text}")


def create_chunk(list, size, index):
    return list[index:index + size]


def create_with_headers():
    now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    filename = f"./facilities-command-{now}.csv"
    with open(filename, 'w+') as f:
        writer = csv.writer(f)
        print_with_time("Created file")

        headers = serializer.get_headers()
        writer.writerow(headers)
        print_with_time("Written headers")

    return filename


def modify(filename, chunk):
    with open(filename, 'a') as f:
        writer = csv.writer(f)
        for facility in chunk:
            row = serializer.get_row(facility)
            writer.writerow(row)


class Command(BaseCommand):
    help = 'Export all facilities to a CSV file.'

    def add_arguments(self, parser):
        return

    def handle(self, *args, **options):
        facilities = FacilityIndex.objects.order_by("id").all()
        size_of_chunk = 100000
        count = facilities.count()
        print_with_time(f"Amount of indexed facilities: {count}")

        filename = create_with_headers()

        index = 0
        print_with_time("Fetching data from DB")
        while count > index:
            if index == 0:
                print_with_time(
                    f"Started exporting {count} facilities"
                )

            facility_chunk = create_chunk(facilities, size_of_chunk, index)
            index = index + size_of_chunk
            modify(filename, facility_chunk)

            if index > count:
                index = count
            if index % size_of_chunk == 0:
                print_with_time(
                    f"Wrote {count_with_percent(index, count)}"
                )

        print_with_time(
            f"Finished {count_with_percent(index,count)}"
        )
