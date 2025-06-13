import json

from api.constants import (
    FacilityHistoryActions,
    ProcessingAction,
    FacilityClaimStatuses
)
from api.helpers.helpers import prefix_a_an
from api.models import (
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch
)
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.core.serializers.json import DjangoJSONEncoder

SIMPLE_HISTORY_IGNORE_FIELDS = {
    'history_id',
    'history_date',
    'history_type',
    'history_user',
    'origin_source',
    'created_at',
    'updated_at',
}


def anonymous_source_name(source):
    s = prefix_a_an(source.contributor.contrib_type)
    return s[0].lower() + s[1:]


def create_associate_match_string(facility_str, contributor_str, list_str):
    if list_str is None:
        return 'Associate facility {} with {}'.format(
            facility_str,
            contributor_str,
        )

    return 'Associate facility {} with {} via list {}'.format(
        facility_str,
        contributor_str,
        list_str,
    )


def create_associate_match_change_reason(list_item, facility):
    return create_associate_match_string(
        facility.id,
        list_item.source.contributor.id
        if list_item.source.contributor else '[Unknown]',
        list_item.source.facility_list.id
        if list_item.source.facility_list else '[Unknown]',
    )


def create_associate_match_entry_detail(match, facility_id,
                                        user_can_see_detail):
    source = match.facility_list_item.source
    if user_can_see_detail:
        contrib_name = \
            source.contributor.name if source.contributor else '[Unknown]'
        list_name = \
            source.facility_list.name if source.facility_list else None
    else:
        contrib_name = anonymous_source_name(source) \
            if source.contributor else '[Unknown]'
        list_name = None

    return create_associate_match_string(facility_id, contrib_name, list_name)


def create_dissociate_match_string(facility_str, contributor_str, list_str):
    if list_str is None:
        return 'Dissociate facility {} from {}'.format(
            facility_str,
            contributor_str,
        )
    return 'Dissociate facility {} from {} via list {}'.format(
        facility_str,
        contributor_str,
        list_str,
    )


def create_dissociate_match_change_reason(list_item, facility):
    return create_dissociate_match_string(
        facility.id,
        list_item.source.contributor.id
        if list_item.source.contributor else '[Unknown]',
        list_item.source.facility_list.id
        if list_item.source.facility_list else '[Unknown]',
    )


def create_dissociate_match_entry_detail(match, facility_id,
                                         user_can_see_detail):
    source = match.facility_list_item.source
    if user_can_see_detail:
        contrib_name = \
            source.contributor.name if source.contributor else '[Unknown]'
        list_name = \
            source.facility_list.name if source.facility_list else None
    else:
        contrib_name = anonymous_source_name(source) \
            if source.contributor else '[Unknown]'
        list_name = None

    return create_dissociate_match_string(
        facility_id,
        contrib_name,
        list_name,
    )


def create_dissociate_inactive_item_detail(facility_list_item,
                                           user_can_see_detail):
    source = facility_list_item.source
    if user_can_see_detail:
        contrib_name = \
            source.contributor.name if source.contributor else '[Unknown]'
        list_name = \
            source.facility_list.name if source.facility_list else None
    else:
        contrib_name = anonymous_source_name(source) \
            if source.contributor else '[Unknown]'
        list_name = None

    return create_dissociate_match_string(
        facility_list_item.facility_id,
        contrib_name,
        list_name,
    )


def create_geojson_diff_for_location_change(entry):
    return {
        'old': {
            'type': 'Point',
            'coordinates': [
                entry.prev_record.location.x,
                entry.prev_record.location.y,
            ],
        },
        'new': {
            'type': 'Point',
            'coordinates': [
                entry.location.x,
                entry.location.y,
            ],
        },
    }


def safe_serialize(value):
    for attr in ('pk', 'id'):
        if hasattr(value, attr):
            return getattr(value, attr)
    return str(value)


def is_json_serializable(value):
    try:
        json.dumps(value, cls=DjangoJSONEncoder)
        return True
    except (TypeError, ValueError):
        return False


def get_change_diff_for_history_entry(entry):
    if entry.prev_record is None:
        return {}

    def build_change_dict(old_obj, new_obj, fields):
        changes = {}
        for field in fields:
            if field in SIMPLE_HISTORY_IGNORE_FIELDS:
                continue

            old_val = safe_serialize(getattr(old_obj, field, None))
            new_val = safe_serialize(getattr(new_obj, field, None))

            if (
                old_val != new_val
                and is_json_serializable(old_val)
                and is_json_serializable(new_val)
            ):
                changes[field] = {'old': old_val, 'new': new_val}
        return changes

    try:
        delta = entry.diff_against(entry.prev_record)
        changed_fields = {
            change.field: {'old': safe_serialize(change.old), 'new': safe_serialize(change.new)}
            for change in delta.changes
            if change.field not in SIMPLE_HISTORY_IGNORE_FIELDS
            and safe_serialize(change.old) != safe_serialize(change.new)
            and is_json_serializable(safe_serialize(change.old))
            and is_json_serializable(safe_serialize(change.new))
        }
        return changed_fields

    except KeyError as e:
        if str(e) == "'origin_source'":
            fields = [f.name for f in entry._meta.fields]
            return build_change_dict(entry.prev_record, entry, fields)
        raise


def create_facility_history_dictionary(entry):
    updated_at = str(entry.history_date)
    change_reason = entry.history_change_reason or ''
    history_type_display = entry.get_history_type_display()
    changes = get_change_diff_for_history_entry(entry)

    if 'FacilityLocation' in change_reason:
        changes['location'] = create_geojson_diff_for_location_change(entry)

        return {
            'updated_at': updated_at,
            'action': FacilityHistoryActions.UPDATE,
            'detail': change_reason,
            'changes': changes,
        }
    elif 'Merged with' in change_reason:
        return {
            'updated_at': updated_at,
            'action': FacilityHistoryActions.MERGE,
            'detail': change_reason,
            'changes': changes,
        }
    elif 'Promoted' in change_reason:
        changes['location'] = create_geojson_diff_for_location_change(entry)

        return {
            'updated_at': updated_at,
            'action': FacilityHistoryActions.UPDATE,
            'detail': change_reason,
            'changes': changes,
        }
    elif 'Created' in history_type_display:
        return {
            'updated_at': updated_at,
            'action': FacilityHistoryActions.CREATE,
            'detail': history_type_display,
            'changes': changes,
        }
    elif 'Deleted' in history_type_display:
        return {
            'updated_at': updated_at,
            'action': FacilityHistoryActions.DELETE,
            'detail': history_type_display,
            'changes': changes,
        }
    else:
        return {
            'updated_at': updated_at,
            'action': FacilityHistoryActions.OTHER,
            'detail': history_type_display,
            'changes': changes,
        }


def maybe_get_split_action_time_from_processing_results(item):
    split_processing_times = [
        r.get('finished_at', None)
        for r
        in item.processing_results
        if r.get('action', None) == ProcessingAction.SPLIT_FACILITY
    ]

    return next(iter(split_processing_times), None)


def maybe_get_move_action_time_from_processing_results(item):
    move_processing_times = [
        r.get('finished_at', None)
        for r
        in item.processing_results
        if r.get('action', None) == ProcessingAction.MOVE_FACILITY
    ]

    return next(iter(move_processing_times), None)


def processing_results_has_split_action_for_os_id(list_item, facility_id):
    return facility_id in [
        r.get('previous_facility_os_id', None)
        for r
        in list_item.processing_results
        if r.get('action', None) == ProcessingAction.SPLIT_FACILITY
    ]


def processing_results_has_move_action_for_os_id(list_item, facility_id):
    return facility_id in [
        r.get('previous_facility_os_id', None)
        for r
        in list_item.processing_results
        if r.get('action', None) == ProcessingAction.MOVE_FACILITY
    ]


def create_facility_claim_entry(claim):
    if claim.status == FacilityClaimStatuses.REVOKED:
        return {
            'updated_at': str(claim.history_date),
            'action': FacilityHistoryActions.CLAIM_REVOKE,
            'detail': 'Claim on facility {} by {} was revoked'.format(
                claim.facility.id,
                claim.contributor.name,
            ),
        }

    if claim.status == FacilityClaimStatuses.APPROVED \
       and claim.prev_record.status == FacilityClaimStatuses.PENDING:
        return {
            'updated_at': str(claim.history_date),
            'action': FacilityHistoryActions.CLAIM,
            'detail': 'Facility {} was claimed by {}'.format(
                claim.facility.id,
                claim.contributor.name,
            ),
        }

    if claim.status == FacilityClaimStatuses.APPROVED:
        public_claim_data_keys = [
            'facility_description',
            'facility_name_english',
            'facility_name_native_language',
            'facility_minimum_order',
            'facility_average_lead_time',
            'facility_workers_count',
            'facility_female_workers_percentage',
            'facility_type',
            'other_facility_type',
            'facility_affiliations',
            'facility_product_types',
            'facility_production_types',
            'facility_parent_company',
        ]

        public_changes = {
            k: v
            for k, v
            in get_change_diff_for_history_entry(claim).items()
            if k in public_claim_data_keys
        }

        if any(public_changes):
            return {
                'updated_at': str(claim.history_date),
                'action': FacilityHistoryActions.CLAIM_UPDATE,
                'detail': 'Facility {} claim public data was updated'.format(
                    claim.facility.id,
                ),
                'changes': public_changes,
            }

    return None


def is_claim_for_facility(c, facility_id):
    try:
        return c.facility.id == facility_id
    except ObjectDoesNotExist:
        return False


def create_facility_history_list(entries, facility_id, user=None):
    if user is not None and not user.is_anonymous:
        user_can_see_detail = user.can_view_full_contrib_details
    else:
        user_can_see_detail = True

    facility_split_entries = [
        {
            'updated_at': maybe_get_split_action_time_from_processing_results(
                m.facility_list_item
            ),
            'action': FacilityHistoryActions.SPLIT,
            'detail': '{} was split from {}'.format(
                m.facility.id,
                facility_id,
            )
        }
        for m
        in FacilityMatch
        .objects
        .annotate(
            processing_results=F('facility_list_item__processing_results'))
        .extra(
            where=['processing_results @> \'[{"action": "split_facility"}]\''])
        if processing_results_has_split_action_for_os_id(
            m.facility_list_item,
            facility_id,
        )
    ]

    facility_move_entries = [
        {
            'updated_at': maybe_get_move_action_time_from_processing_results(
                m.facility_list_item
            ),
            'action': FacilityHistoryActions.MOVE,
            'detail': 'Match {} was moved from {}'.format(
                m.id,
                facility_id,
            )
        }
        for m
        in FacilityMatch
        .objects
        .filter(status__in=[
            FacilityMatch.CONFIRMED,
            FacilityMatch.AUTOMATIC,
            FacilityMatch.MERGED,
        ])
        .annotate(
            processing_results=F('facility_list_item__processing_results'))
        .extra(
            where=['processing_results @> \'[{"action": "move_facility"}]\''])
        if processing_results_has_move_action_for_os_id(
            m.facility_list_item,
            facility_id,
        )
    ]

    facility_match_entries = [
        {
            'updated_at': str(m.history_date),
            'action': FacilityHistoryActions.ASSOCIATE
            if m.is_active else FacilityHistoryActions.DISSOCIATE,
            'detail': create_associate_match_entry_detail(
                m, facility_id, user_can_see_detail)
            if m.is_active else create_dissociate_match_entry_detail(
                    m,
                    facility_id,
                    user_can_see_detail,
            ),
        }
        for m
        in FacilityMatch
        .history
        .filter(status__in=[
            FacilityMatch.CONFIRMED,
            FacilityMatch.AUTOMATIC,
            FacilityMatch.MERGED,
        ])
        .filter(facility_id=facility_id)
    ]

    # We don't have a historical model tracking when the `is_active` property
    # of a list source switches from True to False, but we want to have a
    # DISSOCIATE entry in the history when this happens.
    # We use the `created_at` of the replacing list as the date and time at
    # which the now inactive item was dissociated.
    replaced_entries = []
    inactive_items = FacilityListItem.objects.filter(
        facility_id=facility_id, source__is_active=False)
    for item in inactive_items:
        if item.source.facility_list is not None:
            replacing_list_filter = \
                FacilityList.objects.filter(replaces=item.source.facility_list)
            if replacing_list_filter.exists():
                replaced_entries.append({
                    'updated_at':
                    str(replacing_list_filter.first().created_at),
                    'action': FacilityHistoryActions.DISSOCIATE,
                    'detail': create_dissociate_inactive_item_detail(
                        item, user_can_see_detail)
                })

    facility_claim_entries = [
        create_facility_claim_entry(c)
        for c
        in FacilityClaim
        .history
        .filter(status__in=[
            FacilityClaimStatuses.APPROVED,
            FacilityClaimStatuses.REVOKED,
        ])
        if is_claim_for_facility(c, facility_id)
        if create_facility_claim_entry(c) is not None
    ]

    history_entries = [
        create_facility_history_dictionary(entry)
        for entry
        in entries
    ]

    return sorted(history_entries + facility_split_entries +
                  facility_move_entries + facility_match_entries +
                  facility_claim_entries + replaced_entries,
                  key=lambda entry: entry['updated_at'], reverse=True)
