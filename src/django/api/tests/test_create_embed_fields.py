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
