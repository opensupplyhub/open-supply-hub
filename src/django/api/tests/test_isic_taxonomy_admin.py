from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from api.isic_taxonomy.admin_views import user_can_manage_isic_taxonomy
from api.isic_taxonomy.constants import MAX_FILE_SIZE_BYTES
from api.models.isic_taxonomy_config import IsicTaxonomyConfig
from api.models.user import User
from api.tests.test_isic_taxonomy import SAMPLE_CSV

LOC_MEM_VIEW_CACHE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'isic-taxonomy-admin-test-default',
    },
    'view_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'isic-taxonomy-admin-test-view',
    },
}


def create_staff_user(*, email='staff@test.com', with_permission=True):
    user = User.objects.create(
        email=email,
        is_staff=True,
        is_active=True,
    )
    user.set_password('password')
    user.save()

    if with_permission:
        content_type = ContentType.objects.get_for_model(IsicTaxonomyConfig)
        permission = Permission.objects.get(
            codename='change_isictaxonomyconfig',
            content_type=content_type,
        )
        user.user_permissions.add(permission)

    return user


TEST_STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


@override_settings(
    AWS_STORAGE_BUCKET_NAME='test-bucket',
    CACHES=LOC_MEM_VIEW_CACHE,
    STORAGES=TEST_STORAGES,
)
class IsicTaxonomyAdminViewTest(TestCase):
    def setUp(self):
        caches['view_cache'].clear()
        IsicTaxonomyConfig.objects.all().delete()
        IsicTaxonomyConfig.objects.create(
            pk=1,
            is_active=True,
            version=1,
            class_count=1,
        )
        self.admin_url = reverse('admin:api_isictaxonomyconfig_changelist')
        self.manager = create_staff_user()
        self.client.force_login(self.manager)

    def test_unauthenticated_user_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(self.admin_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login', response.url)

    def test_user_can_manage_requires_staff_and_permission(self):
        regular = User.objects.create(
            email='regular@test.com',
            is_staff=False,
            is_active=True,
        )
        staff_without_permission = create_staff_user(
            email='staff-no-perm@test.com',
            with_permission=False,
        )

        self.assertFalse(user_can_manage_isic_taxonomy(regular))
        self.assertFalse(
            user_can_manage_isic_taxonomy(staff_without_permission),
        )
        self.assertTrue(user_can_manage_isic_taxonomy(self.manager))

    def test_requires_change_permission(self):
        staff_without_permission = create_staff_user(
            email='staff-no-perm@test.com',
            with_permission=False,
        )
        self.client.force_login(staff_without_permission)

        response = self.client.get(self.admin_url)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            user_can_manage_isic_taxonomy(staff_without_permission),
        )

    def test_get_renders_admin_page(self):
        response = self.client.get(self.admin_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ISIC Taxonomy')
        self.assertContains(response, 'ISIC Rev 4 Taxonomy')
        self.assertContains(response, 'Current status')
        self.assertContains(response, 'Not recorded')

    @patch('api.isic_taxonomy.admin_views.load_published_isic4_taxonomy')
    def test_get_renders_published_hierarchy_after_refresh(
        self,
        mock_load_published,
    ):
        config = IsicTaxonomyConfig.load()
        config.json_s3_key = 'taxonomy/isic4/v1/isic_rev4.json'
        config.version = 1
        config.class_count = 1
        config.save()

        mock_load_published.return_value = {
            'sections': [
                {
                    'code': 'A',
                    'displayLabel': 'A - Agriculture',
                    'divisions': [
                        {
                            'code': '01',
                            'displayLabel': '01 - Crop production',
                            'groups': [
                                {
                                    'code': '011',
                                    'displayLabel': '011 - Crops',
                                    'classes': [
                                        {
                                            'displayLabel': (
                                                '0111 - Growing of cereals'
                                            ),
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        response = self.client.get(self.admin_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Taxonomy hierarchy')
        self.assertContains(response, 'Growing of cereals')
        mock_load_published.assert_called_once()

    def test_preview_renders_validation_errors(self):
        bad_csv = SimpleUploadedFile(
            'bad.csv',
            b'section,division\nA,1\n',
            content_type='text/csv',
        )

        response = self.client.post(
            self.admin_url,
            {
                'action': 'preview',
                'source_file': bad_csv,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Missing required column')
        self.assertIsNone(response.context['preview_taxonomy'])

    def test_preview_renders_hierarchy(self):
        upload = SimpleUploadedFile(
            'sample.csv',
            SAMPLE_CSV,
            content_type='text/csv',
        )

        response = self.client.post(
            self.admin_url,
            {
                'action': 'preview',
                'source_file': upload,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['preview_counts']['class_count'], 1)
        self.assertEqual(
            response.context['preview_taxonomy']['sections'][0]['code'],
            'A',
        )
        self.assertContains(response, 'Growing of cereals')

    def test_form_rejects_unsupported_file_type(self):
        upload = SimpleUploadedFile(
            'sample.pdf',
            SAMPLE_CSV,
            content_type='application/pdf',
        )

        response = self.client.post(
            self.admin_url,
            {
                'action': 'preview',
                'source_file': upload,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unsupported file type')

    def test_form_rejects_oversized_file(self):
        oversized = SimpleUploadedFile(
            'large.csv',
            b'x' * (MAX_FILE_SIZE_BYTES + 1),
            content_type='text/csv',
        )

        response = self.client.post(
            self.admin_url,
            {
                'action': 'preview',
                'source_file': oversized,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'size limit')

    @patch('api.isic_taxonomy.admin_views.publish_taxonomy')
    def test_publish_updates_config(self, mock_publish_taxonomy):
        mock_publish_taxonomy.return_value = {
            'version': 2,
            'counts': {
                'section_count': 1,
                'division_count': 1,
                'group_count': 1,
                'class_count': 1,
            },
            'taxonomy': {
                'sections': [
                    {
                        'code': 'A',
                        'label': 'A - Agriculture',
                        'divisions': [],
                    },
                ],
            },
        }
        upload = SimpleUploadedFile(
            'sample.csv',
            SAMPLE_CSV,
            content_type='text/csv',
        )

        response = self.client.post(
            self.admin_url,
            {
                'action': 'publish',
                'source_file': upload,
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_publish_taxonomy.assert_called_once()
        self.assertContains(response, 'sample.csv')
        config = IsicTaxonomyConfig.load()
        self.assertEqual(config.source_filename, 'sample.csv')
        self.assertEqual(
            response.context['preview_taxonomy']['sections'][0]['code'],
            'A',
        )

    @patch('api.isic_taxonomy.admin_views.publish_taxonomy')
    def test_publish_surfaces_validation_errors(self, mock_publish_taxonomy):
        from api.isic_taxonomy.errors import (
            IsicTaxonomyError,
            IsicTaxonomyValidationError,
        )

        mock_publish_taxonomy.side_effect = IsicTaxonomyValidationError([
            IsicTaxonomyError(message='Duplicate class code "0111".'),
        ])
        upload = SimpleUploadedFile(
            'sample.csv',
            SAMPLE_CSV,
            content_type='text/csv',
        )

        response = self.client.post(
            self.admin_url,
            {
                'action': 'publish',
                'source_file': upload,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Duplicate class code')
        self.assertContains(response, '0111')

    def test_disable_toggle_turns_off_active_config(self):
        response = self.client.post(
            self.admin_url,
            {'action': 'disable'},
        )

        self.assertRedirects(response, self.admin_url)
        config = IsicTaxonomyConfig.load()
        self.assertFalse(config.is_active)

    def test_enable_toggle_turns_on_inactive_config(self):
        config = IsicTaxonomyConfig.load()
        config.is_active = False
        config.save()

        response = self.client.post(
            self.admin_url,
            {'action': 'enable'},
        )

        self.assertRedirects(response, self.admin_url)
        config.refresh_from_db()
        self.assertTrue(config.is_active)
