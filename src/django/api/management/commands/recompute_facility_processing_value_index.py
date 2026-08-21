import logging
import time

from django.core.management.base import BaseCommand
from django.db import connection

logger = logging.getLogger(__name__)

TABLE = 'api_facility_processing_value'


class Command(BaseCommand):
    help = (
        'Rebuild the {} table, which holds the distinct facility type and '
        'processing type values of the facility index behind the processing '
        'type typeahead. The counts are maintained by triggers, so this is '
        'only needed after a bulk rewrite of api_facilityindex such as '
        'index_facilities_new or backfill_facility_index, or to correct '
        'drift.'.format(TABLE)
    )

    def handle(self, *args, **options):
        started_at = time.monotonic()

        with connection.cursor() as cursor:
            cursor.execute('CALL recompute_facility_processing_values();')
            cursor.execute(
                'SELECT COUNT(*) FROM api_facility_processing_value'
            )
            value_count = cursor.fetchone()[0]

        logger.info(
            'Recomputed %s in %.1f seconds. It holds %d values.',
            TABLE,
            time.monotonic() - started_at,
            value_count,
        )
