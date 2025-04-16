from dataclasses import dataclass, field
from typing import Dict

from rest_framework import status

from api.models.moderation_event import ModerationEvent
from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility


@dataclass
class CreateModerationEventDTO:
    contributor: Contributor
    raw_data: Dict
    request_type: str
    os: Facility = None
    cleaned_data: Dict = field(default_factory=dict)
    source: str = ''
    geocode_result: Dict = field(default_factory=dict)
    errors: Dict = field(default_factory=dict)
    status_code: int = status.HTTP_202_ACCEPTED
    moderation_event: ModerationEvent = None
