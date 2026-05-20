from api.models import (
    Contributor,
    EmbedConfig,
    EmbedField,
    ExtendedField,
    User,
)
from api.serializers.embed_config import EmbedConfigSerializer

from django.test import TestCase


class EmbedConfigSerializerTest(TestCase):
    """
    Tests for EmbedConfigSerializer's SerializerMethodField getters.

    Covers:
      * get_extended_fields - only return nonstandard fields that the
        contributor has data for AND that the user has left visible in
        their /settings -> Embed page.
      * get_contributor - returns contributor.id (or None when orphan).
      * get_contributor_name - returns contributor.name (or None).
      * get_embed_fields - returns the embed config's EmbedField rows
        serialized and ordered by `order`.
    """

    def setUp(self):
        self.user = User.objects.create(email="embed-test@example.com")
        self.user.set_password("password")
        self.user.save()

        self.embed_config = EmbedConfig.objects.create()
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="Embed Test Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
            embed_config=self.embed_config,
        )

    def _add_extended_field(self, field_name, raw_value="x"):
        return ExtendedField.objects.create(
            contributor=self.contributor,
            field_name=field_name,
            value={"raw_value": raw_value},
        )

    def _add_embed_field(
        self,
        column_name,
        order,
        visible=True,
        searchable=False,
        display_name=None,
        embed_config=None,
    ):
        return EmbedField.objects.create(
            embed_config=(
                embed_config
                if embed_config is not None
                else self.embed_config
            ),
            order=order,
            column_name=column_name,
            display_name=(
                display_name if display_name is not None else column_name
            ),
            visible=visible,
            searchable=searchable,
        )

    def _serialize(self, embed_config=None):
        config = (
            embed_config if embed_config is not None else self.embed_config
        )
        return EmbedConfigSerializer(config).data

    def _extended(self, embed_config=None):
        return list(self._serialize(embed_config)["extended_fields"])

    # =====================================================================
    # get_extended_fields
    # =====================================================================

    def test_extended_fields_returns_present_and_visible(self):
        """Happy path: all fields have data and are visible -> all returned."""
        self._add_extended_field(ExtendedField.FACILITY_TYPE)
        self._add_extended_field(ExtendedField.PROCESSING_TYPE)
        self._add_embed_field(
            ExtendedField.FACILITY_TYPE, order=0, visible=True
        )
        self._add_embed_field(
            ExtendedField.PROCESSING_TYPE, order=1, visible=True
        )

        self.assertCountEqual(
            self._extended(),
            [ExtendedField.FACILITY_TYPE, ExtendedField.PROCESSING_TYPE],
        )

    def test_extended_fields_excludes_unchecked(self):
        """
        Unchecking a field in /settings -> Embed must hide it
        from the search form, even if the contributor has data for it.
        """
        self._add_extended_field(ExtendedField.FACILITY_TYPE)
        self._add_extended_field(ExtendedField.PROCESSING_TYPE)
        self._add_extended_field(ExtendedField.PARENT_COMPANY)
        self._add_embed_field(
            ExtendedField.FACILITY_TYPE, order=0, visible=False
        )
        self._add_embed_field(
            ExtendedField.PROCESSING_TYPE, order=1, visible=False
        )
        self._add_embed_field(
            ExtendedField.PARENT_COMPANY, order=2, visible=True
        )

        self.assertEqual(
            self._extended(), [ExtendedField.PARENT_COMPANY]
        )

    def test_extended_fields_all_unchecked_returns_empty(self):
        self._add_extended_field(ExtendedField.FACILITY_TYPE)
        self._add_extended_field(ExtendedField.PROCESSING_TYPE)
        self._add_embed_field(
            ExtendedField.FACILITY_TYPE, order=0, visible=False
        )
        self._add_embed_field(
            ExtendedField.PROCESSING_TYPE, order=1, visible=False
        )

        self.assertEqual(self._extended(), [])

    def test_extended_fields_without_matching_embed_field_excluded(self):
        """
        A contributor may have ExtendedField data for a field that has
        no EmbedField row yet (e.g. user has never customized embed
        settings). In that case, the field should not appear.
        """
        self._add_extended_field(ExtendedField.FACILITY_TYPE)
        # Deliberately no corresponding EmbedField row.

        self.assertEqual(self._extended(), [])

    def test_extended_fields_visible_without_data_excluded(self):
        """
        Visibility alone is not enough -- there must be at least one
        ExtendedField row from this contributor for that field.
        """
        self._add_embed_field(
            ExtendedField.FACILITY_TYPE, order=0, visible=True
        )
        # Deliberately no ExtendedField rows.

        self.assertEqual(self._extended(), [])

    def test_extended_fields_deduplicates_repeated_field_names(self):
        """Multiple ExtendedField rows for the same field_name -> one entry."""
        self._add_extended_field(ExtendedField.FACILITY_TYPE, raw_value="a")
        self._add_extended_field(ExtendedField.FACILITY_TYPE, raw_value="b")
        self._add_extended_field(ExtendedField.FACILITY_TYPE, raw_value="c")
        self._add_embed_field(
            ExtendedField.FACILITY_TYPE, order=0, visible=True
        )

        self.assertEqual(self._extended(), [ExtendedField.FACILITY_TYPE])

    def test_extended_fields_orphan_config_returns_empty(self):
        """
        An EmbedConfig with no associated Contributor (the reverse
        OneToOne is null) should return an empty list and must not leak
        ExtendedField rows from other contributors.
        """
        orphan_config = EmbedConfig.objects.create()
        self._add_extended_field(ExtendedField.FACILITY_TYPE)
        self._add_embed_field(
            ExtendedField.FACILITY_TYPE, order=0, visible=True
        )

        self.assertEqual(self._extended(orphan_config), [])

    def test_extended_fields_does_not_leak_other_contributors(self):
        """
        Extended fields belonging to a different contributor must not
        appear in this embed config's serialized output.
        """
        other_user = User.objects.create(email="other@example.com")
        other_user.set_password("password")
        other_user.save()
        other_contributor = Contributor.objects.create(
            admin=other_user,
            name="Other Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        ExtendedField.objects.create(
            contributor=other_contributor,
            field_name=ExtendedField.PROCESSING_TYPE,
            value={"raw_value": "leak"},
        )

        # The current contributor only has facility_type data.
        self._add_extended_field(ExtendedField.FACILITY_TYPE)
        self._add_embed_field(
            ExtendedField.FACILITY_TYPE, order=0, visible=True
        )
        self._add_embed_field(
            ExtendedField.PROCESSING_TYPE, order=1, visible=True
        )

        self.assertEqual(self._extended(), [ExtendedField.FACILITY_TYPE])

    # =====================================================================
    # get_contributor
    # =====================================================================

    def test_contributor_returns_contributor_id(self):
        self.assertEqual(
            self._serialize()["contributor"], self.contributor.id
        )

    def test_contributor_returns_none_for_orphan_config(self):
        """
        An EmbedConfig without an associated Contributor (the reverse
        OneToOne raises DoesNotExist) should serialize contributor=None.
        """
        orphan_config = EmbedConfig.objects.create()
        self.assertIsNone(self._serialize(orphan_config)["contributor"])

    # =====================================================================
    # get_contributor_name
    # =====================================================================

    def test_contributor_name_returns_contributor_name(self):
        self.assertEqual(
            self._serialize()["contributor_name"], self.contributor.name
        )

    def test_contributor_name_returns_none_for_orphan_config(self):
        orphan_config = EmbedConfig.objects.create()
        self.assertIsNone(
            self._serialize(orphan_config)["contributor_name"]
        )

    # =====================================================================
    # get_embed_fields
    # =====================================================================

    def test_embed_fields_returns_serialized_rows(self):
        self._add_embed_field(
            "facility_type",
            order=0,
            visible=True,
            searchable=True,
            display_name="Facility Type",
        )
        self._add_embed_field(
            "processing_type",
            order=1,
            visible=False,
            searchable=False,
            display_name="Processing Type",
        )

        result = self._serialize()["embed_fields"]

        self.assertEqual(len(result), 2)
        self.assertEqual(
            result[0],
            {
                "column_name": "facility_type",
                "display_name": "Facility Type",
                "visible": True,
                "order": 0,
                "searchable": True,
            },
        )
        self.assertEqual(
            result[1],
            {
                "column_name": "processing_type",
                "display_name": "Processing Type",
                "visible": False,
                "order": 1,
                "searchable": False,
            },
        )

    def test_embed_fields_empty_when_no_rows(self):
        self.assertEqual(self._serialize()["embed_fields"], [])

    def test_embed_fields_orders_by_order_not_insertion(self):
        """Rows must be sorted by `order`, regardless of insertion sequence."""
        self._add_embed_field("c", order=2)
        self._add_embed_field("a", order=0)
        self._add_embed_field("b", order=1)

        result = self._serialize()["embed_fields"]
        column_names = [row["column_name"] for row in result]
        orders = [row["order"] for row in result]
        self.assertEqual(column_names, ["a", "b", "c"])
        self.assertEqual(orders, [0, 1, 2])

    def test_embed_fields_does_not_leak_other_configs_rows(self):
        """
        Rows belonging to a different EmbedConfig must not appear in
        this config's serialized output.
        """
        other_config = EmbedConfig.objects.create()
        self._add_embed_field("foreign", order=0, embed_config=other_config)
        self._add_embed_field("local", order=0)

        result = self._serialize()["embed_fields"]
        self.assertEqual(len(result), 1)
