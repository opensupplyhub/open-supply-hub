from api.constants import ProcessingAction
from api.helpers.helpers import get_raw_json
from api.models import (
    Contributor,
    ExtendedField,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.processing import ItemRemovedException, parse_facility_list_item
from api.sector_product_type_parser import SectorProductTypeParser
from api.tests.processing_test_case import ProcessingTestCase


class FacilityListItemParseTest(ProcessingTestCase):
    fixtures = ["sectors"]

    def setUp(self):
        SectorProductTypeParser.sector_cache.refetch_sectors()
        self.email = "test@example.com"
        self.password = "password"
        self.name = "Test User"
        self.user = User(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.contributor = Contributor.objects.create(
            name=self.name, admin=self.user
        )

    def assert_successful_parse_results(self, item):
        self.assertEqual(FacilityListItem.PARSED, item.status)
        self.assert_status(item, ProcessingAction.PARSE)
        results = self.get_first_status(item, ProcessingAction.PARSE)
        self.assertTrue("error" in results)
        self.assertFalse(results["error"])
        self.assertTrue("started_at" in results)
        self.assertTrue("finished_at" in results)
        self.assertTrue(results["finished_at"] > results["started_at"])

    def assert_failed_parse_results(self, item, message=None):
        self.assertEqual(FacilityListItem.ERROR_PARSING, item.status)
        self.assert_status(item, ProcessingAction.PARSE)
        results = self.get_first_status(item, ProcessingAction.PARSE)
        self.assertTrue("error" in results)
        self.assertTrue(results["error"])
        self.assertTrue("message" in results)
        if message is not None:
            self.assertEqual(message, results["message"])
        self.assertTrue("started_at" in results)
        self.assertTrue("finished_at" in results)
        self.assertTrue(results["finished_at"] > results["started_at"])

    def test_expects_facility_list_item(self):
        self.assertRaises(ValueError, parse_facility_list_item, "bad")

    def test_raises_if_item_is_not_uploaded(self):
        item = FacilityListItem(status=FacilityListItem.ERROR)
        self.assertRaises(ValueError, parse_facility_list_item, item)

    def test_parses_using_header(self):
        facility_list = FacilityList.objects.create(
            header="sector,address,country,name"
        )
        source = Source.objects.create(
            source_type=Source.LIST, facility_list=facility_list
        )
        item = FacilityListItem(
            raw_data="Apparel,1234 main st,de,Shirts!",
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                "Apparel,1234 main st,de,Shirts!", facility_list.header
            ),
            source=source,
        )
        parse_facility_list_item(item)
        self.assert_successful_parse_results(item)
        self.assertEqual("DE", item.country_code)
        self.assertEqual("Shirts!", item.name)
        self.assertEqual("1234 main st", item.address)

    def test_converts_country_name_to_code(self):
        facility_list = FacilityList.objects.create(
            header="sector,address,country,name"
        )
        source = Source.objects.create(
            source_type=Source.LIST, facility_list=facility_list
        )
        item = FacilityListItem(
            raw_data="Apparel,1234 main st,ChInA,Shirts!",
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                "Apparel,1234 main st,ChInA,Shirts!", facility_list.header
            ),
            source=source,
        )
        parse_facility_list_item(item)
        self.assert_successful_parse_results(item)
        self.assertEqual("CN", item.country_code)
        self.assertEqual("Shirts!", item.name)
        self.assertEqual("1234 main st", item.address)

    def test_error_status_if_country_is_unknown(self):
        facility_list = FacilityList.objects.create(
            header="sector,address,country,name"
        )
        source = Source.objects.create(
            source_type=Source.LIST, facility_list=facility_list
        )
        item = FacilityListItem(
            raw_data="Apparel,1234 main st,Unknownistan,Shirts!",
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                "Apparel,1234 main st,Unknownistan,Shirts!",
                facility_list.header,
            ),
            source=source,
        )
        parse_facility_list_item(item)
        self.assert_failed_parse_results(
            item, 'Could not find a country code for "Unknownistan".'
        )

    def test_ppe_field_parsing(self):
        facility_list = FacilityList.objects.create(
            header=(
                "sector,address,country,name,ppe_product_types,"
                "ppe_contact_phone,ppe_contact_email,ppe_website"
            )
        )
        source = Source.objects.create(
            source_type=Source.LIST, facility_list=facility_list
        )
        item = FacilityListItem(
            raw_data=(
                "Apparel,1234 main st,de,Shirts!, Mask | Gloves ,"
                "123-456-7890,ppe@example.com,https://example.com/ppe"
            ),
            raw_header=(
                "sector,address,country,name,ppe_product_types,"
                "ppe_contact_phone,ppe_contact_email,ppe_website"
            ),
            raw_json=get_raw_json(
                (
                    "Apparel,1234 main st,de,Shirts!, Mask | Gloves ,"
                    "123-456-7890,ppe@example.com,https://example.com/ppe"
                ),
                (
                    "sector,address,country,name,ppe_product_types,"
                    "ppe_contact_phone,ppe_contact_email,ppe_website"
                ),
            ),
            source=source,
        )
        parse_facility_list_item(item)
        self.assert_successful_parse_results(item)
        self.assertEqual(["Mask", "Gloves"], item.ppe_product_types)
        self.assertEqual("123-456-7890", item.ppe_contact_phone)
        self.assertEqual("ppe@example.com", item.ppe_contact_email)
        self.assertEqual("https://example.com/ppe", item.ppe_website)

    def test_ppe_product_type_empty_values(self):
        facility_list = FacilityList.objects.create(
            header="sector,address,country,name,ppe_product_types"
        )
        source = Source.objects.create(
            source_type=Source.LIST, facility_list=facility_list
        )
        # The trailing space is important as we are testing a literally
        # non-empty but logically empty value
        item = FacilityListItem(
            raw_data="Apparel,1234 main st,de,Shirts!,| ",
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                "Apparel,1234 main st,de,Shirts!,| ", facility_list.header
            ),
            source=source,
        )
        parse_facility_list_item(item)
        self.assert_successful_parse_results(item)
        self.assertEqual([], item.ppe_product_types)

    def test_ppe_product_type_invalid_values(self):
        facility_list = FacilityList.objects.create(
            header="sector,address,country,name,ppe_product_types"
        )
        source = Source.objects.create(
            source_type=Source.LIST, facility_list=facility_list
        )
        # Using a long string for ppe_product_types to trigger a error
        item = FacilityListItem(
            raw_data=(
                "Apparel,1234 main st,de,Shirts!,"
                "012345678901234567890123456789012345678901234567890123"
                "456789012345678901234567890123456789012345678901234567"
                "89"
            ),
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                (
                    "Apparel,1234 main st,de,Shirts!,"
                    "012345678901234567890123456789012345678901"
                    "234567890123456789012345678901234567890123"
                    "45678901234567890123456789"
                ),
                facility_list.header,
            ),
            source=source,
        )
        parse_facility_list_item(item)
        # After validation error results should be cleared
        self.assert_failed_parse_results(
            item,
            "There is a problem with the ppe_product_types: "
            "Item 1 in the array did not validate: "
            "Ensure this value has at most 100 characters (it has 110).",
        )
        self.assertEqual([], item.ppe_product_types)

    def test_sector_parsing(self):
        facility_list = FacilityList.objects.create(
            header="sector,address,country,name"
        )
        source = Source.objects.create(
            source_type=Source.LIST, facility_list=facility_list
        )
        item = FacilityListItem(
            raw_data="Apparel| Food,1234 main st,ChInA,Shirts!",
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                "Apparel| Food,1234 main st,ChInA,Shirts!",
                facility_list.header,
            ),
            source=source,
        )
        parse_facility_list_item(item)
        self.assert_successful_parse_results(item)
        self.assertEqual(["Apparel", "Food"], item.sector)

    def test_sector_product_type_parsing(self):
        facility_list = FacilityList.objects.create(
            header="sector_product_type,address,country,name"
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=self.contributor,
        )
        item = FacilityListItem.objects.create(
            row_index=1,
            sector=[],
            raw_data="Apparel| Toys,1234 main st,ChInA,Shirts!",
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                "Apparel| Toys,1234 main st,ChInA,Shirts!",
                facility_list.header,
            ),
            source=source,
        )
        parse_facility_list_item(item)
        self.assert_successful_parse_results(item)
        self.assertEqual(["Apparel"], item.sector)
        self.assertEqual(1, ExtendedField.objects.all().count())
        ef = ExtendedField.objects.first()
        self.assertEqual(ExtendedField.PRODUCT_TYPE, ef.field_name)
        self.assertEqual({"raw_values": [" Toys"]}, ef.value)

    def test_sector_product_type_and_product_type_parsing(self):
        facility_list = FacilityList.objects.create(
            header="sector_product_type,product_type,address,country,name"
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=self.contributor,
        )
        item = FacilityListItem.objects.create(
            row_index=1,
            sector=[],
            raw_data="Apparel| Toys,Games,1234 main st,ChInA,Shirts!",
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                "Apparel| Toys,Games,1234 main st,ChInA,Shirts!",
                facility_list.header,
            ),
            source=source,
        )
        parse_facility_list_item(item)
        self.assert_successful_parse_results(item)
        self.assertEqual(["Apparel"], item.sector)
        self.assertEqual(1, ExtendedField.objects.all().count())
        ef = ExtendedField.objects.first()
        self.assertEqual(ExtendedField.PRODUCT_TYPE, ef.field_name)
        self.assertEqual({"raw_values": [" Toys", "Games"]}, ef.value)

    def test_sector_product_type_parsing_with_only_sector(self):
        facility_list = FacilityList.objects.create(
            header="sector_product_type,address,country,name"
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=self.contributor,
        )
        item = FacilityListItem.objects.create(
            row_index=1,
            sector=[],
            raw_data="Apparel,1234 main st,ChInA,Shirts!",
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                "Apparel,1234 main st,ChInA,Shirts!", facility_list.header
            ),
            source=source,
        )
        parse_facility_list_item(item)
        self.assert_successful_parse_results(item)
        self.assertEqual(["Apparel"], item.sector)
        self.assertEqual(0, ExtendedField.objects.all().count())

    def test_only_valid_sectors_as_product_type(self):
        facility_list = FacilityList.objects.create(
            header="product_type,address,country,name"
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=self.contributor,
        )
        item = FacilityListItem.objects.create(
            row_index=1,
            sector=[],
            raw_data="Apparel,1234 main st,ChInA,Shirts!",
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                "Apparel,1234 main st,ChInA,Shirts!", facility_list.header
            ),
            source=source,
        )
        parse_facility_list_item(item)
        self.assert_successful_parse_results(item)
        self.assertEqual(["Apparel"], item.sector)
        self.assertEqual(0, ExtendedField.objects.all().count())

    def test_parse_multi_line_country(self):
        facility_list = FacilityList.objects.create(
            header="sector,address,country,name"
        )
        source = Source.objects.create(
            source_type=Source.LIST, facility_list=facility_list
        )

        item = FacilityListItem(
            raw_data='Apparel,1234 main st,"United\nKingdom",Shirts!',
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                "Apparel,1234 main st,ChInA,Shirts!", facility_list.header
            ),
            source=source,
        )
        parse_facility_list_item(item)
        self.assert_successful_parse_results(item)

        item = FacilityListItem(
            raw_data='Apparel,1234 main st,"Dominican\r\nRepublic",Shirts!',
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                'Apparel,1234 main st,"Dominican\r\nRepublic",Shirts!',
                facility_list.header,
            ),
            source=source,
        )
        parse_facility_list_item(item)
        self.assert_successful_parse_results(item)

        item = FacilityListItem(
            raw_data='Apparel,1234 main st,"United\n\nKingdom",Shirts!',
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                'Apparel,1234 main st,"United\n\nKingdom",Shirts!',
                facility_list.header,
            ),
            source=source,
        )
        parse_facility_list_item(item)
        self.assert_successful_parse_results(item)

        item = FacilityListItem(
            raw_data='Apparel,1234 main st,"Hong\r\n\r\nKong",Shirts!',
            raw_header=facility_list.header,
            raw_json=get_raw_json(
                'Apparel,1234 main st,"Hong\r\n\r\nKong",Shirts!',
                facility_list.header,
            ),
            source=source,
        )
        parse_facility_list_item(item)
        self.assert_successful_parse_results(item)

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

        item.status = FacilityListItem.ITEM_REMOVED

        with self.assertRaises(ItemRemovedException):
            parse_facility_list_item(item)
