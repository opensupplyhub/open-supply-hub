from django.contrib.gis.geos import Point
from django.test import TestCase

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
from api.serializers import FacilityIndexDetailsSerializer


class SourceContributorReassignmentTest(TestCase):
    def setUp(self):
        self.original_user = User.objects.create(email="original@example.com")
        self.new_user = User.objects.create(email="new@example.com")

        self.original_contributor = Contributor.objects.create(
            admin=self.original_user,
            name="Original Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.new_contributor = Contributor.objects.create(
            admin=self.new_user,
            name="New Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.facility_list = FacilityList.objects.create(
            header="header",
            file_name="list.csv",
            name="List Name",
        )
        self.source = Source.objects.create(
            facility_list=self.facility_list,
            source_type=Source.LIST,
            contributor=self.original_contributor,
            is_active=True,
            is_public=True,
        )

        self.list_item = FacilityListItem.objects.create(
            name="Facility Name",
            address="Facility Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )

        self.facility = Facility.objects.create(
            name="Facility Name",
            address="Facility Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item,
        )
        self.list_item.facility = self.facility
        self.list_item.save()

        FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results="",
            facility_list_item=self.list_item,
        )

        self.extended_field = ExtendedField.objects.create(
            field_name=ExtendedField.NUMBER_OF_WORKERS,
            value={"min": 10, "max": 20},
            contributor=self.original_contributor,
            facility=self.facility,
            facility_list_item=self.list_item,
        )

    def test_reassigning_source_updates_extended_field_attribution(self):
        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        initial_entry = [
            ef
            for ef in facility_index.extended_fields
            if ef["id"] == self.extended_field.id
        ][0]
        self.assertEqual(
            initial_entry["contributor"]["id"],
            self.original_contributor.id,
        )

        self.source.contributor = self.new_contributor
        self.source.save()

        self.extended_field.refresh_from_db()
        self.assertEqual(
            self.extended_field.contributor_id,
            self.new_contributor.id,
        )

        facility_index.refresh_from_db()
        updated_entry = [
            ef
            for ef in facility_index.extended_fields
            if ef["id"] == self.extended_field.id
        ][0]
        self.assertEqual(
            updated_entry["contributor"]["id"],
            self.new_contributor.id,
        )

        serializer_data = FacilityIndexDetailsSerializer(
            facility_index
        ).data
        serialized_fields = serializer_data["properties"]["extended_fields"][
            ExtendedField.NUMBER_OF_WORKERS
        ]
        serialized_entry = [
            ef for ef in serialized_fields if ef["id"] == self.extended_field.id
        ][0]
        self.assertEqual(
            serialized_entry["contributor_id"],
            self.new_contributor.id,
        )

