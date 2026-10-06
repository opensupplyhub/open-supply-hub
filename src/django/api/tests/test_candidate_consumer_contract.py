"""
OSDEV-3250: brand / CSO consumer contract for candidate facilities.

Every bulk surface a data consumer reads must behave as if candidates did
not exist: ``/api/facilities-downloads/`` (CSV rows), ``GET
/api/facilities/`` (search list), the vector tiles (both layers), the
``export_csv`` management command and the v1 ``/api/v1/production-locations/``
search. Candidates are reachable only by direct OS ID lookup and the
candidates bbox endpoint (pinned in test_candidate_detail_responses).

The fixture forces one candidate into ``api_facilityindex`` on purpose:
the index trigger (0246) keeps candidates out, but the Django-side guard
(``FacilityIndex.objects.without_candidates()``, OSDEV-3378) must hold
for rows indexed before that change shipped too.
"""
import csv
import inspect
import os
import tempfile
from unittest.mock import patch

from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.cache import caches
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex
from api.views.v1.production_locations import ProductionLocations

V1_OPEN_SEARCH_SERVICE = 'api.views.v1.production_locations.OpenSearchService'
GOOGLE_DRIVE_UPLOAD = (
    'api.management.commands.export_csv.upload_file_to_google_drive'
)
LOGSTASH_SQL = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    '..', '..', '..', 'logstash', 'sql', 'sync_production_locations.sql',
))

SOURCE = 'earth_genome'
# The confirmed facility sits west of Greenwich, the candidates east of
# it, so one z=3 tile holds only candidates (x=4, y=3: lon 0..45,
# lat 0..40.98) while the z=0 world tile holds everything.
CONFIRMED_LOCATION = Point(-10.0, 10.0)
CANDIDATE_LOCATIONS = {
    'eg-contract-0001': Point(20.5, 20.5),
    'eg-contract-0002': Point(21.0, 21.0),
    'eg-contract-0003': Point(21.5, 21.5),
}
WORLD_TILE = dict(z=0, x=0, y=0)
CANDIDATES_ONLY_TILE = dict(z=3, x=4, y=3)


def _square(point, half=0.01):
    lng, lat = point.x, point.y
    return GEOSGeometry(
        'POLYGON(({0} {1}, {0} {3}, {2} {3}, {2} {1}, {0} {1}))'.format(
            lng - half, lat - half, lng + half, lat + half
        ),
        srid=4326,
    )


@override_settings(ALLOWED_HOSTS=['testserver', '.allowed.org'])
@override_switch('vector_tile', active=True)
class CandidateConsumerContractTest(APITestCase):
    fixtures = ['sectors']

    def setUp(self):
        # The burst throttle lives in the shared 'api_throttling' cache,
        # which outlives a test; start each test with a clean budget and
        # leave one for the modules that follow.
        caches['api_throttling'].clear()
        self.addCleanup(caches['api_throttling'].clear)

        self.user = User.objects.create(email='one@example.com')
        self.user.set_password('example123')
        self.user.save()
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='Earth Genome',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        guard_settings = override_settings(
            EARTH_GENOME_CONTRIBUTOR_ID=self.contributor.id
        )
        guard_settings.enable()
        self.addCleanup(guard_settings.disable)

        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='First List'
        )
        self.list_source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        self.candidate_source = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            create=True,
            contributor=self.contributor,
        )
        self.next_row_index = 0

        self.confirmed = self._create_facility(
            self.list_source,
            name='Confirmed Mill',
            location=CONFIRMED_LOCATION,
        )
        self.candidates = [
            self._create_facility(
                self.candidate_source,
                name='',
                address='',
                location=location,
                is_candidate=True,
                polygon=_square(location),
                confidence=0.87,
                external_id=external_id,
                source=SOURCE,
            )
            for external_id, location in CANDIDATE_LOCATIONS.items()
        ]
        self.candidate_ids = {c.id for c in self.candidates}
        self.stale_indexed_candidate = self.candidates[0]
        self._force_index_row(self.stale_indexed_candidate)

        self.client.login(email='one@example.com', password='example123')

    # --- fixture helpers ----------------------------------------------

    def _create_facility(self, item_source, **kwargs):
        self.next_row_index += 1
        location = kwargs.get('location', Point(0, 0))
        item = FacilityListItem.objects.create(
            name='Item',
            address='Address',
            country_code='US',
            sector=['Apparel'],
            row_index=self.next_row_index,
            geocoded_point=location,
            status=FacilityListItem.MATCHED,
            source=item_source,
        )
        defaults = {
            'name': 'Name',
            'address': 'Address',
            'country_code': 'US',
            'location': location,
            'created_from': item,
        }
        defaults.update(kwargs)
        facility = Facility.including_candidates.create(**defaults)
        item.facility = facility
        item.save()
        FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=facility,
            facility_list_item=item,
            confidence=1.0,
            results={},
        )
        return facility

    def _force_index_row(self, facility):
        FacilityIndex.objects.get_or_create(
            id=facility.id,
            defaults={
                'name': facility.name,
                'address': facility.address,
                'country_code': facility.country_code,
                'location': facility.location,
                'contributors_count': 1,
                'contributors_id': [self.contributor.id],
                'contributors': [
                    {'id': self.contributor.id, 'name': self.contributor.name}
                ],
                'contrib_types': [self.contributor.contrib_type],
                'facility_addresses': [{'address': facility.address}],
                'extended_fields': [],
                'lists': [],
                'approved_claim_ids': [],
                'facility_names': [],
                'sector': ['Agriculture'],
            },
        )

    def _tile(self, layer, **tile):
        return self.client.get(
            reverse(
                'tile',
                kwargs={
                    'layer': layer,
                    'cachekey': '1567700347-1-95f951f7',
                    'ext': 'pbf',
                    **tile,
                },
            ),
            {},
            HTTP_REFERER='http://allowed.org/',
        )

    def _assert_no_candidate_id(self, text):
        for os_id in self.candidate_ids:
            self.assertNotIn(os_id, text)

    # --- preconditions -------------------------------------------------

    def test_fixture_has_candidates_and_a_stale_index_row(self):
        self.assertEqual(
            3, Facility.including_candidates.filter(is_candidate=True).count()
        )
        self.assertEqual(
            [self.confirmed.id], [f.id for f in Facility.objects.all()]
        )
        self.assertTrue(
            FacilityIndex.objects.filter(
                id=self.stale_indexed_candidate.id
            ).exists()
        )

    # --- /api/facilities-downloads/ ------------------------------------

    def test_download_rows_never_carry_a_candidate_os_id(self):
        response = self.client.get('/api/facilities-downloads/')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        results = response.data['results']
        column = results['headers'].index('os_id')
        os_ids = [row[column] for row in results['rows']]
        self.assertEqual([self.confirmed.id], os_ids)
        self.assertEqual(1, response.data['count'])
        self._assert_no_candidate_id(str(results['rows']))

        for os_id in self.candidate_ids:
            response = self.client.get(
                '/api/facilities-downloads/', {'q': os_id}
            )
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual([], response.data['results']['rows'])

    # --- GET /api/facilities/ -------------------------------------------

    def test_facilities_list_never_carries_a_candidate(self):
        response = self.client.get(reverse('facility-list'))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            [self.confirmed.id], [f['id'] for f in response.data['features']]
        )
        self._assert_no_candidate_id(response.content.decode())

        # Neither free text nor the explicit id filter leaks one.
        for os_id in self.candidate_ids:
            for params in ({'q': os_id}, {'id': os_id}):
                response = self.client.get(reverse('facility-list'), params)
                self.assertEqual(
                    status.HTTP_200_OK, response.status_code, params
                )
                self.assertEqual([], response.data['features'], params)

        response = self.client.get('/api/facilities/count/')
        self.assertEqual(1, response.data['count'])

    # --- vector tiles ---------------------------------------------------

    def test_facilities_tile_layer_never_carries_a_candidate(self):
        response = self._tile('facilities', **WORLD_TILE)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # ST_AsMVT stores string attributes verbatim, so the confirmed OS
        # ID is visible in the tile bytes and a candidate's never is.
        self.assertIn(self.confirmed.id.encode(), response.content)
        for os_id in self.candidate_ids:
            self.assertNotIn(os_id.encode(), response.content)

        response = self._tile('facilities', **CANDIDATES_ONLY_TILE)
        self.assertIn(
            response.status_code,
            (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT),
        )
        for os_id in self.candidate_ids:
            self.assertNotIn(os_id.encode(), response.content)
        self.assertNotIn(b'facilities', response.content)

    def test_facility_grid_tile_layer_counts_no_candidates(self):
        response = self._tile('facilitygrid', **WORLD_TILE)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn(b'facilitygrid', response.content)

        # A tile around the candidates alone (one of them with a stale
        # index row) has no hexagon to draw.
        response = self._tile('facilitygrid', **CANDIDATES_ONLY_TILE)
        self.assertIn(
            response.status_code,
            (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT),
        )
        self.assertNotIn(b'facilitygrid', response.content)

    # --- export_csv -----------------------------------------------------

    def test_export_csv_never_writes_a_candidate_row(self):
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        previous_cwd = os.getcwd()
        os.chdir(tmpdir.name)
        self.addCleanup(os.chdir, previous_cwd)

        with patch(GOOGLE_DRIVE_UPLOAD, return_value='drive-file-id'):
            call_command('export_csv', '--limit', '2')

        [filename] = [
            name for name in os.listdir(tmpdir.name) if name.endswith('.csv')
        ]
        with open(os.path.join(tmpdir.name, filename), newline='') as handle:
            rows = list(csv.reader(handle))
        header, data_rows = rows[0], rows[1:]
        column = header.index('os_id')
        self.assertEqual(
            [self.confirmed.id], [row[column] for row in data_rows]
        )
        self._assert_no_candidate_id('\n'.join(','.join(r) for r in rows))

    # --- v1 /api/v1/production-locations/ ---------------------------------

    def test_v1_search_is_opensearch_only_and_never_falls_back_to_candidates(
        self
    ):
        with patch(V1_OPEN_SEARCH_SERVICE) as search_mock:
            search_mock.return_value.search_index.return_value = {
                'count': 0, 'data': []
            }

            response = self.client.get(
                '/api/v1/production-locations/', {'size': 10}
            )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual({'count': 0, 'data': []}, response.data)
        search_mock.return_value.search_index.assert_called_once()
        # The list action has no database branch at all: only retrieve()
        # consults Facility.including_candidates, and only for one OS ID.
        source = inspect.getsource(ProductionLocations.list)
        self.assertNotIn('Facility', source)
        self.assertNotIn('including_candidates', source)

    def test_logstash_sync_excludes_candidates(self):
        """
        The production-locations index is fed by logstash, not Django, so
        the exclusion lives in SQL; this pins the clause. The logstash
        sources sit outside src/django and are not mounted into every
        test container, hence the skip rather than a failure.
        """
        if not os.path.exists(LOGSTASH_SQL):
            self.skipTest(f'{LOGSTASH_SQL} is not available in this run')
        with open(LOGSTASH_SQL) as handle:
            sql = handle.read()

        self.assertIn('NOT af.is_candidate', sql)
        where_clause = sql[sql.rfind('WHERE'):sql.rfind('ORDER BY')]
        self.assertIn('NOT af.is_candidate', where_clause)
