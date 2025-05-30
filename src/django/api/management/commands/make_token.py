from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = ('Create an API token for a given user and '
            'set admin/superuser rights.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            required=True,
            help='ID of the user'
        )
        parser.add_argument(
            '--is-admin',
            type=bool,
            required=True,
            help='Grant superuser and staff rights'
        )
        parser.add_argument(
            '--token-key',
            type=str,
            required=True,
            help='Token key to set manually'
        )

    def handle(self, *args, **options):
        user_id = options['user_id']
        is_admin = options['is_admin']
        token_key = options['token_key']

        call_command(
            'shell',
            '-c',
            (
                "from rest_framework.authtoken.models import Token;"
                "from api.models import User;"
                f"user = User.objects.get(id={user_id});"
                f"user.is_staff = {str(is_admin)};"
                f"user.is_superuser = {str(is_admin)};"
                "user.save();"
                "token = Token.objects.create(user=user,"
                f"key='{token_key}');"
                "print(f'Token for {user.email}: {token.key}')"
            )
        )
