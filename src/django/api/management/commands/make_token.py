from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = ('Usage: Create an API token for the user during the database '
            'reset, and set admin rights.')

    def handle(self, *args, **options):
        call_command(
            'shell',
            '-c',
            (
                "from rest_framework.authtoken.models import Token;"
                "from api.models import User;"
                "user = User.objects.get(id=2);"
                "user.is_staff = True;"
                "user.is_superuser = True;"
                "user.save();"
                "token = Token.objects.create(user=user,"
                "key='1d18b962d6f976b0b7e8fcf9fcc39b56cf278051');"
                "print(f'Token for {user.email}: {token.key}')"
            )
        )
