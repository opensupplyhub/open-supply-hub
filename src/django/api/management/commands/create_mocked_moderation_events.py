# TODO: DELETE THIS FILE. IT IS FOR TESTING
# TODO: DELETE THIS FILE. IT IS FOR TESTING
# TODO: DELETE THIS FILE. IT IS FOR TESTING

import uuid
from datetime import datetime
from random import choice, randint
from django.core.management.base import BaseCommand
from api.models.contributor.contributor import Contributor
from api.models.moderation_event import ModerationEvent


class Command(BaseCommand):
    help = 'Generate mocked ModerationEvent data'

    def handle(self, *args, **kwargs):
        # Example lists for random choices
        request_types = [
            ModerationEvent.RequestType.CREATE,
            ModerationEvent.RequestType.UPDATE,
            ModerationEvent.RequestType.CLAIM,
        ]

        statuses = [
            ModerationEvent.Status.PENDING,
            ModerationEvent.Status.RESOLVED,
        ]

        sources = [
            ModerationEvent.Source.API,
            ModerationEvent.Source.SLC,
            '',
        ]

        # Fetch existing contributors
        contributors = list(Contributor.objects.all())

        # Generate mocked data
        events = []
        num_events = 10  # Adjust this number as needed
        for _ in range(num_events):
            event = ModerationEvent(
                uuid=uuid.uuid4(),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                status_change_date=(
                    datetime.now() if choice([True, False]) else None
                ),
                contributor=choice(contributors) if contributors else None,
                request_type=choice(request_types),
                raw_data={
                    "name": "raw_name",
                    "country_code": "UK"
                },  # Fill with realistic mock data
                cleaned_data={
                    "name": "cleaned_name",
                    "country_code": "UK"
                },
                geocode_result={
                    "latitude": round(randint(-90, 90), 6),
                    "longitude": round(randint(-180, 180), 6)
                },
                status=choice(statuses),
                source=choice(sources),
            )
            events.append(event)

        # Bulk create moderation events
        ModerationEvent.objects.bulk_create(events)
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(events)} mocked moderation events."
            )
        )
