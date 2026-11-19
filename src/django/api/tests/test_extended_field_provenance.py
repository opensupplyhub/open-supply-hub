from django.test import TestCase

from api.helpers.provenance import (
    ADDED_ON_DATE_KEY,
    build_extended_field_provenance_map,
    collect_facility_list_item_ids,
)
from api.models import (
    Contributor,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.serializers.facility.facility_query_params_serializer import (
    DETAIL_PROVENANCE_DATA_REQUIRES_DETAIL,
    FacilityQueryParamsSerializer,
)


class BuildExtendedFieldProvenanceMapTest(TestCase):
    def setUp(self):
        user = User.objects.create(email='provenance@example.com')
        contributor = Contributor.objects.create(
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
            contributor=contributor,
        )

    def _create_list_item(self, row_index, **provenance):
        return FacilityListItem.objects.create(
            name='Item {}'.format(row_index),
            address='Address {}'.format(row_index),
            country_code='US',
            sector=['Apparel'],
            row_index=row_index,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
            **provenance,
        )

    @staticmethod
    def _added_on(item):
        return item.created_at.date().isoformat()

    def test_collect_ids_skips_missing_and_malformed_entries(self):
        self.assertEqual(
            collect_facility_list_item_ids([
                {'facility_list_item_id': 1},
                {'facility_list_item_id': 1},
                {'facility_list_item_id': None},
                {'field_name': 'name_operator'},
                'not-a-dict',
                {'facility_list_item_id': 2},
            ]),
            {1, 2},
        )

    def test_no_list_item_makes_no_query(self):
        with self.assertNumQueries(0):
            self.assertEqual(
                build_extended_field_provenance_map([
                    {'facility_list_item_id': None},
                    {'field_name': 'name_operator'},
                ]),
                {},
            )

    def test_returns_provenance_with_added_on_date(self):
        item = self._create_list_item(
            1,
            source_name='US EPA FRS',
            source_link='https://example.com/dc?id=1',
            information_source_type='air quality permit',
            date_of_source='2024-06',
            notes='Values copied from the permit.',
            data_collection_methodology='Desk research',
            ai_usage_notes='AI-extracted; human reviewed',
        )

        self.assertEqual(
            build_extended_field_provenance_map(
                [{'facility_list_item_id': item.id}]
            ),
            {
                item.id: {
                    'source_name': 'US EPA FRS',
                    'source_link': 'https://example.com/dc?id=1',
                    'information_source_type': 'air quality permit',
                    'date_of_source': '2024-06',
                    'notes': 'Values copied from the permit.',
                    'data_collection_methodology': 'Desk research',
                    'ai_usage_notes': 'AI-extracted; human reviewed',
                    ADDED_ON_DATE_KEY: self._added_on(item),
                },
            },
        )

    def test_empty_values_are_left_out(self):
        item = self._create_list_item(1, source_name='', notes='Some notes')

        self.assertEqual(
            build_extended_field_provenance_map(
                [{'facility_list_item_id': item.id}]
            ),
            {
                item.id: {
                    'notes': 'Some notes',
                    ADDED_ON_DATE_KEY: self._added_on(item),
                },
            },
        )

    def test_item_without_provenance_values_has_only_added_on_date(self):
        item = self._create_list_item(1)

        self.assertEqual(
            build_extended_field_provenance_map(
                [{'facility_list_item_id': item.id}]
            ),
            {item.id: {ADDED_ON_DATE_KEY: self._added_on(item)}},
        )

    def test_unknown_list_item_is_left_out(self):
        item = self._create_list_item(1, source_name='Known')
        missing_id = item.id + 1000

        result = build_extended_field_provenance_map([
            {'facility_list_item_id': item.id},
            {'facility_list_item_id': missing_id},
        ])

        self.assertIn(item.id, result)
        self.assertNotIn(missing_id, result)

    def test_many_list_items_load_in_one_query(self):
        items = [
            self._create_list_item(
                index, source_name='Source {}'.format(index)
            )
            for index in range(1, 6)
        ]

        with self.assertNumQueries(1):
            result = build_extended_field_provenance_map(
                {'facility_list_item_id': item.id} for item in items
            )

        self.assertEqual(set(result), {item.id for item in items})


class FacilityQueryParamsDetailProvenanceDataTest(TestCase):
    def test_defaults_to_false(self):
        params = FacilityQueryParamsSerializer(data={})
        self.assertTrue(params.is_valid())
        self.assertFalse(params.validated_data['detail_provenance_data'])

    def test_valid_together_with_detail(self):
        params = FacilityQueryParamsSerializer(
            data={'detail': 'true', 'detail_provenance_data': 'true'}
        )
        self.assertTrue(params.is_valid())
        self.assertTrue(params.validated_data['detail_provenance_data'])

    def test_invalid_without_detail(self):
        for data in (
            {'detail_provenance_data': 'true'},
            {'detail': 'false', 'detail_provenance_data': 'true'},
        ):
            params = FacilityQueryParamsSerializer(data=data)
            self.assertFalse(params.is_valid())
            self.assertEqual(
                params.errors['detail_provenance_data'],
                [DETAIL_PROVENANCE_DATA_REQUIRES_DETAIL],
            )
