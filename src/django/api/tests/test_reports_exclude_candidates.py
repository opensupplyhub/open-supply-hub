import os
from datetime import datetime, timezone
from glob import glob

from api.constants import FacilityClaimStatuses
from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.reports import run_report
from django.contrib.gis.geos import GEOSGeometry, Point
from django.db import connection
from django.test import TestCase

REPORTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports'
)

# Raw-SQL reports that were given an explicit `is_candidate` predicate in
# OSDEV-3377. Every other report either never reaches a facility-, item-,
# match- or source-level row, or filters on statuses a synthetic candidate
# record never takes (it is created directly as MATCHED / AUTOMATIC).
FIXED_REPORTS = [
    'average_matches_per_facility',
    'average_matches_per_facility_by_type',
    'confirm_reject_counts',
    'contributor_first_appearance',
    'contributor_source_count',
    'contributor_type_by_percent',
    'contributors_with_active_facilities',
    'country_first_appearance',
    'do_not_open_average_affiliations',
    'do_not_open_percent_facilities_with_multiple_matches',
    'facilities_created_not_matched',
    'facilities_matched',
    'facilities_with_extended_field_data',
    'facility_country_count',
    'facility_counts_by_country',
    'facility_list_items_uploaded',
    'facility_uploads',
    'history_of_contributor_uploads',
    'industry_data_vs_oar_data',
    'industry_data_vs_oar_data_cumulative',
    'non_public_contributors',
    'percent_data_by_contributor_type',
    'percent_data_by_contributor_type_cumulative',
    'percent_data_by_source_type',
    'percent_facilities_claimed',
    'public_contributors',
    'unique_contributor_count_by_type',
]

CANDIDATE_POLYGON_WKT = 'POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'

# Most reports drop the current month, so fixtures are back-dated. The
# candidate sits in a different month from the confirmed facility so that
# any leak shows up as an extra month row, not just a changed count.
CONFIRMED_AT = datetime(2024, 1, 15, tzinfo=timezone.utc)
CANDIDATE_AT = datetime(2024, 3, 15, tzinfo=timezone.utc)


class ReportsExcludeCandidatesTest(TestCase):
    """Raw-SQL admin reports bypass the ORM, so the Facility default manager
    cannot hide candidates from them. Each fixed report must produce the
    same output whether or not candidate rows exist (OSDEV-3377 AC #1).
    """

    def setUp(self):
        self.next_row_index = 0
        user = User.objects.create(email='reports-contributor@example.com')
        self.contributor = Contributor.objects.create(
            admin=user,
            name='Reports contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='Reports list'
        )
        self.source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            create=True,
            contributor=self.contributor,
        )
        self.facility = self._create_facility_bundle(
            item_source=self.source,
            created_at=CONFIRMED_AT,
            item_status=FacilityListItem.CONFIRMED_MATCH,
            match_status=FacilityMatch.CONFIRMED,
            name='Confirmed facility',
            address='1 Confirmed Street',
        )
        FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            status=FacilityClaimStatuses.APPROVED,
            status_change_date=CONFIRMED_AT,
        )

    # --- fixtures --------------------------------------------------------

    def _create_facility_bundle(
        self,
        item_source,
        created_at,
        item_status,
        match_status,
        **facility_kwargs
    ):
        """Create Facility + FacilityListItem + FacilityMatch the way the
        pipeline leaves them, then back-date all three."""
        self.next_row_index += 1
        item = FacilityListItem.objects.create(
            name=facility_kwargs.get('name', 'Item'),
            address=facility_kwargs.get('address', 'Address'),
            country_code='US',
            sector=['Apparel'],
            row_index=self.next_row_index,
            geocoded_point=Point(0, 0),
            status=item_status,
            source=item_source,
        )
        defaults = {
            'name': 'Name',
            'address': 'Address',
            'country_code': 'US',
            'location': Point(0, 0),
            'created_from': item,
        }
        defaults.update(facility_kwargs)
        # Facility.objects.create is correct on both main and the
        # OSDEV-3380 branch: the default manager filter never applies to
        # create(), only to reads.
        facility = Facility.objects.create(**defaults)
        match = FacilityMatch.objects.create(
            status=match_status,
            facility=facility,
            facility_list_item=item,
            confidence=0.9,
            results={},
        )
        item.facility = facility
        item.save()

        Facility.objects.filter(pk=facility.pk).update(created_at=created_at)
        FacilityListItem.objects.filter(pk=item.pk).update(
            created_at=created_at
        )
        FacilityMatch.objects.filter(pk=match.pk).update(
            created_at=created_at
        )
        Source.objects.filter(pk=item_source.pk).update(
            created_at=created_at
        )
        return facility

    def _create_candidate(self):
        """Mirror the Earth Genome ingest shape (design decision D2): an
        "Earth Genome" contributor, a synthetic SINGLE source per detection,
        a MATCHED list item with empty name/address, an AUTOMATIC match and
        an api_facility row with is_candidate = true."""
        user = User.objects.create(email='earth-genome@example.com')
        contributor = Contributor.objects.create(
            admin=user,
            name='Earth Genome',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        source = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            create=True,
            contributor=contributor,
        )
        return self._create_facility_bundle(
            item_source=source,
            created_at=CANDIDATE_AT,
            item_status=FacilityListItem.MATCHED,
            match_status=FacilityMatch.AUTOMATIC,
            name='',
            address='',
            is_candidate=True,
            polygon=GEOSGeometry(CANDIDATE_POLYGON_WKT, srid=4326),
            confidence=0.87,
            external_id='eg-facility-0001',
            source='earth_genome',
        )

    @staticmethod
    def _run(name):
        return run_report(name)['rows']

    @staticmethod
    def _candidate_count():
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT COUNT(*) FROM api_facility WHERE is_candidate = true'
            )
            return cursor.fetchone()[0]

    # --- tests -------------------------------------------------------------

    def test_fixed_reports_are_unchanged_by_candidate_rows(self):
        baseline = {name: self._run(name) for name in FIXED_REPORTS}
        self.assertEqual(self._candidate_count(), 0)

        self._create_candidate()
        self.assertEqual(self._candidate_count(), 1)

        for name in FIXED_REPORTS:
            with self.subTest(report=name):
                self.assertEqual(self._run(name), baseline[name])

    def test_baseline_fixture_is_visible_to_reports(self):
        """Guard against a vacuous pass: the confirmed facility must show
        up, so an equal-output assertion is comparing real rows."""
        self._create_candidate()

        self.assertEqual(
            self._run('facility_counts_by_country'), [('US', 1)]
        )
        self.assertEqual(
            self._run('country_first_appearance'), [('US', '2024-01')]
        )
        claimed = self._run('percent_facilities_claimed')
        self.assertEqual([row[0] for row in claimed], ['2024-01'])

    def test_fixed_reports_list_matches_sql_files(self):
        """FIXED_REPORTS is the contract for the PR verdict table: every
        report SQL that mentions is_candidate is covered here, and nothing
        listed here lacks the predicate."""
        with_predicate = set()
        for path in glob(os.path.join(REPORTS_DIR, '*.sql')):
            with open(path) as sql_file:
                if 'is_candidate' in sql_file.read():
                    name = os.path.splitext(os.path.basename(path))[0]
                    with_predicate.add(name)

        self.assertEqual(with_predicate, set(FIXED_REPORTS))
