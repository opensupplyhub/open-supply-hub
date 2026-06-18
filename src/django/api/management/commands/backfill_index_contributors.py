import subprocess
import sys
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction


UPDATE_CONTRIBUTORS_BATCH_SQL = """
UPDATE api_facilityindex afi
SET
    contributors = COALESCE(
        (SELECT array_agg(contributor) FROM index_contributors(afi.id)),
        '{}'
    ),
    updated_at = now()
WHERE afi.id IN (
    SELECT id
    FROM api_facilityindex
    WHERE id > %(last_id)s
      AND mod(abs(hashtext(id::text)), %(workers)s) = %(worker_id)s
      {only_with_contributors_clause}
    ORDER BY id
    LIMIT %(batch_size)s
)
"""

COUNT_WORKER_ROWS_SQL = """
SELECT COUNT(*)
FROM api_facilityindex
WHERE mod(abs(hashtext(id::text)), %(workers)s) = %(worker_id)s
  {only_with_contributors_clause}
"""

MAX_LAST_ID_SQL = """
SELECT id
FROM api_facilityindex
WHERE id > %(last_id)s
  AND mod(abs(hashtext(id::text)), %(workers)s) = %(worker_id)s
  {only_with_contributors_clause}
ORDER BY id
LIMIT 1 OFFSET %(offset)s
"""


class Command(BaseCommand):
    help = (
        'Backfill api_facilityindex.contributors using index_contributors() '
        'in batches. Use --workers and --worker-id for parallel runs, or '
        '--parallel to spawn multiple worker processes.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10000,
            help='Number of rows to update per batch (default: 10000).',
        )
        parser.add_argument(
            '--workers',
            type=int,
            default=1,
            help=(
                'Total number of parallel workers partitioning the table '
                'by facility id hash (default: 1).'
            ),
        )
        parser.add_argument(
            '--worker-id',
            type=int,
            default=0,
            help=(
                'Zero-based worker id in [0, workers). Each worker processes '
                'a disjoint subset of rows.'
            ),
        )
        parser.add_argument(
            '--parallel',
            type=int,
            metavar='N',
            help=(
                'Spawn N worker subprocesses (equivalent to running with '
                '--workers N and --worker-id 0..N-1). Cannot be combined '
                'with --worker-id.'
            ),
        )
        parser.add_argument(
            '--only-with-contributors',
            action='store_true',
            help='Only update rows where contributors_count > 0.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show row counts per worker without updating.',
        )

    def handle(self, *args, **options):
        parallel = options.get('parallel')
        if parallel is not None:
            if parallel < 1:
                raise CommandError('--parallel must be at least 1.')
            if options['worker_id'] != 0 and options['workers'] != 1:
                raise CommandError(
                    'Do not pass --worker-id or --workers with --parallel.'
                )
            self._spawn_parallel_workers(parallel, options)
            return

        workers = options['workers']
        worker_id = options['worker_id']
        if workers < 1:
            raise CommandError('--workers must be at least 1.')
        if worker_id < 0 or worker_id >= workers:
            raise CommandError(
                f'--worker-id must be between 0 and {workers - 1}.'
            )

        self._run_worker(
            worker_id=worker_id,
            workers=workers,
            batch_size=options['batch_size'],
            only_with_contributors=options['only_with_contributors'],
            dry_run=options['dry_run'],
        )

    def _spawn_parallel_workers(self, parallel, options):
        manage_py = sys.argv[0]
        base_args = [
            manage_py,
            'backfill_index_contributors',
            '--workers',
            str(parallel),
            '--batch-size',
            str(options['batch_size']),
        ]
        if options['only_with_contributors']:
            base_args.append('--only-with-contributors')
        if options['dry_run']:
            base_args.append('--dry-run')

        self.stdout.write(
            f'Spawning {parallel} backfill worker processes...'
        )
        processes = []
        for worker_id in range(parallel):
            cmd = [
                sys.executable,
                *base_args,
                '--worker-id',
                str(worker_id),
            ]
            self.stdout.write(f'  worker {worker_id}: {" ".join(cmd)}')
            processes.append(subprocess.Popen(cmd))

        failures = []
        for worker_id, process in enumerate(processes):
            return_code = process.wait()
            if return_code != 0:
                failures.append((worker_id, return_code))

        if failures:
            details = ', '.join(
                f'worker {worker_id} (exit {code})'
                for worker_id, code in failures
            )
            raise CommandError(f'Backfill failed for: {details}')

        self.stdout.write(
            self.style.SUCCESS(
                f'All {parallel} workers completed successfully.'
            )
        )

    def _only_with_contributors_clause(self, only_with_contributors):
        if only_with_contributors:
            return 'AND contributors_count > 0'
        return ''

    def _run_worker(
        self,
        worker_id,
        workers,
        batch_size,
        only_with_contributors,
        dry_run,
    ):
        only_clause = self._only_with_contributors_clause(
            only_with_contributors
        )
        sql_params = {
            'workers': workers,
            'worker_id': worker_id,
        }

        with connection.cursor() as cursor:
            cursor.execute(
                COUNT_WORKER_ROWS_SQL.format(
                    only_with_contributors_clause=only_clause
                ),
                sql_params,
            )
            row_count = cursor.fetchone()[0]

        self.stdout.write(
            f'Worker {worker_id}/{workers}: {row_count} rows assigned.'
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: worker {worker_id} would update {row_count} '
                    'rows. Run without --dry-run to apply changes.'
                )
            )
            return

        last_id = ''
        total_updated = 0
        batch_number = 0
        started_at = time.monotonic()

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
                    cursor.execute(
                        UPDATE_CONTRIBUTORS_BATCH_SQL.format(
                            only_with_contributors_clause=only_clause
                        ),
                        params,
                    )
                    updated = cursor.rowcount

            if updated == 0:
                break

            total_updated += updated
            offset = max(updated - 1, 0)
            with connection.cursor() as cursor:
                cursor.execute(
                    MAX_LAST_ID_SQL.format(
                        only_with_contributors_clause=only_clause
                    ),
                    {
                        'last_id': last_id,
                        'workers': workers,
                        'worker_id': worker_id,
                        'offset': offset,
                    },
                )
                row = cursor.fetchone()
                last_id = row[0] if row else last_id

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
