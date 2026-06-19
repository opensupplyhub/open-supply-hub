import os
import subprocess
import sys
import tempfile
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

WORKER_ID_ENV = 'BACKFILL_INDEX_CONTRIBUTORS_WORKER_ID'
WORKERS_ENV = 'BACKFILL_INDEX_CONTRIBUTORS_WORKERS'
RESULT_FILE_ENV = 'BACKFILL_INDEX_CONTRIBUTORS_RESULT_FILE'

NON_EMPTY_CONTRIBUTORS_CLAUSE = (
    "AND cardinality(COALESCE(contributors, '{}')) > 0"
)

UPDATE_CONTRIBUTORS_BATCH_SQL = f"""
UPDATE api_facilityindex afi
SET
    contributors = COALESCE(
        (SELECT array_agg(contributor) FROM index_contributors(afi.id)),
        '{{}}'
    ),
    updated_at = now()
WHERE afi.id IN (
    SELECT id
    FROM api_facilityindex
    WHERE id > %(last_id)s
      AND mod(abs(hashtext(id::text)), %(workers)s) = %(worker_id)s
      {NON_EMPTY_CONTRIBUTORS_CLAUSE}
    ORDER BY id
    LIMIT %(batch_size)s
)
RETURNING afi.id
"""

COUNT_WORKER_ROWS_SQL = f"""
SELECT COUNT(*)
FROM api_facilityindex
WHERE mod(abs(hashtext(id::text)), %(workers)s) = %(worker_id)s
  {NON_EMPTY_CONTRIBUTORS_CLAUSE}
"""


class Command(BaseCommand):
    help = (
        'Backfill api_facilityindex.contributors using index_contributors() '
        'in batches. Skips rows with an empty contributors array. '
        'Use --parallel to run multiple worker processes.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10000,
            help='Number of rows to update per batch (default: 10000).',
        )
        parser.add_argument(
            '--parallel',
            type=int,
            default=1,
            metavar='N',
            help=(
                'Number of parallel worker processes partitioning the table '
                'by facility id hash (default: 1).'
            ),
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show row counts per worker without updating.',
        )

    def handle(self, *args, **options):
        parallel = options['parallel']
        if parallel < 1:
            raise CommandError('--parallel must be at least 1.')

        worker_id_env = os.environ.get(WORKER_ID_ENV)
        workers_env = os.environ.get(WORKERS_ENV)
        if worker_id_env is not None and workers_env is not None:
            workers = int(workers_env)
            worker_id = int(worker_id_env)
            if workers < 1:
                raise CommandError('Worker count must be at least 1.')
            if worker_id < 0 or worker_id >= workers:
                raise CommandError(
                    f'Worker id must be between 0 and {workers - 1}.'
                )
            self._run_worker(
                worker_id=worker_id,
                workers=workers,
                batch_size=options['batch_size'],
                dry_run=options['dry_run'],
            )
            return

        started_at = time.monotonic()
        if parallel > 1:
            total_rows = self._spawn_parallel_workers(
                parallel, options
            )
        else:
            total_rows = self._run_worker(
                worker_id=0,
                workers=1,
                batch_size=options['batch_size'],
                dry_run=options['dry_run'],
            )

        self._write_summary(
            total_rows,
            time.monotonic() - started_at,
            options['dry_run'],
        )

    def _write_summary(self, total_rows, elapsed, dry_run):
        if dry_run:
            message = (
                f'Backfill dry run: {total_rows} rows would be updated in '
                f'{elapsed:.1f}s.'
            )
        else:
            message = (
                f'Backfill completed: {total_rows} rows updated in '
                f'{elapsed:.1f}s.'
            )
        self.stdout.write(self.style.SUCCESS(message))

    def _write_worker_result(self, row_count):
        result_file = os.environ.get(RESULT_FILE_ENV)
        if not result_file:
            return
        with open(result_file, 'w', encoding='utf-8') as result:
            result.write(str(row_count))

    def _spawn_parallel_workers(self, parallel, options):
        manage_py = sys.argv[0]
        base_args = [
            manage_py,
            'backfill_index_contributors',
            '--batch-size',
            str(options['batch_size']),
        ]
        if options['dry_run']:
            base_args.append('--dry-run')

        self.stdout.write(
            f'Spawning {parallel} backfill worker processes...'
        )
        processes = []
        result_files = []
        for worker_id in range(parallel):
            fd, result_path = tempfile.mkstemp(
                suffix=f'-worker{worker_id}.txt',
            )
            os.close(fd)
            result_files.append(result_path)
            env = os.environ.copy()
            env[WORKERS_ENV] = str(parallel)
            env[WORKER_ID_ENV] = str(worker_id)
            env[RESULT_FILE_ENV] = result_path
            cmd = [sys.executable, *base_args]
            self.stdout.write(f'  worker {worker_id}: {" ".join(cmd)}')
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
                f'worker {worker_id} (exit {code})'
                for worker_id, code in failures
            )
            raise CommandError(f'Backfill failed for: {details}')

        total_rows = 0
        for result_path in result_files:
            with open(result_path, encoding='utf-8') as result:
                total_rows += int(result.read())
            os.unlink(result_path)

        return total_rows

    def _run_worker(
        self,
        worker_id,
        workers,
        batch_size,
        dry_run,
    ):
        started_at = time.monotonic()
        sql_params = {
            'workers': workers,
            'worker_id': worker_id,
        }

        with connection.cursor() as cursor:
            cursor.execute(COUNT_WORKER_ROWS_SQL, sql_params)
            row_count = cursor.fetchone()[0]

        self.stdout.write(
            f'Worker {worker_id}/{workers}: {row_count} rows assigned.'
        )

        if dry_run:
            elapsed = time.monotonic() - started_at
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: worker {worker_id} would update {row_count} '
                    'rows. Run without --dry-run to apply changes.'
                )
            )
            self.stdout.write(
                f'Worker {worker_id} dry run finished in {elapsed:.1f}s.'
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
                    cursor.execute(UPDATE_CONTRIBUTORS_BATCH_SQL, params)
                    returned_ids = [row[0] for row in cursor.fetchall()]

            if not returned_ids:
                break

            updated = len(returned_ids)
            total_updated += updated
            last_id = max(returned_ids)

            batch_seconds = time.monotonic() - batch_started_at
            self.stdout.write(
                f'Worker {worker_id}: batch {batch_number} updated '
                f'{updated} rows (total {total_updated}, last_id={last_id}, '
                f'{batch_seconds:.1f}s)'
            )

        elapsed = time.monotonic() - started_at
        self.stdout.write(
            self.style.SUCCESS(
                f'Worker {worker_id} finished: {total_updated} rows updated '
                f'in {elapsed:.1f}s.'
            )
        )
        self._write_worker_result(total_updated)
        return total_updated
