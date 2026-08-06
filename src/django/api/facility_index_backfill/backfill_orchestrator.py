"""Parallel orchestration for FacilityIndex backfills."""

import os
import subprocess
import sys
import tempfile
import time

from django.core.management.base import CommandError, OutputWrapper
from django.core.management.color import Style

from api.facility_index_backfill.specs import get_field_spec
from api.facility_index_backfill.utils import format_worker_number


class BackfillOrchestrator:
    """Coordinate backfill jobs across facility index field groups."""

    worker_command_name = 'backfill_facility_index_worker'

    def __init__(self, stdout: OutputWrapper, style: Style) -> None:
        self.stdout = stdout
        self.style = style

    def run(
        self,
        field_names: list[str],
        parallel: int,
        batch_size: int,
        dry_run: bool,
    ) -> int:
        """Backfill the requested field groups; return total rows updated."""
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

    def _run_field_group(
        self,
        field_name: str,
        parallel: int,
        batch_size: int,
        dry_run: bool,
    ) -> int:
        """Backfill one field group by spawning worker subprocesses."""
        get_field_spec(field_name)
        self.stdout.write(f'Backfilling field group: {field_name}')

        return self._spawn_parallel_workers(
            field_name=field_name,
            parallel=parallel,
            batch_size=batch_size,
            dry_run=dry_run,
        )

    def _write_summary(
        self,
        field_names: list[str],
        total_rows: int,
        elapsed: float,
        dry_run: bool,
    ) -> None:
        """Print the final backfill summary line."""
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

    def _spawn_parallel_workers(
        self,
        field_name: str,
        parallel: int,
        batch_size: int,
        dry_run: bool,
    ) -> int:
        """Spawn one subprocess per hash partition and aggregate row counts."""
        manage_py = sys.argv[0]

        self.stdout.write(
            f'Spawning {parallel} backfill worker processes for '
            f'{field_name}...'
        )
        processes: list[subprocess.Popen[bytes]] = []
        result_files: list[str] = []
        for worker_id in range(parallel):
            fd, result_path = tempfile.mkstemp(
                suffix=f'-{field_name}-worker{worker_id}.txt',
            )
            os.close(fd)
            result_files.append(result_path)
            cmd = [
                sys.executable,
                manage_py,
                self.worker_command_name,
                '--field',
                field_name,
                '--worker-id',
                str(worker_id),
                '--workers',
                str(parallel),
                '--batch-size',
                str(batch_size),
                '--result-file',
                result_path,
            ]
            if dry_run:
                cmd.append('--dry-run')
            self.stdout.write(
                f'  worker {format_worker_number(worker_id)}: '
                f'{" ".join(cmd)}'
            )
            processes.append(subprocess.Popen(cmd))

        failures: list[tuple[int, int]] = []
        for worker_id, process in enumerate(processes):
            return_code = process.wait()
            if return_code != 0:
                failures.append((worker_id, return_code))

        if failures:
            for result_path in result_files:
                if os.path.exists(result_path):
                    os.unlink(result_path)
            details = ', '.join(
                f'worker {format_worker_number(worker_id)} (exit {code})'
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
