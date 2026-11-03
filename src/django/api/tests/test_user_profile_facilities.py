from django.contrib.gis.geos import Point
from django.core.cache import caches
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from waffle.testutils import override_switch

from api.models import Contributor, Polygon, User, ZoneSet
from api.models.extended_field import ExtendedField
from api.models.facility.facility_index import FacilityIndex
from api.models.partner_field import PartnerField
from api.partner_fields.india_labour_line_provider import (
    IndiaLabourLineProvider,
)
from api.partner_fields.registry import ZONE_SETS_SWITCH
from api.tests.test_partner_contributor_filter_zone_sets import make_facility
from api.tests.test_zone_set_provider import EAST, WEST, feature, zone_records


class TestUserProfileFacilities(APITestCase):
    def setUp(self):
        caches["view_cache"].clear()
        self.user_email = "test@example.com"
        self.other_user_email = "other@example.com"
        self.no_contrib_user_email = "no-contrib@example.com"

        self.user = User.objects.create(email=self.user_email)
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="Test Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.facility = FacilityIndex.objects.create(
            id="US2021250D1DTN7",
            name="Test Facility",
            address="123 Main St",
            country_code="US",
            location=Point(0, 0),
            contributors_count=1,
            contributors_id=[self.contributor.id],
            contributors=[{"id": self.contributor.id, "name": "Test"}],
            contrib_types=[Contributor.OTHER_CONTRIB_TYPE],
            facility_addresses=[{"address": "123 Main St"}],
            extended_fields=[],
            lists=[],
            approved_claim_ids=[],
            facility_names=[],
        )

    def _url(self, pk):
        return f"/user-profile/{pk}/facilities/"

    def test_returns_404_for_nonexistent_user(self):
        response = self.client.get(self._url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_404_for_user_without_contributor(self):
        user_no_contrib = User.objects.create(email=self.no_contrib_user_email)
        response = self.client.get(self._url(user_no_contrib.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_facilities_for_valid_user(self):
        response = self.client.get(self._url(self.user.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        features = response.data["results"]["features"]
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]["id"], self.facility.id)

    def test_returns_empty_for_user_with_no_facilities(self):
        other_user = User.objects.create(email=self.other_user_email)
        Contributor.objects.create(
            admin=other_user,
            name="Other Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        response = self.client.get(self._url(other_user.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]["features"]), 0)


class TestIndiaLabourLineSpotlight(APITestCase):
    """Tests for the polygon-driven India Labour Line spotlight."""

    def setUp(self):
        """Create the partner, its boundary, and in/out facilities."""
        caches["view_cache"].clear()
        self.user = User.objects.create(email="india-partner@example.com")
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="India Labour Line",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.coverage_polygon = Polygon.objects.create(
            name="helpline_coverage_for_tests",
            description="Helpline coverage boundary for tests.",
            geom=MultiPolygon(GEOSGeometry(
                "POLYGON((76.8 28.4, 76.8 28.9, 77.4 28.9, "
                "77.4 28.4, 76.8 28.4))"
            )),
        )
        self.partner_field, _ = PartnerField.objects \
            .get_all_including_inactive() \
            .get_or_create(
                name=IndiaLabourLineProvider.FIELD_NAME,
                defaults={
                    "type": PartnerField.OBJECT,
                    "label": "India Labour Line Helpline",
                    "system_field": True,
                    "active": True,
                },
            )
        self.partner_field.display_text = "1-800-833-9020"
        self.partner_field.polygon = self.coverage_polygon
        self.partner_field.save()
        self.partner_field.contributor_set.clear()
        self.contributor.partner_fields.add(self.partner_field)

        self.inside = self._make_facility("IN2026000INSD", 77.2, 28.6)
        self.outside = self._make_facility("IN2026000OUTS", 75.0, 20.0)

    def tearDown(self):
        """Detach the contributor but keep the system partner field."""
        self.partner_field.contributor_set.clear()

    def _make_facility(self, facility_id, lon, lat, sector=None):
        """Create a FacilityIndex row in India at the given lon/lat."""
        return FacilityIndex.objects.create(
            id=facility_id,
            name="Test Facility",
            address="123 Main St",
            country_code="IN",
            sector=sector or ["Apparel"],
            location=Point(lon, lat),
            contributors_count=1,
            contributors_id=[self.contributor.id],
            contributors=[{"id": self.contributor.id, "name": "Test"}],
            contrib_types=[Contributor.OTHER_CONTRIB_TYPE],
            facility_addresses=[{"address": "123 Main St"}],
            extended_fields=[],
            lists=[],
            approved_claim_ids=[],
            facility_names=[],
        )

    def _spotlight_ids(self):
        """GET the profile spotlight and return the facility ids."""
        response = self.client.get(
            f"/user-profile/{self.user.pk}/facilities/?spotlight=true"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return {
            feature["id"]
            for feature in response.data["results"]["features"]
        }

    def test_spotlight_lists_only_in_boundary_facilities(self):
        """Spotlight shows in-polygon locations and no others."""
        ids = self._spotlight_ids()
        self.assertIn(self.inside.id, ids)
        self.assertNotIn(self.outside.id, ids)

    def test_spotlight_excludes_uncovered_sectors(self):
        """In-boundary locations outside the covered sectors are
        left out of the spotlight."""
        electronics = self._make_facility(
            "IN2026000ELEC", 77.1, 28.7, sector=["Electronics"]
        )
        self.assertNotIn(electronics.id, self._spotlight_ids())

    def test_spotlight_is_empty_when_no_polygon_is_linked(self):
        """Without a linked coverage polygon the spotlight shows
        nothing — never everything."""
        self.partner_field.polygon = None
        self.partner_field.save()
        self.assertEqual(self._spotlight_ids(), set())


@override_switch(ZONE_SETS_SWITCH, active=True)
class TestZoneSetSpotlight(APITestCase):
    """Tests for the zone-set-backed contributor profile spotlight."""

    def setUp(self):
        """Create the zone-set partner and in/out facilities."""
        caches["view_cache"].clear()
        self.user = User.objects.create(email="aqueduct@example.com")
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="WRI Aqueduct",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.other_user = User.objects.create(email="other@example.com")
        self.other_contributor = Contributor.objects.create(
            admin=self.other_user,
            name="Other",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.partner_field = PartnerField.objects.create(
            name="aqueduct_water_stress",
            type=PartnerField.STRING,
            label="Baseline water stress",
            active=True,
        )
        self.contributor.partner_fields.add(self.partner_field)
        self.zone_set = ZoneSet.objects.create(
            name="aqueduct_bws",
            description="Baseline water stress bands.",
            partner_field=self.partner_field,
            value_property="bws_label",
        )
        self.zone_set.replace_zones(zone_records(
            feature(WEST, {"bws_label": "Extremely High"}),
            feature(EAST, {"bws_label": "Low"}),
        ))

        # Both facilities belong to another contributor: the spotlight
        # is "locations the dataset covers", not "locations the
        # partner contributed".
        self.inside = make_facility(self.other_contributor, 77.2, 28.6)
        self.outside = make_facility(self.other_contributor, 75.0, 20.0)

    def _spotlight_ids(self):
        """GET the profile spotlight and return the facility ids."""
        caches["view_cache"].clear()
        response = self.client.get(
            f"/user-profile/{self.user.pk}/facilities/?spotlight=true"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return {
            feature["id"]
            for feature in response.data["results"]["features"]
        }

    def test_spotlight_lists_covered_locations(self):
        """The spotlight shows every location a zone covers, whoever
        contributed it, and nothing outside the zones."""
        self.assertEqual(self._spotlight_ids(), {self.inside.id})

    @override_switch(ZONE_SETS_SWITCH, active=False)
    def test_spotlight_is_empty_when_switch_is_off(self):
        """With the switch off the spotlight shows nothing, never every
        location."""
        self.assertEqual(self._spotlight_ids(), set())

    def test_spotlight_is_empty_when_zone_set_is_inactive(self):
        """A retired zone set shows nothing."""
        self.zone_set.active = False
        self.zone_set.save()
        self.assertEqual(self._spotlight_ids(), set())

    def test_spotlight_unions_zone_set_and_contributed_fields(self):
        """A partner holding a zone-set field and a contributed field
        sees the covered locations plus the ones it contributed partner
        data to (and, as before, not a row it left on someone else's
        location)."""
        contributed = PartnerField.objects.create(
            name="aqueduct_notes",
            type=PartnerField.STRING,
            label="Notes",
            active=True,
        )
        self.contributor.partner_fields.add(contributed)
        own_facility = make_facility(self.contributor, 75.0, 21.0)
        for facility in (own_facility, self.outside):
            ExtendedField.objects.create(
                contributor=self.contributor,
                facility=facility,
                field_name="aqueduct_notes",
                value={"raw_values": ["note"]},
            )
        self.assertEqual(
            self._spotlight_ids(), {self.inside.id, own_facility.id}
        )

    def test_contributed_only_spotlight_is_unchanged(self):
        """A partner with no zone set still sees only the locations it
        contributed partner data to."""
        self.zone_set.partner_field = None
        self.zone_set.save()
        own_facility = make_facility(self.contributor, 75.0, 21.0)
        ExtendedField.objects.create(
            contributor=self.contributor,
            facility=own_facility,
            field_name=self.partner_field.name,
            value={"raw_values": ["note"]},
        )
        self.assertEqual(self._spotlight_ids(), {own_facility.id})
