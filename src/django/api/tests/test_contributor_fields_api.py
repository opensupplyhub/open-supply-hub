import json

from api.helpers.helpers import get_raw_json, parse_raw_data
from api.models import (
    Contributor,
    EmbedConfig,
    EmbedField,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex
from api.models.transactions.index_facilities_new import index_facilities_new
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.gis.geos import Point


class ContributorFieldsApiTest(APITestCase):
    def setUp(self):
        self.url = "/api/facilities/"
        self.user_email = "test@example.com"
        self.user_password = "example123"
        self.user = User.objects.create(email=self.user_email)
        self.user.set_password(self.user_password)
        self.user.save()

        self.embed_config = EmbedConfig.objects.create()

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor 1",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
            embed_config=self.embed_config,
        )
        self.embed_one = EmbedField.objects.create(
            embed_config=self.embed_config,
            order=0,
            column_name="extra_1",
            display_name="ExtraOne",
            visible=True,
            searchable=True,
        )
        self.embed_two = EmbedField.objects.create(
            embed_config=self.embed_config,
            order=1,
            column_name="extra_2",
            display_name="ExtraTwo",
            visible=True,
            searchable=True,
        )

        self.list = FacilityList.objects.create(
            header="country,name,address,extra_1",
            file_name="one",
            name="First List",
        )

        self.list_source = Source.objects.create(
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        raw_data = '"US","Towel Factory 42","42 Dolphin St","data one"'
        self.list_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.list_source,
            raw_header="country,name,address,extra_1",
            raw_json=get_raw_json(raw_data, "country,name,address,extra_1"),
            raw_data=raw_data,
        )

        self.facility = Facility.objects.create(
            country_code=self.list_item.country_code,
            created_from=self.list_item,
            location=Point(0, 0),
        )
        self.list_item.facility = self.facility
        self.list_item.save()

        self.match_one = FacilityMatch.objects.create(
            facility_list_item=self.list_item,
            facility=self.facility,
            is_active=True,
            results={},
        )

        self.api_source = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.api_list_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            raw_data=(
                "{'country': 'US', 'name': 'Item',"
                "'address': 'Address', 'extra_2': 'data two'}"
            ),
            raw_json=parse_raw_data(
                (
                    "{'country': 'US', 'name': 'Item',"
                    "'address': 'Address', 'extra_2': 'data two'}"
                )
            ),
            raw_header="",
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.api_source,
        )
        self.facility_two = Facility.objects.create(
            country_code=self.api_list_item.country_code,
            created_from=self.api_list_item,
            location=Point(0, 0),
        )
        self.api_list_item.facility = self.facility_two
        self.api_list_item.save()
        self.match_two = FacilityMatch.objects.create(
            facility_list_item=self.api_list_item,
            facility=self.facility_two,
            is_active=True,
            results={},
        )

    def test_list_fields(self):
        response = self.client.get(
            self.url
            + self.facility.id
            + "/?embed=1&contributor="
            + str(self.contributor.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        contributor_fields = content["properties"]["contributor_fields"]
        self.assertEqual(2, len(contributor_fields))
        field = contributor_fields[0]
        field_two = contributor_fields[1]
        self.assertEqual("ExtraOne", field["label"])
        self.assertEqual("data one", field["value"])
        self.assertEqual("ExtraTwo", field_two["label"])
        self.assertEqual(None, field_two["value"])

    def test_single_fields(self):
        response = self.client.get(
            self.url
            + self.facility_two.id
            + "/?embed=1&contributor="
            + str(self.contributor.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        contributor_fields = content["properties"]["contributor_fields"]
        self.assertEqual(2, len(contributor_fields))
        field = contributor_fields[0]
        field_two = contributor_fields[1]
        self.assertEqual("ExtraOne", field["label"])
        self.assertEqual(None, field["value"])
        self.assertEqual("ExtraTwo", field_two["label"])
        self.assertEqual("data two", field_two["value"])

    def test_without_embed(self):
        response = self.client.get(
            self.url
            + self.facility.id
            + "/?contributor="
            + str(self.contributor.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        contributor_fields = content["properties"]["contributor_fields"]
        self.assertEqual(0, len(contributor_fields))

    def test_without_contributor(self):
        response = self.client.get(self.url + self.facility.id + "/?embed=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        contributor_fields = content["properties"]["contributor_fields"]
        self.assertEqual(0, len(contributor_fields))

    def test_inactive_match(self):
        self.match_one.is_active = False
        self.match_one.save()
        response = self.client.get(
            self.url
            + self.facility.id
            + "/?embed=1&contributor="
            + str(self.contributor.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        contributor_fields = content["properties"]["contributor_fields"]
        self.assertEqual(2, len(contributor_fields))
        field = contributor_fields[0]
        field_two = contributor_fields[1]
        self.assertEqual("ExtraOne", field["label"])
        self.assertEqual(None, field["value"])
        self.assertEqual("ExtraTwo", field_two["label"])
        self.assertEqual(None, field_two["value"])

    def test_custom_text(self):
        indexes = FacilityIndex.objects.count()
        self.assertEqual(2, indexes)
        index_one = FacilityIndex.objects.get(id=self.facility.id)
        index_two = FacilityIndex.objects.get(id=self.facility_two.id)
        index_one_data = "{}|data one".format(self.contributor.id)
        self.assertIn(index_one_data, index_one.custom_text)
        index_two_data = "{}|data two".format(self.contributor.id)
        self.assertIn(index_two_data, index_two.custom_text)

    def test_custom_text_excludes_unsearchable(self):
        self.embed_two.searchable = False
        self.embed_two.save()

        # Run indexing manually because we don't use a post_save signal for
        # embed fields (since they are deleted and recreated each time the
        # config is updated, it creates a lot of overhead) and instead update
        # the index directly in the embed config update views
        f_ids = Facility.objects.filter(
            facilitylistitem__source__contributor=self.contributor
        ).values_list("id", flat=True)
        if len(f_ids) > 0:
            index_facilities_new(list(f_ids))

        index_one = FacilityIndex.objects.get(id=self.facility.id)
        index_one_data = "{}|data one".format(self.contributor.id)
        self.assertIn(index_one_data, index_one.custom_text)
        index_two = FacilityIndex.objects.get(id=self.facility_two.id)
        index_two_data = "{}|data two".format(self.contributor.id)
        self.assertNotIn(index_two_data, index_two.custom_text)

    def test_custom_text_excludes_inactive(self):
        self.match_one.is_active = False
        self.match_one.save()

        index_one = FacilityIndex.objects.get(id=self.facility.id)
        index_one_data = "{}|data one".format(self.contributor.id)
        self.assertNotIn(index_one_data, index_one.custom_text)
        index_two = FacilityIndex.objects.get(id=self.facility_two.id)
        index_two_data = "{}|data two".format(self.contributor.id)
        self.assertIn(index_two_data, index_two.custom_text)

    def test_custom_text_uses_both_items(self):
        new_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            raw_data=(
                "{'country': 'US', 'name': 'Item',"
                + "'address': 'Address',"
                + " 'extra_2': 'data three'}"
            ),
            raw_json=parse_raw_data(
                (
                    "{'country': 'US', 'name': 'Item',"
                    "'address': 'Address',"
                    " 'extra_2': 'data three'}"
                )
            ),
            raw_header="",
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.api_source,
        )
        new_item.facility = self.facility_two
        new_item.save()
        FacilityMatch.objects.create(
            facility_list_item=new_item,
            facility=self.facility_two,
            is_active=True,
            results={},
        )

        index_one = FacilityIndex.objects.get(id=self.facility.id)
        index_one_data = "{}|data one".format(self.contributor.id)
        self.assertIn(index_one_data, index_one.custom_text)
        index_two = FacilityIndex.objects.get(id=self.facility_two.id)
        index_two_data = "{}|data two".format(self.contributor.id)
        self.assertIn(index_two_data, index_two.custom_text)
        index_three_data = "{}|data three".format(self.contributor.id)
        self.assertIn(index_three_data, index_two.custom_text)

    def test_custom_text_uses_field_contributor(self):
        user_two = User.objects.create(email="test2@example.com")
        contributor_two = Contributor.objects.create(
            admin=user_two,
            name="test contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        api_source_two = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=contributor_two,
        )

        new_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            raw_data=(
                "{'country': 'US', 'name': 'Item',"
                + "'address': 'Address',"
                + " 'extra_2': 'data three'}"
            ),
            raw_json=parse_raw_data(
                (
                    "{'country': 'US', 'name': 'Item',"
                    "'address': 'Address',"
                    " 'extra_2': 'data three'}"
                )
            ),
            raw_header="",
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=api_source_two,
            source_uuid=api_source_two,
        )
        new_item.facility = self.facility_two
        new_item.save()
        FacilityMatch.objects.create(
            facility_list_item=new_item,
            facility=self.facility_two,
            is_active=True,
            results={},
        )

        index_one = FacilityIndex.objects.get(id=self.facility.id)
        index_one_data = "{}|data one".format(self.contributor.id)
        self.assertIn(index_one_data, index_one.custom_text)
        index_two = FacilityIndex.objects.get(id=self.facility_two.id)
        index_two_data = "{}|data two".format(self.contributor.id)
        self.assertIn(index_two_data, index_two.custom_text)
        index_three_data = "{}|data three".format(contributor_two.id)
        self.assertNotIn(index_three_data, index_two.custom_text)
