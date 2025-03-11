import time
import traceback
import logging

from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils import timezone
from django.db import transaction

from api.constants import ProcessingAction
from api.geocoding import geocode_address
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_list_item_temp import FacilityListItemTemp
from api.models.facility.facility_match import FacilityMatch
from api.models.facility.facility_match_temp import FacilityMatchTemp
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.facility_list import FacilityList
from contricleaner.lib.contri_cleaner import ContriCleaner
from contricleaner.lib.exceptions.handler_not_set_error \
    import HandlerNotSetError
from api.sector_cache import SectorCache
from api.facility_actions.processing_facility_executor import (
    ProcessingFacilityExecutor
)
from api.facility_actions.processing_facility_list import (
    ProcessingFacilityList
)
from oar.rollbar import report_error_to_rollbar

logger = logging.getLogger(__name__)


class ItemRemovedException(Exception):
    pass


@transaction.atomic
def parse_production_location_list(location_list: FacilityList):
    parsing_started = str(timezone.now())
    logger.info('[List Upload] Started CC Parse process!')

    contri_cleaner = ContriCleaner(location_list.file, SectorCache())
    internal_errors = []
    processing_input = {
        'facility_list': location_list,
        'parsing_started': parsing_started
    }
    try:
        contri_cleaner_processed_data = contri_cleaner.process_data()
        processing_input['contri_cleaner_processed_data'] = \
            contri_cleaner_processed_data
    except HandlerNotSetError as err:
        error_message = f'[List Upload] Internal ContriCleaner Error: {err}'
        logger.error(error_message)
        report_error_to_rollbar(
            message=error_message,
            extra_data={'affected_list': str(location_list)}
        )
        internal_errors.append({
            'message': ('We are currently experiencing an issue with our '
                        'system and will address it as soon as we can. '
                        'Please wait and try your upload again.'),
            'type': 'InternalError'
        })
        processing_input['internal_errors'] = internal_errors

    processing_facility_executor = ProcessingFacilityExecutor(
        ProcessingFacilityList(processing_input)
    )
    processing_facility_executor.run_processing()


def geocode_facility_list_item(item):
    started = str(timezone.now())
    if type(item) != FacilityListItem:
        raise ValueError('Argument must be a FacilityListItem')
    if item.status == FacilityListItem.ITEM_REMOVED:
        raise ItemRemovedException()
    if item.status != FacilityListItem.PARSED:
        raise ValueError('Items to be geocoded must be in the PARSED status')
    try:
        if item.geocoded_point is None:
            data = geocode_address(item.address, item.country_code)
            if data['result_count'] > 0:
                item.status = FacilityListItem.GEOCODED
                item.geocoded_point = Point(
                    data["geocoded_point"]["lng"],
                    data["geocoded_point"]["lat"]
                )
                item.geocoded_address = data["geocoded_address"]
            else:
                item.status = FacilityListItem.GEOCODED_NO_RESULTS
            item.processing_results.append({
                'action': ProcessingAction.GEOCODE,
                'started_at': started,
                'error': False,
                'skipped_geocoder': False,
                'data': data['full_response'],
                'finished_at': str(timezone.now()),
               })
        else:
            item.status = FacilityListItem.GEOCODED
            item.geocoded_address = item.address
            item.processing_results.append({
                'action': ProcessingAction.GEOCODE,
                'started_at': started,
                'error': False,
                'skipped_geocoder': True,
                'finished_at': str(timezone.now()),
            })

    except Exception as e:
        item.status = FacilityListItem.ERROR_GEOCODING
        item.processing_results.append({
            'action': ProcessingAction.GEOCODE,
            'started_at': started,
            'error': True,
            'message': str(e),
            'trace': traceback.format_exc(),
            'finished_at': str(timezone.now()),
        })
        logger.error(f'[List Upload] Geocoding Error: {str(e)}')
        logger.info(f'[List Upload] FacilityListItem Id: {item.id}')
        logger.info(f'[List Upload] Address: {item.address}, '
                    f'Country_Code: {item.country_code}')


def handle_external_match_process_result(id, result, request, should_create):
    context = {'request': request}
    if should_create:
        list_item_object_type = FacilityListItem
    else:
        list_item_object_type = FacilityListItemTemp
    end_match_process_status = [list_item_object_type.MATCHED,
                                list_item_object_type.POTENTIAL_MATCH,
                                list_item_object_type.ERROR_MATCHING]
    f_l_item = None
    timer = 0
    timeout = 25
    while True:
        if timer > timeout:
            break
        facility_list_item = list_item_object_type.objects.get(id=id)
        if facility_list_item.status in end_match_process_status:
            f_l_item = facility_list_item
            break
        time.sleep(1)
        timer = timer + 1

    if f_l_item is None:
        # Timeout
        return get_error_match_result(id, result)
    if should_create:
        match_object_type = FacilityMatch
    else:
        match_object_type = FacilityMatchTemp
    queryset_f_m = match_object_type.objects.filter(
        facility_list_item=f_l_item.id)
    if queryset_f_m.count() == 0:
        # No Match and Geocoder Returned No Results
        return get_error_match_result(f_l_item.id, result)

    automatic_matches = [
        match for match in queryset_f_m
        if match.status == match_object_type.AUTOMATIC
    ]
    if (len(automatic_matches) == 1):
        if isinstance(f_l_item, FacilityListItem):
            # New Facility
            if f_l_item.facility is None:
                return get_new_facility_match_result(f_l_item.id, None, result)
            if f_l_item.facility.created_from == f_l_item:
                return get_new_facility_match_result(
                    f_l_item.id, f_l_item.facility.id, result
                )

            # Automatic Match
            return get_automatic_match_result(f_l_item.id,
                                              f_l_item.facility.id,
                                              automatic_matches[0].confidence,
                                              context,
                                              result)
        else:
            # New Facility
            if f_l_item.facility_id is None:
                return get_new_facility_match_result(f_l_item.id, None, result)

            # Automatic Match
            return get_automatic_match_result(f_l_item.id,
                                              f_l_item.facility_id,
                                              automatic_matches[0].confidence,
                                              context,
                                              result)

    pending_matches = [
        match for match in queryset_f_m
        if match.status == match_object_type.PENDING
    ]

    result_matches = []
    for item in pending_matches:
        # Potential Matches
        result_matches.append(
            get_potential_match_result(
                f_l_item,
                item,
                len(pending_matches),
                context,
                should_create,
                result
            )
        )

    return result_matches


def get_error_match_result(id, result):
    result['status'] = FacilityListItem.ERROR_MATCHING
    result['item_id'] = id

    return result


def get_new_facility_match_result(list_item_id, facility_id, result):
    result['status'] = FacilityListItem.NEW_FACILITY
    result['item_id'] = list_item_id

    if facility_id is not None:
        result['os_id'] = facility_id

    return result


def get_automatic_match_result(list_item_id, facility_id, confidence, context,
                               result):
    from api.serializers import FacilityIndexDetailsSerializer

    facility_index = FacilityIndex.objects.get(id=facility_id)
    facility_dict = FacilityIndexDetailsSerializer(
        facility_index,
        context=context
        ).data
    facility_dict['confidence'] = confidence

    result['matches'].append(facility_dict)
    result['item_id'] = list_item_id
    result['os_id'] = facility_id
    result['status'] = FacilityListItem.MATCHED

    return result


def get_potential_match_result(list_item, item, items_count, context,
                               should_create, result):
    from api.serializers import FacilityIndexDetailsSerializer

    AUTOMATIC_THRESHOLD = 0.8

    facility = Facility.objects.get(id=item.facility_id)
    facility_index = FacilityIndex.objects.get(id=facility.id)
    facility_dict = FacilityIndexDetailsSerializer(
        facility_index,
        context=context
        ).data
    facility_dict['confidence'] = item.confidence

    if item.confidence < AUTOMATIC_THRESHOLD or items_count > 1:
        if should_create:
            facility_dict['confirm_match_url'] = reverse(
                'facility-match-confirm',
                kwargs={'pk': item.id})
            facility_dict['reject_match_url'] = reverse(
                'facility-match-reject',
                kwargs={'pk': item.id})
    result['matches'].append(facility_dict)
    result['item_id'] = list_item.id
    result['status'] = list_item.status

    return result
