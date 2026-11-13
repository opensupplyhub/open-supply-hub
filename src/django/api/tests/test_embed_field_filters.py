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
from api.models.facility.facility_index import FacilityIndex
from api.models.transactions.index_facilities_new import index_facilities_new
from api.serializers.embed_config import EmbedConfigSerializer
from api.services.embed_field_filters import (
    apply_embed_filters,
    embed_color_by_column,
    embed_color_value_subquery,
    embed_field_sort,
    embed_filter_options,
    embed_settings_version,
    parse_embed_filters,
    resolve_embed_sort,
)
from api.tiler import get_facilities_vector_tile
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

    # ------------------------------------------------------------------ #
    # coloring markers by a field                                         #
    # ------------------------------------------------------------------ #
    def _color_by(self, column, colors=None):
        config = self.contributor.embed_config
        config.color_by_field = column
        config.color_by_colors = colors or {}
        config.save()

    def _tile_params(self, extra=""):
        return QueryDict(
            "embed=1&contributors={}{}".format(self.contributor.id, extra)
        )

    def test_color_column_is_only_the_one_the_contributor_chose(self):
        self._color_by("tier")

        self.assertEqual(
            "tier", embed_color_by_column(self._tile_params("&color_by=tier"))
        )
        self.assertIsNone(
            embed_color_by_column(self._tile_params("&color_by=secret"))
        )
        self.assertIsNone(embed_color_by_column(self._tile_params()))
        self.assertIsNone(
            embed_color_by_column(
                QueryDict(
                    "contributors={}&color_by=tier".format(
                        self.contributor.id
                    )
                )
            )
        )

    def test_color_value_is_read_from_the_contributors_row(self):
        params = self._tile_params("&color_by=tier")
        values = dict(
            Facility.objects.annotate(
                embed_color_value=embed_color_value_subquery(params, "tier")
            ).values_list("name", "embed_color_value")
        )

        self.assertEqual(
            {"Health Factory": "1", "Sunrise Mill": "2", "Plain Factory": "1"},
            values,
        )

    def test_marker_tile_carries_the_color_value(self):
        self._color_by("tier")
        # Tiles are built from the facility index, which needs to know the
        # facilities belong to this contributor.
        index_facilities_new(
            [self.health.id, self.sunrise.id, self.plain.id]
        )
        FacilityIndex.objects.update(contributors_id=[self.contributor.id])

        colored = get_facilities_vector_tile(
            self._tile_params("&color_by=tier"), "facilities", 0, 0, 0
        )
        plain = get_facilities_vector_tile(
            self._tile_params(), "facilities", 0, 0, 0
        )

        self.assertIn(b"embed_color_value", bytes(colored))
        self.assertNotIn(b"embed_color_value", bytes(plain))

    def test_color_settings_are_validated(self):
        def errors(data):
            serializer = EmbedConfigSerializer(
                self.contributor.embed_config, data=data, partial=True
            )
            serializer.is_valid()
            return serializer.errors

        self.assertEqual(
            {},
            errors(
                {
                    "color_by_field": "tier",
                    "color_by_colors": {"1": "#14507a", "2": "#2a9d8f"},
                }
            ),
        )
        self.assertIn(
            "color_by_colors", errors({"color_by_colors": {"1": "red"}})
        )
        self.assertIn(
            "color_by_colors", errors({"color_by_colors": ["#14507a"]})
        )

    def test_public_embed_config_includes_the_color_values(self):
        self._color_by("tier", {"1": "#14507a"})

        response = self.client.get(
            "/api/contributor-embed-configs/{}/".format(self.contributor.id)
        )
        content = json.loads(response.content)

        self.assertEqual("tier", content["color_by_field"])
        self.assertEqual({"1": "#14507a"}, content["color_by_colors"])
        self.assertEqual(
            [{"value": "1", "count": 2}, {"value": "2", "count": 1}],
            content["color_by_options"],
        )

    def test_public_embed_config_without_a_color_field(self):
        response = self.client.get(
            "/api/contributor-embed-configs/{}/".format(self.contributor.id)
        )
        content = json.loads(response.content)

        self.assertIsNone(content["color_by_field"])
        self.assertEqual([], content["color_by_options"])

    # ------------------------------------------------------------------ #
    # list order                                                          #
    # ------------------------------------------------------------------ #
    def _listed_names(self, sort_by):
        index_facilities_new(
            list(Facility.objects.values_list("id", flat=True))
        )
        FacilityIndex.objects.update(contributors_id=[self.contributor.id])
        response = self.client.get(
            "/api/facilities/?embed=1&contributors={}&sort_by={}".format(
                self.contributor.id, sort_by
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return [
            feature["properties"]["name"]
            for feature in json.loads(response.content)["features"]
        ]

    def test_embed_default_sort_is_by_name_until_one_is_chosen(self):
        params = self._tile_params()

        self.assertEqual(
            "name_asc", resolve_embed_sort(params, "embed_default")
        )
        self.assertEqual("name_desc", resolve_embed_sort(params, "name_desc"))
        self.assertIsNone(resolve_embed_sort(params, None))

    def test_embed_default_sort_uses_the_contributors_choice(self):
        config = self.contributor.embed_config
        config.default_sort = "-field:tier"
        config.save()

        self.assertEqual(
            "-field:tier",
            resolve_embed_sort(self._tile_params(), "embed_default"),
        )
        self.assertEqual(
            "name_asc",
            resolve_embed_sort(
                QueryDict("contributors={}".format(self.contributor.id)),
                "embed_default",
            ),
        )

    def test_only_a_visible_field_can_order_the_list(self):
        params = self._tile_params()

        self.assertEqual(
            ("tier", False), embed_field_sort(params, "field:tier")
        )
        self.assertEqual(
            ("tier", True), embed_field_sort(params, "-field:tier")
        )
        self.assertIsNone(embed_field_sort(params, "field:unknown"))
        self.assertIsNone(embed_field_sort(params, "name_asc"))
        self.assertIsNone(
            embed_field_sort(
                QueryDict("contributors={}".format(self.contributor.id)),
                "field:tier",
            )
        )

        EmbedField.objects.filter(column_name="tier").update(visible=False)
        self.assertIsNone(embed_field_sort(params, "field:tier"))

    def test_list_is_ordered_by_a_field_with_numbers_as_numbers(self):
        self._facility("Big Factory", {"tier": "10"})
        self._facility("No Tier Factory", {"project": "RISE"})

        self.assertEqual(
            [
                "Health Factory",
                "Plain Factory",
                "Sunrise Mill",
                "Big Factory",
                "No Tier Factory",
            ],
            self._listed_names("field:tier"),
        )
        self.assertEqual(
            [
                "Big Factory",
                "Sunrise Mill",
                "Health Factory",
                "Plain Factory",
                "No Tier Factory",
            ],
            self._listed_names("-field:tier"),
        )

    def test_list_uses_the_contributors_default_order(self):
        config = self.contributor.embed_config
        config.default_sort = "-field:tier"
        config.save()

        self.assertEqual(
            ["Sunrise Mill", "Health Factory", "Plain Factory"],
            self._listed_names("embed_default"),
        )

    def test_list_is_ordered_by_name_without_a_default_order(self):
        self.assertEqual(
            ["Health Factory", "Plain Factory", "Sunrise Mill"],
            self._listed_names("embed_default"),
        )

    def test_default_sort_is_validated(self):
        def errors(value):
            serializer = EmbedConfigSerializer(
                self.contributor.embed_config,
                data={"default_sort": value},
                partial=True,
            )
            serializer.is_valid()
            return serializer.errors

        for value in ("name_asc", "name_desc", "field:tier", "-field:tier"):
            with self.subTest(value=value):
                self.assertEqual({}, errors(value))
        for value in ("random", "field:", "contributors_desc"):
            with self.subTest(value=value):
                self.assertIn("default_sort", errors(value))

    # ------------------------------------------------------------------ #
    # blurbed facilities first                                            #
    # ------------------------------------------------------------------ #
    def _blurb_setup(self, blurbs_first=True):
        self._add_field("note", order=3, filterable=False)
        EmbedField.objects.filter(column_name="note").update(
            display_as=EmbedField.BLURB
        )
        config = self.contributor.embed_config
        config.blurbs_first = blurbs_first
        config.save()
        self._facility("Zebra Factory", {"tier": "3", "note": "A note."})
        self._facility("Empty Note Factory", {"tier": "3", "note": "  "})

    def test_blurbed_facilities_are_listed_first(self):
        self._blurb_setup()

        self.assertEqual(
            [
                "Zebra Factory",
                "Empty Note Factory",
                "Health Factory",
                "Plain Factory",
                "Sunrise Mill",
            ],
            self._listed_names("embed_default"),
        )

    def test_blurbs_first_applies_on_top_of_a_field_order(self):
        self._blurb_setup()
        self._facility("Alpha Factory", {"tier": "9", "note": "Another."})

        self.assertEqual(
            ["Alpha Factory", "Zebra Factory", "Empty Note Factory"],
            self._listed_names("-field:tier")[:3],
        )

    def test_blurbs_are_not_listed_first_unless_chosen(self):
        self._blurb_setup(blurbs_first=False)

        self.assertEqual(
            "Empty Note Factory", self._listed_names("embed_default")[0]
        )

    def test_blurbs_first_needs_a_visible_blurb_field(self):
        self._blurb_setup()
        EmbedField.objects.filter(column_name="note").update(visible=False)

        self.assertEqual(
            "Empty Note Factory", self._listed_names("embed_default")[0]
        )

    # ------------------------------------------------------------------ #
    # cached lists follow the settings                                    #
    # ------------------------------------------------------------------ #
    def test_settings_version_changes_when_the_settings_are_saved(self):
        params = self._tile_params()
        before = embed_settings_version(params)
        self.assertTrue(before)

        config = self.contributor.embed_config
        config.blurbs_first = True
        config.save()

        self.assertNotEqual(before, embed_settings_version(params))

    def test_settings_version_is_empty_outside_an_embedded_map(self):
        self.assertEqual(
            "",
            embed_settings_version(
                QueryDict("contributors={}".format(self.contributor.id))
            ),
        )
        self.assertEqual("", embed_settings_version(QueryDict("embed=1")))

    def test_cached_list_is_not_reused_after_the_settings_change(self):
        self._blurb_setup(blurbs_first=False)
        self.assertEqual(
            "Empty Note Factory", self._listed_names("embed_default")[0]
        )

        config = self.contributor.embed_config
        config.blurbs_first = True
        config.save()

        self.assertEqual(
            "Zebra Factory", self._listed_names("embed_default")[0]
        )
