from unittest.mock import Mock, patch

from api.constants import ProcessingAction
from api.helpers.helpers import get_raw_json
from api.models import FacilityList, FacilityListItem, Source
from api.processing import (
    ItemRemovedException,
    geocode_facility_list_item,
    parse_facility_list_item,
)
from api.tests.processing_test_case import ProcessingTestCase
from api.tests.test_data import listitem_geocode_data

from django.contrib.gis.geos import Point


class FacilityListItemGeocodingTest(ProcessingTestCase):
    def test_invalid_argument_raises_error(self):
        with self.assertRaises(ValueError) as cm:
            geocode_facility_list_item("hello")

        self.assertEqual(
            cm.exception.args, ("Argument must be a FacilityListItem",)
        )

    def test_unparsed_item_raises_error(self):
        facility_list = FacilityList(header="sector,address,country,name")
        source = Source(source_type=Source.LIST, facility_list=facility_list)
        item = FacilityListItem(
            raw_data="Apparel,1400 JFK Blvd, Philly,us,Shirts!",
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                "Apparel,1400 JFK Blvd, Philly,us,Shirts!",
                facility_list.header,
            ),
            source=source,
        )

        with self.assertRaises(ValueError) as cm:
            geocode_facility_list_item(item)

        self.assertEqual(
            cm.exception.args,
            ("Items to be geocoded must be in the PARSED status",),
        )

    @patch("api.geocoding.requests.get")
    def test_nested_correct_country_code_succeeds(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = listitem_geocode_data
        facility_list = FacilityList.objects.create(
            header="sector,address,country,name"
        )
        source = Source.objects.create(
            source_type=Source.LIST, facility_list=facility_list
        )
        item = FacilityListItem(
            raw_data='Apparel,"Linjiacun Town, Zhucheng City Weifang, '
            'Daman, Daman, 396210",IN,Shirts!',
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                (
                    'Apparel,"Linjiacun Town, Zhucheng City Weifang, '
                    'Daman, Daman, 396210",IN,Shirts!'
                ),
                facility_list.header,
            ),
            source=source,
        )
        parse_facility_list_item(item)
        geocode_facility_list_item(item)

        expected_result = listitem_geocode_data["results"][1]
        expected_address = expected_result["formatted_address"]

        self.assertEqual(item.status, FacilityListItem.GEOCODED)
        self.assertEqual(item.geocoded_address, expected_address)
        self.assertIsInstance(item.geocoded_point, Point)

    @patch("api.geocoding.requests.get")
    def test_incorrect_country_code_has_error_status(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = listitem_geocode_data
        facility_list = FacilityList.objects.create(
            header="sector,address,country,name"
        )
        source = Source.objects.create(
            source_type=Source.LIST, facility_list=facility_list
        )
        item = FacilityListItem(
            raw_data='Apparel,"Linjiacun Town, Zhucheng City Weifang, '
            'Daman, Daman, 396210",BD,Shirts!',
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                (
                    'Apparel,"Linjiacun Town, Zhucheng City Weifang, '
                    'Daman, Daman, 396210",BD,Shirts!'
                ),
                facility_list.header,
            ),
            source=source,
        )
        parse_facility_list_item(item)
        geocode_facility_list_item(item)

        self.assertEqual(item.status, FacilityListItem.ERROR_GEOCODING)
        self.assertIsNone(item.geocoded_address)
        self.assertIsNone(item.geocoded_point)

    def test_successfully_geocoded_item_has_correct_results(self):
        facility_list = FacilityList.objects.create(
            header="sector,address,country,name"
        )
        source = Source.objects.create(
            source_type=Source.LIST, facility_list=facility_list
        )
        item = FacilityListItem(
            raw_data='Apparel,"City Hall, Philly, PA",us,Shirts!',
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                'Apparel,"City Hall, Philly, PA",us,Shirts!',
                facility_list.header,
            ),
            source=source,
        )

        parse_facility_list_item(item)
        geocode_facility_list_item(item)

        self.assertIsNotNone(item.geocoded_address)
        self.assertIsInstance(item.geocoded_point, Point)
        self.assertEqual(item.status, FacilityListItem.GEOCODED)
        self.assertIn(
            "results",
            self.get_first_status(item, ProcessingAction.GEOCODE)["data"],
        )

    def test_failed_geocoded_item_has_no_resuts_status(self):
        facility_list = FacilityList.objects.create(
            header="sector,address,country,name"
        )
        source = Source.objects.create(
            source_type=Source.LIST, facility_list=facility_list
        )
        item = FacilityListItem(
            raw_data='Apparel,"hello, world, foo, bar, baz",us,Shirts!',
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                'Apparel,"hello, world, foo, bar, baz",us,Shirts!',
                facility_list.header,
            ),
            source=source,
        )
        parse_facility_list_item(item)
        item.country_code = "$%"
        geocode_facility_list_item(item)

        self.assertEqual(item.status, FacilityListItem.GEOCODED_NO_RESULTS)
        self.assertIsNone(item.geocoded_address)
        self.assertIsNone(item.geocoded_point)

    def test_removed_item_raises_exception(self):
        facility_list = FacilityList.objects.create(
            header="sector,address,country,name"
        )
        source = Source.objects.create(
            source_type=Source.LIST, facility_list=facility_list
        )
        item = FacilityListItem(
            raw_data='Apparel,"hello, world, foo, bar, baz",us,Shirts!',
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                'Apparel,"hello, world, foo, bar, baz",us,Shirts!',
                facility_list.header,
            ),
            source=source,
        )
        parse_facility_list_item(item)

        item.status = FacilityListItem.ITEM_REMOVED

        with self.assertRaises(ItemRemovedException):
            geocode_facility_list_item(item)
