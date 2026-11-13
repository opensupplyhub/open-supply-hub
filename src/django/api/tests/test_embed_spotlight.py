import json

from api.models import (
    Contributor,
    EmbedConfig,
    ExtendedField,
    Facility,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex
from api.models.partner_field import PartnerField
from api.models.partner_field_group import PartnerFieldGroup
from api.models.transactions.index_facilities_new import index_facilities_new
from api.serializers.embed_config import EmbedConfigSerializer
from api.services.embed_field_filters import apply_embed_filters
from api.services.embed_spotlight import (
    embed_has_spotlight,
    embed_spotlight_field_names,
    spotlight_for_settings,
    spotlight_for_visitors,
)
from api.tiler import get_facilities_vector_tile
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.gis.geos import Point
from django.http import QueryDict


class EmbedSpotlightTest(APITestCase):
    """
    Spotlight data on an embedded map: shown only when the contributor
    turns it on, and only for the partner field groups they choose.
    """
    password = "example123"

    def setUp(self):
        self.contributor = self._contributor("brand@example.com", "Brand")
        self.contributor.embed_level = 3
        self.contributor.embed_config = EmbedConfig.objects.create()
        self.contributor.save()
        self.source = self._source(self.contributor)
        self.assessed = self._facility("Assessed Factory")
        self.audited = self._facility("Audited Mill")
        self.plain = self._facility("Plain Factory")

        # Two data partners, each with a field in its own group.
        self.environment = PartnerFieldGroup.objects.create(
            name="Environmental assessment", order=1
        )
        self.audits = PartnerFieldGroup.objects.create(
            name="Social audits", order=2
        )
        self.partner = self._contributor("partner@example.com", "Partner")
        self.partner_source = self._source(self.partner)
        self._partner_field(
            "env_assessment", self.environment, [self.assessed]
        )
        self._partner_field(
            "social_audit", self.audits, [self.assessed, self.audited]
        )

        index_facilities_new(
            list(Facility.objects.values_list("id", flat=True))
        )
        FacilityIndex.objects.update(contributors_id=[self.contributor.id])

    # ------------------------------------------------------------------ #
    # fixtures                                                            #
    # ------------------------------------------------------------------ #
    def _contributor(self, email, name):
        user = User.objects.create(email=email)
        user.set_password(self.password)
        user.save()
        return Contributor.objects.create(
            admin=user,
            name=name,
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

    def _source(self, contributor):
        return Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=contributor,
        )

    def _facility(self, name):
        item = FacilityListItem.objects.create(
            name=name,
            address="Address",
            country_code="GB",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
            raw_header="",
            raw_json={},
            raw_data="",
        )
        facility = Facility.objects.create(
            name=name,
            address="Address",
            country_code="GB",
            created_from=item,
            location=Point(0, 0),
        )
        item.facility = facility
        item.save()
        return facility

    def _partner_field(self, name, group, facilities):
        field = PartnerField.objects.create(
            name=name, type=PartnerField.STRING, label=name, group=group
        )
        self.partner.partner_fields.add(field)
        for facility in facilities:
            self._partner_data(name, facility)
        return field

    def _partner_data(self, field_name, facility):
        # Partner data reaches a facility the way any contribution does:
        # through one of the partner's list items, matched to it.
        item = FacilityListItem.objects.create(
            name=facility.name,
            address="Address",
            country_code="GB",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.MATCHED,
            source=self.partner_source,
            raw_header="",
            raw_json={},
            raw_data="",
            facility=facility,
        )
        FacilityMatch.objects.create(
            facility=facility,
            facility_list_item=item,
            status=FacilityMatch.AUTOMATIC,
            confidence=0.9,
            results="",
            is_active=True,
        )
        ExtendedField.objects.create(
            contributor=self.partner,
            facility=facility,
            facility_list_item=item,
            field_name=field_name,
            value={"raw_value": "Recorded"},
        )

    def _show(self, groups, highlight=True, offer_filter=True):
        config = self.contributor.embed_config
        config.show_spotlight = True
        config.spotlight_highlight = highlight
        config.spotlight_filter = offer_filter
        config.spotlight_groups = [str(group.uuid) for group in groups]
        config.save()

    def _params(self, extra=""):
        return QueryDict(
            "embed=1&contributors={}{}".format(self.contributor.id, extra)
        )

    def _filtered_names(self, extra):
        facilities = apply_embed_filters(
            Facility.objects.all(), self._params(extra)
        )
        return sorted(facilities.values_list("name", flat=True))

    def _public_config(self):
        response = self.client.get(
            "/api/contributor-embed-configs/{}/".format(self.contributor.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return json.loads(response.content)

    # ------------------------------------------------------------------ #
    # off unless the contributor turns it on                              #
    # ------------------------------------------------------------------ #
    def test_is_off_by_default(self):
        self.assertIsNone(spotlight_for_visitors(self.contributor))
        self.assertIsNone(self._public_config()["spotlight"])
        self.assertIsNone(embed_has_spotlight(self._params()))
        self.assertEqual(set(), embed_spotlight_field_names(self._params()))

    def test_the_filter_matches_nothing_while_spotlight_is_off(self):
        self.assertEqual([], self._filtered_names("&embed_spotlight=any"))

    def test_needs_the_deluxe_embed_level(self):
        self._show([self.environment])
        self.contributor.embed_level = 2
        self.contributor.save()

        self.assertIsNone(spotlight_for_visitors(self.contributor))
        self.assertIsNone(embed_has_spotlight(self._params()))
        self.assertEqual([], self._filtered_names("&embed_spotlight=any"))

    def test_shows_nothing_when_no_group_is_chosen(self):
        self._show([])

        self.assertIsNone(spotlight_for_visitors(self.contributor))
        self.assertEqual([], self._filtered_names("&embed_spotlight=any"))

    # ------------------------------------------------------------------ #
    # the filter                                                          #
    # ------------------------------------------------------------------ #
    def test_filters_to_facilities_with_any_shown_data(self):
        self._show([self.environment, self.audits])

        self.assertEqual(
            ["Assessed Factory", "Audited Mill"],
            self._filtered_names("&embed_spotlight=any"),
        )

    def test_filters_to_one_group(self):
        self._show([self.environment, self.audits])

        self.assertEqual(
            ["Assessed Factory"],
            self._filtered_names(
                "&embed_spotlight={}".format(self.environment.uuid)
            ),
        )

    def test_a_group_that_is_not_shown_cannot_be_probed(self):
        self._show([self.environment])

        self.assertEqual(
            ["Assessed Factory"],
            self._filtered_names("&embed_spotlight=any"),
        )
        self.assertEqual(
            [],
            self._filtered_names(
                "&embed_spotlight={}".format(self.audits.uuid)
            ),
        )

    def test_matches_nothing_when_the_filter_is_not_offered(self):
        self._show([self.environment], offer_filter=False)

        self.assertEqual([], self._filtered_names("&embed_spotlight=any"))

    def test_is_ignored_outside_an_embedded_map(self):
        self._show([self.environment])
        params = QueryDict(
            "contributors={}&embed_spotlight=any".format(self.contributor.id)
        )

        self.assertEqual(
            3, apply_embed_filters(Facility.objects.all(), params).count()
        )

    def test_an_inactive_partner_field_is_not_shown(self):
        self._show([self.environment])
        PartnerField.objects.filter(name="env_assessment").update(
            active=False
        )

        self.assertIsNone(spotlight_for_visitors(self.contributor))

    # ------------------------------------------------------------------ #
    # what visitors and the settings screen are given                     #
    # ------------------------------------------------------------------ #
    def test_visitors_get_the_shown_groups_with_counts(self):
        self._show([self.environment, self.audits], highlight=False)

        spotlight = self._public_config()["spotlight"]

        self.assertEqual(False, spotlight["highlight"])
        self.assertEqual(True, spotlight["filter"])
        self.assertEqual(2, spotlight["count"])
        self.assertEqual(
            [("Environmental assessment", 1), ("Social audits", 2)],
            [(g["name"], g["count"]) for g in spotlight["groups"]],
        )
        self.assertEqual(
            ["env_assessment"], spotlight["groups"][0]["field_names"]
        )

    def test_settings_get_every_group_with_counts(self):
        options = spotlight_for_settings(self.contributor)

        self.assertEqual(3, options["total"])
        self.assertEqual(2, options["count"])
        self.assertEqual(
            [("Environmental assessment", 1), ("Social audits", 2)],
            [(g["name"], g["count"]) for g in options["groups"]],
        )

    def test_counts_only_the_contributors_own_facilities(self):
        other = self._contributor("other@example.com", "Other")
        other_item = FacilityListItem.objects.create(
            name="Elsewhere",
            address="Address",
            country_code="GB",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self._source(other),
            raw_header="",
            raw_json={},
            raw_data="",
        )
        elsewhere = Facility.objects.create(
            name="Elsewhere",
            address="Address",
            country_code="GB",
            created_from=other_item,
            location=Point(0, 0),
        )
        self._partner_data("env_assessment", elsewhere)
        index_facilities_new([elsewhere.id])

        options = spotlight_for_settings(self.contributor)

        self.assertEqual(1, options["groups"][0]["count"])

    def test_settings_options_need_a_deluxe_contributor(self):
        url = "/api/embed-spotlight-options/"
        self.assertIn(
            self.client.get(url).status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

        self.client.login(email="brand@example.com", password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, json.loads(response.content)["count"])

        self.contributor.embed_level = 2
        self.contributor.save()
        self.assertEqual(
            status.HTTP_403_FORBIDDEN, self.client.get(url).status_code
        )

    def test_settings_are_saved_and_validated(self):
        def errors(data):
            serializer = EmbedConfigSerializer(
                self.contributor.embed_config, data=data, partial=True
            )
            serializer.is_valid()
            return serializer.errors

        self.assertEqual(
            {},
            errors({
                "show_spotlight": True,
                "spotlight_groups": [str(self.environment.uuid)],
            }),
        )
        self.assertIn(
            "spotlight_groups", errors({"spotlight_groups": "all"})
        )
        self.assertIn(
            "spotlight_groups", errors({"spotlight_groups": [1, 2]})
        )

    # ------------------------------------------------------------------ #
    # the map, the list and a facility's details                          #
    # ------------------------------------------------------------------ #
    def test_marker_tile_says_which_facilities_have_data(self):
        self._show([self.environment], highlight=True)
        ringed = get_facilities_vector_tile(
            self._params(), "facilities", 0, 0, 0
        )
        self._show([self.environment], highlight=False)
        plain = get_facilities_vector_tile(
            self._params(), "facilities", 0, 0, 0
        )

        self.assertIn(b"embed_has_spotlight", bytes(ringed))
        self.assertNotIn(b"embed_has_spotlight", bytes(plain))

    def _listed(self):
        response = self.client.get(
            "/api/facilities/?embed=1&contributors={}".format(
                self.contributor.id
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return {
            feature["properties"]["name"]: feature["properties"]
            for feature in json.loads(response.content)["features"]
        }

    def test_list_marks_the_facilities_that_have_data(self):
        self._show([self.environment], highlight=False)

        listed = self._listed()

        self.assertEqual(True, listed["Assessed Factory"]["has_spotlight"])
        self.assertEqual(False, listed["Audited Mill"]["has_spotlight"])

    def test_list_says_nothing_while_spotlight_is_off(self):
        self.assertNotIn("has_spotlight", self._listed()["Assessed Factory"])

    def _details_partner_fields(self):
        response = self.client.get(
            "/api/facilities/{}/?embed=1&contributor={}".format(
                self.assessed.id, self.contributor.id
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return json.loads(response.content)["properties"]["partner_fields"]

    def test_details_carry_only_the_shown_partner_data(self):
        self.assertEqual({}, self._details_partner_fields())

        self._show([self.environment])
        shown = self._details_partner_fields()

        self.assertIn("env_assessment", shown)
        self.assertNotIn("social_audit", shown)

    def test_details_credit_the_partner(self):
        self._show([self.environment])

        entry = self._details_partner_fields()["env_assessment"][0]

        self.assertEqual("Partner", entry["contributor_name"])
        # A contribution's `contributor_id` is the id of the contributor's
        # admin user, which is what a profile link is built from.
        self.assertEqual(self.partner.admin.id, entry["contributor_id"])
