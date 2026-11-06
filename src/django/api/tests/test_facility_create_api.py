from api.models import (
    Contributor,
    Facility,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.processing import handle_external_match_process_result

from rest_framework.test import APITestCase
from django.contrib.gis.geos import Point


class FacilityCreateAPITest(APITestCase):
    def setUp(self):
        self.user_email = "test@example.com"
        self.user_password = "example123"
        self.user = User.objects.create(email=self.user_email)
        self.user.set_password(self.user_password)
        self.user.save()

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.source_one = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item_one = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.MATCHED,
            source=self.source_one,
        )

        self.facility_one = Facility.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_one,
        )

        self.source_two = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item_two = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.MATCHED,
            source=self.source_two,
            facility=self.facility_one,
        )

        self.match_two = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility_one,
            facility_list_item=self.list_item_two,
            confidence=0.85,
            results="",
        )

        self.source_three = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item_three = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.POTENTIAL_MATCH,
            source=self.source_three,
        )

        self.match_three = FacilityMatch.objects.create(
            status=FacilityMatch.PENDING,
            facility=self.facility_one,
            facility_list_item=self.list_item_three,
            confidence=0.75,
            results="",
        )

        self.source_four = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item_four = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.MATCHED,
            source=self.source_four,
        )

        self.match_four = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility_one,
            facility_list_item=self.list_item_four,
            confidence=1,
            results="",
        )

    def test_handle_match_process_result(self):
        result_obj_two = {
            'matches': [],
            'item_id': self.list_item_two.id,
            'geocoded_geometry': None,
            'geocoded_address': None,
            'status': self.list_item_two.status,
        }

        result_two = handle_external_match_process_result(
            self.list_item_two.id, result_obj_two, None, True
        )
        self.assertEqual(result_two['status'], 'MATCHED')

        result_obj_three = {
            'matches': [],
            'item_id': self.list_item_three.id,
            'geocoded_geometry': None,
            'geocoded_address': None,
            'status': self.list_item_three.status,
        }

        result_three = handle_external_match_process_result(
            self.list_item_three.id, result_obj_three, None, True
        )
        self.assertEqual(result_three['status'], 'POTENTIAL_MATCH')
        self.assertIsNotNone(
            result_three['matches'][0]['confirm_match_url']
        )
        self.assertIsNotNone(
            result_three['matches'][0]['reject_match_url']
        )

        result_obj_four = {
            'matches': [],
            'item_id': self.list_item_four.id,
            'geocoded_geometry': None,
            'geocoded_address': None,
            'status': self.list_item_four.status,
        }

        result_four = handle_external_match_process_result(
            self.list_item_four.id, result_obj_four, None, True
        )
        self.assertEqual(result_four['status'], 'NEW_FACILITY')

    def test_duplicate_automatic_matches_return_the_item_facility(self):
        """
        Only one automatic match is ever written per item. If an item has
        been matched twice, the answer uses the automatic match the item
        points at.
        """
        other_item = FacilityListItem.objects.create(
            name="Other",
            address="Other Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(1, 1),
            status=FacilityListItem.MATCHED,
            source=self.source_one,
        )
        facility_two = Facility.objects.create(
            name="Other",
            address="Other Address",
            country_code="US",
            location=Point(1, 1),
            created_from=other_item,
        )
        source_five = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        list_item_five = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.MATCHED,
            source=source_five,
            facility=self.facility_one,
        )
        for facility, status, confidence in (
            (facility_two, FacilityMatch.PENDING, 0.54),
            (facility_two, FacilityMatch.AUTOMATIC, 0.9),
            (self.facility_one, FacilityMatch.AUTOMATIC, 0.89),
        ):
            FacilityMatch.objects.create(
                status=status,
                facility=facility,
                facility_list_item=list_item_five,
                confidence=confidence,
                results="",
            )

        result = handle_external_match_process_result(
            list_item_five.id,
            {
                'matches': [],
                'item_id': list_item_five.id,
                'geocoded_geometry': None,
                'geocoded_address': None,
                'status': list_item_five.status,
            },
            None,
            True,
        )

        self.assertEqual(result['status'], 'MATCHED')
        self.assertEqual(len(result['matches']), 1)
