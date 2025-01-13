import csv
import logging
import os
import base64
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
    """
    Uploads a file to Google Drive using a service account.
    Args:
        filename (str): The path to the file to be uploaded.
    Returns:
        str: The ID of the uploaded file on Google Drive.
    Raises:
        ValueError: If the Google Service Account credentials
        or the Google Drive shared directory ID are not found
        in the environment variables.
    """

    base64_gdrive_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_CREDS_BASE64")
    print('base64_gdrive_creds >>>', base64_gdrive_creds)

    if base64_gdrive_creds is None:
        raise ValueError("Google Service Account credentials not found!")

    decoded_creds = base64.b64decode(base64_gdrive_creds).decode("utf-8")
    print('decoded_creds >>>', decoded_creds)

    credentials = service_account.Credentials.from_service_account_info(
        info=json.loads(decoded_creds),
    )
    logger.info("Initialized Google Drive service account credentials")

    gdrvie_dir_id = os.getenv("GOOGLE_DRIVE_SHARED_DIRECTORY_ID")

    if gdrvie_dir_id is None:
        raise ValueError("Google Drive shared directory ID not found!")

    file_metadata = {
        "name": os.path.basename(filename),
        "parents": [gdrvie_dir_id],
    }
    media = MediaFileUpload(
        filename,
        mimetype="text/csv",
    )

    logger.info("Initializing the Drive upload")
    service = build(
        "drive",
        "v3",
        credentials=credentials,
    )
    uploaded_file = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id",
        )
        .execute()
    )

    return uploaded_file.get("id")


def create_cvs_writer(file):
    """
    Create a CSV writer object and write the headers to the given file.
    Args:
        file (file object): The file object where the CSV data will be written.
    Returns:
        csv.writer: A CSV writer object that can be used
            to write rows to the file.
    """
    writer = csv.writer(file)
    headers = serializer.get_headers()
    writer.writerow(headers)

    return writer


def write_facilities(writer, facilities):
    """
    Write facility data to a CSV file using the provided writer.
    Args:
        writer (csv.writer): A CSV writer object used to write
            rows to the CSV file.
        facilities (iterable): An iterable of facility objects to be
            written to the CSV file.
    Returns:
        None
    """
    for facility in facilities:
        row = serializer.get_row(facility)
        writer.writerow(row)


def get_facilities(limit=50000, id=None):
    """
    Retrieve a list of facilities from the FacilityIndex.
    Args:
        id (int, optional): The starting ID to filter facilities.
            Only facilities with an ID greater than this value
            will be included. Defaults to None.
        limit (int, optional): The maximum number of facilities to retrieve.
            Defaults to 50000.
    Returns:
        QuerySet: A Django QuerySet containing the filtered
            and ordered facilities.
    """
    facility_objects = FacilityIndex.objects

    if id is not None:
        facility_objects = facility_objects.filter(id__gt=id)

    return facility_objects.order_by("id")[:limit]


class Command(BaseCommand):
    """
    Command class to export all facilities to a CSV file.
    This command fetches facilities in batches and writes them to a CSV file.
    It also uploads the generated CSV file to Google Drive.
    Attributes:
        help (str): Description of the command.
    Methods:
        add_arguments(parser):
            Adds command-line arguments to the parser.
        handle(*args, **options):
            Executes the command to export facilities to a CSV file
            and upload it to Google Drive.
    """

    help = "Export all facilities to a CSV file."

    def add_arguments(self, parser):
        """
        Adds custom command-line arguments to the parser.
        Args:
            parser (argparse.ArgumentParser): The argument parser instance
                to which custom arguments are added.
        Arguments:
            --limit (int): Optional; The maximum number of facilities
                to fetch in each iteration. Default is 50000.
        """
        parser.add_argument(
            "--limit",
            type=int,
            default=50000,
            help="Limit the number of facilities to fetch in each iteration",
        )

    def handle(self, *args, **options):
        """
        Handles the export process of facilities to a CSV file and
            uploads it to Google Drive.
        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments. Expected to contain:
                - "limit" (int): The maximum number of facilities
                    to fetch in each iteration.
        """
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
                    limit=limit,
                    id=last_id,
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
