from api.models import EmbedConfig, EmbedField
from api.views.fields.create_embed_fields import create_embed_fields

from django.test import TestCase
from rest_framework.exceptions import ValidationError


class CreateEmbedFieldsDisplayOptionsTest(TestCase):
    """
    create_embed_fields builds EmbedField rows straight from request data.
    These tests cover the display options: show_in_list and display_as.
    """

    def setUp(self):
        self.embed_config = EmbedConfig.objects.create()

    def _field(self, order=0, **overrides):
        data = {
            "column_name": "column_{}".format(order),
            "display_name": "Column {}".format(order),
            "visible": True,
            "searchable": False,
            "order": order,
        }
        data.update(overrides)
        return data

    def test_defaults_when_display_options_are_omitted(self):
        """Clients that do not send the new keys keep today's display."""
        create_embed_fields([self._field()], self.embed_config)

        field = EmbedField.objects.get(embed_config=self.embed_config)
        self.assertFalse(field.show_in_list)
        self.assertEqual(field.display_as, EmbedField.TEXT)

    def test_display_options_are_saved(self):
        create_embed_fields(
            [
                self._field(0, show_in_list=True, display_as="tags"),
                self._field(1, display_as="blurb"),
            ],
            self.embed_config,
        )

        first, second = EmbedField.objects.filter(
            embed_config=self.embed_config
        ).order_by("order")
        self.assertTrue(first.show_in_list)
        self.assertEqual(first.display_as, EmbedField.TAGS)
        self.assertFalse(second.show_in_list)
        self.assertEqual(second.display_as, EmbedField.BLURB)

    def test_unknown_display_as_is_rejected(self):
        with self.assertRaises(ValidationError):
            create_embed_fields(
                [self._field(0), self._field(1, display_as="marquee")],
                self.embed_config,
            )

        self.assertFalse(
            EmbedField.objects.filter(embed_config=self.embed_config).exists()
        )


class CreateEmbedFieldsExplanationsTest(TestCase):
    """
    A contributor can explain a field on their embedded map: what the
    field means, and what each of its values means.
    """

    def setUp(self):
        self.embed_config = EmbedConfig.objects.create()

    def _field(self, order=0, **overrides):
        data = {
            "column_name": "column_{}".format(order),
            "display_name": "Column {}".format(order),
            "visible": True,
            "searchable": False,
            "order": order,
        }
        data.update(overrides)
        return data

    def _saved(self):
        return EmbedField.objects.get(embed_config=self.embed_config)

    def test_fields_have_no_explanations_by_default(self):
        create_embed_fields([self._field()], self.embed_config)

        self.assertEqual("", self._saved().description)
        self.assertEqual({}, self._saved().value_descriptions)

    def test_explanations_are_saved_and_tidied(self):
        create_embed_fields(
            [
                self._field(
                    description="  Programs this facility takes part in. ",
                    value_descriptions={
                        " Planet Water Foundation ": " Clean water access. ",
                        "RISE": "   ",
                    },
                )
            ],
            self.embed_config,
        )

        field = self._saved()
        self.assertEqual(
            "Programs this facility takes part in.", field.description
        )
        self.assertEqual(
            {"Planet Water Foundation": "Clean water access."},
            field.value_descriptions,
        )

    def test_an_explanation_that_is_too_long_is_rejected(self):
        for overrides in (
            {"description": "x" * 301},
            {"value_descriptions": {"RISE": "x" * 301}},
        ):
            with self.assertRaises(ValidationError):
                create_embed_fields(
                    [self._field(0), self._field(1, **overrides)],
                    self.embed_config,
                )

        # Nothing is created when one field is rejected.
        self.assertFalse(
            EmbedField.objects.filter(embed_config=self.embed_config).exists()
        )

    def test_explanations_in_the_wrong_form_are_rejected(self):
        for overrides in (
            {"description": ["a list"]},
            {"value_descriptions": ["a list"]},
            {"value_descriptions": {"RISE": 5}},
            {
                "value_descriptions": {
                    "value {}".format(i): "x" for i in range(201)
                }
            },
        ):
            with self.assertRaises(ValidationError):
                create_embed_fields(
                    [self._field(**overrides)], self.embed_config
                )
