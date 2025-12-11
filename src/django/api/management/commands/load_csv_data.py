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
from api.moderation_event_actions.approval.update_production_location \
    import UpdateProductionLocation

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Load data from a CSV file stored in Google Drive. "
        "CSV must contain two columns: 'os_id' and 'us_geoid_county'. "
        "Only processes existing facilities."
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

    def _get_google_drive_service(self):
        """Initialize and return Google Drive API service."""
        SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

        base64_gdrive_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_CREDS_BASE64", "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAib3MtaHViLWludGVybmFsLTQ4MDkwOSIsCiAgInByaXZhdGVfa2V5X2lkIjogIjJhMTQ5NGZmYjQzY2VjNWRmYjFkZDg2YjVkNzFlNmVhOWI5MGRjODciLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2d0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktrd2dnU2xBZ0VBQW9JQkFRQzVlblllNGI2TVBKVEJcbjBwVEF3MTdvb0prMjB4YUtXM1BxaUMwWERlWHdKNGt2Znl3L3NlRTFxaVg1ZDYyVS9DRkVIb1JDeHpxUVNaWkhcbkxCYjJvdVlJVnF5RzZGb3diaGJyYWUrbjR0L1dibjJJb3RtV2FrZEJGQ1k5M3FyMWpvQmQ3VUl3eWRTM09GUkNcbktpeWFqbXJVSGcyUG9Ca0Z5RzZ6RTJmZnY4MEJIU1poNHRlR1c3NGx5UiszdXNZM3RQb2NZRFBjM2d5Tnl2cWtcblBDdkxpSlNEWEhaSGNtY0JaaHhUWCtXZnZXSExIWUV1OUtPenBhNmtSU2JZeHhteHdKbjg4UTg3VkRaVnNwS0JcbkdwMk9EMzV3UDZRb2I5ZmxMNUZ2WWxVMUNXU3FUSGo2S25wb043OXBrVGxBbFNBR0ROQmhIak14dEt2UXlhYStcblM4My9WV3duQWdNQkFBRUNnZ0VBTk8zYmMyaWNSY3lyN3J1M00yTU5YSGtuLzlzeEhYNkhqN0FZbmZHYlluTUZcbjFRWUhqSTJvWlBZUExDZVk0MkVuNVJhSVM3NHEyaTRGc24zRWQ5RjRyM3g4YzJzdkFZOEkvMWtWeU9VWFYwdmtcbml1OWVCR3lEdFBDWkVTTFB5bzlGMW9mMFVaUG5IZm4zSVlLRGcvK01RTWZxdXNmSEhEMWNTY0lKN0hJQmdJVmlcbkRYaHQ0L1hFMUJIQ0U4cmxza2pIMFdXa01KREcvQmw5VTQ1QTBwaEdyVDUzdUs1OFROOE9OcUlGeVl0NUlCTjVcbkR1bEd6dEMwTE1vRGVJMW9xTTh0NWJPU0hQcGlGWFZSRldCZXdsbndJdTdTR1Qvdi9iT2VOclVYUkZvSXBPWHdcbkhqcUhPbmdNZnpKaGRZS1ZmSGpDVzlzV0Y0dC82T2EzeHluaEplVU9jUUtCZ1FEd1c4TWxCM0Nva3ZwZEJQdzlcbk1iVmhPcWNPaUVXVjVKN1VINjdWQ09RTTJUVzNZOCtFekFQWDJUcFhvcCtpZzhYNm00MFVjbDVNMEVLYkVjQWxcblAxSG5UM1JzMVJ0QTUwcjhEcUJGbEhKSFNGMXdVRExWd1lZQXI0WHlXck40VWNOYmEwTFlpaXBqdzlHYUlQMVZcbnNIU1BHbnBBSnBnRkZCVU54VVR2TVREZ2RRS0JnUURGakcxMHVuNnBXdnA2clJkaE9wVW5yU3JSMnh5WEFoWHRcbnExbkloc2cyT2JNSnpidG1WbWkycTNuemovbW55NnhFd2Ird2J6SkMyRGt2dXFRTnIzVVlMYm9TQWI0MjFpU3lcbjZOWEh0NUpsSEFRd3VRZEFOUlJPL0cyQ3VoOXVDMHcrTjJaZDRKU3JCZUkzZ1AreTZhd1hmWmZaZmdTS05IOWVcbkswdVU2eUhHcXdLQmdRQ2JwbERSQWVocXdnTnZpWEx2RGVtdmRSUUp6U1dDMC9JbTIvMlQ1NVlHM0FKMUtDV1NcbmthdExkRmpidDJ3NUNheURoWWZ1M2NGRGJQbzFBV0cwdlRTRTNtYytzeUphL1cwSm5VOGN2K3poVEhOMTcvbDdcbmd6OEw0cDZUT3psTmlXVkJKa3k3ZlgzRjdXRW10b1pYbjFWYjlvR0VXWG5Ja0NDeU1qVlowRGtlb1FLQmdRQ3FcbkJOWWZaSEttcHhwMGdveGdyZDY1S3h4elNMVXVjaWtWU0NnWm9ZYW14TG9HY2Y0YmNicmxuR2QwN0REZDdUanlcblpCM3FaNGxHWm5teFRsenJPbHI0MkVJUVJWZkVNa0diaVRDVWxyVjBOOHlUY210L0l5KzdXeDJWS1VMcm51V2JcbmxtcVAyVDJhZzVIU1d6KzJaODRvMlhyYlFNMy9kSGM2UU9EbjVnWkh5UUtCZ1FDTjQvWHgwNTcvVDlHWE5XdkxcblpRRzFBN204RmZKejh0TEF6MVNCakdYeldUYlI4M0hNekhUUmFuUytMcUdESjZYM0V4ZEJlQnpMbkwyc0NqRkJcbkVvYWNqTVNKVFlhNlhBM1hObXdFd2ZGTm85eTRHNm9NeGFjNXNOaW5GekphaXo4QkYxNzhBeCs1NFllNTYwQVhcbkNUWG9rQzhsaTd4ajVaZXhXc3NUVEdlTEh3PT1cbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiIsCiAgImNsaWVudF9lbWFpbCI6ICJvcy1odWItZHJpdmUtYWNjZXNzQG9zLWh1Yi1pbnRlcm5hbC00ODA5MDkuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTE0NzI1NDc3MTkwOTI1MDI1NDkzIiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9vcy1odWItZHJpdmUtYWNjZXNzJTQwb3MtaHViLWludGVybmFsLTQ4MDkwOS5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsCiAgInVuaXZlcnNlX2RvbWFpbiI6ICJnb29nbGVhcGlzLmNvbSIKfQo=")

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
            required_columns = ["os_id", "us_geoid_county"]
            missing_columns = [
                col for col in required_columns if col not in reader.fieldnames
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

                # Validate required columns
                if "os_id" not in row or not row["os_id"]:
                    logger.warning(
                        f"Row {row_idx}: Missing 'os_id', skipping."
                    )
                    continue

                if "us_geoid_county" not in row or not row["us_geoid_county"]:
                    logger.warning(
                        f"Row {row_idx}: Missing 'us_geoid_county', skipping."
                    )
                    continue

                os_id = row["os_id"].strip()
                us_geoid_county = row["us_geoid_county"].strip()

                # Check if facility exists
                facility = None
                try:
                    facility = Facility.objects.get(id=os_id)
                except Facility.DoesNotExist:
                    logger.warning(
                        f"Row {row_idx}: Facility does not exist "
                        f"with os_id: '{os_id}'. Skipping (MVP only processes "
                        "existing facilities)."
                    )
                    continue

                logger.info(
                    f"Row {row_idx}: Processing os_id='{os_id}', "
                    f"us_geoid_county='{us_geoid_county}'"
                )

                # Build raw_data from CSV row
                # For MVP, we're only processing os_id and us_geoid_county
                # Since we're updating existing facilities, we need minimal data
                raw_data = {
                    "source": ModerationEvent.Source.API.value,
                }

                # Store us_geoid_county (for future processing)
                raw_data["us_geoid_county"] = { "value": str(us_geoid_county) }
                logger.info(
                    f"Row {row_idx}: us_geoid_county value: '{us_geoid_county}'"
                )

                # Create moderation event for updating existing facility
                # Note: MVP version only updates existing facilities with geoid data
                me_creator = ModerationEventCreator(
                    LocationContribution(),
                )
                req_types = ModerationEvent.RequestType
                event_dto = CreateModerationEventDTO(
                    contributor=contributor,
                    raw_data=raw_data,
                    request_type=req_types.UPDATE.value,
                    os=facility,
                )

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

                # Process moderation event (always updating existing facility)
                processor = UpdateProductionLocation(
                    ec_result.moderation_event,
                    user,
                    facility.id,
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

