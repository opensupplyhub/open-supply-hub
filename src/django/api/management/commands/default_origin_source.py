from django.core.management.base import BaseCommand
from django.db import models

from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityActivityReport,
    FacilityAlias,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    FacilityLocation,
    User,
)


class Command(BaseCommand):
    help = "Set origin_source on all tables where it is NULL or empty."

    def handle(self, *args, **options):
        models_to_update = [
            Contributor,
            ExtendedField,
            Facility,
            FacilityActivityReport,
            FacilityAlias,
            FacilityClaim,
            FacilityList,
            FacilityListItem,
            FacilityMatch,
            Source,
            FacilityLocation,
            User,
        ]

        for model in models_to_update:
            updated = model.objects.filter(
                models.Q(origin_source__isnull=True)
                | models.Q(origin_source='')
            ).update(origin_source='os_hub')

            self.stdout.write(
                self.style.SUCCESS(
                    f"{model.__name__}: {updated} rows updated."
                )
            )
