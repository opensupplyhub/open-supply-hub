import copy
from typing import Any, Dict, List

from api.constants import CLAIMED_DOWNLOAD_FIELDS_MAPPING
from api.csv_download import (
    CLAIMED_DOWNLOAD_FIELDS,
    format_download_claimed_fields,
)
from api.helpers.helpers import prefix_a_an
from api.models.facility.facility_manager_index_new import (
    FacilityIndexNewManager,
)
from api.models.partner_field import PartnerField
from api.serializers.facility.facility_download_serializer_base import (
    FacilityDownloadSerializerBase,
)
from api.serializers.facility.mit_living_wage_download_helper import (
    MIT_LIVING_WAGE_DOWNLOAD_HEADERS,
    MITLivingWageDownloadHelper,
)
from api.serializers.facility.partner_field_helper import (
    apply_schema_defaults,
    build_object_field_cells,
    build_primitive_field_cell,
    get_cached_all_partner_fields,
    group_extended_fields_by_name,
    partner_field_property_paths,
)
from api.serializers.facility.wage_indicator_download_helper import (
    WAGE_INDICATOR_DOWNLOAD_HEADERS,
    WageIndicatorDownloadHelper,
)
from api.partner_fields.mit_living_wage_provider import MITLivingWageProvider
from api.partner_fields.wage_indicator_provider import WageIndicatorProvider
from api.trade_union import strip_union_extended_fields


class FacilityDownloadSerializer(FacilityDownloadSerializerBase):
    """Builds CSV headers and rows for full (non-embed) facility downloads."""

    CLAIMED_FIELDS_HEADERS = [
        header for header, _ in CLAIMED_DOWNLOAD_FIELDS_MAPPING
    ]

    PARTNER_FIELD_HEADER_SEPARATOR = "."
    PARTNER_FIELD_VALUE_SEPARATOR = "|"

    def __init__(
        self,
        *args,
        partner_fields: List[PartnerField] | None = None,
        **kwargs,
    ) -> None:
        """Cache partner fields and wage helpers once per download instance.

        Pass ``partner_fields`` to override the active download fields loaded
        from cache (used in tests).
        """
        super().__init__(*args, **kwargs)
        self.__mit_living_wage_helper = MITLivingWageDownloadHelper()
        self.__wage_indicator_helper = WageIndicatorDownloadHelper()

        partner_fields_override = partner_fields is not None
        fields = (
            partner_fields
            if partner_fields_override
            else [
                field
                for field in get_cached_all_partner_fields()
                if field.active and field.available_in_data_downloads
            ]
        )
        fields = sorted(fields, key=lambda field: field.name)
        self.__default_partner_fields = [
            field
            for field in fields
            if (
                partner_fields_override
                or not getattr(field, "system_field", False)
            )
        ]
        self.__system_partner_fields = {
            field.name
            for field in fields
            if getattr(field, "system_field", False)
        }

    def get_headers(self) -> List[str]:
        """Return the ordered CSV column headers for a full download."""
        return [
            *self.COMMON_HEADERS,
            "contributor (list)",
            *self.EXTENDED_FIELDS_HEADERS,
            *self.CLAIMED_FIELDS_HEADERS,
            self.IS_CLOSED_HEADER,
            *self.get_partner_fields_headers(),
            *self.get_mit_living_wage_headers(),
            *self.get_wage_indicator_headers(),
        ]

    def get_row(self, facility: FacilityIndexNewManager) -> List[str]:
        """Return one CSV row for a facility, aligned with ``get_headers``."""
        # Drop union-contributed extended and contributor-supplied partner
        # fields up front. System/synthesized partner fields (MIT living wage,
        # wage indicator) are derived from facility data, not from
        # ``extended_fields``, so they are unaffected (OSDEV-2786).
        extended_fields = strip_union_extended_fields(
            facility.extended_fields, self.exclude_contributor_ids
        )
        return [
            *self.get_common_row(facility),
            self.get_contributors(facility),
            *self.get_extended_fields(extended_fields),
            *self.get_claimed_fields(facility),
            self.get_is_closed(facility),
            *self.get_partner_fields_row(extended_fields),
            *self.get_mit_living_wage_row(facility),
            *self.get_wage_indicator_row(facility),
        ]

    def get_contributors(self, facility: FacilityIndexNewManager) -> str:
        """Return pipe-separated contributor names, marking the claimer when
        present.

        Trade union contributors are omitted entirely when their fields are
        being stripped (OSDEV-2786). Even the anonymized "A Union" form would
        disclose union involvement, so excluded contributors are dropped from
        the column rather than anonymized.
        """
        contributors = []
        claim = facility.approved_claim
        if claim is not None:
            contributors.append("{} (Claimed)".format(
                claim["contributor"]["name"]
            ))

        for contributor in facility.contributors:
            if contributor.get("id") in self.exclude_contributor_ids:
                continue
            contributors.append(
                contributor["name"]
                if contributor["should_display_associations"]
                else "{}".format(prefix_a_an(contributor["contrib_type"]))
            )
        return "|".join(contributors)

    def get_claimed_fields(
        self, facility: FacilityIndexNewManager
    ) -> List[str]:
        """Return claim columns from ``approved_claim``, or empty strings when
        unclaimed."""
        claimed_fields = [""] * len(CLAIMED_DOWNLOAD_FIELDS)
        claim = facility.approved_claim
        if claim:
            format_download_claimed_fields(claim, claimed_fields)
        return claimed_fields

    def get_partner_fields_headers(self) -> List[str]:
        """Return partner-field headers; object schemas expand to dotted
        paths."""
        headers: List[str] = []
        for partner_field in self.__default_partner_fields:
            paths = partner_field_property_paths(partner_field)
            if paths:
                for path in paths:
                    headers.append(
                        self.PARTNER_FIELD_HEADER_SEPARATOR.join(
                            (partner_field.name, *path)
                        )
                    )
            else:
                headers.append(partner_field.name)
        return headers

    def get_partner_fields_row(
        self,
        extended_fields: List[Dict[str, Any]],
    ) -> List[str]:
        """Return partner-field cells aligned with
        ``get_partner_fields_headers``."""
        grouped = group_extended_fields_by_name(extended_fields)
        separator = self.PARTNER_FIELD_VALUE_SEPARATOR
        row: List[str] = []

        for partner_field in self.__default_partner_fields:
            entries = copy.deepcopy(grouped.get(partner_field.name, []))

            for entry in entries:
                if not isinstance(entry, dict):
                    continue

                value = entry.get("value", {})

                if not isinstance(value, dict):
                    continue

                if "raw_values" not in value:
                    continue

                raw_values = value.get("raw_values", {})

                if not isinstance(raw_values, dict):
                    continue

                schema = partner_field.json_schema

                if not isinstance(schema, dict):
                    continue

                entry["value"]["raw_values"] = apply_schema_defaults(
                    raw_values,
                    schema,
                )

            paths = partner_field_property_paths(partner_field)

            if paths:
                row.extend(build_object_field_cells(entries, paths, separator))
            else:
                row.append(build_primitive_field_cell(entries, separator))

        return row

    def get_mit_living_wage_headers(self) -> List[str]:
        """Return MIT living wage columns when that system partner field is
        active."""
        field_name = MITLivingWageProvider.FIELD_NAME
        if field_name not in self.__system_partner_fields:
            return []
        return MIT_LIVING_WAGE_DOWNLOAD_HEADERS

    def get_mit_living_wage_row(
        self, facility: FacilityIndexNewManager
    ) -> List[str]:
        """Return MIT living wage cells, or empty strings when data is
        unavailable."""
        field_name = MITLivingWageProvider.FIELD_NAME
        if field_name not in self.__system_partner_fields:
            return []
        return self.__mit_living_wage_helper.get_cells(facility)

    def get_wage_indicator_headers(self) -> List[str]:
        """Return wage indicator columns when that system partner field is
        active."""
        field_name = WageIndicatorProvider.FIELD_NAME
        if field_name not in self.__system_partner_fields:
            return []
        return WAGE_INDICATOR_DOWNLOAD_HEADERS

    def get_wage_indicator_row(
        self, facility: FacilityIndexNewManager
    ) -> List[str]:
        """Return wage indicator cells, or empty strings when data is
        unavailable."""
        field_name = WageIndicatorProvider.FIELD_NAME
        if field_name not in self.__system_partner_fields:
            return []
        return self.__wage_indicator_helper.get_cells(facility)
