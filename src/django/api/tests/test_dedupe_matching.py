from api.matching import GazetteerCache, match_facility_list_items
from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
)
from api.processing import is_string_match, reduce_matches

from django.test import TestCase


def junk_chars(string):
    return "AA" + string + "YY"


class DedupeMatchingTest(TestCase):
    fixtures = [
        "users",
        "contributors",
        "facility_lists",
        "sources",
        "facility_list_items",
        "facilities",
        "facility_matches",
    ]

    def setUp(self):
        self.contributor = Contributor.objects.first()

    def tearDown(self):
        GazetteerCache._gazetter = None
        GazetteerCache._facility_version = None
        GazetteerCache._match_version = None

    def create_list(self, items, status=FacilityListItem.GEOCODED):
        facility_list = FacilityList(
            name="test",
            description="",
            file_name="test.csv",
            header="country,name,address,sector",
        )
        facility_list.save()
        source = Source(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=self.contributor,
        )
        source.save()
        for index, item in enumerate(items):
            country_code, name, address = item
            list_item = FacilityListItem(
                source=source,
                row_index=index,
                raw_data="",
                status=status,
                name=name,
                address=address,
                country_code=country_code,
                geocoded_address="",
                sector=["Apparel"],
            )
            list_item.save()
        return facility_list

    def test_matches(self):
        facility = Facility.objects.first()
        facility_list = self.create_list(
            [
                (
                    facility.country_code,
                    junk_chars(facility.name.upper()),
                    junk_chars(facility.address.upper()),
                )
            ]
        )
        facility_list = self.create_list(
            [
                (
                    facility.country_code,
                    facility.name.upper(),
                    junk_chars(facility.address.upper()),
                )
            ]
        )
        result = match_facility_list_items(facility_list)
        matches = result["item_matches"]
        item_id = str(facility_list.source.facilitylistitem_set.all()[0].id)
        self.assertIn(item_id, matches)
        self.assertEqual(1, len(matches[item_id]))
        self.assertEqual(str(facility.id), matches[item_id][0][0])
        self.assertEqual(0.5, result["results"]["gazetteer_threshold"])
        self.assertFalse(result["results"]["no_gazetteer_matches"])
        self.assertFalse(result["results"]["no_geocoded_items"])

    def assert_match_count_after_delete(
        self, delete_facility=True, match_count=0
    ):
        # First create a list and match it. We use a multiple item list so that
        # there is valid training data available after we delete records later
        # in the test case.
        facility_list = self.create_list(
            [
                (
                    f.country_code,
                    junk_chars(f.name.upper()),
                    junk_chars(f.address.upper()),
                )
                for f in Facility.objects.all()[:3]
            ]
        )
        result = match_facility_list_items(facility_list)
        matches = result["item_matches"]
        item_ids = [
            str(i.id) for i in facility_list.source.facilitylistitem_set.all()
        ]
        matched_ids = [id for id in item_ids if id in matches.keys()]
        self.assertTrue(len(matched_ids) > 0)

        # Now we delete the previously matched facility and try to match it
        # again
        matched_facility_id = matches[matched_ids[0]][0][0]

        facility = Facility.objects.get(pk=matched_facility_id)
        for item in FacilityListItem.objects.filter(facility=facility):
            item.facility = None
            item.save()

        for match in FacilityMatch.objects.filter(facility=facility):
            match.delete()

        facility_list = self.create_list(
            [(facility.country_code, facility.name, facility.address)]
        )
        item_id = str(facility_list.source.facilitylistitem_set.all()[0].id)

        if delete_facility:
            facility.delete()

        result = match_facility_list_items(facility_list)
        matches = result["item_matches"]
        self.assertEqual(match_count, len(matches[item_id]))

    def test_does_not_match_after_delete_facility_and_match(self):
        self.assert_match_count_after_delete(
            delete_facility=True, match_count=0
        )

    def test_matches_after_delete_match(self):
        self.assert_match_count_after_delete(
            delete_facility=False, match_count=1
        )

    def test_does_not_match(self):
        facility_list = self.create_list(
            [("US", "Azavea", "990 Spring Garden St.")]
        )
        result = match_facility_list_items(facility_list)
        matches = result["item_matches"]
        self.assertEqual(0, len(matches))
        self.assertTrue(result["results"]["no_gazetteer_matches"])

    def test_no_geocoded_items(self):
        facility = Facility.objects.first()
        facility_list = self.create_list(
            [
                (
                    facility.country_code,
                    junk_chars(facility.name.upper()),
                    junk_chars(facility.address.upper()),
                )
            ],
            status=FacilityListItem.PARSED,
        )
        result = match_facility_list_items(facility_list)
        self.assertTrue(result["results"]["no_geocoded_items"])

    def test_reduce_matches(self):
        matches = [
            ("US2020052GKF19F", 75),
            ("US2020052GKF19F_MATCH-23", 88),
            ("US2020052YDVKBQ", 45),
        ]
        expected = [("US2020052GKF19F", 88), ("US2020052YDVKBQ", 45)]
        self.assertEqual(expected, reduce_matches(matches))

    def test_is_string_match(self):
        # The clean function will remove stray characters
        item = FacilityListItem(
            country_code="US", name="Pants Ahoy", address="123 Main St"
        )
        facility = Facility(
            country_code="US",
            name='"PANTS AHOY"',
            address="123     MAIN     ST",
        )
        self.assertTrue(is_string_match(item, facility))

        # Needs to be an exact character match
        item = FacilityListItem(
            country_code="US", name="Pants Ahoy", address="123 Main St"
        )
        facility = Facility(
            country_code="US", name="Pants Ahoy", address="123 Main Street"
        )
        self.assertFalse(is_string_match(item, facility))
