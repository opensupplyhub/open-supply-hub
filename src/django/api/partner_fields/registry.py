from typing import List
from api.partner_fields.base_provider import SystemPartnerFieldProvider
from api.partner_fields.wage_indicator_provider import WageIndicatorProvider
from api.partner_fields.mit_living_wage_provider import MITLivingWageProvider


class SystemPartnerFieldRegistry:
    """Registry for system-generated partner field providers."""

    def __init__(self):
        """Initialize and register all system partner field providers."""
        self.__providers: List[SystemPartnerFieldProvider] = []
        self.__register_providers()

    @property
    def providers(self) -> List[SystemPartnerFieldProvider]:
        """Get all registered providers."""
        return self.__providers

    def __register_providers(self) -> None:
        """Register all system partner field providers."""
        self.__providers.extend(
            [
                WageIndicatorProvider(),
                MITLivingWageProvider(),
            ]
        )


system_partner_field_registry = SystemPartnerFieldRegistry()
