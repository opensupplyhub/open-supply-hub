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
from api.os_id_cache import OSIDCache
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

    contri_cleaner = ContriCleaner(
        location_list.file,
        SectorCache(),
        OSIDCache()
    )
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
    list_item_object_type = (
        FacilityListItem if should_create else FacilityListItemTemp
    )
    match_object_type = (
        FacilityMatch if should_create else FacilityMatchTemp
    )

    f_l_item = wait_for_match_processing(id, list_item_object_type)

    if not f_l_item:
        # Timeout
        return get_error_match_result(id, result)

    matches = match_object_type.objects.filter(facility_list_item=f_l_item.id)

    # No Match and Geocoder Returned No Results
    if not matches.exists():
        return get_error_match_result(f_l_item.id, result)

    return process_matches(f_l_item, matches, context, should_create, result)


def wait_for_match_processing(id, list_item_object_type, timeout=25):
    end_match_statuses = {
        list_item_object_type.MATCHED,
        list_item_object_type.POTENTIAL_MATCH,
        list_item_object_type.ERROR_MATCHING
    }

    for _ in range(timeout):
        facility_list_item = list_item_object_type.objects.get(id=id)
        if facility_list_item.status in end_match_statuses:
            return facility_list_item
        time.sleep(1)

    return None


def process_matches(f_l_item, matches, context, should_create, result):
    automatic_matches = [
        m for m in matches if m.status == FacilityMatch.AUTOMATIC
    ]
    if len(automatic_matches) == 1:
        return handle_new_facility_or_automatic_match(
            f_l_item, automatic_matches[0], context, result
        )

    # Potential Matches
    pending_matches = [
        m for m in matches if m.status == FacilityMatch.PENDING
    ]
    if pending_matches:
        return handle_potential_matches(
            f_l_item, pending_matches, context, should_create, result
        )

    return result


def handle_new_facility_or_automatic_match(f_l_item, match, context, result):
    facility_id = (
        getattr(f_l_item, 'facility_id', None)
        or
        getattr(f_l_item, 'facility', None)
    )

    # New Facility
    if facility_id is None:
        return get_new_facility_match_result(f_l_item.id, None, result)
    if (
        hasattr(f_l_item, 'facility')
        and
        f_l_item.facility.created_from == f_l_item
    ):
        return get_new_facility_match_result(f_l_item.id, facility_id, result)

    # Automatic Match
    return get_automatic_match_result(
            f_l_item.id,
            facility_id,
            match.confidence,
            context,
            result
        )


def handle_potential_matches(
    f_l_item,
    pending_matches,
    context,
    should_create,
    result
):
    matches = [
        get_potential_match_result(
            match_item,
            len(pending_matches),
            context,
            should_create,
        )
        for match_item in pending_matches
    ]
    result['matches'] = matches
    result['item_id'] = f_l_item.id
    result['status'] = f_l_item.status
    return result


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


def get_potential_match_result(match_item, items_count, context,
                               should_create):
    from api.serializers import FacilityIndexDetailsSerializer

    AUTOMATIC_THRESHOLD = 0.8

    facility = Facility.objects.get(id=match_item.facility_id)
    facility_index = FacilityIndex.objects.get(id=facility.id)
    facility_dict = FacilityIndexDetailsSerializer(
        facility_index,
        context=context
        ).data
    facility_dict['confidence'] = match_item.confidence

    if (
        (match_item.confidence < AUTOMATIC_THRESHOLD or items_count > 1)
        and
        should_create
    ):
        facility_dict['confirm_match_url'] = reverse(
            'facility-match-confirm',
            kwargs={'pk': match_item.id})
        facility_dict['reject_match_url'] = reverse(
            'facility-match-reject',
            kwargs={'pk': match_item.id})

    return facility_dict
