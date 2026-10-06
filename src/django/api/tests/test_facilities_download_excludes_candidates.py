from django.contrib.gis.geos import Point
from django.http import QueryDict
from rest_framework import status

from api.models import Facility, FacilityListItem
from api.models.facility.facility_index import FacilityIndex
from api.services.facilities_download_service import (
    FacilitiesDownloadService,
)
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


class FacilitiesDownloadExcludesCandidatesTest(FacilityAPITestCaseBase):
    """
    FacilityIndex-backed surfaces must not expose candidate rows.

    ``/api/facilities-downloads/`` and ``/api/facilities/`` serialize
    ``FacilityIndex``, not ``Facility``, so the ``Facility.objects``
    default manager (OSDEV-3380) does not protect them. The index trigger
    is being taught to skip candidates separately (OSDEV-3243); these
    tests force a candidate row into ``api_facilityindex`` so they hold
    whether or not that trigger change is present.
    """

    fixtures = ["sectors"]

    def setUp(self):
        super().setUp()
        self.download_url = "/api/facilities-downloads/"
        self.facilities_url = "/api/facilities/"

        candidate_item = FacilityListItem.objects.create(
            name="",
            address="",
            country_code="US",
            sector=["Agriculture"],
            row_index=2,
            geocoded_point=Point(1, 1),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )
        self.candidate = Facility.objects.create(
            name="Candidate poultry house",
            address="Unnamed road",
            country_code="US",
            location=Point(1, 1),
            created_from=candidate_item,
            is_candidate=True,
            source="earth_genome",
            external_id="eg-download-0001",
        )
        self.candidate_index = self._force_index_row(self.candidate)

        self.client.login(
            email=self.user_email, password=self.user_password
        )

    def _force_index_row(self, facility):
        """
        Make sure a FacilityIndex row exists for ``facility``.

        Today the index trigger writes one on insert; once OSDEV-3243
        lands it will not. Either way the test needs the row present.
        """
        row, _ = FacilityIndex.objects.get_or_create(
            id=facility.id,
            defaults={
                "name": facility.name,
                "address": facility.address,
                "country_code": facility.country_code,
                "location": facility.location,
                "contributors_count": 1,
                "contributors_id": [self.contributor.id],
                "contributors": [
                    {"id": self.contributor.id, "name": self.contributor.name}
                ],
                "contrib_types": [self.contributor.contrib_type],
                "facility_addresses": [{"address": facility.address}],
                "extended_fields": [],
                "lists": [],
                "approved_claim_ids": [],
                "facility_names": [],
                "sector": ["Agriculture"],
            },
        )
        return row

    def _os_ids_in_download(self, response):
        results = response.data["results"]
        os_id_column = results["headers"].index("os_id")
        return [row[os_id_column] for row in results["rows"]]

    def test_candidate_row_is_in_the_index(self):
        """Precondition: the row the surfaces must hide really exists."""
        self.assertTrue(
            FacilityIndex.objects.filter(id=self.candidate.id).exists()
        )
        self.assertFalse(
            Facility.objects.filter(id=self.candidate.id).exists()
        )

    def test_download_omits_candidate(self):
        response = self.client.get(self.download_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        os_ids = self._os_ids_in_download(response)
        self.assertIn(self.facility.id, os_ids)
        self.assertNotIn(self.candidate.id, os_ids)
        self.assertEqual(response.data["count"], 1)

    def test_download_by_candidate_os_id_returns_nothing(self):
        """A direct OS ID lookup must not leak the candidate either."""
        response = self.client.get(
            self.download_url, {"q": self.candidate.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._os_ids_in_download(response), [])
        self.assertEqual(response.data["count"], 0)

    def test_download_service_queryset_excludes_candidate(self):
        class Request:
            query_params = QueryDict("")

        queryset = FacilitiesDownloadService.get_filtered_queryset(Request())

        self.assertEqual(
            list(queryset.values_list("id", flat=True)), [self.facility.id]
        )

    def test_without_candidates_manager_method(self):
        ids = set(
            FacilityIndex.objects.without_candidates().values_list(
                "id", flat=True
            )
        )

        self.assertIn(self.facility.id, ids)
        self.assertNotIn(self.candidate.id, ids)
        # Plain FacilityIndex.objects is left alone on purpose, so the
        # details view can still resolve a candidate (OSDEV-3249).
        self.assertTrue(
            FacilityIndex.objects.filter(id=self.candidate.id).exists()
        )

    def test_facilities_list_omits_candidate(self):
        """/api/facilities/ shares filter_by_query_params with downloads."""
        response = self.client.get(self.facilities_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [f["id"] for f in response.data["features"]]
        self.assertIn(self.facility.id, ids)
        self.assertNotIn(self.candidate.id, ids)

    def test_facilities_list_by_candidate_os_id_returns_nothing(self):
        response = self.client.get(
            self.facilities_url, {"q": self.candidate.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["features"], [])
