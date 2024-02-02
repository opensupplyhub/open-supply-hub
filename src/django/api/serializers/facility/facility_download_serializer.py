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
            self.IS_CLOSED_HEADER,
        ]

    def get_row(self, facility: FacilityIndexNewManager) -> List[str]:
        return [
            *self.get_common_row(facility),
            self.get_contributors(facility),
            *self.get_extended_fields(self.get_extended_fields_raw(facility)),
            self.get_is_closed(facility),
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

    def check_contributor(
        self, facility: FacilityIndexNewManager, contributor_id: int
    ) -> bool:
        claim = facility.approved_claim
        if claim is None:
            return True

        return claim["contributor_id"] == contributor_id

    def get_extended_fields_raw(self, facility: FacilityIndexNewManager):
        return [
            field
            for field in facility.extended_fields
            if self.check_contributor(facility, field["contributor"]["id"])
        ]
