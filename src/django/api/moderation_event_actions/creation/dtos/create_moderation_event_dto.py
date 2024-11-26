from dataclasses import dataclass, field
from typing import Dict

from rest_framework import status

from api.models.moderation_event import ModerationEvent


@dataclass
class CreateModerationEventDTO:
    contributor_id: int
    raw_data: Dict
    request_type: str
    cleaned_data: Dict = field(default_factory=dict)
    source: str = ''
    geocode_result: Dict = field(default_factory=dict)
    errors: Dict = field(default_factory=dict)
    status_code: int = status.HTTP_202_ACCEPTED
    moderation_event: ModerationEvent = None
