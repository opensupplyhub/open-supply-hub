from django.test import TestCase
from rest_framework.test import APIClient

from api.models import AnnouncementBanner


class AnnouncementBannerModelTest(TestCase):
    def test_migration_seeds_a_single_inactive_row(self):
        self.assertEqual(AnnouncementBanner.objects.count(), 1)
        banner = AnnouncementBanner.objects.get()
        self.assertFalse(banner.is_active)
        self.assertEqual(banner.content, '')

    def test_save_clears_ckeditor_empty_placeholder(self):
        banner = AnnouncementBanner.objects.get()
        banner.content = '<p>&nbsp;</p>'
        banner.save()
        banner.refresh_from_db()
        self.assertEqual(banner.content, '')


class AnnouncementBannerViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api-announcement-banner/'
        self.banner = AnnouncementBanner.objects.get()

    def test_is_available_without_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_returns_inactive_by_default(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response.json(),
            {'is_active': False, 'content': ''},
        )

    def test_returns_content_when_active(self):
        content = '<p>Support us! <a href="https://example.test">Give</a></p>'
        self.banner.is_active = True
        self.banner.content = content
        self.banner.save()

        response = self.client.get(self.url)
        self.assertEqual(
            response.json(),
            {'is_active': True, 'content': content},
        )

    def test_active_banner_without_content_reports_inactive(self):
        self.banner.is_active = True
        self.banner.content = ''
        self.banner.save()

        response = self.client.get(self.url)
        self.assertEqual(
            response.json(),
            {'is_active': False, 'content': ''},
        )

    def test_inactive_banner_hides_content(self):
        self.banner.is_active = False
        self.banner.content = '<p>Not yet live</p>'
        self.banner.save()

        response = self.client.get(self.url)
        self.assertEqual(
            response.json(),
            {'is_active': False, 'content': ''},
        )
