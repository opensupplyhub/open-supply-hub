from collections import defaultdict
from typing import Dict, List, Any
from rest_framework.serializers import (
  SerializerMethodField,
)
from waffle import switch_is_active
from django.core.cache import cache

from api.constants import FacilityClaimStatuses, PARTNER_FIELD_LIST_KEY
from api.partner_fields.registry import system_partner_field_registry
from ...models.contributor.contributor import Contributor
from ...models.facility.facility_index import FacilityIndex
from ...models.embed_field import EmbedField
from ...models.facility.facility_claim import FacilityClaim
from ...models.partner_field import PartnerField
from api.models.facility.facility import Facility
from ...helpers.helpers import parse_raw_data, get_csv_values, prefix_a_an
from ..utils import (
    is_embed_mode_active,
    get_contributor_id_new,
    get_contributor_name_new,
)
from .facility_index_serializer import FacilityIndexSerializer
from .facility_index_extended_field_list_serializer import (
    FacilityIndexExtendedFieldListSerializer
)
from .utils import (
    format_numeric,
    can_user_see_detail,
    should_show_pending_claim_info,
    get_contributor_name_from_facilityindex,
    format_date,
    is_created_at_main_date
)


class FacilityIndexDetailsSerializer(FacilityIndexSerializer):
    other_names = SerializerMethodField()
    other_addresses = SerializerMethodField()
    other_locations = SerializerMethodField()
    claim_info = SerializerMethodField()
    activity_reports = SerializerMethodField()
    contributor_fields = SerializerMethodField()
    created_from = SerializerMethodField()
    is_claimed = SerializerMethodField()
    partner_fields = SerializerMethodField()

    class Meta:
        model = FacilityIndex
        fields = (
            'id',
            'name',
            'address',
            'country_code',
            'location',
            'os_id',
            'other_names',
            'other_addresses',
            'contributors',
            'country_name',
            'claim_info',
            'other_locations',
            'is_closed',
            'activity_reports',
            'contributor_fields',
            'new_os_id',
            'has_inexact_coordinates',
            'extended_fields',
            'created_from',
            'sector',
            'is_claimed',
            'partner_fields',
        )
        geo_field = 'location'

    def get_other_names(self, facility):
        if is_embed_mode_active(self):
            return []

        other_names = {
            name_obj.get('name') for name_obj in facility.facility_names
            if name_obj.get('name') != facility.name
        }

        return other_names

    def get_other_addresses(self, facility):
        if is_embed_mode_active(self):
            return []

        other_addresses = {
            address_obj.get('address')
            for address_obj in facility.facility_addresses
            if address_obj.get('address') != facility.address
        }

        if facility.approved_claim is not None:
            return set([facility.address]).union(other_addresses)

        return other_addresses

    def get_other_locations(self, facility):
        if is_embed_mode_active(self):
            return []

        user_can_see_detail = can_user_see_detail(self)

        facility_locations = [
            {
                'lat': loc['location_lat']
                if loc['location_lat'] is not None else None,
                'lng': loc['location_lng']
                if loc['location_lng'] is not None else None,
                'contributor_id': get_contributor_id_new(
                    loc['contributor'],
                    user_can_see_detail),
                'contributor_name': get_contributor_name_new(
                    loc['contributor'],
                    user_can_see_detail),
                'notes': loc['location_notes'],
            }
            for loc
            in facility.facility_locations
        ]

        facility_items_location = [
            {
                'lat': item['location_lat']
                if item['location_lat'] is not None else None,
                'lng': item['location_lng']
                if item['location_lng'] is not None else None,
                'contributor_id': get_contributor_id_new(
                    item['contributor'],
                    user_can_see_detail),
                'contributor_name': get_contributor_name_new(
                    item['contributor'],
                    user_can_see_detail),
                'notes': None,
            }
            for item
            in facility.facility_list_items
        ]

        claim_locations = []
        claim = facility.approved_claim
        if claim is not None:
            if (claim['facility_address']
                    and claim['facility_address'] is not None):
                claim_locations = [
                    {
                        'lat': (claim['facility_location_info'])['lat']
                        if claim['facility_location'] is not None else None,
                        'lng': (claim['facility_location_info'])['lng']
                        if claim['facility_location'] is not None else None,
                        'contributor_id': get_contributor_id_new(
                            claim['contributor'],
                            user_can_see_detail),
                        'contributor_name': get_contributor_name_new(
                            claim['contributor'],
                            user_can_see_detail),
                        'notes': None,
                        'is_from_claim': True,
                        'has_invalid_location': (
                            claim['facility_location'] is None
                        )
                    },
                ]

        return claim_locations + facility_locations + facility_items_location

    def get_claim_info(self, facility):
        if not switch_is_active('claim_a_facility'):
            return None

        claim_info = None
        user_can_see_detail = can_user_see_detail(self)

        approved_claim_info = facility.claim_info
        if approved_claim_info:
            claim_info = approved_claim_info
            claim_info['contributor'] = \
                get_contributor_name_from_facilityindex(
                    claim_info['contributor'],
                    user_can_see_detail)
            return claim_info

        if should_show_pending_claim_info(self):
            pending_claim_info = FacilityClaim.objects \
                .filter(
                    status=FacilityClaimStatuses.PENDING,
                    facility_id=facility.id
                ) \
                .values_list('id', flat=True)

            if pending_claim_info:
                claim_info = {'status': FacilityClaimStatuses.PENDING}

        return claim_info

    def get_activity_reports(self, facility):
        return [
            {
                'facility': item.get('facility'),
                'reported_by_contributor': item.get('reported_by_contributor'),
                'closure_state': item.get('closure_state'),
                'approved_at': (
                    format_date(item.get('approved_at'))
                    if item.get('approved_at')
                    else None
                ),
                'status_change_reason': item.get('status_change_reason'),
                'status': item.get('status'),
                'status_change_by': item.get('status_change_by'),
                'status_change_date': (
                    format_date(item.get('status_change_date'))
                    if item.get('status_change_date')
                    else None
                ),
                'created_at': format_date(item.get('created_at')),
                'updated_at': format_date(item.get('updated_at')),
                'id': item.get('id'),
                'reason_for_report': item.get('reason_for_report'),
                'facility_name': item.get('facility_name'),
            }
            for item in facility.activity_reports_info
        ]

    def get_contributor_fields(self, facility):
        request = self.context.get('request') \
            if self.context is not None else []
        if request is None or request.query_params is None:
            return []

        embed = request.query_params.get('embed')
        contributor_id = request.query_params.get('contributor', None)
        if not embed == '1' or contributor_id is None:
            return []

        contributor_data_json = None
        if len(facility.custom_field_info) > 0:
            for custom_field_info in facility.custom_field_info:
                if custom_field_info['contributor_id'] == int(contributor_id):
                    contributor_data_json = custom_field_info
                    break

        if contributor_data_json is not None:
            try:
                contributor_fields = []
                embed_fields = contributor_data_json['embed_field']
                embed_display_fields = contributor_data_json[
                    'embed_display_field'
                ]
                # If there are any configured fields to apply
                if (len(embed_fields) > 0
                        and len(embed_display_fields) == len(embed_fields)):
                    for index in range(0, len(embed_fields)):
                        contributor_fields.append({
                            'label': embed_display_fields[index],
                            'value': None,
                            'column_name': embed_fields[index]
                        })

                source_type = contributor_data_json['source_type']
                raw_data = contributor_data_json['raw_data']
                if source_type == 'SINGLE':
                    data = parse_raw_data(raw_data)
                    for f in contributor_fields:
                        value = data.get(f['column_name'], None)
                        if value is not None:
                            f['value'] = value
                        else:
                            f['value'] = None
                else:
                    list_header = contributor_data_json['list_header']
                    data_values = get_csv_values(raw_data)
                    list_fields = get_csv_values(list_header)
                    for f in contributor_fields:
                        if f['column_name'] in list_fields:
                            index = list_fields.index(f['column_name'])
                            if 0 <= index < len(data_values):
                                value = data_values[index]
                                f['value'] = value
                            else:
                                f['value'] = None
                        else:
                            f['value'] = None

                return [
                    {
                        'value': format_numeric(f['value']),
                        'label': f['label'],
                        'fieldName': f['column_name'],
                    }
                    for f in contributor_fields
                ]
            except Exception:
                return []
        else:
            fields = []
            contributor = Contributor.objects.get(id=contributor_id)
            if contributor.embed_config is not None:
                config = contributor.embed_config
                # If there are any configured fields, they override the
                # defaults set above
                if EmbedField.objects.filter(embed_config=config).count() > 0:
                    fields = EmbedField.objects.filter(
                        embed_config=config, visible=True).order_by('order')

                    return [
                        {
                            'label': f.display_name,
                            'value': None,
                            'column_name': f.column_name
                        }
                        for f in fields
                    ]
                else:
                    return []
            else:
                return []

    def get_created_from(self, facility):
        created_from_info = facility.created_from_info
        user_can_see_detail = can_user_see_detail(self)
        should_display_associations = False
        if created_from_info['should_display_associations'] is not None:
            should_display_associations = created_from_info[
                'should_display_associations'
            ]
        display_detail = (
            user_can_see_detail
            and should_display_associations
            and not is_embed_mode_active(self)
        )

        created_at = None
        contributor_name = None
        if created_from_info['created_at'] is not None:
            created_at = format_date(created_from_info['created_at'])
        if (created_from_info['contributor_name'] is not None
                and display_detail):
            contributor_name = created_from_info['contributor_name']
        else:
            if created_from_info['contrib_type'] is not None:
                name = prefix_a_an(created_from_info['contrib_type'])
                contributor_name = name[0].lower() + name[1:]
        return {
            'created_at': created_at,
            'contributor': contributor_name
        }

    def get_has_inexact_coordinates(self, facility):
        return False

    def get_is_claimed(self, facility):
        return facility.approved_claim is not None

    def get_partner_fields(self, facility):
        request = self._get_request()

        use_main_created_at = is_created_at_main_date(self)
        date_field_to_sort = self._date_field_to_sort(
            use_main_created_at
        )

        # Fetch system-generated partner fields.
        system_fields = self.__fetch_system_partner_fields(facility)

        # Merge with facility.extended_fields.
        all_extended_fields = facility.extended_fields + system_fields

        # Filter the combined list.
        fields = self._filter_contributor_extended_fields(
            all_extended_fields,
            request
        )
        grouped_fields = self.__group_fields_by_name(
            fields
        )

        user_can_see_detail = can_user_see_detail(self)
        embed_mode_active = is_embed_mode_active(self)
        partner_fields = self.__get_cached_partner_fields()

        return self.__serialize_and_sort_partner_fields(
            grouped_fields,
            partner_fields,
            user_can_see_detail,
            embed_mode_active,
            use_main_created_at,
            date_field_to_sort
        )

    def __serialize_and_sort_partner_fields(
        self,
        grouped_fields: Dict[str, List[Dict[str, Any]]],
        partner_fields: List[PartnerField],
        user_can_see_detail: bool,
        embed_mode_active: bool,
        use_main_created_at: bool,
        date_field_to_sort: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        import logging
        logger = logging.getLogger(__name__)

        grouped_data = {}
        for field in partner_fields:
            field_name = field.name
            source_by = field.source_by
            unit = field.unit
            label = field.label
            base_url = field.base_url
            display_text = field.display_text
            json_schema = field.json_schema
            fields = grouped_fields.get(field_name, [])
            if not fields:
                continue

            try:
                serializer = FacilityIndexExtendedFieldListSerializer(
                    fields,
                    context={
                        'user_can_see_detail': user_can_see_detail,
                        'embed_mode_active': embed_mode_active,
                        'source_by': source_by,
                        'unit': unit,
                        'label': label,
                        'base_url': base_url,
                        'display_text': display_text,
                        'json_schema': json_schema
                    },
                    exclude_fields=(
                        ['created_at'] if not use_main_created_at else []
                    )
                )
                grouped_data[field_name] = sorted(
                    serializer.data,
                    key=lambda k: self._sort_order(k, date_field_to_sort),
                    reverse=True
                )
            except Exception as exc:
                logger.error(
                    f"Failed to serialize partner field '{field_name}': "
                    f"{exc}"
                )
                grouped_data[field_name] = []

        return grouped_data

    @staticmethod
    def __fetch_system_partner_fields(production_location: Facility) -> list:
        '''
        Fetch all system-generated partner fields for the production location.
        Returns list of formatted field data matching extended_fields
        structure.
        '''
        system_fields = []

        # Get all registered providers.
        providers = system_partner_field_registry.providers

        for provider in providers:
            field_data = provider.fetch_data(production_location)
            if field_data is not None:
                system_fields.append(field_data)

        return system_fields

    @staticmethod
    def __group_fields_by_name(
        fields: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        grouped = defaultdict(list)
        for field in fields:
            name = field.get('field_name')
            if name:
                grouped[name].append(field)
        return grouped

    @staticmethod
    def __get_cached_partner_fields():
        cached_names = cache.get(PARTNER_FIELD_LIST_KEY)

        if cached_names is not None:
            return cached_names

        partner_fields = list(
            PartnerField.objects.all()
        )

        cache.set(PARTNER_FIELD_LIST_KEY, partner_fields, 60)

        return partner_fields
