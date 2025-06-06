from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.models.facility.facility_manager import FacilityManager
from api.models.facility.facility_manager_index_new import (
    FacilityIndexNewManager,
)

from django.contrib.gis.geos import Point
from django.http import QueryDict
from django.test import TestCase


class FacilitySearchAccentedCharactersTest(TestCase):
    def setUp(self):
        self.email = "example@example.com"
        self.user = User.objects.create(email=self.email)
        self.user.set_password("password")
        self.user.save()

        self.contrib = Contributor.objects.create(
            admin=self.user,
            name="contributor name",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list = FacilityList.objects.create(
            header="header", file_name="one", name="list_one"
        )

        self.source_one = Source.objects.create(
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contrib,
        )

        self.list_item_one = FacilityListItem.objects.create(
            name="name",
            address="address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_one,
            source_uuid=self.source_one,
        )

        self.list_item_two = FacilityListItem.objects.create(
            name="name2",
            address="address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_one,
            source_uuid=self.source_one,
        )

        self.facility_first = Facility.objects.create(
            name="OZEN AYBA TEKSTIL",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_one,
        )

        self.facility_second = Facility.objects.create(
            name="ÖZEN DÜĞME SAN VE TURZ.TİC LTD ŞT",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_two,
        )

        self.params = QueryDict("", mutable=True)

    def test_unaccent_search(self):
        facility_search_names = ("ozen", "özen")
        managers = (FacilityManager, FacilityIndexNewManager)

        for manager in managers:
            for name in facility_search_names:
                self.params.update({"q": name})
                result = manager.filter_by_query_params(self, self.params)

                self.assertEqual(2, len(result))
                self.assertEqual(
                    any(x.name == self.facility_first.name for x in result),
                    True)
                self.assertEqual(
                    any(x.name == self.facility_second.name for x in result),
                    True)
