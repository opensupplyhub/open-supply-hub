from django.core.management.base import BaseCommand, CommandError

from api.facility_index_backfill.runner import FacilityIndexBackfillRunner
from api.facility_index_backfill.specs import list_field_names


class Command(BaseCommand):
    help = (
        'Backfill selected api_facilityindex field groups in batches using '
        'existing index_*() SQL functions. Use --parallel to run multiple '
        'worker processes.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--fields',
            required=True,
            help=(
                'Comma-separated field groups to backfill. '
                f'Available: {", ".join(list_field_names())}.'
            ),
        )
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
        field_names = self._parse_field_names(options['fields'])
        runner = FacilityIndexBackfillRunner(self.stdout, self.style)
        runner.run(
            field_names=field_names,
            parallel=options['parallel'],
            batch_size=options['batch_size'],
            dry_run=options['dry_run'],
        )

    def _parse_field_names(self, fields_arg):
        field_names = [
            field_name.strip()
            for field_name in fields_arg.split(',')
            if field_name.strip()
        ]
        if not field_names:
            raise CommandError('--fields must list at least one field group.')
        return field_names
