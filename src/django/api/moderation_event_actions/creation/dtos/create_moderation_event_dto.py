from dataclasses import dataclass, field
from typing import Dict


@dataclass
class CreateModerationEventDTO:
    cleaned_data: Dict = field(default_factory=dict)
    raw_data: Dict = field(default_factory=dict)
    source: str = ''
    errors: Dict = field(default_factory=dict)
