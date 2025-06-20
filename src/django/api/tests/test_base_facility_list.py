from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from rest_framework.test import APITestCase

from django.contrib.gis.geos import Point


class BaseFacilityListTest(APITestCase):
    def setUp(self):
        self.user_email = "test@example.com"
        self.user_password = "example123"
        self.user = User.objects.create(email=self.user_email)
        self.user.set_password(self.user_password)
        self.user.save()

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list = FacilityList.objects.create(
            header="header", file_name="one", name="First List"
        )

        self.source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.list,
            contributor=self.contributor,
        )

        self.list_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            source=self.source,
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
        )

        self.facility = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item,
        )

        self.inactive_list = FacilityList.objects.create(
            header="header", file_name="one", name="Second List"
        )

        Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.inactive_list,
            is_active=False,
            contributor=self.contributor,
        )

        self.private_list = FacilityList.objects.create(
            header="header", file_name="one", name="Third List"
        )

        Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.private_list,
            is_public=False,
            contributor=self.contributor,
        )

        self.superuser_email = "superuser@example.com"
        self.superuser_password = "superuser"

        self.superuser = User.objects.create_superuser(
            self.superuser_email, self.superuser_password
        )

        self.supercontributor = Contributor.objects.create(
            admin=self.superuser,
            name="test super contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.superlist = FacilityList.objects.create(
            header="header", file_name="one", name="Super List"
        )

        Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.superlist,
            contributor=self.supercontributor,
        )
