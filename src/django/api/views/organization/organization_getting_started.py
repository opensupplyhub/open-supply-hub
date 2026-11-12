from rest_framework.response import Response

from api.permissions import IsOrganizationAdmin
from api.services.organization_service import (
    find_domain_accounts,
    get_onboarding_progress,
)
from api.views.organization.base import OrganizationMemberAPIView


class OrganizationOnboarding(OrganizationMemberAPIView):
    """
    GET /api/organizations/{uuid}/onboarding/: which first steps the
    organization has taken (contributed data, has more than one member,
    claimed a production location), for the checklist on the My
    Organization page. Any member.
    """

    def get(self, request, organization_uuid):
        return Response(get_onboarding_progress(self.organization))


class OrganizationDomainAccounts(OrganizationMemberAPIView):
    """
    GET /api/organizations/{uuid}/domain-accounts/: existing OS Hub
    accounts on the Admin's own email domain that could be invited, so
    the Admin learns which colleagues already use OS Hub. Empty, with a
    null domain, when the Admin's address is on a public mail provider.
    Admin only.
    """
    permission_classes = (IsOrganizationAdmin,)

    def get(self, request, organization_uuid):
        domain, accounts = find_domain_accounts(
            self.organization, request.user
        )
        return Response({
            'domain': domain,
            'accounts': [
                {
                    'email': account.email,
                    'contributor_name': (
                        account.contributor.name
                        if hasattr(account, 'contributor') else None
                    ),
                }
                for account in accounts
            ],
        })
