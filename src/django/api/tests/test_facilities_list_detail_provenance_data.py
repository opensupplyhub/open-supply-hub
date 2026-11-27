from django.contrib.gis.geos import Point
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase

from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.serializers.facility.facility_query_params_serializer import (
    DETAIL_PROVENANCE_DATA_REQUIRES_DETAIL,
)


FACILITIES_URL = '/api/facilities/'

PROVENANCE_VALUES = {
    'source_name': 'US EPA FRS',
    'source_link': 'https://example.com/dc?id=1',
    'information_source_type': 'air quality permit',
    'date_of_source': '2024-06',
    'notes': 'Values copied from the permit.',
    'data_collection_methodology': 'Desk research',
    'ai_usage_notes': 'AI-extracted; human reviewed',
}


class FacilitiesListDetailProvenanceDataTest(APITestCase):
    """OSDEV-3751: `detail_provenance_data` fills the `provenance` of the
    extended fields returned by `GET /api/facilities/?detail=true`."""

    def setUp(self):
        user = User.objects.create(email='provenance-list@example.com')
        self.contributor = Contributor.objects.create(
            admin=user,
            name='Provenance Contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='Provenance List'
        )
        self.source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

    def _create_facility(self, row_index, **provenance):
        '''Create a facility whose `name_operator` extended field was
        contributed through a list item carrying `provenance`.'''
        list_item = FacilityListItem.objects.create(
            name='Facility {}'.format(row_index),
            address='Address {}'.format(row_index),
            country_code='US',
            sector=['Apparel'],
            row_index=row_index,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
            **provenance,
        )
        facility = Facility.objects.create(
            name='Facility {}'.format(row_index),
            address='Address {}'.format(row_index),
            country_code='US',
            location=Point(0, 0),
            created_from=list_item,
        )
        FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=facility,
            facility_list_item=list_item,
            confidence=0.85,
            results='',
        )
        list_item.facility = facility
        list_item.save()

        ExtendedField.objects.create(
            contributor=self.contributor,
            facility=facility,
            facility_list_item=list_item,
            field_name=ExtendedField.NAME_OPERATOR,
            value={'raw_value': 'Operator {}'.format(row_index)},
        )
        return facility, list_item

    def _get(self, query):
        return self.client.get('{}?{}'.format(FACILITIES_URL, query))

    @staticmethod
    def _provenance_queries(queries):
        return [
            query['sql'] for query in queries.captured_queries
            if '"api_facilitylistitem"."source_name"' in query['sql']
        ]

    @staticmethod
    def _operator_entries(response, facility):
        feature = next(
            feature for feature in response.json()['features']
            if feature['id'] == facility.id
        )
        return feature['properties']['extended_fields']['name_operator']

    def test_provenance_is_null_without_the_param(self):
        facility, _ = self._create_facility(1, **PROVENANCE_VALUES)

        with CaptureQueriesContext(connection) as queries:
            response = self._get('detail=true')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._provenance_queries(queries), [])
        entries = self._operator_entries(response, facility)
        self.assertEqual(len(entries), 1)
        self.assertIsNone(entries[0]['provenance'])
        self.assertFalse(response.json()['params']['detail_provenance_data'])

    def test_provenance_is_filled_with_the_param(self):
        facility, list_item = self._create_facility(1, **PROVENANCE_VALUES)

        response = self._get('detail=true&detail_provenance_data=true')

        self.assertEqual(response.status_code, 200)
        entries = self._operator_entries(response, facility)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['provenance'], {
            **PROVENANCE_VALUES,
            'added_on_date': list_item.created_at.date().isoformat(),
        })
        self.assertTrue(response.json()['params']['detail_provenance_data'])

    def test_list_item_without_provenance_values_has_added_on_date(self):
        facility, list_item = self._create_facility(1)

        response = self._get('detail=true&detail_provenance_data=true')

        self.assertEqual(response.status_code, 200)
        entries = self._operator_entries(response, facility)
        self.assertEqual(entries[0]['provenance'], {
            'added_on_date': list_item.created_at.date().isoformat(),
        })

    def test_requires_detail(self):
        self._create_facility(1, **PROVENANCE_VALUES)

        for query in (
            'detail_provenance_data=true',
            'detail=false&detail_provenance_data=true',
        ):
            response = self._get(query)

            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.json()['detail_provenance_data'],
                [DETAIL_PROVENANCE_DATA_REQUIRES_DETAIL],
            )

    def test_provenance_is_loaded_in_one_query_per_page(self):
        facilities = [
            self._create_facility(
                index, source_name='Source {}'.format(index)
            )
            for index in range(1, 4)
        ]

        with CaptureQueriesContext(connection) as queries:
            response = self._get('detail=true&detail_provenance_data=true')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self._provenance_queries(queries)), 1)

        for index, (facility, _) in enumerate(facilities, start=1):
            entries = self._operator_entries(response, facility)
            self.assertEqual(
                entries[0]['provenance']['source_name'],
                'Source {}'.format(index),
            )
