from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

from api.models import Contributor
from api.models.partner_field import PartnerField
from api.models.facility.facility import Facility

logger = logging.getLogger(__name__)

_UNSET = object()


class SystemPartnerFieldProvider(ABC):
    """
    Abstract base class for system-generated partner field data providers.

    Each provider knows how to fetch and format data for a specific
    system partner field type (e.g., wage_indicator, etc.).
    """

    # Whether `fetch_data` logs a warning when a location has no raw
    # data. The hard-wired providers keep this on: their datasets are
    # expected to cover every location they are asked about, so a miss
    # is worth a line. A provider whose normal case is "no value here"
    # (a zone set covers only part of the globe) turns it off, or the
    # details endpoint would log one warning per location per dataset.
    log_missing_raw_data = True

    def fetch_data(
        self,
        production_location: Facility,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch and format data for the given production location.
        Returns None if no data or contributor not found.
        """
        raw_data = self._fetch_raw_data(production_location)
        field_name = self._get_field_name()

        if raw_data is None:
            if self.log_missing_raw_data:
                logger.warning(
                    f"No raw data found for '{field_name}' partner field. "
                    f"Production location '{production_location.id}' ID"
                )
            return None

        contributor_info = self.__get_contributor_info()

        if contributor_info is None:
            logger.warning(
                f"No contributor found for '{field_name}' partner field. "
                f"Production location '{production_location.id}' ID"
            )
            return None

        return self._format_data(
            raw_data=raw_data,
            contributor_info=contributor_info,
        )

    def fetch_only_raw_values(
        self,
        production_location: Facility,
    ) -> Optional[Dict[str, Any]]:
        """
        Download-only fast path. Returns just the `raw_values` dict
        produced by `_format_data`, skipping the `PartnerField` +
        `Contributor` lookup that `fetch_data` does for the details
        endpoint.

        Returns `None` if no raw data is available or the formatted
        payload has no `raw_values` dict.
        """
        raw_data = self._fetch_raw_data(production_location)
        if raw_data is None:
            return None

        formatted = self._format_data(
            raw_data=raw_data,
            contributor_info=None,
        )
        value = (
            formatted.get("value") if isinstance(formatted, dict) else None
        )
        raw_values = (
            value.get("raw_values") if isinstance(value, dict) else None
        )
        if not isinstance(raw_values, dict):
            return None
        return raw_values

    @abstractmethod
    def _get_field_name(self) -> str:
        """
        Return the partner field name for this provider.
        Each provider must define its own field name.
        """
        pass

    @abstractmethod
    def _fetch_raw_data(self, production_location: Facility) -> Optional[Any]:
        """Fetch raw data from the data source."""
        pass

    @abstractmethod
    def _format_data(
        self,
        raw_data: Any,
        contributor_info: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Format raw data into the standard partner field structure."""
        pass

    def __get_contributor_info(self) -> Optional[Dict[str, Any]]:
        """
        Contributor information for this provider's partner field,
        looked up once per instance.

        The partner field and its contributor do not change between the
        locations one request serializes, so the two queries behind
        them run on the first `fetch_data` call and are reused after
        that (including a `None` result, so a field nobody holds is
        not re-checked per location). The registry hands out fresh
        provider instances on each access, which keeps this cache
        request-scoped: an admin change shows up on the next request.
        Subclasses need not call `super().__init__()` for this to work.
        """
        cached = getattr(self, '_contributor_info', _UNSET)
        if cached is _UNSET:
            cached = self.__load_contributor_info()
            self._contributor_info = cached
        return cached

    def __load_contributor_info(self) -> Optional[Dict[str, Any]]:
        """
        Fetch contributor information from database.
        Returns None if contributor not found or contributor_id is None.
        """
        field_name = self._get_field_name()

        try:
            objects = PartnerField.objects.get_all_including_inactive()
            partner_field = objects.get(name=field_name)
        except PartnerField.DoesNotExist:
            logger.warning(
                f"Partner field '{field_name}' not found. "
                "System field must exist in database."
            )
            return None

        contributor = (
            Contributor.objects.filter(partner_fields=partner_field)
            .order_by("id")
            .first()
        )

        if not contributor:
            logger.warning(
                f"No contributor found for '{field_name}' partner field.",
            )
            return None

        return {
            "id": contributor.id,
            "name": contributor.name,
            "admin_id": contributor.admin_id,
            "is_verified": contributor.is_verified,
            "contrib_type": contributor.contrib_type,
        }
