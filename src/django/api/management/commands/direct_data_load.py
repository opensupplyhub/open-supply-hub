import os
import base64
import json
from django.core.management.base import BaseCommand
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
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


class AddProductionLocationWithOsID(AddProductionLocation):
    def __init__(
        self,
        moderation_event: ModerationEvent,
        moderator: User,
        os_id: str = None
    ) -> None:
        super().__init__(moderation_event, moderator)
        self.__os_id = os_id

    def _get_os_id(self, _: str) -> str:
        return self.__os_id


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load data directly into the database from a google sheet."

    def add_arguments(self, parser):
        parser.add_argument(
            "--user_id",
            type=int,
            help="The ID of the user performing the data load.",
            required=True,
        )
        parser.add_argument(
            "--contributor_id",
            type=int,
            help="The ID of the contributor performing the data load.",
            required=True,
        )
        parser.add_argument(
            "--sheet_id",
            type=str,
            help="The ID of the Google Sheet to load data from.",
            required=True,
        )
        parser.add_argument(
            "--range",
            type=str,
            help="The range of cells to read from the Google Sheet.",
            required=True,
        )
        parser.add_argument(
            "--columns",
            type=str,
            help="Comma-separated list of columns to read from the Google Sheet in particular order.",
            required=True,
        )

    def handle(self, *args, **options):
        user_id = options["user_id"]

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError(f"User with ID '{user_id}' does not exist.")

        contributor_id = options["contributor_id"]

        try:
            contributor = Contributor.objects.get(id=contributor_id)
        except Contributor.DoesNotExist:
            raise ValueError(
                f"Contributor with ID '{contributor_id}' does not exist."
            )

        columns = []

        for col in options["columns"].split(","):
            columns.append(col.strip())

        if not columns:
            raise ValueError("No columns specified for data loading.")

        SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

        base64_gdrive_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_CREDS_BASE64")

        if base64_gdrive_creds is None:
            raise ValueError("Google Service Account credentials not found!")

        decoded_creds = base64.b64decode(base64_gdrive_creds).decode("utf-8")

        credentials = service_account.Credentials.from_service_account_info(
            info=json.loads(decoded_creds),
            scopes=SCOPES,
        )
        logger.info("Initialized Google service account credentials")

        sheet_id = options["sheet_id"]

        logger.info(
            f"Starting data load from Google Sheet with ID: {sheet_id}")

        service = build(
            "sheets",
            "v4",
            credentials=credentials,
        )

        logger.info("Built Google Sheets service")

        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=options["range"],  # Adjust the range as needed
        ).execute()

        logger.info(
            f"Fetched data from Google Sheet with ID: '{sheet_id}' and range: '{options['range']}'"
        )

        rows = result.get("values", [])

        if not rows:
            raise ValueError(
                "No data found in the spreadsheet. Please check the range and sheet ID."
            )

        logger.info(f"Data fetched successfully: '{len(rows)}' rows")

        for idx, row in enumerate(rows):
            logger.info(f"Processing row: '{idx + 1}'")
            record = {}

            for col_idx, column in enumerate(columns):
                record[column] = None

                if col_idx < len(row):
                    record[column] = row[col_idx]

            facility = None

            if "os_id" in record and record["os_id"]:
                try:
                    facility = Facility.objects.get(id=record["os_id"])
                except Facility.DoesNotExist:
                    logger.info(
                        f"Facility with os_id '{record['os_id']}' does not exist."
                    )

            raw_data = {
                "source": ModerationEvent.Source.API.value,
            }

            if "rba_id" in record and record["rba_id"]:
                raw_data["rba_id"] = record["rba_id"]

            if "name" in record and record["name"]:
                raw_data["name"] = record["name"]

            if "address" in record and record["address"]:
                raw_data["address"] = record["address"]

            if "country" in record and record["country"]:
                raw_data["country"] = record["country"]

            if "lat" in record and "lng" in record and record["lat"] and record["lng"]:
                raw_data["coordinates"] = {
                    "lat": record["lat"],
                    "lng": record["lng"],
                }

            if "sector" in record and record["sector"]:
                raw_data["sector"] = record["sector"]

            if "facility_type" in record and record["facility_type"]:
                raw_data["location_type"] = [
                    f_type.strip() for f_type in record["facility_type"].split(",")
                ]

            if "processing_type" in record and record["processing_type"]:
                raw_data["processing_type"] = [
                    p_type.strip() for p_type in record["processing_type"].split(",")
                ]

            if "product_type" in record and record["product_type"]:
                raw_data["product_type"] = [
                    p_type.strip() for p_type in record["product_type"].split(",")
                ]

            if "parent_company_os_id" in record and record["parent_company_os_id"]:
                raw_data["parent_company_os_id"] = [
                    p_id.strip() for p_id in record["parent_company_os_id"].split(",")
                ]

            me_creator = ModerationEventCreator(
                LocationContribution(),
            )
            event_dto = CreateModerationEventDTO(
                contributor=contributor,
                raw_data=raw_data,
                request_type=ModerationEvent.RequestType.CREATE.value
            )

            if facility:
                event_dto.os = facility
                event_dto.request_type = ModerationEvent.RequestType.UPDATE.value

            try:
                ec_result = me_creator.perform_event_creation(
                    event_dto)
            except Exception as error:
                logger.error(
                    f"Error creating moderation event for row {idx + 1}: {str(error)}"
                )
                break

            if ec_result.errors:
                logger.error(
                    f"Error processing row {idx + 1}: {json.dumps(ec_result.errors)}"
                )
                break

            processor = AddProductionLocationWithOsID(
                ec_result.moderation_event,
                user,
                record.get("os_id"),
            )

            if facility:
                processor = UpdateProductionLocation(
                    ec_result.moderation_event,
                    user,
                    facility.id,
                )

            try:
                item = processor.process_moderation_event()
                logger.info(
                    f"Processed row {idx + 1} successfully: {item.facility_id}"
                )
            except Exception as error:
                logger.error(
                    f"Error processing row {idx + 1}: {str(error)}"
                )
                break
