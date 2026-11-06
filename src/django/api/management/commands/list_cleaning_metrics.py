import json

from django.core.management.base import BaseCommand

from api.services.list_cleaning import metrics_summary


class Command(BaseCommand):
    help = ('How contributors use the list-cleaning review screen '
            '(OSDEV-3726 v3): how many submit through it, with or without '
            'changes, versus click away and let the window lapse.')

    def add_arguments(self, parser):
        parser.add_argument('--json', action='store_true',
                            help='Print the summary as JSON.')

    def handle(self, *args, **options):
        summary = metrics_summary()
        if options['json']:
            self.stdout.write(json.dumps(summary, indent=2))
            return
        rows = [
            ('Completed runs', summary['runs_complete']),
            ('  still open', summary['runs_open']),
            ('  review screen opened', summary['review_opened']),
            ('Submitted with changes', summary['submitted_with_changes']),
            ('Submitted as uploaded', summary['submitted_as_uploaded']),
            ('Lapsed after opening the screen',
             summary['lapsed_after_opening']),
            ('Lapsed without opening it', summary['lapsed_never_opened']),
            ('Left the screen at least once',
             summary['left_at_least_once']),
            ('Came back at least once', summary['resumed_at_least_once']),
            ('Submit rate (of closed runs)', summary['submit_rate']),
            ('Median minutes to submit',
             summary['median_minutes_to_submit']),
            ('Median changes applied', summary['median_changes_applied']),
        ]
        width = max(len(label) for label, _ in rows)
        for label, value in rows:
            shown = '-' if value is None else value
            self.stdout.write(f'{label.ljust(width)}  {shown}')
