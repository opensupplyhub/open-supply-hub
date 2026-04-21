from typing import Any, Dict, Iterable, List
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
from api.serializers.facility.mit_living_wage_download_helper import (
    MIT_LIVING_WAGE_DOWNLOAD_HEADERS,
    MITLivingWageDownloadHelper,
)
from api.serializers.facility.partner_field_helper import (
    build_object_field_cells,
    build_primitive_field_cell,
    group_extended_fields_by_name,
    partner_field_property_paths,
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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Built once per serializer instance so the `mit_living_wage`
        # PartnerField lookup and the provider are reused for every row
        # in a paginated download instead of being rebuilt per facility.
        self.__mit_living_wage_helper = MITLivingWageDownloadHelper()

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
        separator = cls.PARTNER_FIELD_VALUE_SEPARATOR
        row: List[str] = []

        for partner_field in partner_fields:
            entries = grouped.get(partner_field.name, [])
            paths = partner_field_property_paths(partner_field)

            if paths:
                row.extend(
                    build_object_field_cells(entries, paths, separator)
                )
            else:
                row.append(build_primitive_field_cell(entries, separator))

        return row

    def get_mit_living_wage_headers(self) -> List[str]:
        '''
        Download-only headers for the `mit_living_wage` system partner
        field. Kept separate from `get_partner_fields_headers` because
        `mit_living_wage` is filtered out of the regular active-partner
        pipeline (it has `system_field=True`) and the two columns are
        synthesized at download time from the provider + partner-field
        row, not from `facility.extended_fields`.
        '''
        return MIT_LIVING_WAGE_DOWNLOAD_HEADERS

    def get_mit_living_wage_row(
        self, facility: FacilityIndexNewManager
    ) -> List[str]:
        '''
        Download-only cells matching `get_mit_living_wage_headers`.
        Returns two empty strings for any facility the MIT provider
        can't resolve (non-US/PR/VI, no TIGER/Line match, missing
        partner-field row, etc.).
        '''
        return self.__mit_living_wage_helper.get_cells(facility)
