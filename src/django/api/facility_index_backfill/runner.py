import os
import subprocess
import sys
import tempfile
import time

from django.core.management.base import CommandError
from django.db import connection, transaction

from api.facility_index_backfill.specs import (
    build_count_sql,
    build_update_sql,
    get_field_spec,
)

WORKER_ID_ENV = 'BACKFILL_FACILITY_INDEX_WORKER_ID'
WORKERS_ENV = 'BACKFILL_FACILITY_INDEX_WORKERS'
RESULT_FILE_ENV = 'BACKFILL_FACILITY_INDEX_RESULT_FILE'
FIELD_NAME_ENV = 'BACKFILL_FACILITY_INDEX_FIELD_NAME'


class FacilityIndexBackfillRunner:
    command_name = 'backfill_facility_index'

    def __init__(self, stdout, style):
        self.stdout = stdout
        self.style = style

    def run(self, field_names, parallel, batch_size, dry_run):
        if parallel < 1:
            raise CommandError('--parallel must be at least 1.')

        worker_id_env = os.environ.get(WORKER_ID_ENV)
        workers_env = os.environ.get(WORKERS_ENV)
        field_name_env = os.environ.get(FIELD_NAME_ENV)

        if worker_id_env is not None and workers_env is not None:
            if not field_name_env:
                raise CommandError(
                    f'{FIELD_NAME_ENV} must be set for worker processes.'
                )
            workers = int(workers_env)
            worker_id = int(worker_id_env)
            if workers < 1:
                raise CommandError('Worker count must be at least 1.')
            if worker_id < 0 or worker_id >= workers:
                raise CommandError(
                    f'Worker id must be between 0 and {workers - 1}.'
                )
            return self._run_worker(
                field_name=field_name_env,
                worker_id=worker_id,
                workers=workers,
                batch_size=batch_size,
                dry_run=dry_run,
            )

        started_at = time.monotonic()
        total_rows = 0
        for field_name in field_names:
            total_rows += self._run_field_group(
                field_name=field_name,
                parallel=parallel,
                batch_size=batch_size,
                dry_run=dry_run,
            )

        self._write_summary(
            field_names,
            total_rows,
            time.monotonic() - started_at,
            dry_run,
        )
        return total_rows

    @staticmethod
    def _format_worker_number(worker_id, workers=None):
        """1-based worker label for logs; internal worker_id stays 0-based."""
        number = worker_id + 1
        if workers is not None:
            return f'{number}/{workers}'
        return str(number)

    def _run_field_group(self, field_name, parallel, batch_size, dry_run):
        get_field_spec(field_name)
        self.stdout.write(f'Backfilling field group: {field_name}')

        if parallel > 1:
            return self._spawn_parallel_workers(
                field_name=field_name,
                parallel=parallel,
                batch_size=batch_size,
                dry_run=dry_run,
            )

        return self._run_worker(
            field_name=field_name,
            worker_id=0,
            workers=1,
            batch_size=batch_size,
            dry_run=dry_run,
        )

    def _write_summary(self, field_names, total_rows, elapsed, dry_run):
        fields_label = ', '.join(field_names)
        if dry_run:
            message = (
                f'Backfill dry run ({fields_label}): {total_rows} rows would '
                f'be updated in {elapsed:.1f}s.'
            )
        else:
            message = (
                f'Backfill completed ({fields_label}): {total_rows} rows '
                f'updated in {elapsed:.1f}s.'
            )
        self.stdout.write(self.style.SUCCESS(message))

    def _write_worker_result(self, row_count):
        result_file = os.environ.get(RESULT_FILE_ENV)
        if not result_file:
            return
        with open(result_file, 'w', encoding='utf-8') as result:
            result.write(str(row_count))

    def _spawn_parallel_workers(
        self,
        field_name,
        parallel,
        batch_size,
        dry_run,
    ):
        manage_py = sys.argv[0]
        base_args = [
            manage_py,
            self.command_name,
            '--fields',
            field_name,
            '--batch-size',
            str(batch_size),
        ]
        if dry_run:
            base_args.append('--dry-run')

        self.stdout.write(
            f'Spawning {parallel} backfill worker processes for '
            f'{field_name}...'
        )
        processes = []
        result_files = []
        for worker_id in range(parallel):
            fd, result_path = tempfile.mkstemp(
                suffix=f'-{field_name}-worker{worker_id}.txt',
            )
            os.close(fd)
            result_files.append(result_path)
            env = os.environ.copy()
            env[WORKERS_ENV] = str(parallel)
            env[WORKER_ID_ENV] = str(worker_id)
            env[RESULT_FILE_ENV] = result_path
            env[FIELD_NAME_ENV] = field_name
            cmd = [sys.executable, *base_args]
            self.stdout.write(
                f'  worker {self._format_worker_number(worker_id)}: '
                f'{" ".join(cmd)}'
            )
            processes.append(subprocess.Popen(cmd, env=env))

        failures = []
        for worker_id, process in enumerate(processes):
            return_code = process.wait()
            if return_code != 0:
                failures.append((worker_id, return_code))

        if failures:
            for result_path in result_files:
                if os.path.exists(result_path):
                    os.unlink(result_path)
            details = ', '.join(
                f'worker {self._format_worker_number(worker_id)} (exit {code})'
                for worker_id, code in failures
            )
            raise CommandError(
                f'Backfill failed for {field_name}: {details}'
            )

        total_rows = 0
        for result_path in result_files:
            with open(result_path, encoding='utf-8') as result:
                total_rows += int(result.read())
            os.unlink(result_path)

        return total_rows

    def _run_worker(
        self,
        field_name,
        worker_id,
        workers,
        batch_size,
        dry_run,
    ):
        spec = get_field_spec(field_name)
        count_sql = build_count_sql(spec)
        update_sql = build_update_sql(spec)

        started_at = time.monotonic()
        sql_params = {
            'workers': workers,
            'worker_id': worker_id,
        }

        with connection.cursor() as cursor:
            cursor.execute(count_sql, sql_params)
            row_count = cursor.fetchone()[0]

        worker_number = self._format_worker_number(worker_id, workers)
        worker_label = self._format_worker_number(worker_id)

        self.stdout.write(
            f'Worker {worker_number} ({field_name}): '
            f'{row_count} rows assigned.'
        )

        if dry_run:
            elapsed = time.monotonic() - started_at
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: worker {worker_label} would update '
                    f'{row_count} rows for {field_name}. '
                    f'Run without --dry-run to apply.'
                )
            )
            self.stdout.write(
                f'Worker {worker_label} dry run finished in {elapsed:.1f}s.'
            )
            self._write_worker_result(row_count)
            return row_count

        last_id = ''
        total_updated = 0
        batch_number = 0

        while True:
            batch_number += 1
            batch_started_at = time.monotonic()
            params = {
                'last_id': last_id,
                'workers': workers,
                'worker_id': worker_id,
                'batch_size': batch_size,
            }

            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(update_sql, params)
                    returned_ids = [row[0] for row in cursor.fetchall()]

            if not returned_ids:
                break

            updated = len(returned_ids)
            total_updated += updated
            last_id = max(returned_ids)

            batch_seconds = time.monotonic() - batch_started_at
            self.stdout.write(
                f'Worker {worker_label} ({field_name}): '
                f'batch {batch_number} updated {updated} rows '
                f'(total {total_updated}, last_id={last_id}, '
                f'{batch_seconds:.1f}s)'
            )

        elapsed = time.monotonic() - started_at
        self.stdout.write(
            self.style.SUCCESS(
                f'Worker {worker_label} ({field_name}) finished: '
                f'{total_updated} rows updated in {elapsed:.1f}s.'
            )
        )
        self._write_worker_result(total_updated)
        return total_updated
