from unittest.mock import MagicMock, patch

from django.core.cache import caches
from django.test import TestCase, override_settings
from django.urls import reverse

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
            bundle_s3_key='taxonomy/isic4/v2/isicRev4Taxonomy.js',
        )

    @patch('api.isic_taxonomy.runtime_config.get_s3_client')
    def test_returns_enabled_config_with_presigned_bundle_url(
        self,
        mock_get_s3_client,
    ):
        s3_client = MagicMock()
        mock_get_s3_client.return_value = s3_client
        s3_client.generate_presigned_url.return_value = (
            'https://example.com/presigned/isicRev4Taxonomy.js'
        )

        response = self.client.get(reverse('taxonomy_config'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'isic4': {
                    'enabled': True,
                    'version': 2,
                    'bundleUrl': (
                        'https://example.com/presigned/isicRev4Taxonomy.js'
                    ),
                },
            },
        )
        s3_client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={
                'Bucket': 'test-bucket',
                'Key': 'taxonomy/isic4/v2/isicRev4Taxonomy.js',
            },
            ExpiresIn=3600,
        )

    @patch('api.isic_taxonomy.runtime_config.get_s3_client')
    def test_disabled_config_omits_bundle_url(self, mock_get_s3_client):
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
                    'bundleUrl': None,
                },
            },
        )
        mock_get_s3_client.assert_not_called()

    @patch('api.isic_taxonomy.runtime_config.get_s3_client')
    def test_response_is_cached_for_sixty_seconds(self, mock_get_s3_client):
        s3_client = MagicMock()
        mock_get_s3_client.return_value = s3_client
        s3_client.generate_presigned_url.return_value = (
            'https://example.com/presigned/isicRev4Taxonomy.js'
        )

        first = self.client.get(reverse('taxonomy_config'))
        second = self.client.get(reverse('taxonomy_config'))

        self.assertEqual(first.json(), second.json())
        s3_client.generate_presigned_url.assert_called_once()
        self.assertIsNotNone(
            caches['view_cache'].get(TAXONOMY_CONFIG_CACHE_KEY),
        )

    @patch('api.isic_taxonomy.runtime_config.get_s3_client')
    def test_cache_invalidates_after_toggle(self, mock_get_s3_client):
        s3_client = MagicMock()
        mock_get_s3_client.return_value = s3_client
        s3_client.generate_presigned_url.return_value = (
            'https://example.com/presigned/isicRev4Taxonomy.js'
        )

        self.client.get(reverse('taxonomy_config'))
        s3_client.generate_presigned_url.assert_called_once()

        self.config.is_active = False
        self.config.save()
        invalidate_taxonomy_config_cache()

        response = self.client.get(reverse('taxonomy_config'))
        self.assertFalse(response.json()['isic4']['enabled'])
        self.assertIsNone(response.json()['isic4']['bundleUrl'])
        self.assertEqual(s3_client.generate_presigned_url.call_count, 1)

    @patch('api.isic_taxonomy.runtime_config.get_s3_client')
    def test_environment_js_includes_isic4_fields(self, mock_get_s3_client):
        s3_client = MagicMock()
        mock_get_s3_client.return_value = s3_client
        s3_client.generate_presigned_url.return_value = (
            'https://example.com/presigned/isicRev4Taxonomy.js'
        )

        response = self.client.get(reverse('environment'))

        self.assertEqual(response.status_code, 200)
        body = response.content.decode('utf-8')
        self.assertIn("'ISIC4_TAXONOMY_ENABLED': 'true'", body)
        self.assertIn("'ISIC4_TAXONOMY_VERSION': '2'", body)
        self.assertIn(
            "'ISIC4_TAXONOMY_BUNDLE_URL': "
            "'https://example.com/presigned/isicRev4Taxonomy.js'",
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
                'ISIC4_TAXONOMY_BUNDLE_URL': '',
            },
        )
