from typing import List, Set
from api.models.zone_set import ZoneSet
from api.partner_fields.base_provider import SystemPartnerFieldProvider
from api.partner_fields.wage_indicator_provider import WageIndicatorProvider
from api.partner_fields.india_labour_line_provider import (
    IndiaLabourLineProvider,
)
from api.partner_fields.mit_living_wage_provider import MITLivingWageProvider
from api.partner_fields.zone_set_provider import ZoneSetProvider


class SystemPartnerFieldRegistry:
    """Registry for system-generated partner field providers."""

    def __init__(self):
        """Initialize and register all system partner field providers."""
        self.__providers: List[SystemPartnerFieldProvider] = []
        self.__register_providers()

    @property
    def providers(self) -> List[SystemPartnerFieldProvider]:
        """
        Get all registered providers.

        The hard-wired providers are registered once at startup. Zone
        set providers are added on each access, one per active
        `ZoneSet` that has a partner field linked, so a dataset
        uploaded or retired in the admin takes effect on the next
        request without a deploy. The lookup is one small query per
        call (the table holds a handful of rows).
        """
        return [*self.__providers, *self.__zone_set_providers()]

    @property
    def hard_wired_field_names(self) -> Set[str]:
        """
        Names of the partner fields the hard-wired providers serve.

        A zone set must not be linked to one of these: the registry
        would then yield two providers for the same field name, and
        the two surfaces that read them would show one or the other
        depending on iteration order. The admin form checks this.
        """
        return {provider._get_field_name() for provider in self.__providers}

    def __register_providers(self) -> None:
        """Register all system partner field providers."""
        self.__providers.extend(
            [
                WageIndicatorProvider(),
                MITLivingWageProvider(),
                IndiaLabourLineProvider(),
            ]
        )

    def __zone_set_providers(self) -> List[ZoneSetProvider]:
        """Build a provider for every active, linked zone set."""
        zone_sets = (
            ZoneSet.objects.filter(active=True, partner_field__isnull=False)
            .select_related('partner_field')
            .order_by('name')
        )
        return [ZoneSetProvider(zone_set) for zone_set in zone_sets]


system_partner_field_registry = SystemPartnerFieldRegistry()
