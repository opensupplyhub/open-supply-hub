from typing import List, Set, Type

from waffle import switch_is_active

from api.models.zone_set import ZoneSet
from api.partner_fields.base_provider import SystemPartnerFieldProvider
from api.partner_fields.wage_indicator_provider import WageIndicatorProvider
from api.partner_fields.india_labour_line_provider import (
    IndiaLabourLineProvider,
)
from api.partner_fields.mit_living_wage_provider import MITLivingWageProvider
from api.partner_fields.zone_set_provider import ZoneSetProvider

# Gates the zone set providers. Created inactive by migration 0246 so
# the registry never queries `api_zoneset` on an image that is live
# before `migrate` has run in post-deploy, and so every zone-set-backed
# field can be pulled from both Spotlight surfaces at once without a
# deploy. The hard-wired providers do not depend on it.
ZONE_SETS_SWITCH = 'enable_zone_sets'


class SystemPartnerFieldRegistry:
    """Registry for system-generated partner field providers."""

    def __init__(self):
        """Initialize and register all system partner field providers."""
        self.__provider_classes: List[Type[SystemPartnerFieldProvider]] = []
        self.__register_providers()

    @property
    def providers(self) -> List[SystemPartnerFieldProvider]:
        """
        Get all registered providers.

        Every access builds fresh instances. Each instance memoizes its
        partner field and contributor lookup, so a caller that serves
        many locations with one list pays for them once, and a new
        request still sees admin changes. The hard-wired providers are
        registered once at startup; zone set providers are added one
        per active `ZoneSet` that has a partner field linked, so a
        dataset uploaded or retired in the admin takes effect on the
        next request without a deploy. That lookup is one small query
        per call (the table holds a handful of rows) and is skipped
        entirely while the `enable_zone_sets` switch is off.
        """
        return [*self.__hard_wired_providers(), *self.__zone_set_providers()]

    @property
    def hard_wired_field_names(self) -> Set[str]:
        """
        Names of the partner fields the hard-wired providers serve.

        A zone set must not be linked to one of these: the registry
        would then yield two providers for the same field name, and
        the two surfaces that read them would show one or the other
        depending on iteration order. The admin form checks this.
        """
        return {
            provider._get_field_name()
            for provider in self.__hard_wired_providers()
        }

    def __register_providers(self) -> None:
        """Register all system partner field providers."""
        self.__provider_classes.extend(
            [
                WageIndicatorProvider,
                MITLivingWageProvider,
                IndiaLabourLineProvider,
            ]
        )

    def __hard_wired_providers(self) -> List[SystemPartnerFieldProvider]:
        """Instantiate the hard-wired providers (constructors are free)."""
        return [cls() for cls in self.__provider_classes]

    def __zone_set_providers(self) -> List[ZoneSetProvider]:
        """Build a provider for every active, linked zone set."""
        if not switch_is_active(ZONE_SETS_SWITCH):
            return []
        zone_sets = (
            ZoneSet.objects.filter(active=True, partner_field__isnull=False)
            .select_related('partner_field')
            .order_by('name')
        )
        return [ZoneSetProvider(zone_set) for zone_set in zone_sets]


system_partner_field_registry = SystemPartnerFieldRegistry()
