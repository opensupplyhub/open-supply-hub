from typing import List
from ...models import (
    FacilityList,
    FacilityListItem,
    Source,
)

from django.core.management.base import (BaseCommand)


def create_facility_list() -> FacilityList:
    facility_props = {
        "status": FacilityList.APPROVED,
        "name": "Very New Facility List",
        "match_responsibility": "moderator",
        "description": "Some not empty description",
        "header": "country,name,address,sector,lat,lng",
    }
    facility_list = FacilityList(**facility_props)
    facility_list.save()

    print(f'FacilityListItem: {facility_list}')

    return facility_list


def create_source(facility_list: FacilityList) -> Source:
    source_props = {
        "create": True,
        "is_active": True,
        "is_public": True,
        "contributor_id": 2,
        "facility_list_id": facility_list.id
    }
    source = Source(**source_props)
    source.save()

    print(f'Source: {source}')
    return source


def create_facility_list_item(source: Source, i: int) -> FacilityListItem:
    facility_list_item_props = {
        "row_index": 40,
        "raw_data": f"Gaizhan {i}, Guizhou {i}",
        "name": f"Gaizhan {i}",
        "address": f"Guizhou {i}",
        "country_code": "CN",
        "status": FacilityListItem.MATCHED,
        "sector": r'{Apparel}',
        "source_id": source.id
    }
    facility_list_item = FacilityListItem(**facility_list_item_props)
    facility_list_item.save()
    print(f'FacilityListItem: {facility_list_item}')
    return facility_list_item


class Command(BaseCommand):
    help = 'Create facility list with content'

    def handle(self, *args, **options) -> None:
        facility_list = create_facility_list()
        source = create_source(facility_list)
        facility_list_items: List[FacilityListItem] = []

        for i in range(5):
            facility_list_item = create_facility_list_item(source, i)
            facility_list_items.append(facility_list_item)

        for facility_list_item in facility_list_items:
            facility_list_item.delete()

        source.delete()
        facility_list.delete()
