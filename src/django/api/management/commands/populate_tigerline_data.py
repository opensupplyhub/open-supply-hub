from django.core.management.base import BaseCommand, CommandError

from api.models.us_county_tigerline import USCountyTigerline
from api.migrations._tigerline_helper import (
    populate_tigerline_data,
)


class Command(BaseCommand):
    help = (
        'Populate US County Tigerline data from CSV file stored in S3. '
        'This command can be used to populate data after migration if '
        'the CSV file was not available during migration.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--s3-key',
            type=str,
            required=True,
            help='S3 key/path to the CSV file (e.g., data/us_county_tigerline_2021.csv)',
        )
        parser.add_argument(
            '--source-srid',
            type=int,
            default=4326,
            help='SRID of the geometry data in CSV (default: 4326 for WGS84)',
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        s3_key = options['s3_key']
        source_srid = options['source_srid']
        clear_existing = options['clear_existing']

        self.stdout.write(
            f'Starting to populate Tigerline data from {s3_key}...'
        )

        try:
            self.stdout.write(f'Processing CSV file: {s3_key}...')
            populate_tigerline_data(
                USCountyTigerline,
                s3_key,
                source_srid=source_srid,
                clear_existing=clear_existing
            )

            if clear_existing:
                self.stdout.write(
                    self.style.SUCCESS('Cleared existing records')
                )
        except Exception as e:
            raise CommandError(
                f'Failed to populate Tigerline data: {e}'
            ) from e

        total_count = USCountyTigerline.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully populated Tigerline data!\n'
                f'  Total records in database: {total_count}'
            )
        )
