import base64
import csv
import io
import json
import logging
import os
import tempfile
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db.models.signals import post_save
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from api.models.facility.facility import Facility
from api.models.moderation_event import ModerationEvent
from api.models.user import User
from api.moderation_event_actions.approval.add_production_location import (
    AddProductionLocation,
)
from api.moderation_event_actions.approval.update_production_location import (
    UpdateProductionLocation,
)
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto import (
    CreateModerationEventDTO,
)
from api.moderation_event_actions.creation.location_contribution.location_contribution import (
    LocationContribution,
)
from api.moderation_event_actions.creation.moderation_event_creator import (
    ModerationEventCreator,
)
from api.signals import moderation_event_update_handler_for_opensearch

logger = logging.getLogger(__name__)


class AddProductionLocationWithOsID(AddProductionLocation):
    """Helper class to allow specifying os_id when creating a new facility."""
    def __init__(
        self,
        moderation_event: ModerationEvent,
        moderator: User,
        os_id: str = None
    ) -> None:
        super().__init__(moderation_event, moderator)
        self.__os_id = os_id

    def _get_os_id(self, country_code: str) -> str:
        if self.__os_id is not None:
            return self.__os_id
        # If os_id is None, use parent's method to generate one
        return super()._get_os_id(country_code)


class Command(BaseCommand):
    help = (
        "Load data from a CSV file stored in Google Drive. "
        "CSV must contain columns specified in --columns argument. "
        "If 'os_id' is provided, updates existing facilities. "
        "If 'os_id' is not provided, creates new facilities."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--user_id",
            type=int,
            help="The ID of the user performing the data load.",
            required=True,
        )
        parser.add_argument(
            "--contributor_email",
            type=str,
            help="The email of the contributor that uploads the data.",
            required=True,
        )
        parser.add_argument(
            "--file_id",
            type=str,
            help="The Google Drive file ID to load CSV from.",
            required=True,
        )
        parser.add_argument(
            "--columns",
            type=str,
            help="Comma-separated list of columns to read from.",
            required=True,
        )

    def _get_google_drive_service(self):
        """Initialize and return Google Drive API service."""
        SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

        base64_gdrive_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_CREDS_BASE64")
        if base64_gdrive_creds is None:
            raise ValueError("Google Service Account credentials not found!")

        decoded_creds = base64.b64decode(base64_gdrive_creds).decode("utf-8")
        credentials = service_account.Credentials.from_service_account_info(
            info=json.loads(decoded_creds),
            scopes=SCOPES,
        )
        logger.info("Initialized Google service account credentials")

        service = build("drive", "v3", credentials=credentials)
        logger.info("Built Google Drive service")
        return service

    def _download_csv_from_google_drive(self, file_id):
        """Download CSV file from Google Drive and return file path."""
        service = self._get_google_drive_service()

        logger.info(
            f"Downloading CSV file from Google Drive with ID: {file_id}"
        )

        try:
            # Get file metadata
            file_metadata = service.files().get(
                fileId=file_id,
                fields="name, mimeType"
            ).execute()

            file_name = file_metadata.get("name", "downloaded_file.csv")
            mime_type = file_metadata.get("mimeType", "")

            logger.info(
                f"File name: '{file_name}', MIME type: '{mime_type}'"
            )

            # Download file content
            request = service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logger.info(
                        f"Download progress: {int(status.progress() * 100)}%"
                    )

            file_content.seek(0)

            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                mode='w+b',
                suffix='.csv',
                delete=False
            )
            temp_file.write(file_content.read())
            temp_file.close()

            logger.info(
                f"Downloaded CSV file to temporary location: {temp_file.name}"
            )

            return Path(temp_file.name)

        except Exception as error:
            logger.error(
                f"Error downloading file from Google Drive: {str(error)}"
            )
            raise

    def _parse_columns(self, columns_str):
        """Parse and validate columns from comma-separated string."""
        columns = [
            col.strip() for col in columns_str.split(",") if col.strip()
        ]
        if not columns:
            raise ValueError("No columns specified for data loading.")
        return columns

    def _build_raw_data(self, row, columns):
        """Build raw_data dictionary from CSV row based on specified columns."""
        raw_data = {"source": ModerationEvent.Source.API.value}

        for column in columns:
            if column == "os_id":
                # Skip os_id as it's used for facility lookup only
                continue

            if column in row and row[column]:
                value = row[column].strip()

                # Special handling for us_geoid_county
                if column == "us_geoid_county":
                    raw_data[column] = {"value": str(value)}
                else:
                    # Default structure for other columns
                    raw_data[column] = value

        return raw_data

    def _process_row(self, row, row_idx, columns, contributor, user):
        """Process a single CSV row and create/update facility."""
        # Check if os_id is provided (optional)
        os_id = None
        facility = None

        if "os_id" in row and row["os_id"]:
            os_id = row["os_id"].strip()
            try:
                facility = Facility.objects.get(id=os_id)
            except Facility.DoesNotExist:
                logger.debug(
                    f"Row {row_idx}: Facility does not exist with "
                    f"os_id='{os_id}'. Will create new facility."
                )

        # Build raw_data from CSV row dynamically based on columns
        raw_data = self._build_raw_data(row, columns)

        # Determine request type and log message
        req_types = ModerationEvent.RequestType
        if facility:
            request_type = req_types.UPDATE.value
            log_message = f"Row {row_idx}: Updating facility os_id='{os_id}'"
        else:
            request_type = req_types.CREATE.value
            if os_id:
                log_message = (
                    f"Row {row_idx}: Creating new facility with "
                    f"os_id='{os_id}'"
                )
            else:
                log_message = f"Row {row_idx}: Creating new facility"

        logger.debug(
            f"{log_message} with columns: "
            f"{', '.join([col for col in columns if col != 'os_id'])}"
        )

        # Create moderation event (temporary, will be deleted after processing)
        me_creator = ModerationEventCreator(LocationContribution())
        event_dto = CreateModerationEventDTO(
            contributor=contributor,
            raw_data=raw_data,
            request_type=request_type,
        )

        if facility:
            event_dto.os = facility

        try:
            ec_result = me_creator.perform_event_creation(event_dto)
        except Exception as error:
            logger.error(f"Row {row_idx}: Error creating event: {str(error)}")
            return False, None

        if ec_result.errors:
            logger.error(
                f"Row {row_idx}: Validation errors: {ec_result.errors}"
            )
            return False, None

        # Process moderation event to create/update facility
        if facility:
            processor = UpdateProductionLocation(
                ec_result.moderation_event, user, facility.id
            )
        else:
            processor = AddProductionLocationWithOsID(
                ec_result.moderation_event, user, os_id
            )

        try:
            item = processor.process_moderation_event()
            facility_id = item.facility_id

            # Delete the ModerationEvent after successful processing
            # (only needed for processing logic, not stored in DB)
            moderation_event_uuid = ec_result.moderation_event.uuid
            ec_result.moderation_event.delete()
            logger.debug(
                f"Row {row_idx}: Deleted ModerationEvent "
                f"{moderation_event_uuid} after successful processing"
            )

            logger.info(
                f"Row {row_idx}: Successfully processed facility ID: "
                f"'{facility_id}'"
            )
            return True, facility_id

        except Exception as error:
            ec_result.moderation_event.delete()
            logger.error(f"Row {row_idx}: Error processing: {str(error)}")
            return False, None

    def handle(self, *args, **options):
        """Main command handler."""
        # Validate and get user
        user_id = options["user_id"]
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError(f"User with ID '{user_id}' does not exist.")

        # Validate and get contributor
        contributor_email = options["contributor_email"]
        try:
            cont_user = User.objects.get(email=contributor_email)
        except User.DoesNotExist:
            raise ValueError(
                f"Contributor user '{contributor_email}' does not exist. "
                "Please create the user first."
            )

        if not cont_user.has_contributor:
            raise ValueError(
                f"User '{contributor_email}' has no contributor profile."
            )

        contributor = cont_user.contributor

        # Disconnect OpenSearch signal to avoid race condition during batch
        # processing. ModerationEvents will be deleted after processing, so no
        # OpenSearch updates needed
        post_save.disconnect(
            moderation_event_update_handler_for_opensearch,
            sender=ModerationEvent
        )
        logger.info("Disconnected OpenSearch signal for batch processing")

        csv_path = None
        temp_file_created = False
        try:
            # Parse columns from argument
            columns = self._parse_columns(options["columns"])

            # Download CSV file from Google Drive
            csv_path = self._download_csv_from_google_drive(options["file_id"])
            temp_file_created = True

            if not csv_path.exists():
                raise ValueError(
                    f"CSV file not found at: {csv_path}. "
                    "Failed to download from Google Drive."
                )

            logger.info(f"Reading data from CSV file: {csv_path}")

            # Statistics tracking
            stats = {
                "total": 0,
                "success": 0,
                "errors": 0,
            }

            # Read and process CSV file
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                if not reader.fieldnames:
                    raise ValueError("CSV file is empty or has no headers.")

                logger.info(f"CSV columns: {', '.join(reader.fieldnames)}")

                # Validate required columns exist in CSV
                missing_columns = [
                    col for col in columns if col not in reader.fieldnames
                ]
                if missing_columns:
                    raise ValueError(
                        f"CSV file is missing required columns: "
                        f"{', '.join(missing_columns)}"
                    )

                # Process each row
                for row_idx, row in enumerate(reader, start=2):
                    stats["total"] += 1

                    # Log progress every 10 rows
                    if row_idx % 10 == 0:
                        logger.info(
                            f"Processing row {row_idx}... "
                            f"(Success: {stats['success']}, "
                            f"Errors: {stats['errors']})"
                        )

                    success, facility_id = self._process_row(
                        row, row_idx, columns, contributor, user
                    )

                    if success:
                        stats["success"] += 1
                    else:
                        stats["errors"] += 1

                logger.info(
                    f"Completed processing CSV file: {csv_path}. "
                    f"Total: {stats['total']}, Success: {stats['success']}, "
                    f"Errors: {stats['errors']}"
                )

        finally:
            # Always reconnect the signal, even if there was an error
            post_save.connect(
                moderation_event_update_handler_for_opensearch,
                sender=ModerationEvent
            )
            logger.info("Reconnected OpenSearch signal")

            # Clean up temporary file if downloaded from Google Drive
            if temp_file_created and csv_path and csv_path.exists():
                try:
                    csv_path.unlink()
                    logger.info(f"Cleaned up temporary file: {csv_path}")
                except Exception as error:
                    logger.warning(
                        f"Failed to delete temporary file {csv_path}: "
                        f"{str(error)}"
                    )

