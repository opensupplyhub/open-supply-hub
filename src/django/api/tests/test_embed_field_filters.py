import json

from api.models import (
    Contributor,
    EmbedConfig,
    EmbedField,
    Facility,
    FacilityListItem,
    Source,
    User,
)
from api.services.embed_field_filters import (
    apply_embed_filters,
    embed_filter_options,
    parse_embed_filters,
)
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.gis.geos import Point
from django.http import QueryDict


class EmbedFieldFiltersTest(APITestCase):
    """
    Filtering an embedded map by the values of a contributor's own columns,
    and the dropdown options offered for those columns.
    """

    def setUp(self):
        self.contributor = self._contributor("brand@example.com", "Brand")
        self.contributor.embed_level = 3
        self.contributor.embed_config = EmbedConfig.objects.create()
        self.contributor.save()
        self._add_field("project", order=0, filterable=True)
        self._add_field("tier", order=1, filterable=True)
        self._add_field("secret", order=2, filterable=False)

        self.source = self._source(self.contributor)
        self.health = self._facility(
            "Health Factory",
            {"project": "HERhealth|RISE", "tier": "1", "secret": "x"},
        )
        self.sunrise = self._facility(
            "Sunrise Mill", {"project": "SUNRISE", "tier": "2"}
        )
        self.plain = self._facility("Plain Factory", {"tier": "1"})

    # ------------------------------------------------------------------ #
    # fixtures                                                            #
    # ------------------------------------------------------------------ #
    def _contributor(self, email, name):
        user = User.objects.create(email=email)
        return Contributor.objects.create(
            admin=user,
            name=name,
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

    def _source(self, contributor, is_active=True):
        return Source.objects.create(
            source_type=Source.SINGLE,
            is_active=is_active,
            is_public=True,
            contributor=contributor,
        )

    def _add_field(self, column_name, order, filterable, visible=True):
        return EmbedField.objects.create(
            embed_config=self.contributor.embed_config,
            column_name=column_name,
            display_name=column_name.title(),
            order=order,
            visible=visible,
            filterable=filterable,
        )

    def _facility(self, name, raw_json, source=None, facility=None):
        item = FacilityListItem.objects.create(
            name=name,
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source or self.source,
            raw_header="",
            raw_json=raw_json,
            raw_data=str(raw_json),
        )
        if facility is None:
            facility = Facility.objects.create(
                name=name,
                address="Address",
                country_code="US",
                created_from=item,
                location=Point(0, 0),
            )
        item.facility = facility
        item.save()
        return facility

    def _filtered_names(self, query):
        params = QueryDict(
            query.format(contributor=self.contributor.id)
        )
        facilities = apply_embed_filters(Facility.objects.all(), params)
        return sorted(facilities.values_list("name", flat=True))

    # ------------------------------------------------------------------ #
    # filtering                                                           #
    # ------------------------------------------------------------------ #
    def test_no_embed_filters_leaves_the_queryset_alone(self):
        self.assertEqual(
            3, len(self._filtered_names("embed=1&contributors={contributor}"))
        )

    def test_matches_one_value_of_a_multi_value_cell(self):
        self.assertEqual(
            ["Health Factory"],
            self._filtered_names(
                "embed=1&contributors={contributor}"
                "&embed_filters=project::RISE"
            ),
        )

    def test_match_is_case_insensitive(self):
        self.assertEqual(
            ["Health Factory"],
            self._filtered_names(
                "embed=1&contributors={contributor}"
                "&embed_filters=project::herhealth"
            ),
        )

    def test_does_not_match_part_of_a_value(self):
        """RISE must not match SUNRISE, and the reverse."""
        self.assertEqual(
            ["Sunrise Mill"],
            self._filtered_names(
                "embed=1&contributors={contributor}"
                "&embed_filters=project::SUNRISE"
            ),
        )

    def test_several_filters_must_all_match(self):
        self.assertEqual(
            ["Health Factory", "Plain Factory"],
            self._filtered_names(
                "embed=1&contributors={contributor}&embed_filters=tier::1"
            ),
        )
        self.assertEqual(
            ["Health Factory"],
            self._filtered_names(
                "embed=1&contributors={contributor}"
                "&embed_filters=tier::1&embed_filters=project::HERhealth"
            ),
        )

    def test_a_column_that_is_not_filterable_matches_nothing(self):
        self.assertEqual(
            [],
            self._filtered_names(
                "embed=1&contributors={contributor}&embed_filters=secret::x"
            ),
        )

    def test_a_hidden_field_cannot_be_filtered(self):
        EmbedField.objects.filter(column_name="tier").update(visible=False)
        self.assertEqual(
            [],
            self._filtered_names(
                "embed=1&contributors={contributor}&embed_filters=tier::1"
            ),
        )

    def test_ignored_outside_embed_mode(self):
        self.assertEqual(
            3,
            len(
                self._filtered_names(
                    "contributors={contributor}&embed_filters=tier::1"
                )
            ),
        )

    def test_another_contributors_values_do_not_match(self):
        other = self._contributor("other@example.com", "Other")
        self._facility(
            "Plain Factory again",
            {"project": "HERhealth"},
            source=self._source(other),
            facility=self.plain,
        )
        self.assertEqual(
            ["Health Factory"],
            self._filtered_names(
                "embed=1&contributors={contributor}"
                "&embed_filters=project::HERhealth"
            ),
        )

    def test_values_from_an_inactive_source_do_not_match(self):
        self._facility(
            "Plain Factory old row",
            {"project": "HERhealth"},
            source=self._source(self.contributor, is_active=False),
            facility=self.plain,
        )
        self.assertEqual(
            ["Health Factory"],
            self._filtered_names(
                "embed=1&contributors={contributor}"
                "&embed_filters=project::HERhealth"
            ),
        )

    def test_malformed_filters_are_skipped(self):
        params = QueryDict(
            "embed_filters=project&embed_filters=::x&embed_filters=tier::"
            "&embed_filters=tier::1"
        )
        self.assertEqual([("tier", "1")], parse_embed_filters(params))

    # ------------------------------------------------------------------ #
    # options                                                             #
    # ------------------------------------------------------------------ #
    def test_options_count_facilities_per_value(self):
        options = embed_filter_options(self.contributor)

        self.assertEqual(["project", "tier"], sorted(options))
        self.assertEqual(
            [
                {"value": "1", "count": 2},
                {"value": "2", "count": 1},
            ],
            options["tier"],
        )
        self.assertEqual(
            ["HERhealth", "RISE", "SUNRISE"],
            [option["value"] for option in options["project"]],
        )

    def test_options_leave_out_fields_that_are_not_filterable(self):
        self.assertNotIn("secret", embed_filter_options(self.contributor))

    def test_public_embed_config_includes_the_options(self):
        response = self.client.get(
            "/api/contributor-embed-configs/{}/".format(self.contributor.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)

        self.assertEqual(
            {"value": "1", "count": 2}, content["filter_options"]["tier"][0]
        )
        filterable = {
            field["column_name"]: field["filterable"]
            for field in content["embed_fields"]
        }
        self.assertEqual(
            {"project": True, "tier": True, "secret": False}, filterable
        )
