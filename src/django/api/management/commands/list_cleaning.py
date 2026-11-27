import json
import sys

from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import FacilityList, ListCleaningRun
from api.services.list_cleaning import (
    ReviewOpen,
    ensure_restartable,
    ingest_result,
    refresh_run,
    restart_run,
    review_deadline,
    start_run,
)


class Command(BaseCommand):
    help = ('Start, refresh or import a list-cleaning run (OSDEV-3726) for '
            'a facility list. --records imports an aggregated result file '
            'produced by run_list_cleaning.py --out in the '
            'automated-single-location-contribution repo. A new run is '
            'refused while the contributor is still reviewing the current '
            'one, unless --force is given.')

    def add_arguments(self, parser):
        parser.add_argument('-l', '--list-id', required=True, type=int)
        parser.add_argument('--runner', choices=['stub', 'stepfunctions'],
                            help='Override LIST_CLEANING_RUNNER.')
        parser.add_argument('--records',
                            help='Path to a records JSON file to import '
                                 'instead of executing the pipeline.')
        parser.add_argument('--refresh', action='store_true',
                            help='Poll the latest running run for a result.')
        parser.add_argument('--force', action='store_true',
                            help='Start or import even while the '
                                 'contributor\'s review window is open; '
                                 'their decisions so far are discarded.')

    def handle(self, *args, **options):
        try:
            facility_list = FacilityList.objects.get(pk=options['list_id'])
        except FacilityList.DoesNotExist:
            self.stderr.write(f'No facility list {options["list_id"]}')
            sys.exit(1)

        try:
            run = self._run(facility_list, options)
        except ReviewOpen as e:
            self.stderr.write(f'{e} Pass --force to discard their review.')
            sys.exit(1)

        self.stdout.write(
            f'Run {run.id}: {run.status} ({run.runner}), '
            f'{run.suggestions.count()} suggestions'
            + (f', error: {run.error}' if run.error else ''))

    def _run(self, facility_list, options):
        if options['refresh']:
            run = facility_list.cleaning_runs.first()
            if run is None:
                self.stderr.write('No run to refresh')
                sys.exit(1)
            return refresh_run(run)
        if options['records']:
            with open(options['records']) as f:
                result = json.load(f)
            if isinstance(result, list):
                result = {'records': result}
            # The same guard, and the same list lock, as a restart: an
            # import replaces the current run for the contributor too.
            with transaction.atomic():
                if not options['force']:
                    facility_list = ensure_restartable(facility_list)
                run = ListCleaningRun.objects.create(
                    facility_list=facility_list,
                    runner=ListCleaningRun.IMPORT,
                    review_until=review_deadline())
                ingest_result(run, result)
            return run
        if options['force']:
            return start_run(
                facility_list, runner_name=options['runner'], force=True)
        return restart_run(
            facility_list, runner_name=options['runner'], force=True)
