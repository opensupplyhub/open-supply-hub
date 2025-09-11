# ---------------------------------------------------------------------------
# NOTE: Test framework used: django.test.TestCase (unittest-style).
# These tests are compatible with pytest/pytest-django if present in the repo.
# Focus: Comprehensive validation of PartnerField per recent diff.
# ---------------------------------------------------------------------------

import time
import uuid

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase


def _get_partner_field_model():
    """
    Resolve the PartnerField model dynamically from installed apps to avoid
    hard-coding import paths. This works across app/module refactors.
    """
    for model in apps.get_models():
        if model.__name__ == "PartnerField":
            return model
    raise AssertionError("PartnerField model not found in installed apps.")


class PartnerFieldModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.PartnerField = _get_partner_field_model()

    # ----- Meta and field definitions -------------------------------------------------

    def test_meta_verbose_name_plural_is_partner_field(self):
        self.assertEqual(self.PartnerField._meta.verbose_name_plural, "partner field")

    def test_field_metadata_and_help_texts(self):
        uuid_f = self.PartnerField._meta.get_field("uuid")
        self.assertFalse(uuid_f.editable)
        self.assertEqual(uuid_f.help_text, "Unique identifier for the partner field.")

        name_f = self.PartnerField._meta.get_field("name")
        self.assertTrue(name_f.primary_key)
        self.assertEqual(name_f.max_length, 200)
        self.assertEqual(name_f.help_text, "The partner field name.")

        type_f = self.PartnerField._meta.get_field("type")
        self.assertEqual(type_f.max_length, 200)
        self.assertFalse(type_f.null)
        self.assertFalse(type_f.blank)
        self.assertEqual(type_f.help_text, "The partner field type.")
        self.assertEqual(type_f.choices, self.PartnerField.TYPE_CHOICES)

    def test_type_choices_definition(self):
        expected = {
            ("int", "int"),
            ("float", "float"),
            ("string", "string"),
            ("object", "object"),
        }
        self.assertEqual(set(self.PartnerField.TYPE_CHOICES), expected)

    # ----- Instance behavior ----------------------------------------------------------

    def test_str_returns_name(self):
        obj = self.PartnerField.objects.create(name="age", type=self.PartnerField.INT)
        self.assertEqual(str(obj), "age")

    def test_uuid_defaults_and_is_unique(self):
        a = self.PartnerField.objects.create(name="n1", type=self.PartnerField.INT)

        b = self.PartnerField.objects.create(name="n2", type=self.PartnerField.FLOAT)
        self.assertIsInstance(a.uuid, uuid.UUID)
        self.assertIsInstance(b.uuid, uuid.UUID)
        self.assertNotEqual(a.uuid, b.uuid)

    def test_created_at_and_updated_at_are_set_and_update(self):
        obj = self.PartnerField.objects.create(name="ts_check", type=self.PartnerField.INT)
        self.assertIsNotNone(obj.created_at)
        self.assertIsNotNone(obj.updated_at)
        initial_updated_at = obj.updated_at
        # Ensure timestamp resolution differences across DBs won't cause flakes
        time.sleep(0.05)
        obj.type = self.PartnerField.FLOAT
        obj.save()
        obj.refresh_from_db()
        self.assertGreater(obj.updated_at, initial_updated_at)

    # ----- Validation: choices, required, lengths, uniqueness ------------------------

    def test_type_choices_accept_valid_values(self):
        for choice_value, _ in self.PartnerField.TYPE_CHOICES:
            instance = self.PartnerField(name=f"ok_{choice_value}", type=choice_value)
            # Should not raise
            instance.full_clean()

    def test_type_choices_reject_invalid_value(self):
        instance = self.PartnerField(name="bad", type="boolean")
        with self.assertRaises(ValidationError):
            instance.full_clean()

    def test_type_blank_and_none_invalid(self):
        blank = self.PartnerField(name="blank", type="")
        with self.assertRaises(ValidationError):
            blank.full_clean()

        nonev = self.PartnerField(name="none", type=None)
        with self.assertRaises(ValidationError):
            nonev.full_clean()

    def test_name_max_length_validation(self):
        long_name = "x" * 201
        instance = self.PartnerField(name=long_name, type=self.PartnerField.STRING)
        with self.assertRaises(ValidationError):
            instance.full_clean()

    def test_name_is_primary_key_and_uniqueness_enforced(self):
        self.PartnerField.objects.create(name="dup", type=self.PartnerField.STRING)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.PartnerField.objects.create(name="dup", type=self.PartnerField.OBJECT)