from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.management import call_command
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = "Create a superuser in the RBA database"

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email address for the superuser'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='Password for the superuser'
        )
        parser.add_argument(
            '--username',
            type=str,
            default='',
            help='Username (optional)'
        )
        parser.add_argument(
            '--origin-source',
            type=str,
            default='rba',
            choices=['os_hub', 'rba'],
            help='Origin source for the user (default: rba)'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        username = options['username']
        origin_source = options['origin_source']

        self.stdout.write(f"Creating superuser in RBA database...")
        self.stdout.write(f"Email: {email}")
        self.stdout.write(f"Username: {username or '(empty)'}")
        self.stdout.write(f"Origin Source: {origin_source}")

        # Check if RBA database is configured
        if 'rba' not in settings.DATABASES:
            self.stdout.write(
                self.style.ERROR("RBA database is not configured in settings")
            )
            return

        # Check if user already exists in RBA database
        try:
            existing_user = User.objects.using('rba').get(email=email)
            self.stdout.write(
                self.style.WARNING(f"User with email {email} already exists in RBA database")
            )
            return
        except User.DoesNotExist:
            pass

        # Create the superuser in RBA database
        try:
            with transaction.atomic(using='rba'):
                user = User.objects.using('rba').create(
                    email=email,
                    username=username,
                    is_superuser=True,
                    is_staff=True,
                    is_active=True,
                    should_receive_newsletter=False,
                    has_agreed_to_terms_of_service=False,
                    origin_source=origin_source
                )
                user.set_password(password)
                user.save(using='rba')

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created superuser in RBA database:\n"
                    f"  ID: {user.id}\n"
                    f"  Email: {user.email}\n"
                    f"  UUID: {user.uuid}\n"
                    f"  Origin Source: {user.origin_source}"
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to create superuser in RBA database: {e}")
            )
            raise 