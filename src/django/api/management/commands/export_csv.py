import csv
import logging
import os
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from api.serializers.facility.facility_download_serializer import (
    FacilityDownloadSerializer,
)
from api.models.facility.facility_index import FacilityIndex
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

serializer = FacilityDownloadSerializer()
logger = logging.getLogger(__name__)


def upload_file_to_google_drive(filename):
    google_service_account_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_CREDS")
    credentials = service_account.Credentials.from_service_account_info(
        info=json.loads(google_service_account_creds),
    )
    logger.info("Initialized Google Drive service account credentials")

    file_metadata = {
        "name": os.path.basename(filename),
        "parents": [os.getenv("GOOGLE_DRIVE_SHARED_DIRECTORY_ID")],
    }
    media = MediaFileUpload(filename, mimetype="text/csv")

    logger.info("Initializing the Drive upload")
    service = build("drive", "v3", credentials=credentials)
    uploaded_file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    return uploaded_file.get("id")


def create_cvs_writer(file):
    writer = csv.writer(file)
    headers = serializer.get_headers()
    writer.writerow(headers)

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
                logger.info(f"Facilities processed: {len(facilities)}")
                logger.info(f"End of iteration, ID: {last_id}")

        logger.info("Starting to upload the file to Google Drive!")
        file_id = upload_file_to_google_drive(filename=filename)
        logger.info(f"Finished writing {filename} with id {file_id}")

        logger.info("Finished the export process!")
        logger.info(f"Total number of facilities: {total_facilities}")
