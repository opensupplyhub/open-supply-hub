import json
from typing import Mapping

from api.models.facility.facility import Facility
from api.models.moderation_event import ModerationEvent
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto import (  # noqa: E501
    CreateModerationEventDTO,
)
from api.moderation_event_actions.creation.moderation_event_creator import (
    ModerationEventCreator,
)
from api.partner_data_file_upload.parsing.parser import PartnerFieldSheetParser
from api.partner_data_file_upload.parsing.types import ColumnMapping


class PartnerPatchModerationEventCreator:
    def __init__(self, me_creator: ModerationEventCreator):
        self.me_creator = me_creator

    def create(
        self,
        contributor,
        record: Mapping[str, object],
        column_mappings: Mapping[str, ColumnMapping],
    ) -> str:
        os_id = str(record.get("os_id") or "").strip()
        if not os_id:
            raise ValueError("Missing required value for 'os_id'")

        try:
            facility = Facility.objects.get(id=os_id)
        except Facility.DoesNotExist as error:
            raise ValueError(
                f"Facility with os_id '{os_id}' was not found"
            ) from error

        raw_data = PartnerFieldSheetParser.build_patch_raw_data(
            record,
            column_mappings,
        )
        event_dto = CreateModerationEventDTO(
            contributor=contributor,
            raw_data=raw_data,
            request_type=ModerationEvent.RequestType.UPDATE.value,
            os=facility,
        )
        result = self.me_creator.perform_event_creation(event_dto)
        if result.errors:
            raise ValueError(self.format_api_errors(result.errors))

        return str(result.moderation_event.uuid)

    @staticmethod
    def format_api_errors(errors: Mapping[str, object]) -> str:
        if not errors:
            return "Unknown error."

        messages = []
        detail = errors.get("detail")
        if isinstance(detail, str) and detail:
            messages.append(detail)

        error_items = errors.get("errors", [])
        if isinstance(error_items, list):
            for item in error_items:
                if isinstance(item, dict):
                    field = item.get("field", "")
                    item_detail = item.get("detail", "")
                    if field and item_detail:
                        messages.append(f"{field}: {item_detail}")
                    elif item_detail:
                        messages.append(str(item_detail))
                    elif field:
                        messages.append(str(field))
                elif item:
                    messages.append(str(item))

        if messages:
            return "; ".join(messages)

        return json.dumps(errors)
