import json
import sys

from django.core.management.base import BaseCommand

from api.models import FacilityList, ListCleaningRun
from api.services.list_cleaning import (
    ingest_result,
    refresh_run,
    review_deadline,
    start_run,
)


class Command(BaseCommand):
    help = ('Start, refresh or import a list-cleaning run (OSDEV-3726) for '
            'a facility list. --records imports an aggregated result file '
            'produced by run_list_cleaning.py --out in the '
            'automated-single-location-contribution repo.')

    def add_arguments(self, parser):
        parser.add_argument('-l', '--list-id', required=True, type=int)
        parser.add_argument('--runner', choices=['stub', 'stepfunctions'],
                            help='Override LIST_CLEANING_RUNNER.')
        parser.add_argument('--records',
                            help='Path to a records JSON file to import '
                                 'instead of executing the pipeline.')
        parser.add_argument('--refresh', action='store_true',
                            help='Poll the latest running run for a result.')

    def handle(self, *args, **options):
        try:
            facility_list = FacilityList.objects.get(pk=options['list_id'])
        except FacilityList.DoesNotExist:
            self.stderr.write(f'No facility list {options["list_id"]}')
            sys.exit(1)

        if options['refresh']:
            run = facility_list.cleaning_runs.first()
            if run is None:
                self.stderr.write('No run to refresh')
                sys.exit(1)
            run = refresh_run(run)
        elif options['records']:
            with open(options['records']) as f:
                result = json.load(f)
            if isinstance(result, list):
                result = {'records': result}
            run = ListCleaningRun.objects.create(
                facility_list=facility_list, runner=ListCleaningRun.IMPORT,
                review_until=review_deadline())
            ingest_result(run, result)
        else:
            run = start_run(
                facility_list, runner_name=options['runner'], force=True)

        self.stdout.write(
            f'Run {run.id}: {run.status} ({run.runner}), '
            f'{run.suggestions.count()} suggestions'
            + (f', error: {run.error}' if run.error else ''))
