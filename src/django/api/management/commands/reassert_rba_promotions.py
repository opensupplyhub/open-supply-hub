from django.core.management.base import BaseCommand, CommandError

from api.reassert_rba_promotions import (
    is_rba_instance,
    reassert_rba_promotions,
)


class Command(BaseCommand):
    help = (
        'Restore promotions that the one-way sync from OS Hub has reverted. '
        'The sync overwrites every synced field of a shared facility, '
        'including created_from, so a promotion made on this instance is '
        'undone whenever the public record changes. Intended to run after '
        'each sync. Safe to run repeatedly: facilities already created from '
        'their newest RBA match are not selected.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report what would be re-asserted without making changes'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Process at most this many facilities in one run'
        )
        parser.add_argument(
            '--allow-non-rba-instance',
            action='store_true',
            help=('Run even when this is not the RBA instance. For local '
                  'testing only.')
        )

    def handle(self, *args, **options):
        if not is_rba_instance() and not options['allow_non_rba_instance']:
            raise CommandError(
                'This command only applies to the RBA instance, where the '
                'sync reverts promotions. Pass --allow-non-rba-instance to '
                'override for local testing.'
            )

        summary = reassert_rba_promotions(
            dry_run=options['dry_run'],
            limit=options['limit'],
        )

        if summary['dry_run']:
            self.stdout.write(
                f'[DRY RUN] {summary["found"]} promotion(s) would be '
                're-asserted. No changes were made.'
            )
            return

        self.stdout.write(
            f'Found {summary["found"]} reverted promotion(s); '
            f're-asserted {summary["reasserted"]}, '
            f'errors {summary["errors"]}.'
        )

        if summary['errors']:
            raise CommandError(
                f'{summary["errors"]} promotion(s) could not be '
                're-asserted. See the log for details.'
            )
