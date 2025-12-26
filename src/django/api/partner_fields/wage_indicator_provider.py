import logging
from typing import Dict, Any, Optional

from api.models.wage_indicator_country_data import WageIndicatorCountryData
from api.partner_fields.base_provider import SystemPartnerFieldProvider
from api.models.facility.facility import Facility


logger = logging.getLogger(__name__)


class WageIndicatorProvider(SystemPartnerFieldProvider):
    """
    Provides wage indicator data based on production location country code.
    Fetches data from WageIndicatorCountryData table.
    """

    def _get_field_name(self) -> str:
        """Return the partner field name for this provider."""
        return "wage_indicator"

    def _fetch_raw_data(
        self,
        production_location: Facility,
    ) -> Optional[WageIndicatorCountryData]:
        """Fetch wage indicator data from database by country code."""
        try:
            return WageIndicatorCountryData.objects.get(
                country_code=production_location.country_code,
            )
        except WageIndicatorCountryData.DoesNotExist:
            logger.warning(
                f"WageIndicator not found for `{production_location.country_code}` country code."
                f"Production location `{production_location.id}` ID."
            )

        return None

    def _format_data(
        self, raw_data: WageIndicatorCountryData, contributor_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format wage indicator data into standard partner field structure.
        """
        links_with_text = raw_data.get_links_with_text()

        raw_values = {}

        for link in links_with_text:
            link_type = link["type"]
            raw_values[link_type] = link["url"]
            raw_values[f"{link_type}_text"] = link["text"]

        return {
            "id": None,
            "value": {
                "raw_values": raw_values,
            },
            "created_at": raw_data.created_at.isoformat(),
            "updated_at": raw_data.updated_at.isoformat(),
            "field_name": self._get_field_name(),
            "contributor": contributor_info,
            "is_verified": False,
            "value_count": 1,
            "facility_list_item_id": 1111,
            "should_display_association": True,
        }
