from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
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


class FacilityFacetIndexTest(TestCase):
    """
    The array facet filters stay matched to the GIN indexes of 0287.

    A plain GIN on an array column serves the overlap operator ``&&``, and
    nothing else. Rewriting a filter to compare a transformed column would
    leave its index in place but unused, silently returning that facet's
    searches to a sequential scan over all production locations.
    """

    @staticmethod
    def filter_sql(param, *values):
        params = QueryDict("", mutable=True)
        params.setlist(param, list(values))
        return str(
            FacilityIndexNewManager.filter_by_query_params(
                FacilityIndex.objects, params
            ).values("id").query
        )

    def test_product_type_filter_uses_the_overlap_operator(self):
        sql = self.filter_sql("product_type", "knitwear")
        self.assertIn("&&", sql)
        self.assertIn("product_type", sql)

    def test_number_of_workers_filter_uses_the_overlap_operator(self):
        sql = self.filter_sql("number_of_workers", "Less than 1000")
        self.assertIn("&&", sql)
        self.assertIn("number_of_workers", sql)

    def test_parent_company_name_filter_uses_the_overlap_operator(self):
        # A non-numeric parent_company value filters by name.
        sql = self.filter_sql("parent_company", "BASF SE")
        self.assertIn("&&", sql)
        self.assertIn("parent_company_name", sql)

    def test_facet_columns_are_not_transformed(self):
        # An expression around the column would not match the index
        # expression, so the planner would ignore it.
        for param, value, column in (
            ("product_type", "knitwear", "product_type"),
            ("number_of_workers", "Less than 1000", "number_of_workers"),
            ("parent_company", "BASF SE", "parent_company_name"),
        ):
            sql = self.filter_sql(param, value).upper()
            self.assertNotIn(
                'LOWER("API_FACILITYINDEX"."{}")'.format(column.upper()),
                sql,
            )
            self.assertNotIn("LOWER_VARCHAR_ARRAY(", sql)


class FacilityFacetPipelineTest(TestCase):
    """
    Store-side and query-side transforms agree, end to end.

    These store values through the real indexing path (the extended-field
    triggers populate FacilityIndex) and filter them back, so they fail if
    either side's transform drifts. That is the bug class the SQL pins
    above cannot see: OSDEV-3920 exists because product_type's two
    transforms disagree, and only a pipeline test catches that.
    """

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

        self.list_item = FacilityListItem.objects.create(
            name="Brandix Apparel India",
            address="address",
            country_code="IN",
            sector=["Apparel"],
            row_index=0,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )
        self.facility = Facility.objects.create(
            name="Brandix Apparel India",
            address="Address",
            country_code="IN",
            location=Point(0, 0),
            created_from=self.list_item,
        )
        # index_extended_fields() walks list item -> match -> source, so
        # fields read through it (number_of_workers) index nothing without
        # an active match and the item linked to the facility.
        FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=self.list_item,
            confidence=0.85,
            results="",
        )
        self.list_item.facility = self.facility
        self.list_item.save()

    def create_extended_field(self, field_name, value):
        return ExtendedField.objects.create(
            contributor=self.contrib,
            facility=self.facility,
            facility_list_item=self.list_item,
            field_name=field_name,
            value=value,
        )

    def search(self, param, *values):
        params = QueryDict("", mutable=True)
        params.setlist(param, list(values))
        result = FacilityIndexNewManager.filter_by_query_params(self, params)
        return sorted(facility.name for facility in result)

    def test_product_type_round_trips_without_punctuation(self):
        self.create_extended_field(
            ExtendedField.PRODUCT_TYPE, {"raw_values": ["Knitwear"]}
        )
        # Stored lowered (0130_index_product_type.sql); the query side's
        # clean() also lowers, so punctuation-free values agree.
        self.assertEqual(
            ["Brandix Apparel India"],
            self.search("product_type", "Knitwear"),
        )

    def test_punctuated_product_type_is_unfilterable_today(self):
        # Records the OSDEV-3920 boundary as an executable fact: the store
        # side keeps the dash while clean() strips it, so the two sides can
        # never be equal. When OSDEV-3920 lands, this flips to a positive
        # assertion.
        self.create_extended_field(
            ExtendedField.PRODUCT_TYPE, {"raw_values": ["T-Shirts"]}
        )
        self.assertEqual([], self.search("product_type", "T-Shirts"))

    def test_number_of_workers_round_trips_through_the_range_label(self):
        # The index function turns min/max into the fixed range labels the
        # UI offers, so both sides draw from the same vocabulary.
        self.create_extended_field(
            ExtendedField.NUMBER_OF_WORKERS, {"min": 1500, "max": 2000}
        )
        self.assertEqual(
            ["Brandix Apparel India"],
            self.search("number_of_workers", "1001-5000"),
        )

    def test_parent_company_name_round_trips_with_exact_case(self):
        self.create_extended_field(
            ExtendedField.PARENT_COMPANY, {"name": "BASF SE"}
        )
        self.assertEqual(
            ["Brandix Apparel India"],
            self.search("parent_company", "BASF SE"),
        )

    def test_parent_company_name_match_is_case_sensitive(self):
        # Neither side lowercases, so matching depends on the UI typeahead
        # serving stored spellings; a freeform lowercase query misses.
        # Documents the boundary from the OSDEV-3897 review audit.
        self.create_extended_field(
            ExtendedField.PARENT_COMPANY, {"name": "BASF SE"}
        )
        self.assertEqual([], self.search("parent_company", "basf se"))
