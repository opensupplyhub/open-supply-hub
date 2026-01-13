import unittest.mock
from django.contrib.gis.geos import Point, MultiPolygon
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status
from api.views.v1.response_mappings.production_locations_response \
    import ProductionLocationsResponseMapping
from api.models.partner_field import PartnerField
from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source
from api.models.user import User
from api.models.us_county_tigerline import USCountyTigerline
from api.models.wage_indicator_country_data import WageIndicatorCountryData


OPEN_SEARCH_SERVICE = "api.views.v1.production_locations.OpenSearchService"


class TestProductionLocationsViewSet(APITestCase):

    def setUp(self):
        self.search_mock = unittest.mock.patch(OPEN_SEARCH_SERVICE).start()
        self.search_index_mock = self.search_mock.return_value.search_index
        self.os_id = "CN2021250D1DTN7"
        self.ohs_response_mock = {
            "count": 2,
            "data": [
                {
                    "os_id": self.os_id,
                    "name": "location1",
                },
                {
                    "name": "location2",
                },
            ],
        }

    def test_get_production_locations(self):
        self.search_index_mock.return_value = self.ohs_response_mock
        api_res = self.client.get("/api/v1/production-locations/")
        self.assertEqual(api_res.data, self.ohs_response_mock)
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)

    def test_get_single_production_location(self):
        self.search_index_mock.return_value = self.ohs_response_mock
        url = f"/api/v1/production-locations/{self.os_id}/"
        api_res = self.client.get(url)
        self.assertEqual(api_res.data, self.ohs_response_mock["data"][0])
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)

    def test_get_single_production_location_not_found(self):
        self.search_index_mock.return_value = {}
        url = f"/api/v1/production-locations/{self.os_id}/"
        api_res = self.client.get(url)
        detail = {"detail": "The location with the given id was not found."}
        self.assertEqual(api_res.data, detail)
        self.assertEqual(api_res.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_production_locations_includes_geocode_fields(self):
        response_with_geocode = {
            "count": 1,
            "data": [
                {
                    "os_id": self.os_id,
                    "name": "location1",
                    "geocoded_location_type": "ROOFTOP",
                    "geocoded_address": "123 Main St, City, Country",
                }
            ],
        }
        self.search_index_mock.return_value = response_with_geocode
        api_res = self.client.get("/api/v1/production-locations/")
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)
        self.assertIn("data", api_res.data)
        self.assertEqual(len(api_res.data["data"]), 1)
        item = api_res.data["data"][0]
        self.assertEqual(item.get("geocoded_location_type"), "ROOFTOP")
        self.assertEqual(
            item.get("geocoded_address"), "123 Main St, City, Country"
        )

    def test_get_single_production_location_includes_geocode_fields(self):
        response_with_geocode = {
            "count": 1,
            "data": [
                {
                    "os_id": self.os_id,
                    "name": "location1",
                    "geocoded_location_type": "RANGE_INTERPOLATED",
                    "geocoded_address": "456 Side Rd, Town, Country",
                }
            ],
        }
        self.search_index_mock.return_value = response_with_geocode
        url = f"/api/v1/production-locations/{self.os_id}/"
        api_res = self.client.get(url)
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            api_res.data.get("geocoded_location_type"), "RANGE_INTERPOLATED"
        )
        self.assertEqual(
            api_res.data.get("geocoded_address"), "456 Side Rd, Town, Country"
        )

    def test_production_locations_response_mapping(self):
        self.search_index_mock.return_value = {"count": 0, "data": []}

        api_res = self.client.get("/api/v1/production-locations/")
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)

        args = self.search_index_mock.call_args[0]
        self.assertEqual(len(args), 2)
        query_body = args[1]
        self.assertIn("_source", query_body)
        self.assertListEqual(
            query_body["_source"],
            ProductionLocationsResponseMapping.PRODUCTION_LOCATIONS,
        )

    def test_single_production_location_response_mapping(self):
        self.search_index_mock.return_value = {
            "count": 1,
            "data": [
                {
                    "os_id": self.os_id,
                    "name": "location1",
                }
            ],
        }

        url = f"/api/v1/production-locations/{self.os_id}/"
        api_res = self.client.get(url)
        self.assertEqual(api_res.status_code, status.HTTP_200_OK)

        args = self.search_index_mock.call_args[0]
        self.assertEqual(len(args), 2)
        query_body = args[1]
        self.assertIn("_source", query_body)
        self.assertListEqual(
            query_body["_source"],
            ProductionLocationsResponseMapping.PRODUCTION_LOCATION_BY_OS_ID,
        )

    def _create_facility_with_partner_data(self):
        cache.clear()
        user = User.objects.create(email="partner@example.com")
        contributor = Contributor.objects.create(
            admin=user,
            name="Test Contributor",
            description="",
            website="",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        wage_indicator_field, _ = PartnerField.objects.get_or_create(
            name="wage_indicator",
            defaults={
                "type": PartnerField.OBJECT,
                "system_field": True,
                "base_url": "https://wageindicator.example/",
            }
        )
        mit_living_wage_field, _ = PartnerField.objects.get_or_create(
            name="mit_living_wage",
            defaults={
                "type": PartnerField.OBJECT,
                "system_field": True,
                "base_url": "https://livingwage.mit.edu/counties/",
            }
        )

        contributor.partner_fields.add(
            wage_indicator_field,
            mit_living_wage_field,
        )

        facility_list = FacilityList.objects.create(
            name="Test List",
            file_name="test.csv",
            header="name,address,country",
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=contributor,
        )
        facility_list_item = FacilityListItem.objects.create(
            name="Test Facility",
            address="123 Example St",
            country_code="US",
            sector=["Apparel"],
            row_index=0,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
            raw_data="Test Facility,123 Example St,US",
            raw_header="name,address,country",
            raw_json={},
            processing_results=[],
        )

        location = Point(-73.935242, 40.73061, srid=4326)
        facility = Facility.objects.create(
            id=self.os_id,
            name="Test Facility",
            address="123 Example St",
            country_code="US",
            location=location,
            created_from=facility_list_item,
        )

        WageIndicatorCountryData.objects.update_or_create(
            country_code=facility.country_code,
            defaults={
                "living_wage_link_national": (
                    "https://paywizard.org/salary/living-wages"
                ),
                "minimum_wage_link_english": (
                    "https://wageindicator.org/salary/minimum-wage/"
                    "united-states-of-america"
                ),
                "minimum_wage_link_national": (
                    "https://paywizard.org/salary/minimum-wage"
                ),
            },
        )

        point_5070 = location.transform(5070, clone=True)
        county_geometry = point_5070.buffer(1)
        if county_geometry.geom_type != "MultiPolygon":
            county_geometry = MultiPolygon(county_geometry)

        USCountyTigerline.objects.create(
            geoid="12345",
            name="Test County",
            geometry=county_geometry,
        )

        return facility

    def test_get_single_production_location_includes_partner_fields(self):
        facility = self._create_facility_with_partner_data()

        self.search_index_mock.return_value = {
            "count": 1,
            "data": [
                {
                    "os_id": facility.id,
                    "name": "location1",
                }
            ],
        }

        url = f"/api/v1/production-locations/{facility.id}/"
        api_res = self.client.get(url)

        self.assertEqual(api_res.status_code, status.HTTP_200_OK)
        self.assertIn("wage_indicator", api_res.data)
        self.assertIn("mit_living_wage", api_res.data)

        self.assertEqual(
            api_res.data["wage_indicator"].get("living_wage_link_national"),
            "https://paywizard.org/salary/living-wages",
        )
        self.assertEqual(
            api_res.data["mit_living_wage"].get("county_id"),
            "12345",
        )
