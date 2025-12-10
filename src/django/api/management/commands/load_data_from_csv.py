import csv
import logging
from pathlib import Path
from django.core.management.base import BaseCommand
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
        "Load data from a local CSV file (MVP version). "
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
            "--csv_path",
            type=str,
            help=(
                "Path to the CSV file. "
                "Defaults to test_osid_geoid_df.csv in project root"
            ),
            default=None,
        )

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

        # Determine CSV file path
        if options["csv_path"]:
            csv_path = Path(options["csv_path"])
        else:
            # Default to project root/test_osid_geoid_df.csv
            # Navigate from command file to project root
            # Command file location: .../api/management/commands/load_data_from_csv.py
            # Go up 4 levels to reach project root
            command_file = Path(__file__)
            project_root = command_file.parent.parent.parent.parent
            csv_path = project_root / "test_osid_geoid_df.csv"

        if not csv_path.exists():
            raise ValueError(
                f"CSV file not found at: {csv_path}. "
                "Please provide a valid path using --csv_path."
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

