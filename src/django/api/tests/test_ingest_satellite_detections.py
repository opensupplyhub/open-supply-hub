import json
import os
import tempfile
from io import StringIO

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
from api.services.candidate_matches import suggested_matches
from django.contrib.gis.geos import Point
from django.core.management import call_command
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
