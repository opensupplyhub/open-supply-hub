from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityListItemTemp,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex
from api.signals import location_post_delete_handler_for_opensearch
from django.contrib.gis.geos import Point
from django.db.models.signals import post_delete
from django.test import TestCase

# ContriCleaner limits a submitted name or address to 200 characters, but
# its cleanup can add characters afterwards (a space after each comma), so
# the columns that store the cleaned value hold up to 300 (OSDEV-1085).
STORED_LENGTH = 300


class FacilityNameAddressLengthTest(TestCase):
    def setUp(self):
        # Facility deletion propagation to OpenSearch is outside the scope
        # of Django unit testing.
        post_delete.disconnect(
            location_post_delete_handler_for_opensearch,
            Facility
        )
        self.addCleanup(
            post_delete.connect,
            location_post_delete_handler_for_opensearch,
            Facility
        )

        user = User.objects.create(email='one@example.com')
        contributor = Contributor.objects.create(
            admin=user,
            name='test contributor 1',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='First List'
        )
        self.source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=contributor,
        )
        self.name = 'Pants Hut, ' + 'n' * (STORED_LENGTH - 11)
        self.address = '123 Main St, ' + 'a' * (STORED_LENGTH - 13)

    def test_stores_cleaned_name_and_address_longer_than_limit(self):
        list_item = FacilityListItem.objects.create(
            name=self.name,
            address=self.address,
            country_code='US',
            sector=['Apparel'],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )
        facility = Facility.objects.create(
            name=list_item.name,
            address=list_item.address,
            country_code='US',
            location=Point(0, 0),
            created_from=list_item,
        )

        list_item.refresh_from_db()
        self.assertEqual(len(list_item.name), STORED_LENGTH)
        self.assertEqual(len(list_item.address), STORED_LENGTH)

        # Dedupe Hub matching works on a verbatim copy of the list item.
        FacilityListItemTemp.copy(list_item)
        temp_item = FacilityListItemTemp.objects.get(id=list_item.id)
        self.assertEqual(temp_item.name, self.name)
        self.assertEqual(temp_item.address, self.address)

        facility.refresh_from_db()
        self.assertEqual(facility.name, self.name)
        self.assertEqual(facility.address, self.address)

        latest_history = facility.history.latest()
        self.assertEqual(latest_history.name, self.name)
        self.assertEqual(latest_history.address, self.address)

        # api_facilityindex is filled by the api_facility triggers.
        indexed = FacilityIndex.objects.get(id=facility.id)
        self.assertEqual(indexed.name, self.name)
        self.assertEqual(indexed.address, self.address)
