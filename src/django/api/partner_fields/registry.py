from typing import List
from api.partner_fields.base_provider import SystemPartnerFieldProvider
from api.partner_fields.wage_indicator_provider import WageIndicatorProvider


class SystemPartnerFieldRegistry:
    '''Registry for system-generated partner field providers.'''

    def __init__(self):
        '''Initialize and register all system partner field providers.'''
        self.__providers: List[SystemPartnerFieldProvider] = []
        self.__register_providers()

    @property
    def providers(self) -> List[SystemPartnerFieldProvider]:
        '''Get all registered providers.'''
        return self.__providers

    def __register_providers(self) -> None:
        '''Register all system partner field providers.'''
        # Add new providers here as needed.
        providers = [
            WageIndicatorProvider(),
        ]
        for provider in providers:
            self.__providers.append(provider)


# Global registry instance.
system_partner_field_registry = SystemPartnerFieldRegistry()
