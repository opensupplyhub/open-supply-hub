import csv
import logging
from datetime import datetime
from django.core.management.base import BaseCommand
from api.serializers.facility.facility_download_serializer import (
    FacilityDownloadSerializer,
)
from api.models.facility.facility_index import FacilityIndex

serializer = FacilityDownloadSerializer()
logger = logging.getLogger(__name__)


def create_cvs_writer(file):
    writer = csv.writer(file)

    headers = serializer.get_headers()
    writer.writerow(headers)

    logger.info("Wrote headers to file")

    return writer


def write_facilities(writer, facilities):
    for facility in facilities:
        row = serializer.get_row(facility)
        writer.writerow(row)


def get_facilities(id=None, limit=50000):
    facility_objects = FacilityIndex.objects

    if id is not None:
        facility_objects = facility_objects.filter(id__gt=id)

    return facility_objects.order_by("id")[:limit]


class Command(BaseCommand):
    help = "Export all facilities to a CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=50000,
            help="Limit the number of facilities to fetch in each iteration",
        )

    def handle(self, *args, **options):
        logger.info("Starting the export process!")

        limit = options["limit"]
        logger.info(f"Limit set to: {limit}")

        now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"./facilities-command-{now}.csv"

        with open(filename, "w+") as file:
            logger.info(f"Opened file for writing: {filename}")

            writer = create_cvs_writer(file=file)
            last_id = None
            facilities = None
            total_facilities = 0

            while True:
                logger.info(f"New loop iteration, ID: {last_id}")
                facilities = get_facilities(
                    id=last_id,
                    limit=limit,
                )
                total_facilities += len(facilities)

                if len(facilities) == 0:
                    logger.info("No more facilities, breaking the loop!")
                    break

                write_facilities(
                    writer=writer,
                    facilities=facilities,
                )

                last_id = facilities[len(facilities) - 1].id
                logger.info(f"Number of processed facilities: {len(facilities)}")
                logger.info(f"End of iteration, ID: {last_id}")

        logger.info("Finished the export process!")
        logger.info(f"Total number of facilities: {total_facilities}")
