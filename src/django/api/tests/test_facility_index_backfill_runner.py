import os
import tempfile
from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.management.color import no_style
from django.test import SimpleTestCase

from api.facility_index_backfill.runner import (
    FIELD_NAME_ENV,
    RESULT_FILE_ENV,
    WORKERS_ENV,
    WORKER_ID_ENV,
    FacilityIndexBackfillRunner,
)


_REAL_MKSTEMP = tempfile.mkstemp


def make_runner(stdout=None):
    if stdout is None:
        stdout = StringIO()
    return FacilityIndexBackfillRunner(stdout, no_style()), stdout


class FacilityIndexBackfillRunnerTest(SimpleTestCase):
    def test_write_worker_result_writes_row_count_to_file(self):
        runner, _ = make_runner()
        with tempfile.NamedTemporaryFile(
            mode='w+',
            delete=False,
        ) as result_file:
            result_path = result_file.name

        try:
            with patch.dict(os.environ, {RESULT_FILE_ENV: result_path}):
                runner._write_worker_result(42)

            with open(result_path, encoding='utf-8') as result:
                self.assertEqual(result.read(), '42')
        finally:
            os.unlink(result_path)

    @patch('api.facility_index_backfill.runner.connection')
    def test_run_worker_live_path_updates_in_batches(self, mock_connection):
        runner, stdout = make_runner()
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

        with patch('api.facility_index_backfill.runner.transaction.atomic'):
            total = runner._run_worker(
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

    @patch('api.facility_index_backfill.runner.connection')
    def test_run_worker_zero_rows_skips_update_loop(self, mock_connection):
        runner, stdout = make_runner()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (0,)
        mock_connection.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        with patch('api.facility_index_backfill.runner.transaction.atomic'):
            total = runner._run_worker(
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

    @patch('api.facility_index_backfill.runner.connection')
    @patch.dict(
        os.environ,
        {
            WORKER_ID_ENV: '1',
            WORKERS_ENV: '4',
            FIELD_NAME_ENV: 'contributors',
        },
        clear=False,
    )
    def test_worker_mode_via_env_skips_parallel_spawn(self, mock_connection):
        runner, stdout = make_runner()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (7,)
        mock_connection.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        with patch.object(runner, '_spawn_parallel_workers') as mock_spawn:
            total = runner.run(
                field_names=['contributors'],
                parallel=10,
                batch_size=100,
                dry_run=True,
            )

        mock_spawn.assert_not_called()
        self.assertEqual(total, 7)
        self.assertIn('Worker 2/4 (contributors)', stdout.getvalue())

    @patch.dict(
        os.environ,
        {WORKER_ID_ENV: '0', WORKERS_ENV: '2'},
        clear=False,
    )
    def test_worker_mode_requires_field_name_env(self):
        runner, _ = make_runner()
        env = os.environ.copy()
        env.pop(FIELD_NAME_ENV, None)

        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(CommandError) as context:
                runner.run(
                    field_names=['contributors'],
                    parallel=1,
                    batch_size=100,
                    dry_run=True,
                )

        self.assertIn(FIELD_NAME_ENV, str(context.exception))

    @patch.dict(
        os.environ,
        {
            WORKER_ID_ENV: '2',
            WORKERS_ENV: '2',
            FIELD_NAME_ENV: 'contributors',
        },
        clear=False,
    )
    def test_worker_mode_rejects_out_of_range_worker_id(self):
        runner, _ = make_runner()

        with self.assertRaises(CommandError) as context:
            runner.run(
                field_names=['contributors'],
                parallel=1,
                batch_size=100,
                dry_run=True,
            )

        self.assertIn(
            'Worker id must be between 0 and 1',
            str(context.exception),
        )

    @patch('api.facility_index_backfill.runner.subprocess.Popen')
    @patch('api.facility_index_backfill.runner.tempfile.mkstemp')
    def test_spawn_parallel_workers_aggregates_worker_results(
        self,
        mock_mkstemp,
        mock_popen,
    ):
        runner, stdout = make_runner()
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

        total = runner._spawn_parallel_workers(
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
            env = mock_popen.call_args_list[worker_id][1]['env']
            self.assertEqual(env[WORKERS_ENV], '3')
            self.assertEqual(env[WORKER_ID_ENV], str(worker_id))
            self.assertEqual(env[FIELD_NAME_ENV], 'contributors')
            self.assertIn(RESULT_FILE_ENV, env)

        for path in result_paths:
            self.assertFalse(os.path.exists(path))

    @patch('api.facility_index_backfill.runner.subprocess.Popen')
    @patch('api.facility_index_backfill.runner.tempfile.mkstemp')
    def test_spawn_parallel_workers_raises_on_worker_failure(
        self,
        mock_mkstemp,
        mock_popen,
    ):
        runner, _ = make_runner()
        fd, path = _REAL_MKSTEMP()
        mock_mkstemp.return_value = (fd, path)

        failed_process = MagicMock()
        failed_process.wait.return_value = 1
        mock_popen.return_value = failed_process

        with self.assertRaises(CommandError) as context:
            runner._spawn_parallel_workers(
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

    @patch('api.facility_index_backfill.runner.subprocess.Popen')
    @patch('api.facility_index_backfill.runner.connection')
    def test_parallel_one_does_not_spawn_subprocess(
        self,
        mock_connection,
        mock_popen,
    ):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_connection.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        stdout = StringIO()
        call_command(
            'backfill_facility_index',
            fields='contributors',
            parallel=1,
            dry_run=True,
            stdout=stdout,
        )

        mock_popen.assert_not_called()

    def test_run_writes_completed_summary_for_multiple_field_groups(self):
        runner, stdout = make_runner()

        with patch.object(
            runner,
            '_run_field_group',
            side_effect=[4, 6],
        ):
            total = runner.run(
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
