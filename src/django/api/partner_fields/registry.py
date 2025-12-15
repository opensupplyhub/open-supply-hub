from typing import Dict, List
from api.partner_fields.base_provider import SystemPartnerFieldProvider


class SystemPartnerFieldRegistry:
    '''
    Registry for system-generated partner field providers.
    Uses Singleton pattern to ensure single registry instance.
    '''

    _instance = None
    _providers: Dict[str, SystemPartnerFieldProvider] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, provider: SystemPartnerFieldProvider) -> None:
        '''Register a new system partner field provider.'''
        field_name = provider.get_field_name()
        self._providers[field_name] = provider

    def get_all_providers(self) -> List[SystemPartnerFieldProvider]:
        '''Get all registered providers.'''
        return list(self._providers.values())


# Global registry instance.
system_partner_field_registry = SystemPartnerFieldRegistry()
