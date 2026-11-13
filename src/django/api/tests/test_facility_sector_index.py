from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.facility_manager_index_new import (
    FacilityIndexNewManager,
)

from django.contrib.gis.geos import Point
from django.http import QueryDict
from django.test import TestCase


class FacilitySectorIndexTest(TestCase):
    """
    The sector filter stays matched to the GIN index of 0272.

    A plain GIN on an array column serves the overlap operator ``&&``, and
    nothing else. Rewriting the filter to compare a transformed column --
    lowercasing it the way facility_type is cleaned, say -- would leave the
    index in place but unused, returning every sector-filtered search to a
    sequential scan over all production locations without failing anything.
    """

    FACILITIES = (
        ("Aerospace Parts Company", ["Aerospace"]),
        ("Mining Equipment Works", ["Mining"]),
        ("Mixed Operations Site", ["Aerospace", "Mining"]),
        ("Garment Factory", ["Apparel"]),
    )

    def setUp(self):
        self.user = User.objects.create(email="example@example.com")
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

        self.source = Source.objects.create(
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contrib,
        )

        for row_index, (name, sectors) in enumerate(self.FACILITIES):
            list_item = FacilityListItem.objects.create(
                name=name,
                address="address",
                country_code="US",
                sector=sectors,
                row_index=row_index,
                status=FacilityListItem.CONFIRMED_MATCH,
                source=self.source,
            )
            facility = Facility.objects.create(
                name=name,
                address="Address",
                country_code="US",
                location=Point(0, 0),
                created_from=list_item,
            )
            # FacilityIndex.sector is denormalized from the list items
            # attached to the facility, so without this link the indexed
            # row carries an empty sector and every filter misses it.
            list_item.facility = facility
            list_item.save()

    @staticmethod
    def sector_sql(*sectors):
        params = QueryDict("", mutable=True)
        params.setlist("sectors", list(sectors))
        return str(
            FacilityIndexNewManager.filter_by_query_params(
                FacilityIndex.objects, params
            ).values("id").query
        )

    def search(self, *sectors):
        params = QueryDict("", mutable=True)
        params.setlist("sectors", list(sectors))
        result = FacilityIndexNewManager.filter_by_query_params(self, params)
        return sorted(facility.name for facility in result)

    def test_sector_filter_uses_the_overlap_operator(self):
        # `&&` is the only operator the plain GIN of 0272 can serve.
        self.assertIn("&&", self.sector_sql("Aerospace"))

    def test_sector_column_is_not_transformed(self):
        # An expression around the column would not match the index
        # expression, so the planner would ignore it.
        sql = self.sector_sql("Aerospace").upper()
        self.assertNotIn("LOWER_VARCHAR_ARRAY(", sql)
        self.assertNotIn("LOWER(\"API_FACILITYINDEX\".\"SECTOR\")", sql)

    def test_single_sector_matches_including_multi_sector_rows(self):
        self.assertEqual(
            ["Aerospace Parts Company", "Mixed Operations Site"],
            self.search("Aerospace"),
        )

    def test_overlap_matches_any_of_several_sectors(self):
        self.assertEqual(
            [
                "Aerospace Parts Company",
                "Mining Equipment Works",
                "Mixed Operations Site",
            ],
            self.search("Aerospace", "Mining"),
        )

    def test_unmatched_sector_returns_nothing(self):
        self.assertEqual([], self.search("Shipbuilding"))

    def test_no_sector_filter_returns_everything(self):
        self.assertEqual(
            sorted(name for name, _ in self.FACILITIES), self.search()
        )
