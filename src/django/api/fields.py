"""
Custom JSONTextField for Django.
Needed to preserve the key order when serializing to JSON.
"""

from django.db import models
from psycopg2.extras import Json


class JSONTextField(models.JSONField):
    """JSONField that uses PostgreSQL 'json' type instead of 'jsonb'.

    Two issues with using Django's JSONField with db_type='json':

    1. Read path: psycopg2's typecaster for the 'json' OID auto-deserializes
       values to Python objects, unlike 'jsonb' which returns raw strings.
       Django's from_db_value would call json.loads on the already-deserialized
       value, causing a TypeError.

    2. Write path: Django's adapt_json_value wraps values in psycopg2's Jsonb
       adapter, which casts as ::jsonb in SQL. This causes PostgreSQL to parse
       the value through jsonb (losing key order) before storing in the json
       column. We use psycopg2's Json adapter instead, which casts as ::json.
    """

    def db_type(self, connection):
        """
        Use the 'json' type instead of 'jsonb'.
        """
        return "json"

    def from_db_value(self, value, expression, connection):
        """
        Prevent Django from calling json.loads on an already-deserialized value.
        """
        if value is None:
            return value

        if not isinstance(value, str):
            return value

        return super().from_db_value(value, expression, connection)

    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Use psycopg2's Json adapter instead of Django's JSONField adapter.
        """
        if not prepared:
            value = self.get_prep_value(value)

        if value is None:
            return value

        return Json(value)
