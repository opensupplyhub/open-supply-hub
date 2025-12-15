'''
Setup and registration of all system partner field providers.
Import this module to ensure all providers are registered.
'''

from api.partner_fields.registry import system_partner_field_registry
from api.partner_fields.wage_indicator_provider import WageIndicatorProvider


def register_all_providers():
    '''Register all system partner field providers with the registry.'''
    system_partner_field_registry.register(WageIndicatorProvider())


# Auto-register on module import.
register_all_providers()
