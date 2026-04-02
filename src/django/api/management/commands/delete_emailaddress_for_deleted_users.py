from django.core.management.base import BaseCommand
from allauth.account.models import EmailAddress


class Command(BaseCommand):
    help = (
        'Delete EmailAddress records for users with ###deleted### prefix '
        'in their email addresses.'
    )

    def handle(self, *args, **options):
        count, _ = EmailAddress.objects.filter(
            user__email__startswith='###deleted###'
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Deleted {count} EmailAddress record(s) for deleted users.'
            )
        )
