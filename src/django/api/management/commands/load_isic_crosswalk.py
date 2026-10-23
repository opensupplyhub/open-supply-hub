from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from api.isic_taxonomy.crosswalk import (
    CROSSWALK_CSV_PATH,
    CrosswalkError,
    load_crosswalk_rows,
    replace_crosswalk_entries,
)
from api.models import IsicCrosswalkEntry


class Command(BaseCommand):
    help = (
        'Replace the OS Hub to ISIC Rev 4 crosswalk with the rows of a CSV '
        'file (default: the crosswalk shipped with the code), then refresh '
        'the mapped ISIC values of existing locations.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=CROSSWALK_CSV_PATH,
            help='Path to the crosswalk CSV.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Validate the file without changing the table.',
        )

    def handle(self, *args, **options):
        try:
            rows = load_crosswalk_rows(options['file'])
        except (CrosswalkError, OSError) as error:
            raise CommandError(str(error)) from error

        mapped_rows = sum(1 for row in rows if row['isic_section'])
        if options['dry_run']:
            self.stdout.write(
                f'{len(rows)} rows are valid ({mapped_rows} map to ISIC). '
                'Nothing was changed.'
            )
            return

        count = replace_crosswalk_entries(IsicCrosswalkEntry, rows)
        self.stdout.write(self.style.SUCCESS(
            f'Loaded {count} crosswalk rows ({mapped_rows} map to ISIC). '
            'Refreshing mapped ISIC values.'
        ))
        # The triggers only fire when a location's types change, so apply
        # the new crosswalk to every existing location now.
        call_command('backfill_facility_index', fields='isic_4_mapped')
