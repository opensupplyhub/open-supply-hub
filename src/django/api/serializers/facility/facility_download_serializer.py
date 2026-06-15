from typing import List
from api.models.facility.facility_manager_index_new \
    import FacilityIndexNewManager
from api.helpers.helpers import prefix_a_an
from api.serializers.facility.facility_download_serializer_base import (
    FacilityDownloadSerializerBase,
)


class FacilityDownloadSerializer(FacilityDownloadSerializerBase):
    def get_headers(self) -> List[str]:
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
        return [
            *self.get_common_row(facility),
            self.get_contributors(facility),
            *self.get_extended_fields(facility.extended_fields),
            *self.get_claimed_fields(facility),
            self.get_is_closed(facility),
            *self.get_partner_fields_row(facility.extended_fields),
            *self.get_mit_living_wage_row(facility),
            *self.get_wage_indicator_row(facility),
        ]

    def get_contributors(self, facility: FacilityIndexNewManager) -> str:
        contributors = []
        claim = facility.approved_claim
        if claim is not None:
            contributors.append("{} (Claimed)".format(
                claim["contributor"]["name"]
            ))

        for contributor in facility.contributors:
            contributors.append(
                contributor["name"]
                if contributor["should_display_associations"]
                else "{}".format(prefix_a_an(contributor["contrib_type"]))
            )
        return "|".join(contributors)
