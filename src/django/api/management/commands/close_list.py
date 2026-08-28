from django.core.management.base import BaseCommand

from api.close_list import close_list


class Command(BaseCommand):
    help = ('Closes facilities in a list — all of them, or only those whose '
            'uploaded rows carry given values in a raw status column.')

    def add_arguments(self, parser):
        # Create a group of arguments explicitly labeled as required,
        # because by default named arguments are considered optional.
        group = parser.add_argument_group('required arguments')
        group.add_argument('-l', '--list-id',
                           required=True,
                           help='The id of the facility list to close.')
        group.add_argument('-u', '--user-id',
                           required=True,
                           help='The id of the user to record as responsible' +
                           ' for the closures.')
        parser.add_argument('--status-field',
                            help='Name of the raw uploaded column holding the '
                            'status (e.g. "status"). When given, only '
                            'facilities whose rows match --status-values are '
                            'closed; facilities that any row of this list '
                            'marks with a different value are left open.')
        parser.add_argument('--status-values',
                            nargs='+',
                            default=['INACTIVE', 'SUSPENDED'],
                            help='Raw column values (case-insensitive) that '
                            'mark a row as closed. Default: INACTIVE '
                            'SUSPENDED. Only used with --status-field.')
        parser.add_argument('--apply',
                            action='store_true',
                            help='Actually close facilities. Without this '
                            'flag the command is a DRY RUN: it only reports '
                            'what would be closed.')

    def handle(self, *args, **options):
        summary = close_list(
            options['list_id'],
            options['user_id'],
            status_field=options.get('status_field'),
            status_values=options.get('status_values'),
            dry_run=not options.get('apply', False),
        )
        mode = 'DRY RUN — would close' if summary['dry_run'] else 'Closed'
        count = (summary['to_close'] if summary['dry_run']
                 else summary['closed'])
        self.stdout.write(
            '{0} {1} facilities in list {2}.'.format(
                mode, count, summary['list_id']))
        if summary['dry_run'] and summary['facility_ids']:
            self.stdout.write(
                'Facility ids: {0}'.format(', '.join(
                    str(i) for i in summary['facility_ids'])))
