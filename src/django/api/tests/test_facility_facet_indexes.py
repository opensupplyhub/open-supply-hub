from api.models.facility.facility_index import FacilityIndex
from api.models.facility.facility_manager_index_new import (
    FacilityIndexNewManager,
)

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
