from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    CharField,
    DateTimeField,
    IntegerField,
    JSONField,
    Model,
)


class CountryStats(Model):
    '''
    Precomputed per-country rollup behind the country map.

    One row per country that holds at least one open production location.
    Recalculated on a schedule rather than served live: the whole table is
    224 rows and about 5KB as JSON, where the equivalent live answer meant
    a megabyte-scale vector tile per viewport.

    Nothing writes here except the `compute_country_stats` command. Treat
    every row as derived data, safe to drop and rebuild.
    '''

    country_code = CharField(
        max_length=2,
        primary_key=True,
        help_text='ISO 3166-1 alpha-2 code, matching FacilityIndex.',
    )

    location_count = IntegerField(
        help_text=(
            'Open production locations in this country. Excludes locations '
            'explicitly marked closed; note is_closed is null for almost '
            'every row, so the filter is "is not true" rather than "not".'
        ),
    )

    sectors = JSONField(
        default=list,
        help_text=(
            'Sector groups represented, as [{"sector": str, "count": int}] '
            'sorted by count descending. The key stays "sector" because the '
            'card reads it that way; the value is a sector group name, '
            'rolled up from the raw sectors because the raw list runs to '
            '141 near-duplicate names for a country such as India. Each '
            'count is distinct locations reporting any sector in that '
            'group, so a location naming two sectors in one group counts '
            'once. A sector can belong to several groups, so these counts '
            'still sum to more than location_count. See OSDEV-3802.'
        ),
    )

    partner_fields = ArrayField(
        CharField(max_length=200),
        default=list,
        help_text=(
            'Names of the Spotlight partner fields with data for at least '
            'one location in this country. Presence only, deliberately: the '
            'product question is whether we hold the data, not how much.'
        ),
    )

    computed_at = DateTimeField(
        help_text=(
            'When this row was last rebuilt. Surfaced to readers so a '
            'stalled rebuild is visible rather than silently serving old '
            'numbers.'
        ),
    )

    class Meta:
        verbose_name = 'Country stats'
        verbose_name_plural = 'Country stats'
        ordering = ('-location_count',)

    def __str__(self):
        return f'{self.country_code} ({self.location_count} locations)'
