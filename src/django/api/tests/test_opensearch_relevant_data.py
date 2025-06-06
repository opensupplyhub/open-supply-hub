import unittest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from api.services.opensearch.search import \
    OpenSearchService
from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from django.contrib.gis.geos import Point


class TestPrepareOpenSearchResponse(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.service = OpenSearchService(client=self.mock_client)

        self.email = "user@example.com"
        self.password = "password"
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.contributor = Contributor(name="Contributor", admin=self.user)
        self.contributor.save()

        self.list_one = FacilityList.objects.create(
            header="header", file_name="one", name="list"
        )

        self.source_one = Source.objects.create(
            facility_list=self.list_one,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item_one = FacilityListItem.objects.create(
            name="name",
            address="address",
            country_code="US",
            sector=["Apparel"],
            source=self.source_one,
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source_uuid=self.source_one,
        )

        self.facility = Facility.objects.create(
            name="name",
            address="address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_one,
        )

        self.old_updated_at = '2019-03-24 02:23:22.195 +0100'

        self.facility.updated_at = self.old_updated_at
        self.facility.save()

    @patch('api.services.opensearch.search.logger')
    def test_update_facility_updated_at_field(self, mock_logger):
        current_time = timezone.now()
        Facility.update_facility_updated_at_field(self.facility.id)
        new_updated_at = self.facility.updated_at
        self.assertEqual(current_time.replace(microsecond=0),
                         new_updated_at.replace(microsecond=0))
        self.assertNotEqual(self.old_updated_at, new_updated_at)
        mock_logger.warning.assert_not_called()


if __name__ == '__main__':
    unittest.main()
