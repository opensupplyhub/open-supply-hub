from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class SystemPartnerFieldProvider(ABC):
    '''
    Abstract base class for system-generated partner field data providers.

    Each provider knows how to fetch and format data for a specific
    system partner field type (e.g., wage_indicator, certifications, etc.).
    '''

    @abstractmethod
    def get_field_name(self) -> str:
        '''Return the field name this provider handles.'''
        pass

    @abstractmethod
    def _get_default_contributor_id(self) -> int:
        '''
        Return the default contributor ID for this system field.
        Each provider defines its own default contributor.
        '''
        pass

    @abstractmethod
    def _fetch_raw_data(self, facility) -> Optional[Any]:
        '''Fetch raw data from the data source.'''
        pass

    def fetch_data(self, facility) -> Optional[Dict[str, Any]]:
        '''
        Fetch and format data for the given facility.
        Returns None if no data or contributor not found.
        '''
        raw_data = self._fetch_raw_data(facility)
        if raw_data is None:
            return None

        contributor_id = self._get_default_contributor_id()
        contributor_info = self._get_contributor_info(contributor_id)

        # Guardrail: If contributor not found, return None silently.
        if contributor_info is None:
            return None

        return self._format_data(raw_data, contributor_info)

    @abstractmethod
    def _format_data(
        self,
        raw_data: Any,
        contributor_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        '''Format raw data into the standard partner field structure.'''
        pass

    def _get_contributor_info(
        self,
        contributor_id: int
    ) -> Optional[Dict[str, Any]]:
        '''
        Fetch contributor information from database.
        Returns None if contributor not found.
        '''
        from api.models import Contributor

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
