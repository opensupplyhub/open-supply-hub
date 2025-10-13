from rest_framework.serializers import (
  SerializerMethodField,
)
from waffle import switch_is_active

from api.constants import FacilityClaimStatuses
from countries.lib.countries import COUNTRY_NAMES
from ...models.contributor.contributor import Contributor
from ...models.facility.facility_index import FacilityIndex
from ...models.embed_field import EmbedField
from ...models.facility.facility_claim import FacilityClaim
from ...helpers.helpers import parse_raw_data, get_csv_values, prefix_a_an
from ..utils import (
    is_embed_mode_active,
    get_contributor_id_new,
    get_contributor_name_new,
)
from .facility_index_serializer import FacilityIndexSerializer
from .utils import (
    format_numeric,
    can_user_see_detail,
    should_show_pending_claim_info,
    get_contributor_name_from_facilityindex,
    format_date
)


class FacilityIndexDetailsSerializer(FacilityIndexSerializer):
    other_names = SerializerMethodField()
    other_addresses = SerializerMethodField()
    other_locations = SerializerMethodField()
    country_name = SerializerMethodField()
    claim_info = SerializerMethodField()
    activity_reports = SerializerMethodField()
    contributor_fields = SerializerMethodField()
    extended_fields = SerializerMethodField()
    created_from = SerializerMethodField()
    sector = SerializerMethodField()
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

    def get_country_name(self, facility):
        return COUNTRY_NAMES.get(facility.country_code, '')

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
