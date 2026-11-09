from api.models import ClaimCampaign, ClaimCampaignSupplier, Contributor, User
from api.services.claim_campaign_service import campaign_permissions
from api.tests.test_claim_campaign import (
    ClaimCampaignBaseTest,
    grant_campaign_access,
)
from waffle.testutils import override_switch

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Group
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

URL = "/api/claim-campaigns/"


class NoAccessBaseTest(ClaimCampaignBaseTest):
    """A brand with a campaign but no premium access."""

    def setUp(self):
        super().setUp()
        self.user.groups.clear()
        self.user.set_password("example123")
        self.user.save()
        self.client.login(email=self.user.email, password="example123")


@override_switch("claim_campaigns", active=True)
class CampaignAccessTest(NoAccessBaseTest):
    def test_brand_without_access_gets_404_everywhere(self):
        self.assertEqual(404, self.client.get(URL).status_code)
        self.assertEqual(
            404, self.client.get(f"{URL}candidates/").status_code
        )
        self.assertEqual(
            404,
            self.client.post(f"{URL}{self.campaign.id}/close/").status_code,
        )
        self.campaign.refresh_from_db()
        self.assertEqual(ClaimCampaign.Status.ACTIVE, self.campaign.status)

    def test_access_shows_campaigns_but_not_creation(self):
        grant_campaign_access(self.user)
        self.assertEqual(200, self.client.get(URL).status_code)
        self.assertEqual(
            404, self.client.get(f"{URL}candidates/").status_code
        )

    def test_self_serve_needs_access_too(self):
        self.user.groups.add(
            Group.objects.get(name="claim_campaign_self_serve")
        )
        self.assertEqual(
            {"access": False, "self_serve": False},
            campaign_permissions(self.user),
        )
        self.assertEqual(
            404, self.client.get(f"{URL}candidates/").status_code
        )

    def test_access_and_self_serve(self):
        grant_campaign_access(self.user, self_serve=True)
        self.assertEqual(
            {"access": True, "self_serve": True},
            campaign_permissions(self.user),
        )
        self.assertEqual(
            200, self.client.get(f"{URL}candidates/").status_code
        )

    def test_superusers_have_access(self):
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="example123"
        )
        self.assertEqual(
            {"access": True, "self_serve": True},
            campaign_permissions(superuser),
        )

    def test_login_response_carries_permissions(self):
        self.client.logout()
        response = self.client.post(
            "/user-login/",
            {"email": self.user.email, "password": "example123"},
        )
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual(
            {"access": False, "self_serve": False},
            response.json()["claim_campaigns"],
        )

        grant_campaign_access(self.user)
        response = self.client.post(
            "/user-login/",
            {"email": self.user.email, "password": "example123"},
        )
        self.assertEqual(
            {"access": True, "self_serve": False},
            response.json()["claim_campaigns"],
        )

    def test_invite_from_campaign_needs_access(self):
        ClaimCampaignSupplier.objects.create(
            campaign=self.campaign, facility=self.facility
        )
        from api.services.claim_campaign_service import (
            get_campaign_for_invite,
        )
        from rest_framework.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            get_campaign_for_invite(
                self.user, self.facility, self.campaign.code
            )
        grant_campaign_access(self.user)
        self.assertEqual(
            self.campaign,
            get_campaign_for_invite(
                self.user, self.facility, self.campaign.code
            ),
        )


@override_switch("claim_campaigns", active=False)
class CampaignAccessSwitchOffTest(NoAccessBaseTest):
    def test_switch_off_turns_everything_off(self):
        grant_campaign_access(self.user, self_serve=True)
        self.assertEqual(
            {"access": False, "self_serve": False},
            campaign_permissions(self.user),
        )


class ClaimCampaignAdminActionsTest(NoAccessBaseTest):
    def setUp(self):
        super().setUp()
        from api.admin import ClaimCampaignAdmin

        self.admin = ClaimCampaignAdmin(ClaimCampaign, AdminSite())
        self.request = RequestFactory().post("/")
        self.request.user = User.objects.create_superuser(
            email="staff@example.com", password="example123"
        )
        setattr(self.request, "session", "session")
        setattr(self.request, "_messages", FallbackStorage(self.request))

    def queryset(self):
        return ClaimCampaign.objects.filter(pk=self.campaign.pk)

    def test_admin_closes_and_reopens_any_brands_campaign(self):
        self.admin.close_campaigns(self.request, self.queryset())
        self.campaign.refresh_from_db()
        self.assertEqual(ClaimCampaign.Status.CLOSED, self.campaign.status)

        self.admin.reopen_campaigns(self.request, self.queryset())
        self.campaign.refresh_from_db()
        self.assertEqual(ClaimCampaign.Status.ACTIVE, self.campaign.status)

    def test_admin_gives_the_brand_access(self):
        self.assertFalse(self.admin.has_access(self.campaign))
        self.admin.give_brands_access(self.request, self.queryset())
        self.assertTrue(self.admin.has_access(self.campaign))
        self.assertTrue(
            self.user.groups.filter(name="claim_campaign_access").exists()
        )

    def test_saving_a_campaign_for_a_brand_without_access_warns(self):
        other_user = User.objects.create(email="b2@example.com")
        other = Contributor.objects.create(
            admin=other_user,
            name="Brand Two",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        campaign = ClaimCampaign(contributor=other, name="New", code="B2-26")
        self.admin.save_model(self.request, campaign, None, False)
        messages = [str(m) for m in self.request._messages]
        self.assertTrue(any("premium feature" in m for m in messages))
