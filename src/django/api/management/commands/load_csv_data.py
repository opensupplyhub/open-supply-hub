import os
import csv
import base64
import json
import logging
import tempfile
from pathlib import Path
from django.core.management.base import BaseCommand
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from api.models.facility.facility import Facility
from api.models.moderation_event import ModerationEvent
from api.models.contributor.contributor import Contributor
from api.models.user import User
from api.moderation_event_actions.creation.moderation_event_creator \
    import ModerationEventCreator
from api.moderation_event_actions.creation.location_contribution \
    .location_contribution import LocationContribution
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.moderation_event_actions.approval.add_production_location \
    import AddProductionLocation
from api.moderation_event_actions.approval.update_production_location \
    import UpdateProductionLocation

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

        logger.info(f"Downloading CSV file from Google Drive with ID: {file_id}")

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
            logger.error(f"Error downloading file from Google Drive: {str(error)}")
            raise

    def handle(self, *args, **options):
        user_id = options["user_id"]

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError(f"User with ID '{user_id}' does not exist.")

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

        # Parse columns from argument
        columns = []
        for col in options["columns"].split(","):
            columns.append(col.strip())

        if not columns:
            raise ValueError("No columns specified for data loading.")

        # Download CSV file from Google Drive
        csv_path = self._download_csv_from_google_drive(options["file_id"])
        temp_file_created = True

        if not csv_path.exists():
            raise ValueError(
                f"CSV file not found at: {csv_path}. "
                "Failed to download from Google Drive."
            )

        logger.info(f"Reading data from CSV file: {csv_path}")

        # Read CSV file
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

            row_idx = 1  # Start from 1 (header is row 0)

            for row in reader:
                row_idx += 1
                logger.info(f"Processing row: {row_idx}")

                # Check if os_id is provided (optional)
                os_id = None
                facility = None
                if "os_id" in row and row["os_id"]:
                    os_id = row["os_id"].strip()
                    # Check if facility exists
                    try:
                        facility = Facility.objects.get(id=os_id)
                    except Facility.DoesNotExist:
                        logger.info(
                            f"Row {row_idx}: Facility does not exist "
                            f"with os_id: '{os_id}'. Will create new facility."
                        )

                # Build raw_data from CSV row dynamically based on columns
                raw_data = {
                    "source": ModerationEvent.Source.API.value,
                }

                # Process each column from the columns list
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

                # Determine request type and facility
                req_types = ModerationEvent.RequestType
                if facility:
                    # Update existing facility
                    request_type = req_types.UPDATE.value
                    log_message = f"Row {row_idx}: Updating facility os_id='{os_id}'"
                else:
                    # Create new facility
                    request_type = req_types.CREATE.value
                    if os_id:
                        log_message = f"Row {row_idx}: Creating new facility with os_id='{os_id}'"
                    else:
                        log_message = f"Row {row_idx}: Creating new facility"

                logger.info(
                    f"{log_message} with columns: "
                    f"{', '.join([col for col in columns if col != 'os_id'])}"
                )

                # Create moderation event
                me_creator = ModerationEventCreator(
                    LocationContribution(),
                )
                event_dto = CreateModerationEventDTO(
                    contributor=contributor,
                    raw_data=raw_data,
                    request_type=request_type,
                )

                # Only set os if facility exists (for UPDATE)
                if facility:
                    event_dto.os = facility

                try:
                    ec_result = me_creator.perform_event_creation(event_dto)
                except Exception as error:
                    logger.error(
                        f"Row {row_idx}: Error creating event: {str(error)}"
                    )
                    continue

                if ec_result.errors:
                    logger.error(
                        f"Row {row_idx}: Validation errors: "
                        f"{ec_result.errors}"
                    )
                    continue

                # Process moderation event
                if facility:
                    # Update existing facility
                    processor = UpdateProductionLocation(
                        ec_result.moderation_event,
                        user,
                        facility.id,
                    )
                else:
                    # Create new facility
                    processor = AddProductionLocationWithOsID(
                        ec_result.moderation_event,
                        user,
                        os_id,
                    )

                try:
                    item = processor.process_moderation_event()
                    logger.info(
                        f"Row {row_idx}: Successfully processed "
                        f"facility ID: '{item.facility_id}'"
                    )
                except Exception as error:
                    ModerationEvent.objects.filter(
                        uuid=ec_result.moderation_event.uuid
                    ).update(
                        status=ModerationEvent.Status.REJECTED.value,
                        action_reason_text_cleaned="CSV upload error",
                        action_reason_text_raw="<p>CSV upload error</p>\n"
                    )
                    logger.error(
                        f"Row {row_idx}: Error processing: {str(error)}"
                    )
                    raise

        logger.info(f"Completed processing CSV file: {csv_path}")

        # Clean up temporary file if downloaded from Google Drive
        if temp_file_created and csv_path.exists():
            try:
                csv_path.unlink()
                logger.info(f"Cleaned up temporary file: {csv_path}")
            except Exception as error:
                logger.warning(
                    f"Failed to delete temporary file {csv_path}: {str(error)}"
                )

