import logging
from unittest.mock import Mock, MagicMock, patch
from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    Source,
    User
)
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.gis.geos import Point

logger = logging.getLogger(__name__)

class ProductionLocationsTest(APITestCase):
    def setUp(self):
        self.email = "test_first@example.com"
        self.password = "example123"
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.production_locations_list = FacilityList.objects.create(
            header="header", file_name="list", name="List"
        )

        self.production_locations_contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.production_locations_source = Source.objects.create(
            facility_list=self.production_locations_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.production_locations_contributor,
        )

        self.list_item_1 = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.production_locations_source,
        )

    @patch('api.services.search.OpenSearchService.search_production_locations')
    @patch('api.services.opensearch.OpenSearchServiceConnection.__new__')
    def test_all_production_locations(self, mock_new, mock_search):
        mock_new.return_value = MagicMock()

        mock_search.return_value = {
            'hits': {
                'hits': [
                    {
                        '_source': {
                            'id': '1',
                            'name': 'Test Facility',
                            'address': 'Test Address',
                            'country_code': 'US',
                            'sector': ['Apparel']
                        }
                    }
                ]
            }
        }

        response = self.client.get("/api/v1/production-locations")
        logger.info(f'@@@ response is {response}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Facility', response.content.decode())
