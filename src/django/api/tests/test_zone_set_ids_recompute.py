from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings
from waffle.testutils import override_switch

from api.facility_index_backfill import zone_set_ids_recompute
from api.facility_index_backfill.zone_set_ids_recompute import (
    BATCH_PARALLEL_WORKERS,
    INLINE_RESULT,
    backfill_command,
    recompute_zone_set_ids,
)
from api.models import Contributor, User, Zone, ZoneSet
from api.models.facility.facility_index import FacilityIndex
from api.models.partner_field import PartnerField
from api.partner_fields.registry import ZONE_SETS_SWITCH
from api.tests.test_partner_contributor_filter_zone_sets import make_facility
from api.tests.test_zone_set_provider import EAST, WEST, feature, zone_records

RECOMPUTE = (
    'api.facility_index_backfill.zone_set_ids_recompute.'
    'recompute_zone_set_ids'
)
BOTO_CLIENT = 'api.facility_index_backfill.zone_set_ids_recompute.boto3.client'
ROLLBAR = (
    'api.facility_index_backfill.zone_set_ids_recompute.'
    'report_error_to_rollbar'
)


@override_switch(ZONE_SETS_SWITCH, active=True)
class ZoneSetIdsRecomputeTest(TestCase):
    """Tests for recomputing `FacilityIndex.zone_set_ids` after a zone
    set's zones change."""

    def setUp(self):
        self.user = User.objects.create(email='aqueduct@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='WRI Aqueduct',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.partner_field = PartnerField.objects.create(
            name='aqueduct_water_stress',
            type=PartnerField.STRING,
            label='Baseline water stress',
            active=True,
        )
        self.zone_set = ZoneSet.objects.create(
            name='aqueduct_bws',
            description='Baseline water stress bands.',
            partner_field=self.partner_field,
            value_property='bws_label',
        )
        self.inside = make_facility(self.contributor, 76.9, 28.6)
        self.outside = make_facility(self.contributor, 75.0, 20.0)

    def _zone_set_ids(self, facility):
        return FacilityIndex.objects.get(id=facility.id).zone_set_ids

    def _insert_zones_without_replace_zones(self):
        """Create zones behind the model's back, so the index rows are
        stale until a recompute runs."""
        for index, record in enumerate(zone_records(
            feature(WEST, {'bws_label': 'Extremely High'}),
            feature(EAST, {'bws_label': 'Low'}),
        )):
            Zone.objects.create(
                zone_set=self.zone_set,
                feature_index=index,
                geom=record['geom'],
                value={'label': record['label'], 'properties': {}},
            )

    def test_replace_zones_schedules_the_recompute_on_commit(self):
        """The recompute is queued for commit (not run inside the
        transaction), so it sees the committed zones and a rolled-back
        replacement queues nothing."""
        with patch(RECOMPUTE) as recompute:
            with self.captureOnCommitCallbacks(execute=False) as callbacks:
                self.zone_set.replace_zones(zone_records(
                    feature(WEST, {'bws_label': 'Extremely High'}),
                ))
            recompute.assert_not_called()

            for callback in callbacks:
                callback()
            recompute.assert_called_once_with()

    @override_settings(ENVIRONMENT='Local')
    def test_inline_recompute_refreshes_stale_rows(self):
        """In local development (and here) the backfill runs
        in-process and brings every row's membership up to date."""
        self._insert_zones_without_replace_zones()
        self.assertEqual(self._zone_set_ids(self.inside), [])

        result = recompute_zone_set_ids()

        self.assertEqual(result, INLINE_RESULT)
        self.assertEqual(self._zone_set_ids(self.inside), [self.zone_set.id])
        self.assertEqual(self._zone_set_ids(self.outside), [])

    @override_settings(ENVIRONMENT='Local')
    def test_inline_recompute_clears_rows_the_new_zones_left(self):
        """A location the previous zones covered and the new ones do
        not is cleared, not left with a stale id."""
        with self.captureOnCommitCallbacks(execute=True):
            self.zone_set.replace_zones(zone_records(
                feature(WEST, {'bws_label': 'Extremely High'}),
            ))
        self.assertEqual(self._zone_set_ids(self.inside), [self.zone_set.id])

        Zone.objects.filter(zone_set=self.zone_set).delete()
        recompute_zone_set_ids()

        self.assertEqual(self._zone_set_ids(self.inside), [])

    @override_settings(
        ENVIRONMENT='Test',
        BATCH_JOB_QUEUE_NAME='queueTestDefault',
        BATCH_JOB_DEF_NAME='jobTestDefault',
    )
    def test_deployed_recompute_is_submitted_to_batch(self):
        """Outside local development the pass over the table is handed
        to the default Batch queue, with the container command
        overridden to run the zone_set_ids backfill."""
        client = Mock()
        client.submit_job.return_value = {'jobId': 'job-123'}

        with patch(BOTO_CLIENT, return_value=client) as boto_client:
            result = recompute_zone_set_ids()

        self.assertEqual(result, 'job-123')
        boto_client.assert_called_once()
        self.assertEqual(boto_client.call_args.args, ('batch',))
        kwargs = client.submit_job.call_args.kwargs
        self.assertEqual(kwargs['jobQueue'], 'queueTestDefault')
        self.assertEqual(kwargs['jobDefinition'], 'jobTestDefault')
        self.assertTrue(
            kwargs['jobName'].startswith('zone-set-ids-recompute-')
        )
        self.assertEqual(
            kwargs['containerOverrides'],
            {'command': backfill_command(BATCH_PARALLEL_WORKERS)},
        )
        self.assertEqual(
            backfill_command(2),
            [
                'python', 'manage.py', 'backfill_facility_index',
                '--fields', 'zone_set_ids',
                '--parallel', '2',
                '--batch-size', str(zone_set_ids_recompute.BATCH_SIZE),
            ],
        )

    @override_settings(
        ENVIRONMENT='Test',
        BATCH_JOB_QUEUE_NAME='queueTestDefault',
        BATCH_JOB_DEF_NAME='jobTestDefault',
    )
    def test_submission_failure_is_reported_not_raised(self):
        """The recompute runs after the zones have committed, so a
        Batch failure is logged and reported to Rollbar rather than
        turning a successful save into an error."""
        client = Mock()
        client.submit_job.side_effect = RuntimeError('batch is down')

        with patch(BOTO_CLIENT, return_value=client), \
                patch(ROLLBAR) as rollbar, \
                self.assertLogs(zone_set_ids_recompute.log, level='ERROR'):
            result = recompute_zone_set_ids()

        self.assertIsNone(result)
        rollbar.assert_called_once()
        self.assertIn(
            'batch is down', rollbar.call_args.kwargs['message']
        )

    @override_settings(ENVIRONMENT='Local')
    def test_new_facility_inside_a_zone_is_indexed_on_save(self):
        """The trigger path: a facility saved after the zones exist gets
        its membership from `index_facilities_by` with no recompute."""
        with self.captureOnCommitCallbacks(execute=True):
            self.zone_set.replace_zones(zone_records(
                feature(EAST, {'bws_label': 'Low'}),
            ))

        facility = make_facility(self.contributor, 77.3, 28.6)

        self.assertEqual(self._zone_set_ids(facility), [self.zone_set.id])
        self.assertIsNotNone(
            self.zone_set.resolve_zone(Point(77.3, 28.6, srid=4326))
        )
