from unittest.mock import MagicMock, patch

from django.core.cache import caches
from django.test import TestCase, override_settings
from django.urls import reverse

from api.isic_taxonomy.content import (
    TAXONOMY_CONTENT_CACHE_KEY_PREFIX,
    invalidate_isic4_taxonomy_content_cache,
)
from api.isic_taxonomy.runtime_config import (
    TAXONOMY_CONFIG_CACHE_KEY,
    get_isic4_environment_vars,
    invalidate_taxonomy_config_cache,
)
from api.models.isic_taxonomy_config import IsicTaxonomyConfig

LOC_MEM_VIEW_CACHE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'taxonomy-config-test-default',
    },
    'view_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'taxonomy-config-test-view',
    },
}


@override_settings(
    AWS_STORAGE_BUCKET_NAME='test-bucket',
    CACHES=LOC_MEM_VIEW_CACHE,
)
class TaxonomyConfigAPITest(TestCase):
    def setUp(self):
        caches['view_cache'].clear()
        IsicTaxonomyConfig.objects.all().delete()
        self.config = IsicTaxonomyConfig.objects.create(
            pk=1,
            is_active=True,
            version=2,
            json_s3_key='taxonomy/isic4/v2/isic_rev4.json',
        )

    def test_returns_enabled_config_with_taxonomy_url(self):
        response = self.client.get(reverse('taxonomy_config'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'isic4': {
                    'enabled': True,
                    'version': 2,
                    'taxonomyUrl': reverse('isic_taxonomy'),
                },
            },
        )

    def test_disabled_config_omits_taxonomy_url(self):
        self.config.is_active = False
        self.config.save()

        response = self.client.get(reverse('taxonomy_config'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'isic4': {
                    'enabled': False,
                    'version': 2,
                    'taxonomyUrl': None,
                },
            },
        )

    def test_response_is_cached_for_sixty_seconds(self):
        first = self.client.get(reverse('taxonomy_config'))
        second = self.client.get(reverse('taxonomy_config'))

        self.assertEqual(first.json(), second.json())
        self.assertIsNotNone(
            caches['view_cache'].get(TAXONOMY_CONFIG_CACHE_KEY),
        )

    def test_cache_invalidates_after_toggle(self):
        self.client.get(reverse('taxonomy_config'))

        self.config.is_active = False
        self.config.save()
        invalidate_taxonomy_config_cache()

        response = self.client.get(reverse('taxonomy_config'))
        self.assertFalse(response.json()['isic4']['enabled'])
        self.assertIsNone(response.json()['isic4']['taxonomyUrl'])

    def test_environment_js_includes_isic4_fields(self):
        response = self.client.get(reverse('environment'))

        self.assertEqual(response.status_code, 200)
        body = response.content.decode('utf-8')
        self.assertIn("'ISIC4_TAXONOMY_ENABLED': 'true'", body)
        self.assertIn("'ISIC4_TAXONOMY_VERSION': '2'", body)
        self.assertIn(
            "'ISIC4_TAXONOMY_URL': "
            f"'{reverse('isic_taxonomy')}'",
            body,
        )

    def test_environment_vars_when_disabled(self):
        self.config.is_active = False
        self.config.save()

        env_vars = get_isic4_environment_vars(config=self.config)

        self.assertEqual(
            env_vars,
            {
                'ISIC4_TAXONOMY_ENABLED': 'false',
                'ISIC4_TAXONOMY_VERSION': '2',
                'ISIC4_TAXONOMY_URL': '',
            },
        )


@override_settings(
    AWS_STORAGE_BUCKET_NAME='test-bucket',
    CACHES=LOC_MEM_VIEW_CACHE,
)
class IsicTaxonomyAPITest(TestCase):
    SAMPLE_TAXONOMY = {
        'sections': [
            {
                'code': 'A',
                'label': 'Agriculture',
                'displayLabel': 'A - Agriculture',
                'kind': 'section',
                'divisions': [],
            },
        ],
    }

    def setUp(self):
        caches['view_cache'].clear()
        IsicTaxonomyConfig.objects.all().delete()
        self.config = IsicTaxonomyConfig.objects.create(
            pk=1,
            is_active=True,
            version=3,
            json_s3_key='taxonomy/isic4/v3/isic_rev4.json',
        )

    @patch('api.isic_taxonomy.content.get_s3_client')
    def test_returns_taxonomy_json_from_private_bucket(self, mock_get_s3_client):
        s3_client = MagicMock()
        mock_get_s3_client.return_value = s3_client
        s3_client.get_object.return_value = {
            'Body': MagicMock(
                read=MagicMock(
                    return_value=(
                        '{"sections": [{"code": "A", "label": "Agriculture", '
                        '"displayLabel": "A - Agriculture", "kind": "section", '
                        '"divisions": []}]}'
                    ).encode('utf-8'),
                ),
            ),
        }

        response = self.client.get(reverse('isic_taxonomy'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.SAMPLE_TAXONOMY)
        s3_client.get_object.assert_called_once_with(
            Bucket='test-bucket',
            Key='taxonomy/isic4/v3/isic_rev4.json',
        )

    @patch('api.isic_taxonomy.content.get_s3_client')
    def test_response_is_cached_by_version(self, mock_get_s3_client):
        s3_client = MagicMock()
        mock_get_s3_client.return_value = s3_client
        s3_client.get_object.return_value = {
            'Body': MagicMock(
                read=MagicMock(
                    return_value=b'{"sections": []}',
                ),
            ),
        }

        first = self.client.get(reverse('isic_taxonomy'))
        second = self.client.get(reverse('isic_taxonomy'))

        self.assertEqual(first.json(), second.json())
        s3_client.get_object.assert_called_once()
        self.assertIsNotNone(
            caches['view_cache'].get(
                f'{TAXONOMY_CONTENT_CACHE_KEY_PREFIX}:v3',
            ),
        )

    @patch('api.isic_taxonomy.content.get_s3_client')
    def test_cache_invalidates_after_publish(self, mock_get_s3_client):
        s3_client = MagicMock()
        mock_get_s3_client.return_value = s3_client
        s3_client.get_object.return_value = {
            'Body': MagicMock(
                read=MagicMock(
                    return_value=b'{"sections": []}',
                ),
            ),
        }

        self.client.get(reverse('isic_taxonomy'))
        s3_client.get_object.assert_called_once()

        invalidate_isic4_taxonomy_content_cache(version=3)
        self.client.get(reverse('isic_taxonomy'))
        self.assertEqual(s3_client.get_object.call_count, 2)

    def test_returns_not_found_when_disabled(self):
        self.config.is_active = False
        self.config.save()

        response = self.client.get(reverse('isic_taxonomy'))

        self.assertEqual(response.status_code, 404)

    def test_returns_not_found_when_taxonomy_is_not_published(self):
        self.config.json_s3_key = ''
        self.config.save()

        response = self.client.get(reverse('isic_taxonomy'))

        self.assertEqual(response.status_code, 404)
