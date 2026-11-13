from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

from api.models.country_sector_stats import CountrySectorStats
from api.models.country_stats import CountryStats
from api.models.facility.facility_index import FacilityIndex
from api.models.contributor.contributor import Contributor
from api.models.partner_field import PartnerField
from api.models.sector import Sector
from api.models.facility.partner_contributor_filter import (
    apply_partner_fields_or_filter,
)


# `is_closed` is null for virtually every row, and `NOT null` is null, so
# `WHERE NOT is_closed` returns almost nothing. Everything here filters on
# "is not true" instead.
OPEN_LOCATIONS = 'is_closed IS NOT TRUE'


class Command(BaseCommand):
    help = (
        'Rebuild the per-country rollup behind the country map: open '
        'location counts, the sector groups represented, which Spotlight '
        'partner fields hold data for at least one location, and the '
        'country x sector cube the sector-filtered map reads.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-partner-fields',
            action='store_true',
            help=(
                'Compute counts and sectors only. Partner-field presence is '
                'the slow part; skipping it is useful while iterating.'
            ),
        )

    def handle(self, *args, **options):
        started = timezone.now()

        counts = self.__location_counts()
        self.stdout.write(
            f'Counted {sum(counts.values())} open locations across '
            f'{len(counts)} countries.'
        )

        raw_sectors = self.__raw_sectors_by_country()
        self.stdout.write(
            f'Counted raw sectors for {len(raw_sectors)} countries.'
        )

        sector_groups = self.__sector_groups_by_country()
        self.stdout.write(
            f'Rolled up sector groups for {len(sector_groups)} countries.'
        )

        if options['skip_partner_fields']:
            partners = {}
            self.stdout.write('Skipping partner fields.')
        else:
            partners = self.__partner_fields_by_country()
            self.stdout.write(
                'Resolved partner-field presence for '
                f'{len(partners)} countries.'
            )

        computed_at = timezone.now()
        rows = [
            CountryStats(
                country_code=country_code,
                location_count=location_count,
                sectors=sector_groups.get(country_code, []),
                partner_fields=sorted(partners.get(country_code, set())),
                computed_at=computed_at,
            )
            for country_code, location_count in counts.items()
        ]

        cube_rows = self.__cube_rows(raw_sectors, computed_at)

        # Replace wholesale. The tables are derived data and small enough
        # that a diff would cost more than it saves, and a country that
        # drops to zero locations has to disappear rather than keep a stale
        # row. Both tables move in one transaction so a failed rebuild never
        # leaves the map and its sector filter on different vintages.
        with transaction.atomic():
            CountryStats.objects.all().delete()
            CountryStats.objects.bulk_create(rows, batch_size=500)
            CountrySectorStats.objects.all().delete()
            CountrySectorStats.objects.bulk_create(cube_rows, batch_size=500)

        elapsed = (timezone.now() - started).total_seconds()
        self.stdout.write(self.style.SUCCESS(
            f'Wrote {len(rows)} country rows and {len(cube_rows)} '
            f'country/sector rows in {elapsed:.1f}s.'
        ))

    @staticmethod
    def __cube_rows(raw_sectors, computed_at):
        '''
        The country x sector cube the sector-filtered map reads, built from
        the raw-sector pass rather than from a third query: that pass is
        already grouped by exactly these two keys and carries the same
        open-locations filter, so re-querying would scan api_facilityindex
        again for identical numbers.

        Keyed on raw sector names on purpose. The cube feeds the search
        page's sector filter, which filters on raw sectors, so it must not
        follow the card's rollup to sector groups. See OSDEV-3802.
        '''
        return [
            CountrySectorStats(
                country_code=country_code,
                sector=entry['sector'],
                location_count=entry['count'],
                computed_at=computed_at,
            )
            for country_code, entries in raw_sectors.items()
            for entry in entries
        ]

    def __location_counts(self):
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT country_code, COUNT(*) '
                'FROM api_facilityindex '
                f'WHERE {OPEN_LOCATIONS} '
                'GROUP BY country_code'
            )
            return {code: count for code, count in cursor.fetchall()}

    def __raw_sectors_by_country(self):
        '''
        Per-country counts for raw sector names, which feed the country x
        sector cube only. The card reads the grouped rollup below.

        `sector` is a text array, so one row can contribute to several
        sectors. These counts therefore sum to more than the location count,
        which is why they are reported per sector rather than as a share.
        '''
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT country_code, sector_name, COUNT(*) AS n '
                'FROM api_facilityindex, UNNEST(sector) AS sector_name '
                f'WHERE {OPEN_LOCATIONS} '
                'GROUP BY country_code, sector_name '
                'ORDER BY country_code, n DESC'
            )
            return self.__by_country(cursor.fetchall())

    def __sector_groups_by_country(self):
        '''
        Per-country counts rolled up to sector groups, which is what the
        country card lists. Raw sector names are too many and too redundant
        to read: India alone reports 141 of them, with "Agriculture",
        "Food" and "Food Industry" all sitting in the top three and all
        meaning the same thing. See OSDEV-3802.

        Counts distinct locations per group rather than summing the member
        sectors' counts, because a location reporting both "Food" and
        "Food Industry" would otherwise be counted twice in the one group.
        The lateral resolves each location's own sectors to a DISTINCT set
        of groups first, so the outer count never sees the same location
        twice for one group.

        Groups still overlap across the row: the mapping is many-to-many,
        so a location reporting "Food Manufacturing" counts once for
        "Agriculture, Food & Beverage" and once for "Manufacturing". That
        is the same behavior the card's own note already describes, and the
        reason these counts still sum to more than location_count.

        One pass, with the sector to group mapping handed to Postgres as a
        pair of arrays: a query per group would mean 25 passes over
        api_facilityindex. Measured on a 2,537,087-row anonymized restore,
        this runs in 7.5s against 7.1s for the raw pass above, where
        deduplicating globally with COUNT(DISTINCT id) took 13.9s.
        '''
        sector_names = []
        group_names = []
        for sector_name, group_name in self.__sector_group_pairs():
            sector_names.append(sector_name)
            group_names.append(group_name)

        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT fi.country_code, g.sector_group, COUNT(*) AS n '
                'FROM api_facilityindex fi '
                'CROSS JOIN LATERAL ('
                'SELECT DISTINCT COALESCE(m.group_name, %s) AS sector_group '
                'FROM UNNEST(fi.sector) AS reported(sector_name) '
                'LEFT JOIN UNNEST(%s::varchar[], %s::varchar[]) '
                'AS m(sector_name, group_name) '
                'ON m.sector_name = reported.sector_name'
                ') g '
                f'WHERE {OPEN_LOCATIONS} '
                'GROUP BY 1, 2 '
                'ORDER BY 1, n DESC',
                [Sector.DEFAULT_SECTOR_NAME, sector_names, group_names],
            )
            return self.__by_country(cursor.fetchall())

    @staticmethod
    def __sector_group_pairs():
        '''
        Every (sector, group) link in the taxonomy, minus the ones that must
        not be rolled up.

        "Unspecified" is excluded even though the taxonomy files it under
        "Other": it records the absence of a sector rather than a sector,
        it outranks real ones on volume in several countries, and the card
        pins it last and keeps it out of its bar scale by that exact name.
        Letting it land in "Other" would both hide it in the ordering and
        make a pile of missing data read as a real group.

        Anything the mapping does not cover falls to that same
        "Unspecified" bucket through the COALESCE above: sectors with no
        group link, and the values the index carries that the taxonomy
        does not know at all. The second kind is the real population, and
        most of it is malformed, such as a whole comma-joined list stored
        as one sector name. A lone raw name among 25 group names would
        read as a group, so none of it is shown as one.
        '''
        pairs = (
            Sector.objects
            .exclude(name=Sector.DEFAULT_SECTOR_NAME)
            .values_list('name', 'groups__name')
        )
        return [
            (sector_name, group_name)
            for sector_name, group_name in pairs
            if group_name is not None
        ]

    @staticmethod
    def __by_country(rows):
        '''
        Both rollups store the same {sector, count} shape, grouped by
        country: the card renders one list and does not need to know which
        pass produced it.
        '''
        by_country = defaultdict(list)
        for country_code, name, count in rows:
            by_country[country_code].append({
                'sector': name,
                'count': count,
            })
        return dict(by_country)

    def __partner_fields_by_country(self):
        '''
        One pass per active partner field, reusing the same filter the
        search page applies so that "has data" means exactly what it means
        everywhere else on the site.

        The three matching mechanisms behind that filter (contributed
        ExtendedField rows, country-scoped system fields, and zone-set
        polygons) are deliberately not reimplemented here. Presence is all
        that is recorded, so each field is a DISTINCT over country codes
        rather than a count.
        '''
        by_country = defaultdict(set)
        for field_name in self.__active_partner_field_names():
            # Contributors are scoped per field. A partner's ExtendedField
            # rows only count for the fields that partner actually supplies,
            # which is what Contributor.partner_fields records. Passing one
            # global set here would mean every partner vouching for every
            # field.
            contributor_ids = self.__contributor_ids_for(field_name)

            queryset = apply_partner_fields_or_filter(
                FacilityIndex.objects.filter(is_closed__isnull=True)
                | FacilityIndex.objects.filter(is_closed=False),
                [field_name],
                contributor_ids,
            )
            country_codes = (
                queryset.values_list('country_code', flat=True)
                .distinct()
            )
            for country_code in country_codes:
                by_country[country_code].add(field_name)

        return dict(by_country)

    @staticmethod
    def __active_partner_field_names():
        return list(
            PartnerField.objects
            .filter(active=True)
            .values_list('name', flat=True)
        )

    @staticmethod
    def __contributor_ids_for(field_name):
        '''
        Contributors whose ExtendedField rows count as data for this partner
        field, taken from the same Contributor.partner_fields link the search
        page uses.

        Empty for the country-scoped system fields and for zone sets, which
        carry no ExtendedField rows; those are matched by country code and
        polygon inside the filter instead.
        '''
        return list(
            Contributor.objects
            .filter(partner_fields__name=field_name)
            .values_list('id', flat=True)
        )
