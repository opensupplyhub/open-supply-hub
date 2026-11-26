from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from api.models.organization.organization import Organization
from api.models.organization.organization_membership import (
    OrganizationMembership,
)
from api.services.organization_service import stamp_member_contributions


class Command(BaseCommand):
    help = (
        'Attribute the contributions of organization members to their '
        'organization. Fills only rows that no organization holds yet, '
        'so it is safe to run again: use it to reconcile rows a creation '
        'path missed, or after adding members outside the invitation '
        'flow.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--organization',
            help='UUID of one organization. Defaults to every active one.',
        )

    def handle(self, *args, **options):
        memberships = OrganizationMembership.objects.filter(
            status=OrganizationMembership.ACTIVE,
            organization__is_active=True,
        ).select_related('organization', 'user')

        organization_uuid = options.get('organization')
        if organization_uuid:
            try:
                organization = Organization.objects.get(
                    uuid=organization_uuid
                )
            except (Organization.DoesNotExist, ValidationError) as exc:
                raise CommandError(
                    'No organization has the UUID {}.'.format(
                        organization_uuid
                    )
                ) from exc
            memberships = memberships.filter(organization=organization)

        totals = {}
        member_count = 0
        for membership in memberships.iterator():
            member_count += 1
            for model_name, count in stamp_member_contributions(
                membership
            ).items():
                totals[model_name] = totals.get(model_name, 0) + count

        self.stdout.write(self.style.SUCCESS(
            'Checked {} member(s). Rows attributed: {}'.format(
                member_count,
                ', '.join(
                    '{} {}'.format(count, model_name)
                    for model_name, count in sorted(totals.items())
                ) or 'none',
            )
        ))
