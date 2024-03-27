import os
import sys
import logging
import asyncio

from django.core.management.base import BaseCommand
from django.db import transaction

from api.constants import ProcessingAction
from api.models import (
    FacilityList, FacilityListItem, FacilityListItemTemp, Source
)
from api.processing import (parse_facility_list_item,
                            geocode_facility_list_item,
                            ItemRemovedException)
from api.mail import notify_facility_list_complete
from api.kafka_producer import produce_message_match_process

LINE_ITEM_ACTIONS = {
    ProcessingAction.PARSE: parse_facility_list_item,
    ProcessingAction.GEOCODE: geocode_facility_list_item,
}

LIST_ACTIONS = set([ProcessingAction.MATCH, ProcessingAction.NOTIFY_COMPLETE])

VALID_ACTIONS = list(LINE_ITEM_ACTIONS.keys()) + list(LIST_ACTIONS)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run an action on all items in a facility list. If ' \
           'AWS_BATCH_JOB_ARRAY_INDEX environment variable is set, will ' \
           'process those items whose row_index matches it. Otherwise, will ' \
           'process all items for the given facility list.'

    def add_arguments(self, parser):
        # Create a group of arguments explicitly labeled as required,
        # because by default named arguments are considered optional.
        group = parser.add_argument_group('required arguments')
        group.add_argument('-a', '--action',
                           required=True,
                           help='The processing action to perform. '
                                'One of "parse", "geocode", "match"')
        group.add_argument('-l', '--list-id',
                           required=True,
                           help='The id of the facility list to process.')

    def handle(self, *args, **options):
        action = options['action']
        list_id = options['list_id']

        # Crash if invalid action specified
        if (action not in VALID_ACTIONS):
            self.stderr.write('Validation Error: Invalid action "{0}". '
                              'Must be one of {1}'
                              .format(action, ', '.join(VALID_ACTIONS)))
            sys.exit(1)

        if action in LINE_ITEM_ACTIONS.keys():
            process = LINE_ITEM_ACTIONS[action]

        # Crash if invalid list_id specified
        try:
            facility_list = FacilityList.objects.get(pk=list_id)
        except FacilityList.DoesNotExist:
            self.stderr.write('Validation Error: '
                              'No facility list with id {}.'.format(list_id))
            sys.exit(1)

        if action in LINE_ITEM_ACTIONS.keys():
            self.process_items(facility_list, action, process)
        elif action == ProcessingAction.MATCH:
            source = Source.objects.get(facility_list=list_id)
            logger.info((
                'Try to produce kafka message '
                'to match process with source_id {}'
                ).format(source.id))
            logger.info('[List Upload] Started Match process!')
            logger.info(f'[List Upload] FacilityList Id: {list_id}')
            logger.info(f'[List Upload] Source Id: {source.id}')
            asyncio.run(produce_message_match_process(source.id))
        elif action == ProcessingAction.NOTIFY_COMPLETE:
            logger.info('[List Upload] Notify Complete!')
            logger.info(f'[List Upload] FacilityList Id: {list_id}')
            notify_facility_list_complete(list_id)

    def process_items(self, facility_list, action, process):
        row_index = os.environ.get('AWS_BATCH_JOB_ARRAY_INDEX')
        if row_index:
            items = FacilityListItem.objects.filter(
                source=facility_list.source,
                row_index=row_index)
        else:
            items = FacilityListItem.objects.filter(
                source=facility_list.source)

        result = {
            'success': 0,
            'warning': 0,
            'failure': 0,
        }

        # Process all items, save affected items, facilities, matches,
        # and tally successes and failures
        parsed_items = set()
        for item in items:
            try:
                with transaction.atomic():
                    if action == ProcessingAction.MATCH:
                        matches = process(item)
                        item.save()

                        if len(matches) == 1:
                            [match] = matches

                            if match.facility.created_from == item:
                                item.facility = match.facility
                                item.save()
                            elif match.confidence == 1.0:
                                item.facility = match.facility
                                item.save()
                    elif action == ProcessingAction.PARSE:
                        logger.info('[List Upload] Started Parse process!')
                        logger.info(
                            f'[List Upload] FacilityListItem Id: {item.id}'
                        )
                        process(item)
                        if item.status != FacilityListItem.ERROR_PARSING:
                            core_fields = '{}-{}-{}'.format(item.country_code,
                                                            item.clean_name,
                                                            item.clean_address)
                            if core_fields in parsed_items:
                                item.status = FacilityListItem.DUPLICATE
                            else:
                                parsed_items.add(core_fields)
                        item.save()
                    else:
                        logger.info('[List Upload] Started Geocode process!')
                        logger.info(
                            f'[List Upload] FacilityListItem Id: {item.id}'
                        )
                        process(item)
                        item.save()
                        # [A/B Test] OSHUB-507
                        FacilityListItemTemp.copy(item)

                if item.status in FacilityListItem.ERROR_STATUSES:
                    result['failure'] += 1
                else:
                    result['success'] += 1
            except ValueError as e:
                self.stderr.write('Value Error: {}'.format(e))
                result['failure'] += 1
            except ItemRemovedException:
                self.stderr.write(self.style.WARNING('Skipping removed item'))
                result['warning'] += 1

        # Print successes
        if result['success'] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '{}: {} successes'.format(
                        action, result['success'])))

        # Print warnings
        if result['warning'] > 0:
            self.stdout.write(
                self.style.WARNING(
                    '{}: {} warnings'.format(
                        action, result['warning'])))

        # Print failures
        if result['failure'] > 0:
            self.stdout.write(
                self.style.ERROR(
                    '{}: {} failures'.format(
                        action, result['failure'])))
