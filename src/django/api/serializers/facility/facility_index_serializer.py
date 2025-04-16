from itertools import groupby
from collections import defaultdict
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeometrySerializerMethodField,
)
from rest_framework.serializers import (
    SerializerMethodField,
)

from countries.lib.countries import COUNTRY_NAMES
from ...models import Contributor
from ...models.facility.facility_index import FacilityIndex
from ...models.embed_config import EmbedConfig
from ...models.embed_field import EmbedField
from ...models.extended_field import ExtendedField
from ...models.nonstandard_field import NonstandardField
from ...helpers.helpers import parse_raw_data, get_csv_values
from ..utils import is_embed_mode_active
from .facility_index_extended_field_list_serializer import (
    FacilityIndexExtendedFieldListSerializer
)
from .utils import (
    can_user_see_detail,
    format_field,
    format_numeric,
    format_sectors,
    is_created_at_main_date,
    get_facility_name,
    get_embed_contributor_id,
    get_efs_associated_with_contributor,
    create_name_field_from_facility_name,
    create_address_field_from_facility_address,
    regroup_items_for_sector_field,
    regroup_claims_for_sector_field
)


class FacilityIndexSerializer(GeoFeatureModelSerializer):
    os_id = SerializerMethodField()
    country_name = SerializerMethodField()
    contributors = SerializerMethodField()
    number_of_public_contributors = SerializerMethodField()
    name = SerializerMethodField()
    contributor_fields = SerializerMethodField()
    extended_fields = SerializerMethodField()
    location = GeometrySerializerMethodField()
    address = SerializerMethodField()
    has_approved_claim = SerializerMethodField()
    sector = SerializerMethodField()

    class Meta:
        model = FacilityIndex
        fields = (
            'id',
            'name',
            'address',
            'country_code',
            'location',
            'os_id',
            'country_name',
            'contributors',
            'number_of_public_contributors',
            'has_approved_claim',
            'is_closed',
            'contributor_fields',
            'extended_fields',
            'sector',
        )
        geo_field = 'location'

    def __init__(self, *args, **kwargs):
        exclude_fields = kwargs.pop('exclude_fields', None)
        super(FacilityIndexSerializer, self).__init__(*args, **kwargs)

        if exclude_fields:
            for field_name in exclude_fields:
                self.fields.pop(field_name, None)

    def get_location(self, facility):
        return facility.location

    def get_address(self, facility):
        claim = facility.approved_claim
        if claim is not None:
            if claim['facility_address'] and \
                    claim['facility_address'] is not None:
                return format_field(claim['facility_address'])
        return format_field(facility.address)

    def get_os_id(self, facility):
        return facility.id

    def get_name(self, facility):
        name = get_facility_name(self, facility)
        return format_field(name)

    def get_contributor_fields(self, facility):
        contributor_id = get_embed_contributor_id(self)
        if contributor_id is None or not is_embed_mode_active(self):
            return []

        contributor_data_json = None
        if len(facility.custom_field_info) > 0:
            custom_field_info_list = facility.custom_field_info
            for custom_field_info in custom_field_info_list:
                if custom_field_info['contributor_id'] == int(contributor_id):
                    contributor_data_json = custom_field_info
                    embed_level = contributor_data_json['embed_level']
                    if embed_level is None:
                        return []

        if contributor_data_json is not None:
            try:
                # If the contributor has not created any overriding embed
                # config these transparency pledge fields will always be
                # visible.
                contributor_fields = [
                    {
                        'label': display_name,
                        'value': None,
                        'column_name': column_name
                    }
                    for (column_name, display_name)
                    in NonstandardField.EXTENDED_FIELDS.items()]

                embed_fields = contributor_data_json['embed_field']
                embed_display_fields = contributor_data_json[
                    'embed_display_field']
                # If there are any configured fields to apply
                if (len(embed_fields) > 0
                        and len(embed_display_fields) == len(embed_fields)):
                    contributor_fields.clear()
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
            try:
                contributor = Contributor.objects.get(id=contributor_id)
                if contributor.embed_level is None:
                    return []
            except Contributor.DoesNotExist:
                return []

            # If the contributor has not created any overriding embed config
            # these transparency pledge fields will always be visible.
            fields = [
                EmbedField(column_name=column_name, display_name=display_name)
                for (column_name, display_name)
                in NonstandardField.EXTENDED_FIELDS.items()]

            try:
                config = EmbedConfig.objects.get(contributor=contributor)
                # If there are any configured fields, they override the
                # defaults set above
                if EmbedField.objects.filter(embed_config=config).count() > 0:
                    fields = EmbedField.objects.filter(
                        embed_config=config, visible=True).order_by('order')

                    return [
                        {
                            'label': f.display_name, 'value': None,
                            'column_name': f.column_name
                        }
                        for f in fields
                    ]
            except EmbedConfig.DoesNotExist:
                return fields

    def get_extended_fields(self, facility):
        request = self.context.get('request') \
            if self.context is not None else None

        use_main_created_at = is_created_at_main_date(self)
        date_field_to_sort = (
            'created_at' if use_main_created_at else 'updated_at'
        )

        embed = request.query_params.get('embed') \
            if request is not None else None
        contributor_id = request.query_params.get('contributor', None) \
            if request is not None and embed == '1' else None
        if contributor_id is None and request is not None and embed == '1':
            contributor_ids = request.query_params.getlist('contributors', [])
            if len(contributor_ids):
                contributor_id = contributor_ids[0]

        fields = facility.extended_fields
        if contributor_id is not None:
            fields = get_efs_associated_with_contributor(
                int(contributor_id),
                facility.extended_fields)

        user_can_see_detail = can_user_see_detail(self)
        embed_mode_active = is_embed_mode_active(self)

        grouped_data = defaultdict(list)

        def sort_order(k):
            return (k.get('verified_count', 0), k.get('is_from_claim', False),
                    k.get('value_count', 1), k.get(date_field_to_sort, None))

        def sort_order_excluding_date(k):
            return (k.get('verified_count', 0), k.get('is_from_claim', False),
                    k.get('value_count', 1))

        exclude_fields = []
        if not use_main_created_at:
            exclude_fields.append('created_at')

        for field_name, _ in ExtendedField.FIELD_CHOICES:
            filtered_fields = list(filter(
                lambda field: field_name == field.get('field_name'), fields
            ))
            serializer = FacilityIndexExtendedFieldListSerializer(
                filtered_fields,
                context={'user_can_see_detail': user_can_see_detail,
                         'embed_mode_active': embed_mode_active},
                exclude_fields=exclude_fields
            )

            if field_name == ExtendedField.NAME and not embed_mode_active:
                unsorted_data = serializer.data
                for name_obj in facility.facility_names:
                    f_name = format_field(name_obj.get('name'))
                    if f_name is not None and len(f_name) != 0:
                        created_at = use_main_created_at \
                            and name_obj.get('created_at')

                        unsorted_data.append(
                            create_name_field_from_facility_name(
                                f_name,
                                name_obj.get('contributor'),
                                created_at,
                                name_obj.get('updated_at'),
                                user_can_see_detail))
                data = sorted(unsorted_data,
                              key=sort_order_excluding_date,
                              reverse=True)
            elif field_name == ExtendedField.ADDRESS and not embed_mode_active:
                unsorted_data = serializer.data
                for address_obj in facility.facility_addresses:
                    f_address = format_field(address_obj.get('address'))
                    if f_address is not None and len(f_address) != 0:
                        created_at = use_main_created_at \
                            and address_obj.get('created_at')

                        unsorted_data.append(
                            create_address_field_from_facility_address(
                                f_address,
                                address_obj.get('contributor'),
                                created_at,
                                address_obj.get('updated_at'),
                                user_can_see_detail))
                data = sorted(unsorted_data,
                              key=sort_order_excluding_date,
                              reverse=True)
            else:
                data = sorted(serializer.data, key=sort_order, reverse=True)

            grouped_data[field_name] = data

        return grouped_data

    def get_sector(self, facility):
        user_can_see_detail = can_user_see_detail(self)

        use_main_created_at = is_created_at_main_date(self)
        date_field_to_sort = (
            'created_at' if use_main_created_at else 'updated_at'
        )

        items = regroup_items_for_sector_field(
            facility.item_sectors, date_field_to_sort)

        claims = regroup_claims_for_sector_field(
            facility.claim_sectors, date_field_to_sort
        )

        contributor_id = get_embed_contributor_id(self)
        if is_embed_mode_active(self) and contributor_id is not None:
            contributor_id_int = int(contributor_id)
            items = list(filter(
                lambda item: item['contributor']['id'] == contributor_id_int,
                items
                ))
            claims = list(filter(
                lambda claim: claim['contributor']['id'] == contributor_id_int,
                claims
                ))

        return format_sectors(items,
                              claims,
                              date_field_to_sort,
                              use_main_created_at,
                              user_can_see_detail)

    def get_has_approved_claim(self, facility):
        return len(facility.approved_claim_ids) > 0

    def get_country_name(self, facility):
        return COUNTRY_NAMES.get(facility.country_code, '')

    def get_number_of_public_contributors(self, facility):
        return facility.contributors_count

    def get_contributors(self, facility):
        if is_embed_mode_active(self):
            return []

        request = self.context.get('request') \
            if self.context is not None else None
        user = request.user if request is not None else None
        if user is not None and not user.is_anonymous:
            user_can_see_detail = user.can_view_full_contrib_details
        else:
            user_can_see_detail = True

        def format_source(contributor):
            if type(contributor) is not str:
                return {
                    'id': contributor['admin_id']
                    if contributor['admin_id'] else None,
                    'name': contributor['name'],
                    'is_verified': contributor['is_verified']
                    if contributor['is_verified'] else False,
                    'contributor_name': contributor['contributor_name']
                    if contributor['contributor_name']
                    else '[Unknown Contributor]',
                    'list_name': contributor['list_name']
                    if contributor['list_name'] else None,
                }
            return {
                'name': contributor,
            }

        res = [contributor
               for contributor in facility.contributors
               if contributor['id'] is not None]
        res.sort(key=lambda x: (x['id'], x['fl_id'] or 0))

        public_contributors = []
        anonymous_contributors = []
        for contributor in res:
            if ((contributor['should_display_associations'] is True)
                    and user_can_see_detail):
                public_contributors.append(contributor)
            else:
                anonymous_contributors.append(contributor)

        p_contributors_names = [contributor['name']
                                for contributor in public_contributors]
        p_contributors_id = [contributor['id']
                             for contributor in public_contributors]
        anonymous_contributors_type = []
        for anon_contributor in anonymous_contributors:
            if (anon_contributor['name'] not in p_contributors_names
                    and anon_contributor['id'] not in p_contributors_id):
                p_contributors_names.append(anon_contributor['name'])
                p_contributors_id.append(anon_contributor['id'])
                anonymous_contributors_type.append(
                    anon_contributor['contrib_type'])

        from api.models.contributor.contributor import Contributor
        anonymous_contributors_type = [
            Contributor.prefix_with_count(name, len(list(x)))
            for name, x in groupby(sorted(anonymous_contributors_type))
        ]

        distinct_p_contributors_name = []
        distinct_p_contributors = []
        for pc in public_contributors:
            if pc['name'] not in distinct_p_contributors_name:
                distinct_p_contributors_name.append(pc['name'])
                distinct_p_contributors.append(pc)

        sources = distinct_p_contributors + anonymous_contributors_type
        distinct_names = []
        distinct_sources = []
        formatted_sources = [
            format_source(source) for source in sources]
        for formatted_source in formatted_sources:
            if formatted_source['name'] not in distinct_names:
                distinct_names.append(formatted_source['name'])
                distinct_sources.append(formatted_source)
        return formatted_sources
