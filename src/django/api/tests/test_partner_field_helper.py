from django.test import SimpleTestCase

from api.serializers.facility.partner_field_helper import (
    apply_schema_defaults,
)


class ApplySchemaDefaultsNonDictValueTest(SimpleTestCase):
    """apply_schema_defaults returns non-dict values unchanged."""

    def test_none_value(self):
        result = apply_schema_defaults(None, {"properties": {"a": {}}})
        self.assertIsNone(result)

    def test_string_value(self):
        result = apply_schema_defaults("hello", {"properties": {"a": {}}})
        self.assertEqual(result, "hello")

    def test_list_value(self):
        result = apply_schema_defaults([1, 2], {"properties": {"a": {}}})
        self.assertEqual(result, [1, 2])

    def test_integer_value(self):
        result = apply_schema_defaults(42, {"properties": {"a": {}}})
        self.assertEqual(result, 42)


class ApplySchemaDefaultsInvalidSchemaTest(SimpleTestCase):
    """apply_schema_defaults returns value unchanged for unusable schemas."""

    def test_none_schema(self):
        value = {"a": 1}
        result = apply_schema_defaults(value, None)
        self.assertEqual(result, {"a": 1})

    def test_string_schema(self):
        value = {"a": 1}
        result = apply_schema_defaults(value, "not a schema")
        self.assertEqual(result, {"a": 1})

    def test_schema_without_properties_key(self):
        value = {"a": 1}
        result = apply_schema_defaults(value, {"type": "object"})
        self.assertEqual(result, {"a": 1})

    def test_schema_with_non_dict_properties(self):
        value = {"a": 1}
        result = apply_schema_defaults(value, {"properties": "bad"})
        self.assertEqual(result, {"a": 1})

    def test_schema_with_none_properties(self):
        value = {"a": 1}
        result = apply_schema_defaults(value, {"properties": None})
        self.assertEqual(result, {"a": 1})


class ApplySchemaDefaultsSubSchemaSkipTest(SimpleTestCase):
    """Non-dict sub-schemas are silently skipped."""

    def test_string_sub_schema_is_skipped(self):
        value = {}
        schema = {"properties": {"a": "not a dict"}}
        apply_schema_defaults(value, schema)
        self.assertEqual(value, {})

    def test_none_sub_schema_is_skipped(self):
        value = {}
        schema = {"properties": {"a": None}}
        apply_schema_defaults(value, schema)
        self.assertEqual(value, {})

    def test_valid_sub_schema_still_processed_alongside_invalid(self):
        value = {}
        schema = {
            "properties": {
                "bad": "not a dict",
                "good": {"default": 10},
            }
        }
        apply_schema_defaults(value, schema)
        self.assertNotIn("bad", value)
        self.assertEqual(value["good"], 10)


class ApplySchemaDefaultsPrimitiveDefaultsTest(SimpleTestCase):
    """Missing keys with a 'default' in their sub-schema get populated."""

    def test_string_default(self):
        value = {}
        schema = {"properties": {"color": {"default": "red"}}}
        apply_schema_defaults(value, schema)
        self.assertEqual(value["color"], "red")

    def test_integer_default(self):
        value = {}
        schema = {"properties": {"count": {"default": 0}}}
        apply_schema_defaults(value, schema)
        self.assertEqual(value["count"], 0)

    def test_boolean_false_default(self):
        value = {}
        schema = {"properties": {"enabled": {"default": False}}}
        apply_schema_defaults(value, schema)
        self.assertIs(value["enabled"], False)

    def test_none_default(self):
        value = {}
        schema = {"properties": {"optional": {"default": None}}}
        apply_schema_defaults(value, schema)
        self.assertIn("optional", value)
        self.assertIsNone(value["optional"])

    def test_list_default(self):
        value = {}
        schema = {"properties": {"tags": {"default": ["a", "b"]}}}
        apply_schema_defaults(value, schema)
        self.assertEqual(value["tags"], ["a", "b"])

    def test_multiple_defaults_applied(self):
        value = {}
        schema = {
            "properties": {
                "x": {"default": 1},
                "y": {"default": 2},
                "z": {"default": 3},
            }
        }
        apply_schema_defaults(value, schema)
        self.assertEqual(value, {"x": 1, "y": 2, "z": 3})


class ApplySchemaDefaultsExistingKeysPreservedTest(SimpleTestCase):
    """Keys already present in value are never overwritten by defaults."""

    def test_existing_value_not_replaced_by_default(self):
        value = {"color": "blue"}
        schema = {"properties": {"color": {"default": "red"}}}
        apply_schema_defaults(value, schema)
        self.assertEqual(value["color"], "blue")

    def test_existing_falsy_value_not_replaced(self):
        value = {"count": 0}
        schema = {"properties": {"count": {"default": 99}}}
        apply_schema_defaults(value, schema)
        self.assertEqual(value["count"], 0)

    def test_existing_none_not_replaced(self):
        value = {"field": None}
        schema = {"properties": {"field": {"default": "fallback"}}}
        apply_schema_defaults(value, schema)
        self.assertIsNone(value["field"])

    def test_existing_empty_string_not_replaced(self):
        value = {"name": ""}
        schema = {"properties": {"name": {"default": "unnamed"}}}
        apply_schema_defaults(value, schema)
        self.assertEqual(value["name"], "")


class ApplySchemaDefaultsMissingKeyNoDefaultTest(SimpleTestCase):
    """Missing keys without a default and without object type stay absent."""

    def test_missing_key_no_default(self):
        value = {}
        schema = {"properties": {"optional": {"type": "string"}}}
        apply_schema_defaults(value, schema)
        self.assertNotIn("optional", value)

    def test_empty_sub_schema(self):
        value = {}
        schema = {"properties": {"field": {}}}
        apply_schema_defaults(value, schema)
        self.assertNotIn("field", value)


class ApplySchemaDefaultsNestedObjectCreationTest(SimpleTestCase):
    """Missing keys whose sub-schema is type=object with properties get {}."""

    def test_missing_object_key_gets_empty_dict(self):
        value = {}
        schema = {
            "properties": {
                "address": {
                    "type": "object",
                    "properties": {"city": {"default": "Unknown"}},
                }
            }
        }
        apply_schema_defaults(value, schema)
        self.assertIn("address", value)
        self.assertIsInstance(value["address"], dict)

    def test_created_object_gets_its_own_defaults_applied(self):
        value = {}
        schema = {
            "properties": {
                "address": {
                    "type": "object",
                    "properties": {
                        "city": {"default": "Unknown"},
                        "zip": {"default": "00000"},
                    },
                }
            }
        }
        apply_schema_defaults(value, schema)
        self.assertEqual(
            value, {"address": {"city": "Unknown", "zip": "00000"}}
        )

    def test_object_without_properties_key_not_created(self):
        """type=object but no 'properties' -> treated as primitive."""
        value = {}
        schema = {
            "properties": {
                "blob": {"type": "object"},
            }
        }
        apply_schema_defaults(value, schema)
        self.assertNotIn("blob", value)

    def test_object_type_with_empty_properties_not_created(self):
        """type=object with properties={} -> has 'properties' key, so {} is
        inserted, but there are no sub-defaults to apply."""
        value = {}
        schema = {
            "properties": {
                "meta": {"type": "object", "properties": {}},
            }
        }
        apply_schema_defaults(value, schema)
        self.assertEqual(value, {"meta": {}})


class ApplySchemaDefaultsRecursionTest(SimpleTestCase):
    """Defaults are applied recursively into already-present nested dicts."""

    def test_defaults_applied_inside_existing_nested_dict(self):
        value = {"address": {"city": "Paris"}}
        schema = {
            "properties": {
                "address": {
                    "type": "object",
                    "properties": {
                        "city": {"default": "Unknown"},
                        "country": {"default": "Unknown"},
                    },
                }
            }
        }
        apply_schema_defaults(value, schema)
        self.assertEqual(value["address"]["city"], "Paris")
        self.assertEqual(value["address"]["country"], "Unknown")

    def test_three_levels_deep(self):
        value = {"level1": {"level2": {}}}
        schema = {
            "properties": {
                "level1": {
                    "type": "object",
                    "properties": {
                        "level2": {
                            "type": "object",
                            "properties": {
                                "level3": {"default": "deep"},
                            },
                        }
                    },
                }
            }
        }
        apply_schema_defaults(value, schema)
        self.assertEqual(value["level1"]["level2"]["level3"], "deep")

    def test_three_levels_all_created_from_scratch(self):
        value = {}
        schema = {
            "properties": {
                "a": {
                    "type": "object",
                    "properties": {
                        "b": {
                            "type": "object",
                            "properties": {
                                "c": {"default": "leaf"},
                            },
                        }
                    },
                }
            }
        }
        apply_schema_defaults(value, schema)
        self.assertEqual(value, {"a": {"b": {"c": "leaf"}}})


class ApplySchemaDefaultsMixedScenarioTest(SimpleTestCase):
    """Real-world-like schemas with a mix of present/absent/nested keys."""

    def test_mixed_present_absent_and_nested(self):
        value = {"name": "Acme", "details": {"year": 2020}}
        schema = {
            "properties": {
                "name": {"default": "Unnamed"},
                "active": {"default": True},
                "details": {
                    "type": "object",
                    "properties": {
                        "year": {"default": 1970},
                        "verified": {"default": False},
                    },
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "source": {"default": "manual"},
                    },
                },
            }
        }
        apply_schema_defaults(value, schema)

        self.assertEqual(value["name"], "Acme")
        self.assertIs(value["active"], True)
        self.assertEqual(value["details"]["year"], 2020)
        self.assertIs(value["details"]["verified"], False)
        self.assertEqual(value["metadata"], {"source": "manual"})

    def test_no_defaults_in_schema_leaves_value_unchanged(self):
        original = {"x": 1, "y": 2}
        value = dict(original)
        schema = {
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "z": {"type": "string"},
            }
        }
        apply_schema_defaults(value, schema)
        self.assertEqual(value, original)


class ApplySchemaDefaultsReturnValueTest(SimpleTestCase):
    """The function returns the same object it was given (mutated in place)."""

    def test_returns_same_dict_object(self):
        value = {"a": 1}
        schema = {"properties": {"b": {"default": 2}}}
        result = apply_schema_defaults(value, schema)
        self.assertIs(result, value)

    def test_returns_non_dict_as_is(self):
        sentinel = object()
        result = apply_schema_defaults(sentinel, {"properties": {}})
        self.assertIs(result, sentinel)
