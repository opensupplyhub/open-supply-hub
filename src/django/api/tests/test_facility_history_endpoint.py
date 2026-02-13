import json

from django.db.models.signals import post_delete
from django.contrib import auth
from django.contrib.auth.models import Group
from django.contrib.gis.geos import Point
from django.urls import reverse
from waffle.testutils import override_flag, override_switch

from api.constants import (
    FeatureGroups,
    MatchResponsibility,
    UpdateLocationParams,
)
from api.models import (
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
)
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase
from api.signals import location_post_delete_handler_for_opensearch


class FacilityHistoryEndpointTest(FacilityAPITestCaseBase):
    def setUp(self):
        # Disconnect location deletion propagation to OpenSearch cluster, as
        # it is outside the scope of Django unit testing.
        post_delete.disconnect(
            location_post_delete_handler_for_opensearch,
            Facility
        )

        super(FacilityHistoryEndpointTest, self).setUp()
        self.history_url = "/api/facilities/{}/history/".format(
            self.facility.id
        )

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        self.list_two = FacilityList.objects.create(
            header="header",
            file_name="two",
            name="Second List",
            match_responsibility=MatchResponsibility.CONTRIBUTOR,
        )

        self.source_two = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.list_two,
            contributor=self.contributor,
        )

        self.list_item_two = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_two,
        )

        self.facility_two = Facility.objects.create(
            name="Name Two",
            address="Address Two",
            country_code="US",
            location=Point(5, 5),
            created_from=self.list_item_two,
        )

        self.match_two = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility_two,
            facility_list_item=self.list_item_two,
            confidence=0.85,
            results="",
        )

        self.list_item_two.facility = self.facility_two
        self.list_item_two.save()

        self.list_for_confirm_or_remove = FacilityList.objects.create(
            header="List for confirm or reject",
            file_name="list for confirm or reject",
            name="List for confirm or reject",
            match_responsibility=MatchResponsibility.CONTRIBUTOR,
        )

        self.source_for_confirm_or_remove = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.list_for_confirm_or_remove,
            contributor=self.contributor,
        )

        self.list_item_for_confirm_or_remove = FacilityListItem.objects.create(
            name="List item for confirmed match",
            address="Address for confirmed match",
            country_code="US",
            sector=["Apparel"],
            row_index=2,
            geocoded_point=Point(12, 34),
            status=FacilityListItem.POTENTIAL_MATCH,
            source=self.source_for_confirm_or_remove,
        )

        self.match_for_confirm_or_remove = FacilityMatch.objects.create(
            status=FacilityMatch.PENDING,
            facility_list_item=self.list_item_for_confirm_or_remove,
            facility=self.facility_two,
            confidence=0.65,
            results="",
        )

        self.facility_two_history_url = "/api/facilities/{}/history/".format(
            self.facility_two.id
        )

    def filter_out_manual_updated_at_action(self, data):
        # Filter out action where we manually trigger
        # 'updated_at' field in 'api_facility' table
        # by using update_facility_updated_at_field method
        return [
            item for item in data
            if not (item.get("action") == "OTHER"
                    and item.get("changes") == {})
        ]

    @override_flag(FeatureGroups.CAN_GET_FACILITY_HISTORY, active=True)
    def test_serializes_deleted_facility_history(self):
        delete_facility_url = "/api/facilities/{}/".format(self.facility.id)
        delete_response = self.client.delete(delete_facility_url)

        self.assertEqual(
            delete_response.status_code,
            204,
        )

        response = self.client.get(self.history_url)
        data = json.loads(response.content)

        self.assertEqual(
            data[0]["action"],
            "DELETE",
        )

        self.assertIn(
            "Deleted",
            data[0]["detail"],
        )

        self.assertEqual(
            len(data),
            4,
        )

    @override_flag("can_get_facility_history", active=True)
    def test_serializes_facility_location_change(self):
        location_change_url = "/api/facilities/{}/update-location/".format(
            self.facility.id
        )
        location_change_response = self.client.post(
            location_change_url,
            {
                UpdateLocationParams.LAT: 41,
                UpdateLocationParams.LNG: 43,
            },
        )

        self.assertEqual(location_change_response.status_code, 200)

        response = self.client.get(self.history_url)
        data = json.loads(response.content)

        self.assertEqual(
            data[0]["action"],
            "UPDATE",
        )

        self.assertIn(
            "FacilityLocation",
            data[0]["detail"],
        )

        self.assertEqual(
            data[0]["changes"]["location"]["new"]["coordinates"][0],
            43,
        )

        self.assertEqual(
            data[0]["changes"]["location"]["old"]["coordinates"][0],
            0,
        )

        self.assertEqual(
            len(data),
            3,
        )

    @override_flag("can_get_facility_history", active=True)
    def test_serializes_facility_merge(self):
        merge_facilities_url = (
            "/api/facilities/merge/?target={}&merge={}".format(
                self.facility_two.id, self.facility.id
            )
        )

        merge_facilities_response = self.client.post(
            merge_facilities_url,
        )

        self.assertEqual(merge_facilities_response.status_code, 200)

        response = self.client.get(self.history_url)
        data = json.loads(response.content)

        self.assertEqual(
            data[0]["action"],
            "MERGE",
        )

        self.assertEqual(
            data[0]["detail"], "Merged with {}".format(self.facility_two.id)
        )

        self.assertEqual(
            len(data),
            3,
        )

    @override_flag("can_get_facility_history", active=True)
    def test_serializes_facility_match_promotion(self):
        merge_facilities_url = (
            "/api/facilities/merge/?target={}&merge={}".format(
                self.facility_two.id, self.facility.id
            )
        )

        merge_facilities_response = self.client.post(
            merge_facilities_url,
        )

        self.assertEqual(merge_facilities_response.status_code, 200)

        self.facility_two.refresh_from_db()

        promote_facility_url = "/api/facilities/{}/promote/".format(
            self.facility_two.id
        )

        promote_facility_data = {
            "match_id": self.match.id,
        }

        promote_facility_response = self.client.post(
            promote_facility_url,
            promote_facility_data,
        )

        self.assertEqual(promote_facility_response.status_code, 200)

        response = self.client.get(self.facility_two_history_url)
        data = json.loads(response.content)

        self.assertEqual(
            data[0]["action"],
            "UPDATE",
        )

        self.assertIn(
            "Promoted",
            data[0]["detail"],
        )

        self.assertEqual(
            data[0]["changes"]["location"]["new"]["coordinates"][0],
            0,
        )

        self.assertEqual(
            data[0]["changes"]["location"]["old"]["coordinates"][0],
            5,
        )

        self.assertEqual(
            data[0]["changes"]["name"]["new"],
            self.list_item.name,
        )

        self.assertEqual(
            data[0]["changes"]["name"]["old"],
            "Name Two",
        )

        self.assertEqual(
            data[0]["changes"]["address"]["new"],
            self.list_item.address,
        )

        self.assertEqual(
            data[0]["changes"]["address"]["old"],
            "Address Two",
        )

        self.assertEqual(
            len(data),
            5,
        )

    @override_flag("can_get_facility_history", active=True)
    def test_serializes_facility_match_split(self):
        merge_facilities_url = (
            "/api/facilities/merge/?target={}&merge={}".format(
                self.facility_two.id, self.facility.id
            )
        )

        merge_facilities_response = self.client.post(
            merge_facilities_url,
        )

        self.assertEqual(merge_facilities_response.status_code, 200)

        self.facility_two.refresh_from_db()

        split_facility_url = "/api/facilities/{}/split/".format(
            self.facility_two.id
        )

        split_facility_data = {
            "match_id": self.match.id,
        }

        split_facility_response = self.client.post(
            split_facility_url,
            split_facility_data,
        )

        self.assertEqual(split_facility_response.status_code, 200)

        self.match.refresh_from_db()

        response = self.client.get(self.facility_two_history_url)
        data = json.loads(response.content)

        self.assertEqual(
            data[1]["action"],
            "SPLIT",
        )

        self.assertEqual(
            data[1]["detail"],
            "{} was split from {}".format(
                self.match.facility.id,
                self.facility_two.id,
            ),
        )

        self.assertEqual(
            len(data),
            6,
        )

    @override_flag("can_get_facility_history", active=True)
    def test_serializes_facility_match_move(self):
        move_facility_url = "/api/facilities/{}/move/".format(self.facility.id)

        move_facility_data = {
            "match_id": self.match_two.id,
        }

        move_facility_response = self.client.post(
            move_facility_url,
            move_facility_data,
        )

        self.assertEqual(move_facility_response.status_code, 200)

        self.match_two.refresh_from_db()

        response = self.client.get(self.facility_two_history_url)
        data = json.loads(response.content)

        self.assertEqual(
            data[1]["action"],
            "MOVE",
        )

        self.assertEqual(
            data[1]["detail"],
            "Match {} was moved from {}".format(
                self.match_two.id,
                self.facility_two.id,
            ),
        )

        self.assertEqual(
            len(data),
            4,
        )

    @override_flag("can_get_facility_history", active=True)
    def test_handles_request_for_invalid_facility_id(self):
        invalid_history_url = "/api/facilities/hello/history/"
        invalid_history_response = self.client.get(invalid_history_url)
        self.assertEqual(invalid_history_response.status_code, 404)

    @override_flag("can_get_facility_history", active=True)
    def test_includes_association_for_automatic_match(self):
        automatic_match_response = self.client.get(
            self.facility_two_history_url,
        )

        data = json.loads(automatic_match_response.content)

        self.assertEqual(
            data[0]["action"],
            "ASSOCIATE",
        )

        self.assertEqual(
            data[0]["detail"],
            "Associate facility {} with {} via list {}".format(
                self.facility_two.id,
                self.contributor.name,
                self.list_two.name,
            ),
        )

        self.assertEqual(
            len(data),
            2,
        )

        self.superuser.groups.add(
            Group.objects.get(name=FeatureGroups.CAN_SUBMIT_PRIVATE_FACILITY)
        )
        self.superuser.save()

        automatic_match_response = self.client.get(
            self.facility_two_history_url,
        )

        data = json.loads(automatic_match_response.content)

        self.assertEqual(
            data[0]["detail"],
            "Associate facility {} with an Other".format(
                self.facility_two.id,
            ),
        )

    @override_flag("can_get_facility_history", active=True)
    def test_associate_appears_after_create_in_history_data(self):
        history_response = self.client.get(
            self.history_url,
        )

        self.assertEqual(
            history_response.status_code,
            200,
        )

        data = json.loads(history_response.content)

        self.assertEqual(
            data[0]["action"],
            "ASSOCIATE",
        )

        self.assertEqual(
            data[1]["action"],
            "CREATE",
        )

        self.assertEqual(
            len(data),
            2,
        )

    @override_flag("can_get_facility_history", active=True)
    def test_includes_association_for_confirmed_match(self):
        self.client.logout()
        self.client.login(email=self.user_email, password=self.user_password)

        confirm_url = "/api/facility-matches/{}/confirm/".format(
            self.match_for_confirm_or_remove.id,
        )

        confirm_response = self.client.post(confirm_url)

        self.assertEqual(
            confirm_response.status_code,
            200,
        )

        confirmed_match_response = self.client.get(
            self.facility_two_history_url,
        )

        data = json.loads(confirmed_match_response.content)

        filtered_data = self.filter_out_manual_updated_at_action(data)

        self.assertEqual(
            filtered_data[0]["action"],
            "ASSOCIATE",
        )

        self.assertEqual(
            filtered_data[0]["detail"],
            "Associate facility {} with {} via list {}".format(
                self.facility_two.id,
                self.contributor.name,
                self.list_for_confirm_or_remove.name,
            ),
        )

        self.assertEqual(
            len(filtered_data),
            3,
        )

        self.user.groups.add(
            Group.objects.get(name=FeatureGroups.CAN_SUBMIT_PRIVATE_FACILITY)
        )
        self.user.save()

        confirmed_match_response = self.client.get(
            self.facility_two_history_url,
        )

        data = json.loads(confirmed_match_response.content)

        filtered_data = self.filter_out_manual_updated_at_action(data)

        self.assertEqual(
            filtered_data[0]["detail"],
            "Associate facility {} with an Other".format(
                self.facility_two.id,
            ),
        )

    @override_flag("can_get_facility_history", active=True)
    def test_includes_dissociation_record_when_match_is_severed(self):
        self.client.logout()
        self.client.login(email=self.user_email, password=self.user_password)

        confirm_url = "/api/facility-matches/{}/confirm/".format(
            self.match_for_confirm_or_remove.id,
        )

        confirm_response = self.client.post(confirm_url)

        self.assertEqual(
            confirm_response.status_code,
            200,
        )

        remove_item_url = "/api/facility-lists/{}/remove/".format(
            self.list_for_confirm_or_remove.id,
        )

        remove_item_data = {
            "list_item_id": self.list_item_for_confirm_or_remove.id,
        }

        remove_item_response = self.client.post(
            remove_item_url,
            remove_item_data,
        )

        self.assertEqual(
            remove_item_response.status_code,
            200,
        )

        removed_match_response = self.client.get(
            self.facility_two_history_url,
        )

        data = json.loads(removed_match_response.content)

        filtered_data = self.filter_out_manual_updated_at_action(data)

        self.assertEqual(
            filtered_data[0]["action"],
            "DISSOCIATE",
        )

        self.assertEqual(
            filtered_data[0]["detail"],
            "Dissociate facility {} from {} via list {}".format(
                self.facility_two.id,
                self.contributor.name,
                self.list_for_confirm_or_remove.name,
            ),
        )

        self.assertEqual(
            len(filtered_data),
            4,
        )

        self.user.groups.add(
            Group.objects.get(name=FeatureGroups.CAN_SUBMIT_PRIVATE_FACILITY)
        )
        self.user.save()

        confirmed_match_response = self.client.get(
            self.facility_two_history_url,
        )

        data = json.loads(confirmed_match_response.content)

        filtered_data = self.filter_out_manual_updated_at_action(data)

        self.assertEqual(
            filtered_data[0]["detail"],
            "Dissociate facility {} from an Other".format(
                self.facility_two.id,
            ),
        )

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @override_flag('can_get_facility_history', active=True)
    # def test_includes_dissociation_record_when_item_removed(self):
    #     self.client.logout()
    #     self.client.login(email=self.user_email,
    #                       password=self.user_password)

    #     confirm_url = '/api/facility-matches/{}/confirm/'.format(
    #         self.match_for_confirm_or_remove.id,
    #     )

    #     confirm_response = self.client.post(confirm_url)

    #     self.assertEqual(
    #         confirm_response.status_code,
    #         200,
    #     )

    #     # Upload replacement
    #     csv_file = SimpleUploadedFile(
    #         "facilities.csv", b"country,name,address,sector\n",
    #         content_type="text/csv"
    #     )
    #     replace_response = self.client.post(
    #         reverse('facility-list-list'),
    #         {'file': csv_file,
    #          'replaces': self.list_for_confirm_or_remove.id},
    #         format='multipart')
    #     self.assertEqual(replace_response.status_code, status.HTTP_200_OK)
    #     response_json = json.loads(replace_response.content)
    #     new_list_id = response_json['id']
    #     call_command('batch_process',
    #                  *['--list-id', new_list_id, '--action', 'parse'])
    #     call_command('batch_process',
    #                  *['--list-id', new_list_id, '--action', 'geocode'])
    #     call_command('batch_process',
    #                  *['--list-id', new_list_id, '--action', 'match'])

    #     removed_match_response = self.client.get(
    #         self.facility_two_history_url,
    #     )

    #     data = json.loads(removed_match_response.content)

    #     self.assertEqual(
    #         data[0]['action'],
    #         'DISSOCIATE',
    #     )

    #     self.assertEqual(
    #         data[0]['detail'],
    #         'Dissociate facility {} from {} via list {}'.format(
    #             self.facility_two.id,
    #             self.contributor.name,
    #             self.list_for_confirm_or_remove.name,
    #         ),
    #     )

    @override_flag("can_get_facility_history", active=True)
    def test_includes_dissociation_record_when_dissociate_api_is_called(self):
        self.client.logout()
        self.client.login(email=self.user_email, password=self.user_password)

        confirm_url = "/api/facility-matches/{}/confirm/".format(
            self.match_for_confirm_or_remove.id,
        )

        confirm_response = self.client.post(confirm_url)
        self.assertEqual(
            confirm_response.status_code,
            200,
        )

        dissociate_url = reverse(
            "facility-dissociate", kwargs={"pk": self.facility_two.pk}
        )
        dissociate_response = self.client.post(dissociate_url)
        self.assertEqual(
            dissociate_response.status_code,
            200,
        )

        history_url = reverse(
            "facility-get-facility-history",
            kwargs={"pk": self.facility_two.pk},
        )
        history_response = self.client.get(history_url)
        self.assertEqual(
            history_response.status_code,
            200,
        )
        data = json.loads(history_response.content)
        filtered_data = self.filter_out_manual_updated_at_action(data)
        expected_detail = "Dissociate facility {} from {} via list {}".format(
            self.facility_two.id,
            self.contributor.name,
            self.list_for_confirm_or_remove.name,
        )
        dissociation_entries = [
            entry for entry in filtered_data
            if entry["action"] == "DISSOCIATE"
            and entry["detail"] == expected_detail
        ]

        self.assertEqual(len(dissociation_entries), 1)
        self.assertEqual(
            dissociation_entries[0]["action"],
            "DISSOCIATE",
        )
        self.assertEqual(
            dissociation_entries[0]["detail"],
            expected_detail,
        )

    @override_flag("can_get_facility_history", active=True)
    @override_switch("claim_a_facility", active=True)
    def test_includes_entry_for_claim_approval(self):
        self.client.logout()
        self.client.login(email=self.user_email, password=self.user_password)

        claim_facility_url = "/api/facilities/{}/claim/".format(
            self.facility_two.id,
        )

        claim_facility_data = {
            "your_name": "your_name",
            "your_title": "your_title",
            "your_business_website": "https://example.com",
            "business_website": "https://example.com",
            "business_linkedin_profile": "https://example.com",
        }

        claim_response = self.client.post(
            claim_facility_url,
            claim_facility_data,
        )

        self.assertEqual(
            claim_response.status_code,
            200,
        )

        self.client.logout()
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        claim = FacilityClaim.objects.first()

        approve_claim_url = "/api/facility-claims/{}/approve/".format(
            claim.id,
        )

        approve_claim_response = self.client.post(
            approve_claim_url,
            {"reason": "reason"},
        )

        self.assertEqual(
            approve_claim_response.status_code,
            200,
        )

        history_response = self.client.get(self.facility_two_history_url)

        self.assertEqual(history_response.status_code, 200)

        data = json.loads(history_response.content)

        self.assertEqual(
            data[1]["action"],
            "CLAIM",
        )

        self.assertEqual(
            len(data),
            5,
        )

    @override_flag("can_get_facility_history", active=True)
    @override_switch("claim_a_facility", active=True)
    def test_handles_deleted_facility(self):
        self.client.logout()
        self.client.login(email=self.user_email, password=self.user_password)

        claim_facility_url = "/api/facilities/{}/claim/".format(
            self.facility_two.id,
        )

        claim_facility_data = {
            "your_name": "your_name",
            "your_title": "your_title",
            "your_business_website": "https://example.com",
            "business_website": "https://example.com",
            "business_linkedin_profile": "https://example.com",
        }

        claim_response = self.client.post(
            claim_facility_url,
            claim_facility_data,
        )

        self.assertEqual(
            claim_response.status_code,
            200,
        )

        self.client.logout()
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        claim = FacilityClaim.objects.first()

        approve_claim_url = "/api/facility-claims/{}/approve/".format(
            claim.id,
        )

        approve_claim_response = self.client.post(
            approve_claim_url,
            {"reason": "reason"},
        )

        self.assertEqual(
            approve_claim_response.status_code,
            200,
        )

        list = FacilityList.objects.create(
            header="header", file_name="one", name="List"
        )

        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=list,
            contributor=self.contributor,
        )

        list_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )

        facility = Facility.objects.create(
            name="Name Two",
            address="Address Two",
            country_code="US",
            location=Point(5, 5),
            created_from=list_item,
        )

        FacilityClaim.history.update(facility=facility)
        facility.delete()

        history_response = self.client.get(self.facility_two_history_url)

        self.assertEqual(history_response.status_code, 200)

        data = json.loads(history_response.content)

        self.assertEqual(
            data[2]["action"],
            "ASSOCIATE",
        )

        self.assertEqual(
            len(data),
            4,
        )

    @override_flag("can_get_facility_history", active=True)
    @override_switch("claim_a_facility", active=True)
    def test_includes_entry_for_claim_revocation(self):
        self.client.logout()
        self.client.login(email=self.user_email, password=self.user_password)

        claim_facility_url = "/api/facilities/{}/claim/".format(
            self.facility_two.id,
        )

        claim_facility_data = {
            "your_name": "your_name",
            "your_title": "your_title",
            "your_business_website": "https://example.com",
            "business_website": "https://example.com",
            "business_linkedin_profile": "https://example.com",
        }

        claim_response = self.client.post(
            claim_facility_url,
            claim_facility_data,
        )

        self.assertEqual(
            claim_response.status_code,
            200,
        )

        self.client.logout()
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        claim = FacilityClaim.objects.first()

        approve_claim_url = "/api/facility-claims/{}/approve/".format(
            claim.id,
        )

        approve_claim_response = self.client.post(
            approve_claim_url,
            {"reason": "reason"},
        )

        self.assertEqual(
            approve_claim_response.status_code,
            200,
        )

        revoke_claim_url = "/api/facility-claims/{}/revoke/".format(
            claim.id,
        )

        revoke_claim_response = self.client.post(
            revoke_claim_url,
            {"reason": "reason"},
        )

        self.assertEqual(
            revoke_claim_response.status_code,
            200,
        )

        history_response = self.client.get(self.facility_two_history_url)

        self.assertEqual(history_response.status_code, 200)

        data = json.loads(history_response.content)

        self.assertEqual(
            data[1]["action"],
            "CLAIM_REVOKE",
        )

        self.assertEqual(
            len(data),
            7,
        )

    @override_flag("can_get_facility_history", active=True)
    @override_switch("claim_a_facility", active=True)
    def test_includes_entry_for_public_claimed_facility_data_changes(self):
        self.client.logout()
        self.client.login(email=self.user_email, password=self.user_password)

        claim_facility_url = "/api/facilities/{}/claim/".format(
            self.facility_two.id,
        )

        claim_facility_data = {
            "your_name": "your_name",
            "your_title": "your_title",
            "your_business_website": "https://example.com",
            "business_website": "https://example.com",
            "business_linkedin_profile": "https://example.com",
        }

        claim_response = self.client.post(
            claim_facility_url,
            claim_facility_data,
        )

        self.assertEqual(
            claim_response.status_code,
            200,
        )

        self.client.logout()
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        claim = FacilityClaim.objects.first()

        approve_claim_url = "/api/facility-claims/{}/approve/".format(
            claim.id,
        )

        approve_claim_response = self.client.post(
            approve_claim_url,
            {"reason": "reason"},
        )

        self.assertEqual(
            approve_claim_response.status_code,
            200,
        )

        self.client.logout()
        self.client.login(email=self.user_email, password=self.user_password)

        update_claim_url = "/api/facility-claims/{}/claimed/".format(
            claim.id,
        )

        update_claim_data = {
            "id": claim.id,
            "facility_name_english": "facility_name_english",
            "facility_name_native_language": "facility_name_native_language",
            "facility_address": "facility_address",
            "facility_description": "facility_description",
            "facility_phone_number": 1234567,
            "facility_phone_number_publicly_visible": True,
            "facility_website": "https://opensupplyhub.org",
            "facility_website_publicly_visible": True,
            "facility_minimum_order_quantity": 10,
            "facility_average_lead_time": "2 months",
            "point_of_contact_person_name": "point_of_contact_person_name",
            "point_of_contact_email": "point_of_contact_email",
            "facility_workers_count": 20,
            "facility_female_workers_percentage": 50,
            "point_of_contact_publicly_visible": True,
            "office_official_name": "office_official_name",
            "office_address": "office_address",
            "office_country_code": "US",
            "office_phone_number": 2345678,
            "office_info_publicly_visible": True,
            "facility_type": "Cut and Sew / RMG",
        }

        update_claim_response = self.client.put(
            update_claim_url,
            update_claim_data,
        )

        self.assertEqual(
            update_claim_response.status_code,
            200,
        )

        history_response = self.client.get(self.facility_two_history_url)

        self.assertEqual(history_response.status_code, 200)

        data = json.loads(history_response.content)

        self.assertEqual(
            data[1]["action"],
            "CLAIM_UPDATE",
        )

        self.assertEqual(
            len(data),
            7,
        )

        non_public_keys = [
            "facility_website",
            "facility_website_publicly_visible",
            "point_of_contact_publicly_visible",
            "point_of_contact_person_name",
            "point_of_contact_email",
            "office_info_publicly_visible",
            "office_official_name",
            "office_country_code",
            "office_address",
            "office_phone_number",
        ]

        for non_public_key in non_public_keys:
            self.assertNotIn(
                non_public_key,
                data[0]["changes"],
            )

    def test_unauthenticated_receives_401(self):
        self.client.logout()
        history_response = self.client.get(self.history_url)

        self.assertEqual(
            history_response.status_code,
            401,
        )

    def test_superuser_can_access_endpoint(self):
        # superuser is already signed in via `setUp`
        history_response = self.client.get(self.history_url)

        self.assertEqual(
            history_response.status_code,
            200,
        )

    def test_not_in_group_receives_403(self):
        self.client.logout()
        self.client.login(email=self.user_email, password=self.user_password)

        history_response = self.client.get(self.history_url)

        self.assertEqual(
            history_response.status_code,
            403,
        )

    def test_in_group_receives_200(self):
        self.client.logout()

        history_group = auth.models.Group.objects.get(
            name="can_get_facility_history",
        )

        self.user.groups.set([history_group.id])
        self.user.save()

        self.client.login(email=self.user_email, password=self.user_password)

        history_response = self.client.get(self.history_url)

        self.assertEqual(
            history_response.status_code,
            200,
        )

    def test_describe_change_value(self, **kwargs):
        with self.assertRaises(TypeError):
            json.loads(['Socks'])
