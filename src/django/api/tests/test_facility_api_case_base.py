from api.constants import FeatureGroups
from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from rest_framework.test import APITestCase

from django.contrib import auth
from django.contrib.gis.geos import Point


class FacilityAPITestCaseBase(APITestCase):
    def setUp(self):
        self.user_email = "test@example.com"
        self.user_pass = "example123"
        self.user = User.objects.create(email=self.user_email)
        self.user.set_password(self.user_pass)
        self.user.save()

        self.superuser_email = "super@example.com"
        self.superuser_pass = "example123"
        self.superuser = User.objects.create_superuser(
            email=self.superuser_email, password=self.superuser_pass
        )

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor 1",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list = FacilityList.objects.create(
            header="header", file_name="one", name="First List"
        )

        self.source = Source.objects.create(
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )

        self.facility = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item,
        )

        self.match = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=self.list_item,
            confidence=0.85,
            results="",
        )

        self.list_item.facility = self.facility
        self.list_item.save()

    def join_group_and_login(self):
        self.client.logout()
        group = auth.models.Group.objects.get(
            name=FeatureGroups.CAN_SUBMIT_FACILITY,
        )
        self.user.groups.set([group.id])
        self.user.save()
        self.client.login(email=self.user_email, password=self.user_pass)
