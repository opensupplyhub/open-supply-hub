from unittest.mock import Mock

from django.http import QueryDict
from django.test import SimpleTestCase

from api.pagination_keyset_helpers import create_query_hash


class CreateQueryHashTest(SimpleTestCase):
    def _request(self, query_string):
        return Mock(
            query_params=QueryDict(query_string),
            user=Mock(id=7),
        )

    def test_hash_includes_every_repeated_parameter_value(self):
        first = create_query_hash(
            self._request(
                'processing_type=CAPS&processing_type=cement'
                '&processing_type_exact=CAPS'
            ),
            100,
        )
        second = create_query_hash(
            self._request(
                'processing_type=caps&processing_type=cement'
                '&processing_type_exact=CAPS'
            ),
            100,
        )

        self.assertNotEqual(first, second)

    def test_hash_is_stable_across_parameter_order_and_pages(self):
        first = create_query_hash(
            self._request(
                'processing_type=CAPS&processing_type=cement&page=1'
            ),
            100,
        )
        second = create_query_hash(
            self._request(
                'page=2&processing_type=cement&processing_type=CAPS'
            ),
            100,
        )

        self.assertEqual(first, second)
