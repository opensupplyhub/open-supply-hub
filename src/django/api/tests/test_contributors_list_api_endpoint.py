from api.models import (
    Contributor,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)

from django.test import TestCase


class ContributorsListAPIEndpointTest(TestCase):
    def setUp(self):
        self.name_one = "name_one"
        self.name_two = "name_two"
        self.name_three = "name_three"
        self.name_four = "name_four"

        self.address_one = "address_one"
        self.address_two = "address_two"
        self.address_three = "address_three"
        self.address_four = "address_four"

        self.email_one = "one@example.com"
        self.email_two = "two@example.com"
        self.email_three = "three@example.com"
        self.email_four = "four@example.com"
        self.email_five = "five@example.com"
        self.email_six = "six@example.com"
        self.email_seven = "seven@example.com"

        self.contrib_one_name = "contributor that should be included"
        self.contrib_two_name = "contributor with no lists"
        self.contrib_three_name = "contributor with an inactive list"
        self.contrib_four_name = "contributor with a non public list"
        self.contrib_five_name = "contributor with only error items"
        self.contrib_six_name = "contributor with one good and one error item"
        self.contrib_seven_name = "contributor with create=False API source"

        self.contrib_one_type = "Brand / Retailer"
        self.contrib_two_type = "Multi-Stakeholder Initiative"
        self.contrib_three_type = "Union"
        self.contrib_four_type = "Brand / Retailer"
        self.contrib_five_type = "Multi-Stakeholder Initiative"
        self.contrib_six_type = "Test"
        self.contrib_seven_type = "Union"

        self.country_code = "US"
        self.list_one_name = "one"
        self.list_one_b_name = "one-b"
        self.list_three_name = "three"
        self.list_four_name = "four"
        self.list_five_name = "five"
        self.list_six_name = "six"
        self.list_seven_name = "seven"

        self.user_one = User.objects.create(email=self.email_one)
        self.user_two = User.objects.create(email=self.email_two)
        self.user_three = User.objects.create(email=self.email_three)
        self.user_four = User.objects.create(email=self.email_four)
        self.user_five = User.objects.create(email=self.email_five)
        self.user_six = User.objects.create(email=self.email_six)
        self.user_seven = User.objects.create(email=self.email_seven)

        self.contrib_one = Contributor.objects.create(
            admin=self.user_one,
            name=self.contrib_one_name,
            contrib_type=self.contrib_one_type,
        )

        self.contrib_two = Contributor.objects.create(
            admin=self.user_two,
            name=self.contrib_two_name,
            contrib_type=self.contrib_two_type,
        )

        self.contrib_three = Contributor.objects.create(
            admin=self.user_three,
            name=self.contrib_three_name,
            contrib_type=self.contrib_three_type,
        )

        self.contrib_four = Contributor.objects.create(
            admin=self.user_four,
            name=self.contrib_four_name,
            contrib_type=self.contrib_four_type,
        )

        self.contrib_five = Contributor.objects.create(
            admin=self.user_five,
            name=self.contrib_five_name,
            contrib_type=self.contrib_five_type,
        )

        self.contrib_six = Contributor.objects.create(
            admin=self.user_six,
            name=self.contrib_six_name,
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
            other_contrib_type=self.contrib_six_type,
        )

        self.contrib_seven = Contributor.objects.create(
            admin=self.user_seven,
            name=self.contrib_seven_name,
            contrib_type=self.contrib_seven_type,
        )

        self.list_one = FacilityList.objects.create(
            header="header", file_name="one", name=self.list_one_name
        )

        self.source_one = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.list_one,
            contributor=self.contrib_one,
        )

        self.list_item_one = FacilityListItem.objects.create(
            row_index=0,
            source=self.source_one,
            sector=[],
            status=FacilityListItem.MATCHED,
        )

        self.list_one_b = FacilityList.objects.create(
            header="header", file_name="one-b", name=self.list_one_b_name
        )

        self.source_one_b = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.list_one_b,
            contributor=self.contrib_one,
        )

        self.list_item_one_b = FacilityListItem.objects.create(
            row_index=0,
            source=self.source_one_b,
            sector=[],
            status=FacilityListItem.MATCHED,
        )

        # Contributor two has no lists

        self.list_three = FacilityList.objects.create(
            header="header", file_name="three", name=self.list_three_name
        )

        self.source_three = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.list_three,
            is_public=True,
            is_active=False,
            contributor=self.contrib_three,
        )

        self.list_four = FacilityList.objects.create(
            header="header", file_name="four", name=self.list_four_name
        )

        self.source_four = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.list_four,
            is_public=False,
            is_active=True,
            contributor=self.contrib_four,
        )

        self.list_five = FacilityList.objects.create(
            header="header", file_name="five", name=self.list_five_name
        )

        self.source_five = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.list_five,
            contributor=self.contrib_five,
        )

        self.list_item_five = FacilityListItem.objects.create(
            row_index=0,
            source=self.source_five,
            sector=[],
            status=FacilityListItem.ERROR_PARSING,
        )

        self.list_six = FacilityList.objects.create(
            header="header", file_name="six", name=self.list_six_name
        )

        self.source_six = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.list_six,
            contributor=self.contrib_six,
        )

        self.list_item_six_a = FacilityListItem.objects.create(
            row_index=0,
            source=self.source_six,
            sector=[],
            status=FacilityListItem.ERROR_PARSING,
        )

        self.list_item_six_b = FacilityListItem.objects.create(
            row_index=1,
            source=self.source_six,
            sector=[],
            status=FacilityListItem.MATCHED,
        )

        # Test to ensure contributors don't appear in the list if all of their
        # sources have create=False
        self.source_seven = Source.objects.create(
            source_type=Source.SINGLE,
            create=False,
            contributor=self.contrib_seven,
        )

        self.list_item_seven = FacilityListItem.objects.create(
            row_index=0,
            source=self.source_seven,
            sector=[],
            status=FacilityListItem.MATCHED,
        )

    def test_contributors_list_has_only_contributors_with_active_lists(self):
        response = self.client.get("/api/contributors/")
        response_data = response.json()
        contributor_names = list(zip(*response_data))[1]
        contributor_types = list(zip(*response_data))[2]

        self.assertIn(
            self.contrib_one_name,
            contributor_names,
        )

        self.assertIn(
            self.contrib_one_type,
            contributor_types,
        )

        self.assertNotIn(
            self.contrib_two_name,
            contributor_names,
        )

        self.assertNotIn(
            self.contrib_three_name,
            contributor_names,
        )

        self.assertNotIn(
            self.contrib_four_name,
            contributor_names,
        )

        self.assertNotIn(
            self.contrib_five_name,
            contributor_names,
        )

        self.assertIn(
            self.contrib_six_name,
            contributor_names,
        )

        self.assertIn(
            self.contrib_six_type,
            contributor_types,
        )

        self.assertEqual(
            2,
            len(contributor_names),
        )
