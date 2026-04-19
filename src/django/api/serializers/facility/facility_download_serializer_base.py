from typing import Any, Dict, Iterable, List, Tuple
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.facility_manager_index_new import (
    FacilityIndexNewManager,
)
from api.models.partner_field import PartnerField
from countries.lib.countries import COUNTRY_NAMES
from api.csv_download import (
    format_download_extended_fields,
    format_download_claimed_fields,
    CLAIMED_DOWNLOAD_FIELDS,
)
from api.constants import CLAIMED_DOWNLOAD_FIELDS_MAPPING
from api.helpers.helpers import parse_download_date
from api.serializers.facility.partner_field_helper import (
    group_extended_fields_by_name,
    is_empty_partner_value,
    partner_field_property_paths,
    resolve_nested_value,
)
from rest_framework.serializers import Serializer, SerializerMethodField


class FacilityDownloadSerializerBase(Serializer):
    row = SerializerMethodField()

    class Meta:
        model = FacilityIndex()
        fields = "rows"

    EXTENDED_FIELDS_HEADERS = [
        "number_of_workers",
        "parent_company",
        "processing_type_facility_type_raw",
        "facility_type",
        "processing_type",
        "product_type",
    ]
    COMMON_HEADERS = [
        "os_id",
        "contribution_date",
        "name",
        "address",
        "country_code",
        "country_name",
        "lat",
        "lng",
        "sector",
    ]
    IS_CLOSED_HEADER = "is_closed"

    CLAIMED_FIELDS_HEADERS = [
        header for header, _ in CLAIMED_DOWNLOAD_FIELDS_MAPPING
    ]

    PARTNER_FIELD_HEADER_SEPARATOR = "."
    PARTNER_FIELD_VALUE_SEPARATOR = "|"

    def get_common_row(self, facility: FacilityIndexNewManager):
        return [
            facility.id,
            self.get_contribution_date(facility),
            self.get_name(facility),
            facility.address,
            facility.country_code,
            self.get_country_name(facility),
            *self.get_location(facility),
            self.get_sector(facility),
        ]

    @staticmethod
    def get_contribution_date(facility: FacilityIndexNewManager) -> str:
        created_at = facility.created_from_info["created_at"]
        return parse_download_date(created_at)

    @staticmethod
    def get_name(facility: FacilityIndexNewManager) -> str:
        claim = facility.approved_claim
        if claim and claim.get("facility_name_english"):
            return claim.get("facility_name_english")
        return facility.name

    @staticmethod
    def get_country_name(facility: FacilityIndexNewManager) -> str:
        return COUNTRY_NAMES.get(facility.country_code, "")

    @staticmethod
    def get_location(facility: FacilityIndexNewManager) -> List[str]:
        return list(reversed(facility.location.coords))

    def get_sector(self, facility: FacilityIndex):
        return self.join(facility.sector)

    def get_extended_fields(self, fields) -> List[Any]:
        extended_fields = [[], [], [], [], [], []]
        format_download_extended_fields(fields, extended_fields)

        return list(map("|".join, extended_fields))

    def get_claimed_fields(
            self,
            facility: FacilityIndexNewManager
    ) -> List[str]:
        claimed_fields = [''] * len(CLAIMED_DOWNLOAD_FIELDS)
        claim = facility.approved_claim
        if claim:
            format_download_claimed_fields(claim, claimed_fields)
        return claimed_fields

    @staticmethod
    def get_is_closed(facility: FacilityIndexNewManager) -> str:
        return str(
            facility.is_closed if facility.is_closed is not None else False
        )

    @staticmethod
    def join(arr: List[Any]) -> str:
        return "|".join([item.title() for item in arr])

    @classmethod
    def get_partner_fields_headers(
        cls, partner_fields: Iterable[PartnerField]
    ) -> List[str]:
        '''
        Build CSV headers for the provided active partner fields.

        - Object-typed partner fields with a JSON Schema expand into one
          column per leaf property, joining the path with ".". Nested
          objects are walked recursively until a non-object leaf is
          reached (e.g. "amfori.bsci_audit.submission_date").
        - Any other partner field (or missing schema) emits a single
          column named after the partner field itself.
        '''
        headers: List[str] = []
        for partner_field in partner_fields:
            paths = partner_field_property_paths(partner_field)
            if paths:
                for path in paths:
                    headers.append(
                        cls.PARTNER_FIELD_HEADER_SEPARATOR.join(
                            (partner_field.name, *path)
                        )
                    )
            else:
                headers.append(partner_field.name)
        return headers

    @classmethod
    def get_partner_fields_row(
        cls,
        extended_fields: List[Dict[str, Any]],
        partner_fields: Iterable[PartnerField],
    ) -> List[str]:
        '''
        Build CSV row cells for the provided active partner fields by
        matching each partner field's `name` against entries in the
        facility's `extended_fields`.

        For object-typed partner fields with a JSON Schema each stored
        `raw_values` dict is walked following the schema leaf paths so
        the output columns stay aligned with `get_partner_fields_headers`.
        Multiple contributions for the same partner field on one facility
        are joined with "|" per leaf column (consistent with the existing
        extended-field behavior).
        '''
        grouped = group_extended_fields_by_name(extended_fields)
        row: List[str] = []

        for partner_field in partner_fields:
            entries = grouped.get(partner_field.name, [])
            paths = partner_field_property_paths(partner_field)

            if paths:
                collected: Dict[Tuple[str, ...], List[str]] = {
                    path: [] for path in paths
                }
                for entry in entries:
                    raw_values = (entry.get("value") or {}).get("raw_values")
                    if not isinstance(raw_values, dict):
                        continue
                    for path in paths:
                        value = resolve_nested_value(raw_values, path)
                        if is_empty_partner_value(value):
                            continue
                        collected[path].append(str(value))
                for path in paths:
                    row.append(
                        cls.PARTNER_FIELD_VALUE_SEPARATOR.join(
                            collected[path]
                        )
                    )
            else:
                values: List[str] = []
                for entry in entries:
                    raw_value = (entry.get("value") or {}).get("raw_value")
                    if is_empty_partner_value(raw_value):
                        continue
                    values.append(str(raw_value))
                row.append(
                    cls.PARTNER_FIELD_VALUE_SEPARATOR.join(values)
                )

        return row
