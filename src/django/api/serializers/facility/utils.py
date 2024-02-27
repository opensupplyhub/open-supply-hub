from typing import Union
from itertools import groupby

from dateutil import parser
from django.utils import timezone

from ...helpers.helpers import (
    cleanup_data,
    get_single_contributor_field_values,
    get_list_contributor_field_values,
    replace_invalid_data,
    prefix_a_an
)
from ...models import (
    ExtendedField,
    FacilityClaim,
    FacilityListItem,
    FacilityMatch,
    Facility,
)
from ..utils import (
    get_embed_contributor_id,
    get_contributor_id,
    get_contributor_name,
    prefer_contributor_name,
)


def _get_parent_company(claim):
    if not claim:
        return None
    if claim.parent_company:
        return {
            'id': claim.parent_company.id,
            'name': claim.parent_company.name,
        }
    if claim.parent_company_name:
        return {
            'id': claim.parent_company_name,
            'name': claim.parent_company_name,
        }
    return None


def is_created_at_main_date(serializer):
    if serializer.context is None:
        return False

    request = serializer.context.get('request')
    return (
        request is not None
        and request.query_params.get('created_at_of_data_points') == 'true'
    )


def should_show_pending_claim_info(serializer):
    if serializer.context is None:
        return False

    request = serializer.context.get('request')
    return request is not None \
        and request.query_params.get('pending_claim_info') == 'true'


def get_facility_name(serializer, facility):
    if prefer_contributor_name(serializer):
        contributor = get_embed_contributor_id(serializer)
        facility_list_item_matches = [
            FacilityListItem.objects.get(pk=pk)
            for (pk,)
            in facility
            .facilitymatch_set
            .filter(status__in=[FacilityMatch.AUTOMATIC,
                                FacilityMatch.CONFIRMED,
                                FacilityMatch.MERGED],
                    is_active=True,
                    facility_list_item__source__is_active=True,
                    facility_list_item__source__is_public=True,
                    facility_list_item__source__contributor_id=contributor)
            .order_by('-created_at')
            .values_list('facility_list_item')
        ]

        valid_names = []
        for item in facility_list_item_matches:
            if len(item.name) != 0 and item.name is not None:
                # If the contributor has submitted a name matching the
                # assigned facility name, use the assigned facility name
                if item.name == facility.name:
                    return facility.name
                valid_names.append(item.name)

        # Return the first item with a valid name if it exists
        if len(valid_names) > 0:
            return valid_names[0]

    names = (
        ExtendedField
        .objects
        .filter(facility=facility,
                field_name=ExtendedField.NAME,
                facility_claim__status=FacilityClaim.APPROVED)
        .order_by('-updated_at')
        .values_list('value', flat=True)
    )
    if len(names) > 0:
        return names[0]

    # Return the assigned facility name
    return facility.name


def get_facility_name_index_new(serializer, facility):
    if prefer_contributor_name(serializer):
        contributor = get_embed_contributor_id(serializer)
        facility_list_item_matches = [
            FacilityListItem.objects.get(pk=pk)
            for (pk,)
            in Facility.objects.get(pk=facility.id)
            .facilitymatch_set
            .filter(status__in=[FacilityMatch.AUTOMATIC,
                                FacilityMatch.CONFIRMED,
                                FacilityMatch.MERGED],
                    is_active=True,
                    facility_list_item__source__is_active=True,
                    facility_list_item__source__is_public=True,
                    facility_list_item__source__contributor_id=contributor)
            .order_by('-created_at')
            .values_list('facility_list_item')
        ]

        valid_names = []
        for item in facility_list_item_matches:
            if len(item.name) != 0 and item.name is not None:
                # If the contributor has submitted a name matching the
                # assigned facility name, use the assigned facility name
                if item.name == facility.name:
                    return facility.name
                valid_names.append(item.name)

        # Return the first item with a valid name if it exists
        if len(valid_names) > 0:
            return valid_names[0]

    names = (
        ExtendedField
        .objects
        .filter(facility=facility.id,
                field_name=ExtendedField.NAME,
                facility_claim__status=FacilityClaim.APPROVED)
        .order_by('-updated_at')
        .values_list('value', flat=True)
    )
    if len(names) > 0:
        return names[0]

    # Return the assigned facility name
    return facility.name


def format_field(value):
    invalid_keywords = ['N/A', 'n/a', '?']
    replaced_value = replace_invalid_data(value, invalid_keywords)
    return cleanup_data(replaced_value)


def assign_contributor_field_values(list_item, fields):
    contributor_fields = [{
        'label': f.display_name, 'value': None, 'column_name': f.column_name
    } for f in fields]

    if list_item is None:
        return contributor_fields

    if list_item.source.source_type == 'SINGLE':
        contributor_fields = get_single_contributor_field_values(
            list_item, contributor_fields
        )
    else:
        contributor_fields = get_list_contributor_field_values(
            list_item, contributor_fields
        )

    return [
        {
            'value': f['value'],
            'label': f['label'],
            'fieldName': f['column_name'],
        }
        for f in contributor_fields
    ]


def can_user_see_detail(serializer):
    request = serializer.context.get('request') \
        if serializer.context is not None else None
    user = request.user if request is not None else None

    if user is not None and not user.is_anonymous:
        return user.can_view_full_contrib_details
    else:
        return True


def create_name_field(name, contributor, created_at,
                      updated_at, user_can_see_detail):
    field_data = {
        'value': name,
        'field_name': ExtendedField.NAME,
        'contributor_id': get_contributor_id(contributor, user_can_see_detail),
        'contributor_name':
        get_contributor_name(contributor, user_can_see_detail),
        'updated_at': updated_at,
    }

    if created_at:
        field_data['created_at'] = created_at

    return field_data


def get_facility_names(facility):
    facility_list_item_matches = [
        FacilityListItem.objects.get(pk=pk)
        for (pk,)
        in facility
        .facilitymatch_set
        .filter(status__in=[FacilityMatch.AUTOMATIC,
                            FacilityMatch.CONFIRMED,
                            FacilityMatch.MERGED])
        .filter(is_active=True)
        .exclude(facility_list_item__source__is_active=False)
        .exclude(facility_list_item__source__is_public=False)
        .exclude(facility_list_item__name__isnull=True)
        .values_list('facility_list_item')
    ]

    return facility_list_item_matches


def create_address_field(address, contributor, created_at, updated_at,
                         user_can_see_detail, is_from_claim=False):
    field_data = {
        'value': address,
        'field_name': ExtendedField.ADDRESS,
        'contributor_id': get_contributor_id(contributor, user_can_see_detail),
        'contributor_name':
        get_contributor_name(contributor, user_can_see_detail),
        'updated_at': updated_at,
        'is_from_claim': is_from_claim,
    }

    if created_at:
        field_data['created_at'] = created_at

    return field_data


def get_facility_addresses(facility):
    facility_list_item_matches = [
        FacilityListItem.objects.get(pk=pk)
        for (pk,)
        in facility
        .facilitymatch_set
        .filter(status__in=[FacilityMatch.AUTOMATIC,
                            FacilityMatch.CONFIRMED,
                            FacilityMatch.MERGED])
        .filter(is_active=True)
        .exclude(facility_list_item__source__is_active=False)
        .exclude(facility_list_item__source__is_public=False)
        .exclude(facility_list_item__address__isnull=True)
        .values_list('facility_list_item')
    ]

    return facility_list_item_matches


def get_contributor_name_from_facilityindex(
        contributor_data: dict,
        user_can_see_detail: bool) -> Union[None, str]:
    if contributor_data.get('id') is None:
        return None
    if user_can_see_detail:
        return contributor_data.get('name')
    name = prefix_a_an(contributor_data.get('contrib_type'))
    return name[0].lower() + name[1:]


def get_contributor_id_from_facilityindex(
        contributor: dict,
        user_can_see_detail: bool) -> Union[None, int]:
    if contributor.get('id') is not None and user_can_see_detail:
        return contributor.get('admin_id')
    return None


def get_efs_associated_with_contributor(
        contributor_id: int,
        fields: list) -> list:
    filtered_fields = filter(
        lambda field: field.get('contributor').get('id') == contributor_id,
        fields)

    return list(filtered_fields)


def create_name_field_from_facility_name(name: str,
                                         contributor: dict,
                                         created_at: Union[str, bool],
                                         updated_at: str,
                                         user_can_see_detail: bool) -> dict:
    """Create name field from facility name of the FacilityIndex model."""
    field_data = {
        'value': name,
        'field_name': ExtendedField.NAME,
        'contributor_id': get_contributor_id_from_facilityindex(
            contributor, user_can_see_detail),
        'contributor_name': get_contributor_name_from_facilityindex(
            contributor, user_can_see_detail),
        'updated_at': format_date(updated_at),
    }

    if created_at:
        field_data['created_at'] = format_date(created_at)

    return field_data


def create_address_field_from_facility_address(address: str,
                                               contributor: dict,
                                               created_at: Union[str, bool],
                                               updated_at: str,
                                               user_can_see_detail: bool,
                                               is_from_claim: bool = False
                                               ) -> dict:
    """Create address field from facility address of the FacilityIndex
    model.
    """
    field_data = {
        'value': address,
        'field_name': ExtendedField.ADDRESS,
        'contributor_id': get_contributor_id_from_facilityindex(
            contributor, user_can_see_detail),
        'contributor_name': get_contributor_name_from_facilityindex(
            contributor, user_can_see_detail),
        'updated_at': format_date(updated_at),
        'is_from_claim': is_from_claim,
    }

    if created_at:
        field_data['created_at'] = format_date(created_at)

    return field_data


def regroup_items_for_sector_field(items: list,
                                   date_field_to_sort: str) -> list:
    sorted_items = sorted(
        items,
        key=lambda item: item.get('contributor').get('id') or 9999999
    )

    # Grouping by contributor's id
    distinct_groups = groupby(
        sorted_items, key=lambda item: str(item.get('contributor').get('id')))

    # Sorting within each group
    sorted_groups = [
        sorted(group, key=lambda item: (
            item.get('contributor').get('id') or 9999999,
            not item.get('source').get('is_active'),
            item.get('facilitymatch').get('is_active'),
            -parser.parse(item.get(date_field_to_sort)).timestamp()
        ))
        for _, group in distinct_groups
    ]

    # Extracting the first item from each group
    result = [group[0] for group in sorted_groups]

    return result


def regroup_claims_for_sector_field(claims: list,
                                    date_field_to_sort: str) -> list:
    sorted_claims = sorted(
        claims,
        key=lambda claim: claim.get('contributor').get('id') or 9999999
    )

    # Grouping by contributor's id
    distinct_groups = groupby(
        sorted_claims,
        key=lambda claim: str(claim.get('contributor').get('id'))
    )

    # Sorting within each group
    sorted_groups = [
        sorted(group, key=lambda item: (
            item.get('contributor').get('id') or 9999999,
            -parser.parse(item.get(date_field_to_sort)).timestamp()
        ))
        for _, group in distinct_groups
    ]

    # Extracting the first item from each group
    result = [group[0] for group in sorted_groups]

    return result


def format_date(date: str) -> str:
    # Parse the datetime string into a datetime object.
    original_datetime = parser.isoparse(date)

    # Convert the datetime object to UTC.
    utc_datetime = original_datetime.astimezone(timezone.utc)

    # Format the UTC datetime with the "Z" notation.
    formatted_datetime_str = utc_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    return formatted_datetime_str


def format_numeric(value: str) -> str:
    if value is None or value == '':
        return value

    format_spacing = value.replace(' ', '')
    percent_value = format_spacing.replace('%', '')
    try:
        float_value = float(percent_value)
        if float_value.is_integer():
            return value

        str_float = str(float_value)
        dot_index = str_float.index('.')
        if (str_float[dot_index+3:] is not None
                or int(str_float[dot_index+3:]) != 0):
            if percent_value != format_spacing:
                return str_float[0:dot_index+3] + "%"
            return str_float[0:dot_index+3]
        return value
    except Exception:
        return value


def depromote_unspecified_items(items: list):
    return sorted(items, key=lambda k: (
        k['values'][0] == 'Unspecified' and
        len(k['values']) == 1),
        reverse=False)


def format_sectors(items,
                   claims,
                   date_field_to_sort,
                   use_main_created_at,
                   user_can_see_detail):
    def is_contributor_visible(entity, is_claim):
        if is_claim:
            return user_can_see_detail
        return (user_can_see_detail and entity['source']['is_active']
                and entity['source']['is_public']
                and entity['has_active_complete_match'])

    def format_sector_data(entity, is_claim):
        formatted_data = {
            'updated_at': format_date(entity['updated_at']),
            'contributor_id': get_contributor_id_from_facilityindex(
                entity['contributor'],
                is_contributor_visible(entity, is_claim)),
            'contributor_name': get_contributor_name_from_facilityindex(
                entity['contributor'],
                is_contributor_visible(entity, is_claim)),
            'values': entity['sector'],
            'is_from_claim': is_claim
        }

        if use_main_created_at:
            formatted_data['created_at'] = format_date(entity['created_at'])

        return formatted_data

    item_sectors = [format_sector_data(item, False) for item in items]
    claim_sectors = [format_sector_data(claim, True) for claim in claims]

    sorted_item_sectors = sorted(item_sectors,
                                 key=lambda i: i[date_field_to_sort],
                                 reverse=True)

    return claim_sectors + depromote_unspecified_items(sorted_item_sectors)
