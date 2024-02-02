import json
import os

from django.core.management.base import (BaseCommand)
from api.helpers.helpers import get_raw_json

FIXTURES_DIRECTORY = '/usr/local/src/api/fixtures'


class Command(BaseCommand):
    help = 'Create random but reasonable data fixtures'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        filename = 'facility_list_items.json'
        f = open(os.path.join(FIXTURES_DIRECTORY, filename))
        data = json.load(f)
        for facility in data:
            facility['fields']['raw_header'] = ("country,name,address,"
                                                "sector,lat,lng")
            facility['fields']['raw_json'] = get_raw_json(
                facility['fields']['raw_data'],
                "country,name,address,sector,lat,lng")
        pass

        new_filename = "facility_list_items.json"
        out_file = open(os.path.join(FIXTURES_DIRECTORY, new_filename), "w")
        json.dump(data, out_file, indent=4)
        out_file.close()
