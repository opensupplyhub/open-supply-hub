from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = ('Usage: Create an API token for the user during the database '
            'reset.')

    def handle(self, *args, **options):
        call_command('shell',
                     '-c',
                     ("from rest_framework.authtoken.models import Token; "
                      "from api.models import User; token = "
                      "Token.objects.create(user=User.objects.get(id=2),"
                      "key='1d18b962d6f976b0b7e8fcf9fcc39b56cf278051'); "
                      "print('Token for c2@example.com'); print(token)"))
