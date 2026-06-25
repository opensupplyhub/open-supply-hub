"""Single-partition worker for FacilityIndex backfills."""

import time
from typing import Optional

from django.core.management.base import OutputWrapper
from django.core.management.color import Style
from django.db import connection, transaction

from api.facility_index_backfill.specs import (
    build_count_sql,
    build_update_sql,
    get_field_spec,
)
from api.facility_index_backfill.utils import format_worker_number


class BackfillWorker:
    """Process one hash partition for a single field group."""

    def __init__(self, stdout: OutputWrapper, style: Style) -> None:
        self.stdout = stdout
        self.style = style

    def run(
        self,
        field_name: str,
        worker_id: int,
        workers: int,
        batch_size: int,
        dry_run: bool,
        result_file: Optional[str] = None,
    ) -> int:
        """Count and optionally update rows assigned to this worker."""
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

        worker_number = format_worker_number(worker_id, workers)
        worker_label = format_worker_number(worker_id)

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
            self._write_worker_result(row_count, result_file)
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
        self._write_worker_result(total_updated, result_file)
        return total_updated

    @staticmethod
    def _write_worker_result(
        row_count: int,
        result_file: Optional[str],
    ) -> None:
        """Persist a worker row count for the parent process to aggregate."""
        if not result_file:
            return
        with open(result_file, 'w', encoding='utf-8') as result:
            result.write(str(row_count))
