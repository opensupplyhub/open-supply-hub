from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

from api.models import Contributor
from api.models.partner_field import PartnerField
from api.models.facility.facility import Facility

logger = logging.getLogger(__name__)


class SystemPartnerFieldProvider(ABC):
    '''
    Abstract base class for system-generated partner field data providers.

    Each provider knows how to fetch and format data for a specific
    system partner field type (e.g., wage_indicator, etc.).
    '''

    def fetch_data(
        self, production_location: Facility
    ) -> Optional[Dict[str, Any]]:
        '''
        Fetch and format data for the given production location.
        Returns None if no data or contributor not found.
        '''
        raw_data = self._fetch_raw_data(production_location)
        if raw_data is None:
            return None

        contributor_id = self.__get_default_contributor_id()
        contributor_info = self.__get_contributor_info(contributor_id)

        # Guardrail: If contributor not found, return None silently.
        if contributor_info is None:
            return None

        return self._format_data(raw_data, contributor_info)

    @abstractmethod
    def _get_field_name(self) -> str:
        '''
        Return the partner field name for this provider.
        Each provider must define its own field name.
        '''
        pass

    @abstractmethod
    def _fetch_raw_data(self, production_location: Facility) -> Optional[Any]:
        '''Fetch raw data from the data source.'''
        pass

    @abstractmethod
    def _format_data(
        self,
        raw_data: Any,
        contributor_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        '''Format raw data into the standard partner field structure.'''
        pass

    def __get_default_contributor_id(self) -> Optional[int]:
        '''
        Return the default contributor ID for this system field.
        Gets the first contributor assigned to the partner field.
        '''
        field_name = self._get_field_name()

        try:
            partner_field = PartnerField.objects \
                .get_all_including_inactive() \
                .get(name=field_name)
        except PartnerField.DoesNotExist:
            logger.error(
                f'Partner field \'{field_name}\' not found. '
                'System field must exist in database.'
            )
            return None

        # By default, it is assumed that there is only one contributor
        # assigned to the system partner field.
        # Query contributors directly from the database with explicit ordering
        # to ensure consistent results.
        contributor = Contributor.objects.filter(
            partner_fields=partner_field
        ).order_by('id').first()
        if contributor:
            return contributor.id

        logger.error(
            f'No contributor found for \'{field_name}\' partner field. '
            'However, the contributor must be assigned to this partner field '
            'since it is a system field.'
        )
        # Silently return None if no contributor is found.
        return None

    def __get_contributor_info(
        self,
        contributor_id: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        '''
        Fetch contributor information from database.
        Returns None if contributor not found or contributor_id is None.
        '''
        if contributor_id is None:
            return None

        try:
            contributor = Contributor.objects.get(id=contributor_id)
            return {
                'id': contributor.id,
                'name': contributor.name,
                'admin_id': contributor.admin_id,
                'is_verified': contributor.is_verified,
                'contrib_type': contributor.contrib_type,
            }
        except Contributor.DoesNotExist:
            return None
