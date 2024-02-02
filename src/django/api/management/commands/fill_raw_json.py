from datetime import datetime
from django.core.management.base import BaseCommand

from api.helpers.helpers import (
    parse_raw_data,
    get_raw_json,
)

from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source


def delta_format(delta):
    hours, remainder = divmod(delta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


def count_with_percent(i: int, count: int) -> str:
    return '{} out of {} ({:.2f})%'.format(i, count, i / count * 100)


def update_raw_json(facility_list_item: FacilityListItem):
    if (facility_list_item.source.source_type == Source.SINGLE):
        facility_list_item.raw_header = ''
        facility_list_item.raw_json = parse_raw_data(
            facility_list_item.raw_data)
    else:
        facility_list_item.raw_header = \
            facility_list_item.source.facility_list.header
        facility_list_item.raw_json = get_raw_json(
            facility_list_item.raw_data, facility_list_item.raw_header)

    return facility_list_item


class Command(BaseCommand):
    help = 'Fill raw_json and raw_header columns in facility_list_item table.'

    def add_arguments(self, parser):
        parser.add_argument('--start_from', type=int)
        parser.add_argument('--size', type=int)

    def handle(self, *args, **options):

        items_query = FacilityListItem.objects.select_related(
            "source", "source__facility_list"
        ).filter(raw_json={}).order_by("id")
        count = items_query.count()
        items = items_query.all()
        start = datetime.now()
        batch_size = 2000
        id = 0
        print("{} - Init processing of: {} items".format(
            start.strftime('%Y-%m-%d %H:%M:%S'), count))
        while id < count:
            if (id == 0):
                print("{} - GO!!!!".format(
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            banch_items = [update_raw_json(item)
                           for item in items[id: min(count, id+batch_size)]]

            FacilityListItem.objects.bulk_update(
                banch_items,
                ['raw_header', 'raw_json'],
                batch_size,
            )
            id = min(count, id+batch_size)
            now = datetime.now()
            diff = now - start

            print("{} - In Progress: {} spend {} ".format(
                now.strftime('%Y-%m-%d %H:%M:%S'),
                count_with_percent(id, count), delta_format(diff)))

        print("Done")
