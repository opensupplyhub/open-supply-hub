from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models.contributor.contributor import Contributor
from api.models.moderation_event import ModerationEvent
from api.services.opensearch.search import OpenSearchServiceConnection
from api.views.v1.index_names import OpenSearchIndexNames


class Command(BaseCommand):
    help = 'Creates sample data for testing the moderation queue'

    def handle(self, *args, **options):
        opensearch = OpenSearchServiceConnection()
        opensearch.client.indices.create(
            index=OpenSearchIndexNames.MODERATION_EVENTS_INDEX, ignore=400)
        self.stdout.write(self.style.SUCCESS('Created moderation events index'))

        User = get_user_model()
        admin, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'is_superuser': True,
                'is_staff': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Admin user created'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin user already exists'))

        contributor, c_created = Contributor.objects.get_or_create(
            admin=admin,
            defaults={
                'name': 'Admin User',
                'contrib_type': 'Brand / Retailer',
                'is_verified': True
            }
        )
        self.stdout.write(self.style.SUCCESS(
            f'Contributor {"created" if c_created else "already exists"} for admin user'))

        for i in range(5):
            event = ModerationEvent.objects.create(
                contributor=contributor, status=ModerationEvent.Status.PENDING)
            self.stdout.write(self.style.SUCCESS(
                f'Created moderation event {event.uuid} for contributor {contributor.admin.email}'))
