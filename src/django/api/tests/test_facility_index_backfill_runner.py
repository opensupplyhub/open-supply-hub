import os
import tempfile
from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.management.color import no_style
from django.test import SimpleTestCase

from api.facility_index_backfill.backfill_orchestrator import (
    BackfillOrchestrator,
)
from api.facility_index_backfill.backfill_worker import BackfillWorker


_REAL_MKSTEMP = tempfile.mkstemp


def make_orchestrator(stdout=None):
    if stdout is None:
        stdout = StringIO()
    return BackfillOrchestrator(stdout, no_style()), stdout


def make_worker(stdout=None):
    if stdout is None:
        stdout = StringIO()
    return BackfillWorker(stdout, no_style()), stdout


class BackfillWorkerTest(SimpleTestCase):
    def test_write_worker_result_writes_row_count_to_file(self):
        with tempfile.NamedTemporaryFile(
            mode='w+',
            delete=False,
        ) as result_file:
            result_path = result_file.name

        try:
            BackfillWorker._write_worker_result(42, result_path)

            with open(result_path, encoding='utf-8') as result:
                self.assertEqual(result.read(), '42')
        finally:
            os.unlink(result_path)

    @patch('api.facility_index_backfill.backfill_worker.connection')
    def test_run_updates_in_batches(self, mock_connection):
        worker, stdout = make_worker()
        count_cursor = MagicMock()
        count_cursor.fetchone.return_value = (2,)

        batch_one_cursor = MagicMock()
        batch_one_cursor.fetchall.return_value = [('aaa',), ('bbb',)]

        batch_two_cursor = MagicMock()
        batch_two_cursor.fetchall.return_value = []

        mock_connection.cursor.return_value.__enter__.side_effect = [
            count_cursor,
            batch_one_cursor,
            batch_two_cursor,
        ]

        with patch(
            'api.facility_index_backfill.backfill_worker.transaction.atomic',
        ):
            total = worker.run(
                field_name='contributors',
                worker_id=0,
                workers=1,
                batch_size=10,
                dry_run=False,
            )

        self.assertEqual(total, 2)
        self.assertIn('batch 1 updated 2 rows', stdout.getvalue())
        self.assertIn('finished: 2 rows updated', stdout.getvalue())
        self.assertEqual(
            batch_one_cursor.execute.call_args[0][1]['last_id'],
            '',
        )
        self.assertEqual(
            batch_two_cursor.execute.call_args[0][1]['last_id'],
            'bbb',
        )

    @patch('api.facility_index_backfill.backfill_worker.connection')
    def test_run_zero_rows_skips_update_loop(self, mock_connection):
        worker, stdout = make_worker()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (0,)
        mock_connection.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        with patch(
            'api.facility_index_backfill.backfill_worker.transaction.atomic',
        ):
            total = worker.run(
                field_name='contributors',
                worker_id=0,
                workers=1,
                batch_size=10,
                dry_run=False,
            )

        self.assertEqual(total, 0)
        self.assertEqual(mock_cursor.execute.call_count, 2)
        self.assertIn('0 rows assigned', stdout.getvalue())
        self.assertIn('finished: 0 rows updated', stdout.getvalue())


class BackfillOrchestratorTest(SimpleTestCase):
    @patch(
        'api.facility_index_backfill.backfill_orchestrator.subprocess.Popen',
    )
    @patch(
        'api.facility_index_backfill.backfill_orchestrator.tempfile.mkstemp',
    )
    def test_spawn_parallel_workers_aggregates_worker_results(
        self,
        mock_mkstemp,
        mock_popen,
    ):
        orchestrator, stdout = make_orchestrator()
        result_paths = []
        worker_counts = [10, 20, 5]

        def mkstemp_side_effect(**kwargs):
            fd, path = _REAL_MKSTEMP(
                suffix=kwargs.get('suffix', '.txt'),
            )
            result_paths.append(path)
            return fd, path

        mock_mkstemp.side_effect = mkstemp_side_effect

        processes = []
        for index, count in enumerate(worker_counts):
            process = MagicMock()

            def make_wait(result_index=index, row_count=count):
                def wait():
                    with open(
                        result_paths[result_index],
                        'w',
                        encoding='utf-8',
                    ) as result:
                        result.write(str(row_count))
                    return 0

                return wait

            process.wait.side_effect = make_wait()
            processes.append(process)

        mock_popen.side_effect = processes

        total = orchestrator._spawn_parallel_workers(
            field_name='contributors',
            parallel=3,
            batch_size=100,
            dry_run=True,
        )

        self.assertEqual(total, 35)
        self.assertEqual(mock_popen.call_count, 3)
        self.assertIn(
            'Spawning 3 backfill worker processes',
            stdout.getvalue(),
        )

        for worker_id, process in enumerate(processes):
            cmd = mock_popen.call_args_list[worker_id][0][0]
            self.assertIn('backfill_facility_index_worker', cmd)
            self.assertIn('--field', cmd)
            self.assertIn('contributors', cmd)
            self.assertIn('--worker-id', cmd)
            self.assertIn(str(worker_id), cmd)
            self.assertIn('--workers', cmd)
            self.assertIn('3', cmd)
            self.assertIn('--result-file', cmd)
            self.assertIn('--dry-run', cmd)

        for path in result_paths:
            self.assertFalse(os.path.exists(path))

    @patch(
        'api.facility_index_backfill.backfill_orchestrator.subprocess.Popen',
    )
    @patch(
        'api.facility_index_backfill.backfill_orchestrator.tempfile.mkstemp',
    )
    def test_spawn_parallel_workers_raises_on_worker_failure(
        self,
        mock_mkstemp,
        mock_popen,
    ):
        orchestrator, _ = make_orchestrator()
        fd, path = _REAL_MKSTEMP()
        mock_mkstemp.return_value = (fd, path)

        failed_process = MagicMock()
        failed_process.wait.return_value = 1
        mock_popen.return_value = failed_process

        with self.assertRaises(CommandError) as context:
            orchestrator._spawn_parallel_workers(
                field_name='contributors',
                parallel=1,
                batch_size=100,
                dry_run=False,
            )

        self.assertIn(
            'Backfill failed for contributors',
            str(context.exception),
        )
        self.assertIn('worker 1 (exit 1)', str(context.exception))
        self.assertFalse(os.path.exists(path))

    @patch(
        'api.facility_index_backfill.backfill_orchestrator.subprocess.Popen',
    )
    @patch(
        'api.facility_index_backfill.backfill_orchestrator.tempfile.mkstemp',
    )
    def test_parallel_one_spawns_single_worker_subprocess(
        self,
        mock_mkstemp,
        mock_popen,
    ):
        orchestrator, stdout = make_orchestrator()
        fd, path = _REAL_MKSTEMP()
        mock_mkstemp.return_value = (fd, path)

        process = MagicMock()

        def wait():
            with open(path, 'w', encoding='utf-8') as result:
                result.write('1')
            return 0

        process.wait.side_effect = wait
        mock_popen.return_value = process

        call_command(
            'backfill_facility_index',
            fields='contributors',
            parallel=1,
            dry_run=True,
            stdout=stdout,
        )

        mock_popen.assert_called_once()
        cmd = mock_popen.call_args[0][0]
        self.assertIn('backfill_facility_index_worker', cmd)
        self.assertIn('--worker-id', cmd)
        self.assertIn('0', cmd)
        self.assertIn('--workers', cmd)
        self.assertIn('1', cmd)
        self.assertFalse(os.path.exists(path))

    def test_run_writes_completed_summary_for_multiple_field_groups(self):
        orchestrator, stdout = make_orchestrator()

        with patch.object(
            orchestrator,
            '_run_field_group',
            side_effect=[4, 6],
        ):
            total = orchestrator.run(
                field_names=['contributors', 'contributors'],
                parallel=1,
                batch_size=100,
                dry_run=False,
            )

        self.assertEqual(total, 10)
        self.assertIn(
            'Backfill completed (contributors, contributors): 10 rows updated',
            stdout.getvalue(),
        )


class BackfillFacilityIndexWorkerCommandTest(SimpleTestCase):
    @patch('api.facility_index_backfill.backfill_worker.connection')
    def test_worker_command_runs_single_partition(self, mock_connection):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (7,)
        mock_connection.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        stdout = StringIO()
        call_command(
            'backfill_facility_index_worker',
            field='contributors',
            worker_id=1,
            workers=4,
            dry_run=True,
            stdout=stdout,
        )

        self.assertIn('Worker 2/4 (contributors)', stdout.getvalue())
        self.assertIn('7 rows assigned', stdout.getvalue())

    def test_worker_command_rejects_out_of_range_worker_id(self):
        with self.assertRaises(CommandError) as context:
            call_command(
                'backfill_facility_index_worker',
                field='contributors',
                worker_id=2,
                workers=2,
                dry_run=True,
            )

        self.assertIn(
            'Worker id must be between 0 and 1',
            str(context.exception),
        )

    def test_worker_command_rejects_unknown_field(self):
        with self.assertRaises(CommandError) as context:
            call_command(
                'backfill_facility_index_worker',
                field='bogus',
                worker_id=0,
                workers=1,
                dry_run=True,
            )

        self.assertIn('Unknown field group', str(context.exception))

    def test_worker_command_validates_batch_size(self):
        with self.assertRaises(CommandError) as context:
            call_command(
                'backfill_facility_index_worker',
                field='contributors',
                worker_id=0,
                workers=1,
                batch_size=0,
                dry_run=True,
            )

        self.assertIn(
            '--batch-size must be at least 1',
            str(context.exception),
        )

    def test_worker_command_validates_workers(self):
        with self.assertRaises(CommandError) as context:
            call_command(
                'backfill_facility_index_worker',
                field='contributors',
                worker_id=0,
                workers=0,
                dry_run=True,
            )

        self.assertIn('--workers must be at least 1', str(context.exception))
