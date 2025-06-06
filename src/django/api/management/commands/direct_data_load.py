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
import string


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
            "--tab_id",
            type=int,
            help="The numeric ID of the Google Sheet tab to load data from.",
            required=True,
        )
        parser.add_argument(
            "--sheet_name",
            type=str,
            help="The name of the Google Sheet to load data from.",
            required=True
        )
        parser.add_argument(
            "--start_row",
            type=int,
            help="The row number to start from (1-based index).",
            default=2,
            required=False,
        )
        parser.add_argument(
            "--end_row",
            type=int,
            help="The row number to stop reading from (1-based index).",
            default=None,
            required=True,
        )
        parser.add_argument(
            "--columns",
            type=str,
            help="Comma-separated list of columns to read from.",
            required=True,
        )
        parser.add_argument(
            '--re_geocode',
            dest='re_geocode',
            action='store_true',
            help="Force re-geocoding of addresses every time.",
        )
        parser.set_defaults(re_geocode=False)
        parser.add_argument(
            '--skip_existing',
            dest='skip_existing',
            action='store_true',
            help="Skip existing facilities in the database.",
        )
        parser.set_defaults(skip_existing=False)

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

        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

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
        col_names = [col_name.upper() for col_name in list(
            string.ascii_uppercase[:len(columns)])]
        start_range = f'{col_names[0]}{options["start_row"]}'
        end_range = f'{col_names[len(col_names) - 1]}{options["end_row"]}'
        col_range = f'{options["sheet_name"]}!{start_range}:{end_range}'

        logger.info(
            f"Fetching data from sheet ID: '{sheet_id}' range: '{col_range}'"
        )

        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=col_range,
        ).execute()

        logger.info(
            f"Fetched data from sheet ID: '{sheet_id}' range: '{col_range}'"
        )

        rows = result.get("values", [])

        if not rows:
            raise ValueError(
                "No data found in the spreadsheet."
            )

        logger.info(f"Data fetched successfully: '{len(rows)}' rows")
        row_idx = options["start_row"] - 1

        for row in rows:
            row_idx += 1
            logger.info(f"Processing row: '{row_idx}'")
            record = {}

            for col_idx, column in enumerate(columns):
                record[column] = None

                if col_idx < len(row):
                    record[column] = row[col_idx]

            facility = None

            if "os_id" not in record:
                raise ValueError(
                    f"Column 'os_id' is required but not found, row: '{row_idx}'"
                )

            try:
                facility = Facility.objects.get(id=record["os_id"])
            except Facility.DoesNotExist:
                logger.info(
                    "Facility does not exist" +
                    f" os_id: '{record['os_id']}' row: '{row_idx}'."
                )

            if options["skip_existing"] and facility:
                logger.info(
                    "Skipping facility with os_id: " +
                    f"'{record['os_id']}' row: '{row_idx}'."
                )
                continue

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
                raw_data["country"] = record["country"].replace(
                    '\u00a0', ' ')  # fix non-breaking space

            has_lat_lng = "lat" in record and "lng" in record

            if has_lat_lng and record["lat"] and record["lng"]:
                raw_data["coordinates"] = {
                    "lat": record["lat"],
                    "lng": record["lng"],
                }

            if not options["re_geocode"] and facility and facility.location:
                raw_data["coordinates"] = {
                    "lat": facility.location.coords[1],
                    "lng": facility.location.coords[0],
                }
                logger.info(
                    f"Setting coordinates ID: '{facility.id}' row: '{row_idx}'"
                )
            else:
                os_id = record["os_id"]
                logger.info(
                    f"Geocoding ID: '{os_id}' row: '{row_idx}'"
                )

            if "sector" in record and record["sector"]:
                raw_data["sector"] = record["sector"]

            if "facility_type" in record and record["facility_type"]:
                facility_type = record["facility_type"].split(",")
                raw_data["location_type"] = [
                    f_type.strip() for f_type in facility_type
                ]

            if "processing_type" in record and record["processing_type"]:
                processing_type = record["processing_type"].split(",")
                raw_data["processing_type"] = [
                    p_type.strip() for p_type in processing_type
                ]

            if "product_type" in record and record["product_type"]:
                product_type = record["product_type"].split(",")
                raw_data["product_type"] = [
                    p_type.strip() for p_type in product_type
                ]

            has_parent_company = "parent_company_os_id" in record

            if has_parent_company and record["parent_company_os_id"]:
                pc_os_id = record["parent_company_os_id"].split(",")
                raw_data["parent_company_os_id"] = [
                    p_id.strip() for p_id in pc_os_id
                ]

            me_creator = ModerationEventCreator(
                LocationContribution(),
            )
            req_types = ModerationEvent.RequestType
            event_dto = CreateModerationEventDTO(
                contributor=contributor,
                raw_data=raw_data,
                request_type=req_types.CREATE.value
            )

            if facility:
                event_dto.os = facility
                event_dto.request_type = req_types.UPDATE.value

            try:
                ec_result = me_creator.perform_event_creation(event_dto)
            except Exception as error:
                logger.error(
                    "Error creating event" +
                    f"row:'{row_idx}': err: '{str(error)}'"
                )
                break

            if ec_result.errors:
                mark_row(
                    service=service,
                    spreadsheet_id=sheet_id,
                    tab_id=options["tab_id"],
                    row_index=row_idx - 1,
                    num_columns=len(columns) + 1,
                    col_index=columns.index("error"),
                    message=json.dumps(ec_result.errors),
                    format={
                        "backgroundColor": {
                            "red": 1.0,
                            "green": 0.8,
                            "blue": 0.8,
                        },
                    },
                )
                logger.error(
                    "Error in row" +
                    f"'{row_idx}': '{json.dumps(ec_result.errors)}'"
                )
                continue
            elif "error" in record and record["error"]:
                mark_row(
                    service=service,
                    spreadsheet_id=sheet_id,
                    tab_id=options["tab_id"],
                    row_index=row_idx - 1,
                    num_columns=len(columns) + 1,
                    col_index=columns.index("error"),
                    message="",
                )

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
                    f"Processed row: '{row_idx}' ID: '{item.facility_id}'"
                )
            except Exception as error:
                ModerationEvent.objects.filter(
                    uuid=ec_result.moderation_event.uuid
                ).update(
                    status=ModerationEvent.Status.REJECTED.value,
                    action_reason_text_cleaned="direct upload error",
                    action_reason_text_raw="<p>direct upload error</p>\n"
                )
                logger.error(
                    f"Error processing row '{row_idx}': '{str(error)}'"
                )
                break


def mark_row(
        service,
        spreadsheet_id,
        tab_id,
        row_index,
        num_columns,
        col_index,
        message,
        format={}):
    """
    Highlights the specified row in red and sets an error message.
    - service: Google Sheets API service object
    - spreadsheet_id: The spreadsheet ID
    - tab_id: The numeric sheet ID (not the name)
    - row_index: Zero-based row index to highlight
    - num_columns: Number of columns to highlight (e.g., len(columns))
    - col_index: Zero-based column index to write the error message
    - message: The error message to write
    - format: a dictionary containing the formatting to be applied to the row
    """
    requests = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": tab_id,
                    "startRowIndex": row_index,
                    "endRowIndex": row_index + 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": num_columns,
                },
                "cell": {
                    "userEnteredFormat": format,
                },
                "fields": "userEnteredFormat.backgroundColor",
            }
        },
        {
            "updateCells": {
                "rows": [
                    {
                        "values": [
                            {
                                "userEnteredValue": {
                                    "stringValue": message,
                                }
                            }
                        ]
                    }
                ],
                "fields": "userEnteredValue",
                "start": {
                    "sheetId": tab_id,
                    "rowIndex": row_index,
                    "columnIndex": col_index,
                }
            }
        }
    ]
    body = {"requests": requests}
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body
    ).execute()
