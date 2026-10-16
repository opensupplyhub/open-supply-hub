import json
import os
import shutil
import tempfile
from io import StringIO
from unittest.mock import patch

from api.models import (
    Contributor,
    Facility,
    FacilityAlias,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.models.sector import Sector
from api.services.candidate_matches import suggested_matches
from django.contrib.gis.geos import Point
from django.core.management import call_command
from botocore.exceptions import ClientError
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

# A detection site in North Carolina. Confirmed fixtures below are placed
# relative to it: 0.002 degrees of latitude is roughly 220 metres, 0.05 is
# roughly 5.5 kilometres.
SITE_LNG = -78.6400
SITE_LAT = 35.7800
SOURCE = 'earth_genome'


def _square(lng, lat, half=0.001):
    """A closed GeoJSON polygon ring around (lng, lat)."""
    return {
        'type': 'Polygon',
        'coordinates': [[
            [lng - half, lat - half],
            [lng - half, lat + half],
            [lng + half, lat + half],
            [lng + half, lat - half],
            [lng - half, lat - half],
        ]],
    }


def _prototype_record(eg_id, lng, lat, confidence=0.9, polygon=True):
    return {
        'eg_id': eg_id,
        'polygon': _square(lng, lat) if polygon else None,
        'centroid_lat': lat,
        'centroid_lng': lng,
        'point_only': not polygon,
        'probable_facility_type': 'poultry',
        'confidence_score': confidence,
        'eg_model_version': 'MLP64-16',
        'source': SOURCE,
        'validation_status': 'unverified',
    }


def _feature(eg_id, lng, lat, confidence=0.9, geometry=True):
    return {
        'type': 'Feature',
        'properties': {'confidence': confidence, 'id': eg_id},
        'geometry': _square(lng, lat) if geometry else None,
    }


PROJECT_ID = 'a1671a55-2049-422c-a38c-d22fb753e9af'
LAYER_ID = '4d6d1daf-130b-4a53-a3db-c122ce1e061b'
DEEP_SEARCH_OK = 'f8c5ed5e-2856-4eae-a9bf-52b44cf996c6'
DEEP_SEARCH_RUNNING = '0b1f9c1e-5f0e-4a4c-9d3b-2a3f4e5d6c7b'
DEEP_SEARCH_OLDER = '9a8b7c6d-1234-4e5f-8a9b-0c1d2e3f4a5b'


def _earth_index_feature(detection_id, lng, lat, confidence=0.99,
                         deep_search_id=DEEP_SEARCH_OK):
    """A ``deep_search_result`` feature the way the export endpoint
    writes it (``properties.id`` is the detection id)."""
    return {
        'type': 'Feature',
        'id': f'{deep_search_id}:{detection_id}',
        'properties': {
            'confidence': confidence,
            'deepSearchId': deep_search_id,
            'featureType': 'deep_search_result',
            'id': detection_id,
            'layerId': LAYER_ID,
            'mgrs_id': '17SQV',
            'projectId': PROJECT_ID,
        },
        'geometry': _square(lng, lat),
    }


def _aoi_feature():
    return {
        'type': 'Feature',
        'properties': {
            'featureType': 'aoi',
            'projectId': PROJECT_ID,
            'title': 'Poultry in NC',
        },
        'geometry': {
            'type': 'MultiPolygon',
            'coordinates': [_square(SITE_LNG, SITE_LAT, 1.0)['coordinates']],
        },
    }


def _project_record(target_label=''):
    return {
        'id': PROJECT_ID,
        'title': 'Poultry in NC',
        'targetLabel': target_label,
        'layers': [{'id': LAYER_ID, 'projectId': PROJECT_ID}],
        'deep_searches': [
            {
                'id': DEEP_SEARCH_OK, 'layerId': LAYER_ID,
                'status': 'success', 'createdAt': '2026-09-02T00:00:00Z',
            },
            {
                'id': DEEP_SEARCH_RUNNING, 'layerId': LAYER_ID,
                'status': 'running', 'createdAt': '2026-10-01T00:00:00Z',
            },
            {
                'id': DEEP_SEARCH_OLDER, 'layerId': 'other-layer',
                'status': 'success', 'createdAt': '2026-08-01T00:00:00Z',
            },
        ],
    }


class FakeResponse:
    def __init__(self, status_code=200, body=None, text=''):
        self.status_code = status_code
        self._body = body
        self.text = text if body is None else json.dumps(body)

    def json(self):
        if self._body is None:
            raise ValueError('not json')
        return self._body

    def iter_content(self, chunk_size):
        data = self.text.encode()
        for start in range(0, len(data), chunk_size):
            yield data[start:start + chunk_size]

    def close(self):
        pass


class FakeEarthIndex:
    """Stands in for ``requests.get`` in api.services.earth_index."""

    def __init__(self, project=None, export=None, status=200):
        self.project = project if project is not None else _project_record()
        self.export = export if export is not None else {
            'type': 'FeatureCollection',
            'features': [
                _earth_index_feature('14121408024753508', SITE_LNG,
                                     SITE_LAT, 0.9999),
                _earth_index_feature('14121384851571097', SITE_LNG + 0.2,
                                     SITE_LAT, 0.9831),
            ],
        }
        self.status = status
        self.calls = []

    def __call__(self, url, params=None, headers=None, timeout=None,
                 stream=False):
        self.calls.append(
            {'url': url, 'params': params, 'headers': headers,
             'stream': stream, 'timeout': timeout}
        )
        if self.status != 200:
            return FakeResponse(
                self.status,
                {'Status': self.status, 'Detail': 'invalid api key'},
            )
        if url.endswith('/export'):
            return FakeResponse(200, self.export)
        return FakeResponse(200, self.project)


class IngestSatelliteDetectionsTest(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)

        eg_user = User.objects.create(email='earth-genome@example.com')
        self.contributor = Contributor.objects.create(
            admin=eg_user,
            name='Earth Genome',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        # OSDEV-3248: only the designated contributor may create candidates.
        guard_settings = override_settings(
            EARTH_GENOME_CONTRIBUTOR_ID=self.contributor.id
        )
        guard_settings.enable()
        self.addCleanup(guard_settings.disable)

        other_user = User.objects.create(email='other@example.com')
        self.other_contributor = Contributor.objects.create(
            admin=other_user,
            name='Some other contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='First List'
        )
        self.list_source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.other_contributor,
        )
        self.next_row_index = 0

        # ~220 m north of the site: inside the default 500 m radius.
        self.near_facility = self._create_confirmed_facility(
            'Near Farm', Point(SITE_LNG, SITE_LAT + 0.002)
        )
        # ~5.5 km away: outside it.
        self.far_facility = self._create_confirmed_facility(
            'Far Plant', Point(SITE_LNG, SITE_LAT + 0.05)
        )

        self.json_path = self._write(
            'detections.json',
            [
                _prototype_record('NC0', SITE_LNG, SITE_LAT, 0.95),
                _prototype_record('NC1', SITE_LNG + 0.2, SITE_LAT, 0.80),
                _prototype_record(
                    'NC2', SITE_LNG + 0.4, SITE_LAT, 0.70, polygon=False
                ),
            ],
        )
        self.geojson_path = self._write(
            'detections.geojson',
            {
                'type': 'FeatureCollection',
                'features': [
                    _feature('AL0', SITE_LNG, SITE_LAT, 0.93),
                    _feature('AL1', SITE_LNG + 0.2, SITE_LAT, 0.81),
                    _feature('AL2', SITE_LNG + 0.4, SITE_LAT, 0.77),
                    _feature('AL3', SITE_LNG + 0.6, SITE_LAT, 0.60,
                             geometry=False),
                ],
            },
        )

    # --- fixtures --------------------------------------------------------

    def _write(self, name, data):
        path = os.path.join(self.tmpdir.name, name)
        with open(path, 'w') as handle:
            json.dump(data, handle)
        return path

    def _create_confirmed_facility(self, name, location):
        self.next_row_index += 1
        item = FacilityListItem.objects.create(
            name=name,
            address='1 Main Street',
            country_code='US',
            sector=['Apparel'],
            row_index=self.next_row_index,
            geocoded_point=location,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.list_source,
        )
        facility = Facility.objects.create(
            name=name,
            address='1 Main Street',
            country_code='US',
            location=location,
            created_from=item,
        )
        FacilityMatch.objects.create(
            facility=facility,
            facility_list_item=item,
            status=FacilityMatch.CONFIRMED,
            confidence=1.0,
            results={},
        )
        item.facility = facility
        item.save()
        return facility

    def _run(self, *args, **kwargs):
        out = StringIO()
        err = StringIO()
        call_command(
            'ingest_satellite_detections',
            *args,
            stdout=out,
            stderr=err,
            **kwargs,
        )
        return out.getvalue(), err.getvalue()

    def _candidates(self):
        return Facility.including_candidates.filter(source=SOURCE)

    # --- tests -----------------------------------------------------------

    def test_creates_one_candidate_per_detection_with_synthetic_records(
        self
    ):
        out, _ = self._run('--file', self.json_path)

        self.assertEqual(self._candidates().count(), 3)
        self.assertIn('created=3 updated=0', out)

        facility = self._candidates().get(external_id='NC0')
        self.assertTrue(facility.is_candidate)
        self.assertEqual(facility.name, '')
        self.assertEqual(facility.address, '')
        self.assertEqual(facility.country_code, 'US')
        self.assertEqual(facility.source, SOURCE)
        self.assertAlmostEqual(facility.confidence, 0.95)
        self.assertIsNotNone(facility.polygon)
        self.assertEqual(facility.polygon.srid, 4326)
        self.assertAlmostEqual(facility.location.x, SITE_LNG)
        self.assertAlmostEqual(facility.location.y, SITE_LAT)
        self.assertTrue(facility.id.startswith('US'))

        item = facility.created_from
        self.assertEqual(item.status, FacilityListItem.MATCHED)
        self.assertEqual(item.facility_id, facility.id)
        self.assertEqual(item.name, '')
        self.assertEqual(item.address, '')
        self.assertEqual(item.row_index, 0)
        self.assertEqual(item.raw_json['external_id'], 'NC0')
        self.assertEqual(item.raw_json['confidence'], 0.95)
        self.assertEqual(item.raw_json['eg_model_version'], 'MLP64-16')
        self.assertEqual(item.raw_json['probable_facility_type'], 'poultry')
        self.assertEqual(item.raw_json['polygon']['type'], 'Polygon')
        self.assertIn('external_id', item.raw_header)
        self.assertIn('"NC0"', item.raw_data)
        self.assertEqual(len(item.sector), 1)

        source = item.source
        self.assertEqual(source.source_type, Source.SINGLE)
        self.assertEqual(source.contributor_id, self.contributor.id)
        self.assertIsNone(source.facility_list)
        self.assertTrue(source.is_active)
        self.assertTrue(source.is_public)
        self.assertTrue(source.create)

        match = FacilityMatch.objects.get(facility=facility)
        self.assertEqual(match.facility_list_item_id, item.id)
        self.assertEqual(match.status, FacilityMatch.AUTOMATIC)
        self.assertTrue(match.is_active)
        self.assertEqual(float(match.confidence), 0.95)
        self.assertEqual(match.results['external_id'], 'NC0')

        # A point-only record (null polygon, centroid present) is ingested.
        point_only = self._candidates().get(external_id='NC2')
        self.assertIsNone(point_only.polygon)
        self.assertAlmostEqual(point_only.location.x, SITE_LNG + 0.4)

        # Confirmed surfaces never see the new rows.
        self.assertEqual(Facility.objects.filter(source=SOURCE).count(), 0)

    def test_running_twice_yields_one_facility_and_os_id_per_detection(
        self
    ):
        self._run('--file', self.json_path)
        first_ids = dict(
            self._candidates().values_list('external_id', 'id')
        )
        sources_before = Source.objects.count()
        items_before = FacilityListItem.objects.count()
        matches_before = FacilityMatch.objects.count()

        out, _ = self._run('--file', self.json_path)

        self.assertIn('created=0 updated=3', out)
        self.assertEqual(self._candidates().count(), 3)
        self.assertEqual(
            dict(self._candidates().values_list('external_id', 'id')),
            first_ids,
        )
        self.assertEqual(Source.objects.count(), sources_before)
        self.assertEqual(FacilityListItem.objects.count(), items_before)
        self.assertEqual(FacilityMatch.objects.count(), matches_before)

    def test_reingest_updates_in_place_and_never_flips_is_candidate(self):
        self._run('--file', self.json_path)
        facility = self._candidates().get(external_id='NC0')
        os_id = facility.id
        # Simulate the community confirming the candidate in the meantime.
        Facility.including_candidates.filter(pk=os_id).update(
            is_candidate=False
        )

        changed = self._write(
            'changed.json',
            [_prototype_record('NC0', SITE_LNG + 0.001, SITE_LAT, 0.42)],
        )
        self._run('--file', changed)

        facility = Facility.including_candidates.get(pk=os_id)
        self.assertFalse(facility.is_candidate)
        self.assertAlmostEqual(facility.confidence, 0.42)
        self.assertAlmostEqual(facility.location.x, SITE_LNG + 0.001)
        self.assertAlmostEqual(
            facility.polygon.centroid.x, SITE_LNG + 0.001
        )
        self.assertEqual(
            facility.created_from.raw_json['confidence'], 0.42
        )
        self.assertEqual(
            float(FacilityMatch.objects.get(facility=facility).confidence),
            0.42,
        )
        self.assertEqual(
            Facility.including_candidates.filter(
                source=SOURCE, external_id='NC0'
            ).count(),
            1,
        )

    def test_geojson_feature_collection_skips_null_geometry(self):
        out, _ = self._run('--file', self.geojson_path)

        self.assertEqual(self._candidates().count(), 3)
        self.assertEqual(
            set(self._candidates().values_list('external_id', flat=True)),
            {'AL0', 'AL1', 'AL2'},
        )
        self.assertIn('skipped_no_geometry=1', out)
        self.assertIn('created=3', out)

        facility = self._candidates().get(external_id='AL0')
        self.assertAlmostEqual(facility.confidence, 0.93)
        self.assertAlmostEqual(facility.location.x, SITE_LNG, places=5)
        self.assertAlmostEqual(facility.location.y, SITE_LAT, places=5)
        self.assertEqual(facility.created_from.raw_json['properties'],
                         {'confidence': 0.93, 'id': 'AL0'})

        # Running the GeoJSON again is idempotent too.
        out, _ = self._run('--file', self.geojson_path)
        self.assertIn('created=0 updated=3', out)
        self.assertEqual(self._candidates().count(), 3)

    def test_retired_detection_is_never_recreated(self):
        FacilityAlias.objects.create(
            os_id='US2024000AAAAAA',
            facility=None,
            reason=FacilityAlias.NOT_A_FACILITY,
            retired_source=SOURCE,
            retired_external_id='NC1',
            retirement_tally={'confirmed': 0, 'not_a_facility': 5},
        )

        out, _ = self._run('--file', self.json_path)

        self.assertIn('created=2', out)
        self.assertIn('skipped_retired=1', out)
        self.assertFalse(
            self._candidates().filter(external_id='NC1').exists()
        )
        self.assertEqual(self._candidates().count(), 2)

    def test_retirement_check_is_scoped_to_the_source(self):
        FacilityAlias.objects.create(
            os_id='US2024000AAAAAB',
            facility=None,
            reason=FacilityAlias.NOT_A_FACILITY,
            retired_source='some_other_source',
            retired_external_id='NC1',
            retirement_tally={},
        )

        out, _ = self._run('--file', self.json_path)

        self.assertIn('created=3', out)
        self.assertTrue(
            self._candidates().filter(external_id='NC1').exists()
        )

    def test_suggested_matches_lists_nearby_confirmed_facilities_only(self):
        self._run('--file', self.json_path)
        candidate = self._candidates().get(external_id='NC0')
        # A second candidate right next to the first one.
        self._run(
            '--file',
            self._write(
                'neighbour.json',
                [_prototype_record('NC9', SITE_LNG, SITE_LAT + 0.0005)],
            ),
        )
        self.assertEqual(self._candidates().count(), 4)

        suggestions = suggested_matches(candidate)

        self.assertEqual(
            [row['os_id'] for row in suggestions], [self.near_facility.id]
        )
        near = suggestions[0]
        self.assertEqual(near['name'], 'Near Farm')
        self.assertEqual(near['address'], '1 Main Street')
        self.assertGreater(near['distance_m'], 200)
        self.assertLess(near['distance_m'], 250)

        # The far facility is outside the default radius but inside a
        # wider one; the candidate neighbour is never suggested.
        wider = suggested_matches(candidate, radius_m=10_000)
        self.assertEqual(
            [row['os_id'] for row in wider],
            [self.near_facility.id, self.far_facility.id],
        )
        self.assertEqual(
            [row['os_id'] for row in suggested_matches(candidate, limit=1)],
            [self.near_facility.id],
        )
        other_candidate = self._candidates().get(external_id='NC9')
        self.assertEqual(
            [row['os_id'] for row in suggested_matches(other_candidate)],
            [self.near_facility.id],
        )
        self.assertEqual(
            suggested_matches(self._candidates().get(external_id='NC1')), []
        )

    @override_settings(
        CANDIDATE_SUGGESTION_RADIUS_M=100, CANDIDATE_SUGGESTION_LIMIT=1
    )
    def test_suggested_matches_defaults_come_from_settings(self):
        self._run('--file', self.json_path)
        candidate = self._candidates().get(external_id='NC0')

        self.assertEqual(suggested_matches(candidate), [])
        with override_settings(CANDIDATE_SUGGESTION_RADIUS_M=10_000):
            self.assertEqual(
                [row['os_id'] for row in suggested_matches(candidate)],
                [self.near_facility.id],
            )

    def test_summary_counts_suggestions_and_verbose_lists_them(self):
        out, _ = self._run('--file', self.json_path, verbosity=2)

        self.assertIn('with_suggestions=1 (suggestions=1)', out)
        self.assertIn(self.near_facility.id, out)
        self.assertIn("'Near Farm'", out)
        self.assertNotIn(self.far_facility.id, out)

    def test_dry_run_reports_without_writing(self):
        facilities_before = Facility.including_candidates.count()
        sources_before = Source.objects.count()

        out, _ = self._run('--file', self.json_path, '--dry-run')

        self.assertEqual(
            Facility.including_candidates.count(), facilities_before
        )
        self.assertEqual(Source.objects.count(), sources_before)
        self.assertIn('Dry run', out)
        self.assertIn('CREATE NC0 -> (new OS ID)', out)
        self.assertIn(self.near_facility.id, out)
        self.assertIn('created=3 updated=0', out)

        # After a real run a dry run classifies the same rows as updates.
        self._run('--file', self.json_path)
        out, _ = self._run('--file', self.json_path, '--dry-run')
        self.assertIn('created=0 updated=3', out)
        self.assertIn('UPDATE NC0 -> US', out)

    def test_limit_stops_after_n_records(self):
        out, _ = self._run('--file', self.json_path, '--limit', '2')

        self.assertEqual(
            set(self._candidates().values_list('external_id', flat=True)),
            {'NC0', 'NC1'},
        )
        self.assertIn('created=2', out)

    def test_source_and_country_code_options_are_recorded(self):
        self._run(
            '--file', self.json_path, '--source', 'other_sat',
            '--country-code', 'ca',
        )

        self.assertEqual(self._candidates().count(), 0)
        facility = Facility.including_candidates.get(
            source='other_sat', external_id='NC0'
        )
        self.assertEqual(facility.country_code, 'CA')
        self.assertTrue(facility.id.startswith('CA'))
        self.assertEqual(facility.created_from.country_code, 'CA')

    def test_invalid_country_code_is_refused(self):
        with self.assertRaises(CommandError) as ctx:
            self._run('--file', self.json_path, '--country-code', 'XX')
        self.assertIn('country code', str(ctx.exception))
        self.assertEqual(Facility.including_candidates.count(), 2)

    @override_settings(EARTH_GENOME_CONTRIBUTOR_ID=None)
    def test_refuses_to_run_when_contributor_setting_is_unset(self):
        with self.assertRaises(CommandError) as ctx:
            self._run('--file', self.json_path)
        self.assertIn(
            'EARTH_GENOME_CONTRIBUTOR_ID is not set', str(ctx.exception)
        )
        self.assertEqual(self._candidates().count(), 0)

    def test_refuses_to_run_when_contributor_does_not_exist(self):
        missing_id = Contributor.objects.order_by('-id').first().id + 1000
        with override_settings(EARTH_GENOME_CONTRIBUTOR_ID=missing_id):
            with self.assertRaises(CommandError) as ctx:
                self._run('--file', self.json_path)
        self.assertIn('does not match any Contributor', str(ctx.exception))
        self.assertEqual(self._candidates().count(), 0)

    def test_bad_records_are_counted_and_exit_non_zero(self):
        path = self._write(
            'mixed.json',
            [
                _prototype_record('NC0', SITE_LNG, SITE_LAT),
                {'eg_id': '', 'centroid_lat': 1, 'centroid_lng': 1},
                {
                    'eg_id': 'BAD-GEOM',
                    'polygon': {'type': 'Point', 'coordinates': [1, 1]},
                    'centroid_lat': 1,
                    'centroid_lng': 1,
                },
                _prototype_record('NC1', SITE_LNG + 0.2, SITE_LAT),
            ],
        )

        with self.assertRaises(CommandError) as ctx:
            self._run('--file', path)

        message = str(ctx.exception)
        self.assertIn('errors=2', message)
        self.assertIn('created=2', message)
        self.assertEqual(
            set(self._candidates().values_list('external_id', flat=True)),
            {'NC0', 'NC1'},
        )

    def test_unknown_file_shapes_are_refused(self):
        path = self._write('object.json', {'eg_id': 'NC0'})
        with self.assertRaises(CommandError):
            self._run('--file', path)
        with self.assertRaises(CommandError):
            self._run('--file', os.path.join(self.tmpdir.name, 'nope.json'))

    # --- review fixes: invalid rings are repaired, input can come from S3 -

    @staticmethod
    def _ring(*points):
        return {'type': 'Polygon', 'coordinates': [[list(p) for p in points]]}

    def test_self_touching_ring_is_repaired_with_a_warning(self):
        # A zero-width spike makes the ring self-intersect (the shape of
        # the AL674 polygon in the real export); make_valid drops the spike
        # and leaves the same square.
        x, y = SITE_LNG, SITE_LAT
        spike = self._ring(
            (x, y), (x + 0.002, y), (x + 0.002, y + 0.002),
            (x + 0.001, y + 0.002), (x + 0.001, y + 0.001),
            (x + 0.001, y + 0.002), (x, y + 0.002), (x, y),
        )
        record = _prototype_record('AL674', x + 0.001, y + 0.001)
        record['polygon'] = spike
        path = self._write('spike.json', [record])

        out, err = self._run('--file', path)

        self.assertIn('WARNING AL674: repaired invalid polygon', err)
        self.assertIn('repaired=1 errors=0', out)
        candidate = self._candidates().get(external_id='AL674')
        self.assertTrue(candidate.polygon.valid)
        self.assertAlmostEqual(0.002 * 0.002, candidate.polygon.area, places=9)

    def test_figure_eight_ring_is_an_error_not_a_lossy_repair(self):
        x, y = SITE_LNG, SITE_LAT
        bowtie = self._ring(
            (x, y), (x + 0.002, y + 0.002), (x + 0.002, y),
            (x, y + 0.002), (x, y),
        )
        record = _prototype_record('BOW1', x + 0.001, y + 0.001)
        record['polygon'] = bowtie
        path = self._write('bowtie.json', [record])

        with self.assertRaises(CommandError) as ctx:
            self._run('--file', path)

        self.assertIn('repaired=0 errors=1', str(ctx.exception))
        self.assertEqual(0, self._candidates().count())

    def test_file_can_be_an_s3_uri(self):
        calls = []
        json_path = self.json_path

        class FakeS3:
            def download_file(self, bucket, key, filename, ExtraArgs=None):
                calls.append((bucket, key, ExtraArgs))
                shutil.copyfile(json_path, filename)

        with override_settings(AWS_S3_ENDPOINT_URL='http://minio:9000',
                               AWS_S3_EXPECTED_BUCKET_OWNER=None), \
                patch('boto3.client', return_value=FakeS3()) as client:
            out, _ = self._run(
                '--file', 's3://os-hub-dev/earth-genome/detections.json'
            )

        client.assert_called_once_with(
            's3', endpoint_url='http://minio:9000'
        )
        # No owner configured (local MinIO): no ExpectedBucketOwner.
        self.assertEqual(
            [('os-hub-dev', 'earth-genome/detections.json', {})], calls
        )
        self.assertIn('created=3', out)

    def test_s3_download_verifies_the_bucket_owner_when_configured(self):
        calls = []
        json_path = self.json_path

        class FakeS3:
            def download_file(self, bucket, key, filename, ExtraArgs=None):
                calls.append(ExtraArgs)
                shutil.copyfile(json_path, filename)

        with override_settings(AWS_S3_EXPECTED_BUCKET_OWNER='123456789012'), \
                patch('boto3.client', return_value=FakeS3()):
            out, _ = self._run('--file', 's3://os-hub-dev/detections.json')

        self.assertEqual([{'ExpectedBucketOwner': '123456789012'}], calls)
        self.assertIn('created=3', out)
        self.assertEqual(3, self._candidates().count())

    def test_s3_download_failure_is_a_command_error(self):
        class FailingS3:
            def download_file(self, bucket, key, filename, ExtraArgs=None):
                raise ClientError(
                    {'Error': {'Code': 'NoSuchKey', 'Message': 'missing'}},
                    'GetObject',
                )

        with patch('boto3.client', return_value=FailingS3()):
            with self.assertRaises(CommandError) as ctx:
                self._run('--file', 's3://os-hub-dev/nope.json')

        self.assertIn(
            'Could not download s3://os-hub-dev/nope.json',
            str(ctx.exception),
        )
        self.assertEqual(0, self._candidates().count())

    def test_malformed_s3_uri_is_refused(self):
        with self.assertRaises(CommandError) as ctx:
            self._run('--file', 's3://bucket-only')
        self.assertIn('expected s3://<bucket>/<key>', str(ctx.exception))

    # --- Earth Index API input ------------------------------------------

    def _run_from_earth_index(self, fake, *args, **settings_overrides):
        overrides = {
            'EARTH_INDEX_API_KEY': 'ak_test_key',
            'EARTH_INDEX_API_URL': 'https://earth-index.test',
            **settings_overrides,
        }
        with override_settings(**overrides), \
                patch('api.services.earth_index.requests.get', fake):
            return self._run(*args)

    def test_project_mode_exports_finished_deep_searches(self):
        fake = FakeEarthIndex()

        out, err = self._run_from_earth_index(fake, '--project', PROJECT_ID)

        # Discovery, then one export of the finished deep searches on
        # the project (the running one is left out), newest last.
        self.assertEqual(
            ['https://earth-index.test/v1/projects/' + PROJECT_ID,
             'https://earth-index.test/v1/projects/' + PROJECT_ID
             + '/export'],
            [call['url'] for call in fake.calls],
        )
        export = fake.calls[1]
        self.assertEqual(
            {
                'format': 'geojson',
                'include_deep_search_results': 'true',
                'deep_search_ids': f'{DEEP_SEARCH_OLDER},{DEEP_SEARCH_OK}',
            },
            export['params'],
        )
        self.assertTrue(export['stream'])
        for call in fake.calls:
            self.assertEqual(
                'Bearer ak_test_key', call['headers']['Authorization']
            )
            self.assertIsNotNone(call['timeout'])
        self.assertIn(f'Exported {len(json.dumps(fake.export))} bytes', out)
        self.assertIn(f'from Earth Index project {PROJECT_ID}', out)
        self.assertIn('created=2', out)
        self.assertEqual('', err)

        candidates = self._candidates().order_by('external_id')
        self.assertEqual(
            ['14121384851571097', '14121408024753508'],
            [facility.external_id for facility in candidates],
        )
        facility = candidates.get(external_id='14121408024753508')
        self.assertAlmostEqual(0.9999, facility.confidence)
        item = facility.created_from
        self.assertEqual(DEEP_SEARCH_OK, item.raw_json['eg_model_version'])
        self.assertEqual(
            DEEP_SEARCH_OK, item.raw_json['properties']['deepSearchId']
        )
        self.assertEqual(LAYER_ID, item.raw_json['properties']['layerId'])
        match = FacilityMatch.objects.get(facility=facility)
        self.assertEqual(
            DEEP_SEARCH_OK, match.results['eg_model_version']
        )

    def test_layer_option_limits_discovery_to_one_layer(self):
        fake = FakeEarthIndex()

        self._run_from_earth_index(
            fake, '--project', PROJECT_ID, '--layer', LAYER_ID, '--dry-run'
        )

        self.assertEqual(
            DEEP_SEARCH_OK, fake.calls[1]['params']['deep_search_ids']
        )

    def test_explicit_deep_search_skips_discovery_and_uses_setting(self):
        fake = FakeEarthIndex()

        out, _ = self._run_from_earth_index(
            fake,
            '--deep-search', DEEP_SEARCH_OK,
            '--deep-search', DEEP_SEARCH_OLDER,
            '--facility-type', 'poultry',
            '--dry-run',
            EARTH_INDEX_PROJECT_ID=PROJECT_ID,
        )

        # With the deep searches and the facility type given there is
        # nothing to discover: the export is the only call.
        self.assertEqual(1, len(fake.calls))
        self.assertEqual(
            f'{DEEP_SEARCH_OK},{DEEP_SEARCH_OLDER}',
            fake.calls[0]['params']['deep_search_ids'],
        )
        self.assertIn('Dry run: ingesting 2 record(s)', out)
        self.assertIn('created=2', out)
        self.assertEqual(0, self._candidates().count())

    def test_bare_project_flag_takes_the_project_from_settings(self):
        fake = FakeEarthIndex()

        out, _ = self._run_from_earth_index(
            fake, '--project', '--dry-run', EARTH_INDEX_PROJECT_ID=PROJECT_ID
        )

        self.assertIn(f'/v1/projects/{PROJECT_ID}', fake.calls[0]['url'])
        self.assertIn('created=2', out)

    def test_project_target_label_is_the_default_facility_type(self):
        Sector.objects.get_or_create(name='Animal Production')
        fake = FakeEarthIndex(project=_project_record(target_label='poultry'))

        self._run_from_earth_index(fake, '--project', PROJECT_ID)

        item = self._candidates().first().created_from
        self.assertEqual('poultry', item.raw_json['probable_facility_type'])
        self.assertEqual(['Animal Production'], item.sector)

    def test_facility_type_option_wins_over_target_label(self):
        fake = FakeEarthIndex(project=_project_record(target_label='poultry'))

        self._run_from_earth_index(
            fake, '--project', PROJECT_ID, '--facility-type', 'aquaculture'
        )

        item = self._candidates().first().created_from
        self.assertEqual(
            'aquaculture', item.raw_json['probable_facility_type']
        )

    def test_facility_type_option_applies_to_file_input_too(self):
        Sector.objects.get_or_create(name='Animal Production')

        self._run(
            '--file', self.geojson_path, '--facility-type', 'poultry'
        )

        sectors = {
            tuple(facility.created_from.sector)
            for facility in self._candidates()
        }
        self.assertEqual({('Animal Production',)}, sectors)

    def test_non_detection_features_in_an_export_are_skipped(self):
        fake = FakeEarthIndex()
        fake.export['features'].insert(0, _aoi_feature())

        out, err = self._run_from_earth_index(fake, '--project', PROJECT_ID)

        self.assertIn('created=2', out)
        self.assertIn('skipped_not_detection=1', out)
        self.assertEqual('', err)
        self.assertEqual(2, self._candidates().count())

    def test_project_mode_requires_an_api_key(self):
        fake = FakeEarthIndex()

        with self.assertRaises(CommandError) as ctx:
            self._run_from_earth_index(
                fake, '--project', PROJECT_ID, EARTH_INDEX_API_KEY=None
            )

        self.assertIn('EARTH_INDEX_API_KEY is not set', str(ctx.exception))
        self.assertEqual([], fake.calls)

    def test_project_mode_requires_a_project(self):
        fake = FakeEarthIndex()

        with self.assertRaises(CommandError) as ctx:
            self._run_from_earth_index(
                fake, '--project', EARTH_INDEX_PROJECT_ID=None
            )

        self.assertIn('EARTH_INDEX_PROJECT_ID', str(ctx.exception))
        self.assertEqual([], fake.calls)

    def test_no_finished_deep_search_is_a_command_error(self):
        project = _project_record()
        project['deep_searches'] = [project['deep_searches'][1]]
        fake = FakeEarthIndex(project=project)

        with self.assertRaises(CommandError) as ctx:
            self._run_from_earth_index(fake, '--project', PROJECT_ID)

        self.assertIn('has no finished deep search', str(ctx.exception))
        self.assertEqual(1, len(fake.calls))
        self.assertEqual(0, self._candidates().count())

    def test_earth_index_http_error_is_a_command_error(self):
        fake = FakeEarthIndex(status=401)

        with self.assertRaises(CommandError) as ctx:
            self._run_from_earth_index(fake, '--project', PROJECT_ID)

        message = str(ctx.exception)
        self.assertIn('Earth Index answered 401', message)
        self.assertIn('invalid api key', message)
        self.assertNotIn('ak_test_key', message)
        self.assertEqual(0, self._candidates().count())

    def test_file_and_project_are_mutually_exclusive(self):
        with self.assertRaises(CommandError) as ctx:
            self._run('--file', self.json_path, '--project', PROJECT_ID)
        self.assertIn('not both', str(ctx.exception))

    def test_an_input_is_required(self):
        with self.assertRaises(CommandError) as ctx:
            self._run()
        self.assertIn('Nothing to ingest', str(ctx.exception))
