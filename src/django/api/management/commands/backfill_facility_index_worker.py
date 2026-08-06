from django.core.management.base import BaseCommand, CommandError

from api.facility_index_backfill.backfill_worker import BackfillWorker
from api.facility_index_backfill.specs import get_field_spec


class Command(BaseCommand):
    help = (
        'Run one hash partition of a facility index backfill. '
        'Invoked by backfill_facility_index when --parallel > 1.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--field',
            required=True,
            help='Field group to backfill (e.g. contributors).',
        )
        parser.add_argument(
            '--worker-id',
            type=int,
            required=True,
            help='Zero-based worker index for this hash partition.',
        )
        parser.add_argument(
            '--workers',
            type=int,
            required=True,
            help='Total number of parallel workers partitioning the table.',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10000,
            help='Number of rows to update per batch (default: 10000).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show row counts without updating.',
        )
        parser.add_argument(
            '--result-file',
            default=None,
            help='Path to write the row count for the parent process.',
        )

    def handle(self, *args, **options):
        field_name = options['field']
        worker_id = options['worker_id']
        workers = options['workers']
        batch_size = options['batch_size']

        if batch_size < 1:
            raise CommandError('--batch-size must be at least 1.')
        if workers < 1:
            raise CommandError('--workers must be at least 1.')
        if worker_id < 0 or worker_id >= workers:
            raise CommandError(
                f'Worker id must be between 0 and {workers - 1}, '
                f'got {worker_id}.'
            )

        get_field_spec(field_name)

        worker = BackfillWorker(self.stdout, self.style)
        worker.run(
            field_name=field_name,
            worker_id=worker_id,
            workers=workers,
            batch_size=batch_size,
            dry_run=options['dry_run'],
            result_file=options['result_file'],
        )
