from django.db.models import (
    CharField,
    DateTimeField,
    Index,
    IntegerField,
    Model,
    UniqueConstraint,
)


class CountrySectorStats(Model):
    '''
    Precomputed country x sector cube behind the sector-filtered country map.

    Shading the map for one sector live means grouping the whole of
    api_facilityindex by country: 47ms for a narrow sector but 5.8s for a
    broad one, and broad is the ordinary case. The entire cube is only
    about 8,200 rows and builds in one pass in under five seconds, so the
    filtered map is served as a lookup instead and breadth stops mattering.

    Nothing writes here except the `compute_country_stats` command, which
    rebuilds the whole table alongside CountryStats. Treat every row as
    derived data, safe to drop and rebuild. See OSDEV-3802.
    '''

    country_code = CharField(
        max_length=2,
        help_text='ISO 3166-1 alpha-2 code, matching FacilityIndex.',
    )

    sector = CharField(
        max_length=200,
        help_text=(
            'One sector name exactly as it appears in FacilityIndex.sector, '
            'which is a controlled taxonomy and so is matched verbatim.'
        ),
    )

    location_count = IntegerField(
        help_text=(
            'Open production locations in this country reporting this '
            'sector. A location can report several sectors, so these counts '
            'sum to more than CountryStats.location_count.'
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
        verbose_name = 'Country sector stats'
        verbose_name_plural = 'Country sector stats'
        ordering = ('sector', '-location_count')
        constraints = [
            # The rebuild aggregates by country and sector, so a second row
            # for the same pair could only come from a half-applied rebuild.
            UniqueConstraint(
                fields=('sector', 'country_code'),
                name='unique_country_sector_stats',
            ),
        ]
        indexes = [
            # Sector leads because the only read is "every country for
            # sector X"; the unique constraint already covers that prefix,
            # and this index carries the count so the lookup stays
            # index-only.
            Index(
                fields=('sector', 'country_code', 'location_count'),
                name='country_sector_stats_lookup',
            ),
        ]

    def __str__(self):
        return (
            f'{self.country_code} / {self.sector} '
            f'({self.location_count} locations)'
        )
