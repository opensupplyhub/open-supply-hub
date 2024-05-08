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
        self.user_password = "example123"
        self.user = User.objects.create(email=self.user_email)
        self.user.set_password(self.user_password)
        self.user.save()

        self.user_email_two = "testtwo@example.com"
        self.user_two = User.objects.create(email=self.user_email_two)
        self.user_two.set_password(self.user_password)
        self.user_two.save()

        self.superuser_email = "super@example.com"
        self.superuser_password = "example123"
        self.superuser = User.objects.create_superuser(
            email=self.superuser_email, password=self.superuser_password
        )

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor 1",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.contributor_two = Contributor.objects.create(
            admin=self.user_two,
            name="test contributor 2",
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

        self.source_initial = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor_two,
        )

        self.list_item_initial = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.MATCHED,
            source=self.source_initial,
        )

        self.facility_initial = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_initial,
        )

        self.source_two = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor_two,
        )

        self.list_item_two = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.MATCHED,
            source=self.source_two,
            facility=self.facility_initial,
        )

        self.match_two = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility_initial,
            facility_list_item=self.list_item_two,
            confidence=0.85,
            results="",
        )

        self.source_three = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor_two,
        )

        self.list_item_three = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.POTENTIAL_MATCH,
            source=self.source_three,
        )

        self.match_three = FacilityMatch.objects.create(
            status=FacilityMatch.PENDING,
            facility=self.facility_initial,
            facility_list_item=self.list_item_three,
            confidence=0.75,
            results="",
        )

        self.source_four = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor_two,
        )

        self.list_item_four = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.MATCHED,
            source=self.source_four,
        )

        self.match_four = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility_initial,
            facility_list_item=self.list_item_four,
            confidence=1,
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
        self.client.login(email=self.user_email, password=self.user_password)
