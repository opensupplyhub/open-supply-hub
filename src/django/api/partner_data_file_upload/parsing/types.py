from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional

from api.models.partner_field import PartnerField

if TYPE_CHECKING:
    from api.partner_data_file_upload.sheets.client import SheetWorkbook


def header_label(header) -> str:
    if header is None:
        return ""
    return str(header)


@dataclass
class ColumnMapping:
    column_name: str
    partner_field: PartnerField
    path_segments: Optional[List[str]] = None
    leaf_schema: Optional[dict] = None


@dataclass
class SheetProcessingContext:
    workbook: "SheetWorkbook"
    data_columns: List[str]
    header_map: Dict[str, int]
    column_mappings: Dict[str, ColumnMapping]
    partner_fields_by_name: Dict[str, PartnerField]
    tracking_columns: Dict[str, int]
    cols_count: int
