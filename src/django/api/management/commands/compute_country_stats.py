from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

from api.models.country_stats import CountryStats
from api.models.facility.facility_index import FacilityIndex
from api.models.partner_field import PartnerField
from api.models.facility.partner_contributor_filter import (
    apply_partner_fields_or_filter,
)
from api.partner_fields.registry import SystemPartnerFieldRegistry


# `is_closed` is null for virtually every row, and `NOT null` is null, so
# `WHERE NOT is_closed` returns almost nothing. Everything here filters on
# "is not true" instead.
OPEN_LOCATIONS = 'is_closed IS NOT TRUE'


class Command(BaseCommand):
    help = (
        'Rebuild the per-country rollup behind the country map: open '
        'location counts, the sectors represented, and which Spotlight '
        'partner fields hold data for at least one location.'
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

        sectors = self.__sectors_by_country()
        self.stdout.write(f'Rolled up sectors for {len(sectors)} countries.')

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
                sectors=sectors.get(country_code, []),
                partner_fields=sorted(partners.get(country_code, set())),
                computed_at=computed_at,
            )
            for country_code, location_count in counts.items()
        ]

        # Replace wholesale. The table is derived data and small enough that
        # a diff would cost more than it saves, and a country that drops to
        # zero locations has to disappear rather than keep a stale row.
        with transaction.atomic():
            CountryStats.objects.all().delete()
            CountryStats.objects.bulk_create(rows, batch_size=500)

        elapsed = (timezone.now() - started).total_seconds()
        self.stdout.write(self.style.SUCCESS(
            f'Wrote {len(rows)} country rows in {elapsed:.1f}s.'
        ))

    def __location_counts(self):
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT country_code, COUNT(*) '
                'FROM api_facilityindex '
                f'WHERE {OPEN_LOCATIONS} '
                'GROUP BY country_code'
            )
            return {code: count for code, count in cursor.fetchall()}

    def __sectors_by_country(self):
        '''
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
            by_country = defaultdict(list)
            for country_code, sector_name, count in cursor.fetchall():
                by_country[country_code].append({
                    'sector': sector_name,
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
        registry = SystemPartnerFieldRegistry()
        contributor_ids = self.__partner_contributor_ids(registry)

        by_country = defaultdict(set)
        for field_name in self.__active_partner_field_names():
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
    def __partner_contributor_ids(registry):
        '''
        Contributors whose ExtendedField rows count as partner data. System
        providers carry their own contributor, so they are collected from
        the registry rather than hard-coded.
        '''
        contributor_ids = set()
        for provider in registry.providers:
            contributor = getattr(provider, 'contributor', None)
            contributor_id = getattr(contributor, 'id', None)
            if contributor_id is not None:
                contributor_ids.add(contributor_id)
        return list(contributor_ids)
