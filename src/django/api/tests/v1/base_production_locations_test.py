from django.conf import settings
from rest_framework.test import APITestCase
from api.tests.opensearch.opensearch_test_case \
    import OpenSearchIntegrationTestCase

from api.models import (
    Contributor,
    User,
)


class BaseProductionLocationsTest(APITestCase, OpenSearchIntegrationTestCase):

    def setUp(self):
        super().setUp()

        self.open_search_client = self.getClient()

        setattr(settings, 'DEBUG', True)

        self.user_email = "test@example.com"
        self.user_password = "example123"
        self.user = User.objects.create(email=self.user_email)
        self.user.set_password(self.user_password)
        self.user.save()

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.superuser_email = "superuser@example.com"
        self.superuser_password = "superuser"

        self.superuser = User.objects.create_superuser(
            self.superuser_email, self.superuser_password
        )

        self.supercontributor = Contributor.objects.create(
            admin=self.superuser,
            name="test super contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

    def tearDown(self):
        setattr(settings, 'DEBUG', False)
