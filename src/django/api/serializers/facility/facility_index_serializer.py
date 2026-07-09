import logging

from collections import defaultdict
from functools import wraps
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeometrySerializerMethodField,
)
from rest_framework.serializers import (
    SerializerMethodField,
)

from countries.lib.countries import COUNTRY_NAMES
from ...constants import MASKED_CONTRIBUTOR_LABEL
from ...models import Contributor
from ...models.facility.facility_index import FacilityIndex
from ...models.embed_config import EmbedConfig
from ...models.embed_field import EmbedField
from ...models.extended_field import ExtendedField
from ...models.nonstandard_field import NonstandardField
from ...helpers.helpers import parse_raw_data, get_csv_values
from ...services.contributor_masking_policy import ContributorMaskingPolicy
from ..utils import is_embed_mode_active
from .facility_index_extended_field_list_serializer import (
    FacilityIndexExtendedFieldListSerializer
)
from .utils import (
    can_user_see_detail,
    format_date,
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

logger = logging.getLogger(__name__)


def with_masked_contributors(get_field):
    """Inject the request's ``MaskedContributors`` into a field getter.

    DRF invokes a ``SerializerMethodField`` getter as
    ``get_<field>(self, facility)``. Wrapping it with this decorator resolves
    the masked-contributor set once per serializer instance (see
    ``_masked_contributor_ids``) and passes it as the ``masked`` argument, so
    every field that anonymises contributors receives it the same way instead
    of fetching it inline.
    """
    @wraps(get_field)
    def wrapper(self, facility):
        return get_field(self, facility, self._masked_contributor_ids())
    return wrapper


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

    @with_masked_contributors
    def get_extended_fields(self, facility, masked):
        request = self._get_request()

        use_main_created_at = is_created_at_main_date(self)
        date_field_to_sort = self._date_field_to_sort(
            use_main_created_at
        )

        fields = self._filter_contributor_extended_fields(
            facility.extended_fields,
            request
        )

        user_can_see_detail = can_user_see_detail(self)
        embed_mode_active = is_embed_mode_active(self)

        grouped_data = defaultdict(list)

        for field_name, _ in ExtendedField.FIELD_CHOICES:
            filtered_fields = list(filter(
                lambda field: field_name == field.get('field_name'), fields
            ))
            serializer = FacilityIndexExtendedFieldListSerializer(
                filtered_fields,
                context={'user_can_see_detail': user_can_see_detail,
                         'embed_mode_active': embed_mode_active,
                         'masked_contributor_ids': masked},
                exclude_fields=(
                    ['created_at'] if not use_main_created_at else []
                )
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
                                user_can_see_detail,
                                is_from_created_from=name_obj.get(
                                    'is_from_created_from', False),
                                masked_ids=masked))
                data = sorted(unsorted_data,
                              key=self._sort_order_excluding_date,
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
                                user_can_see_detail,
                                is_from_created_from=address_obj.get(
                                    'is_from_created_from', False),
                                masked_ids=masked))
                data = sorted(unsorted_data,
                              key=self._sort_order_excluding_date,
                              reverse=True)
            else:
                data = sorted(
                    serializer.data,
                    key=lambda k: self._sort_order(k, date_field_to_sort),
                    reverse=True
                )

            grouped_data[field_name] = data

        return grouped_data

    @with_masked_contributors
    def get_sector(self, facility, masked):
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
                              user_can_see_detail,
                              masked)

    def get_has_approved_claim(self, facility):
        return len(facility.approved_claim_ids) > 0

    def get_country_name(self, facility):
        return COUNTRY_NAMES.get(facility.country_code, '')

    def get_number_of_public_contributors(self, facility):
        return facility.contributors_count

    @with_masked_contributors
    def get_contributors(self, facility, masked):
        if is_embed_mode_active(self):
            return []

        user_can_see_detail = can_user_see_detail(self)

        valid_contributors = [
            contributor for contributor in facility.contributors
            if contributor.get('id') is not None
        ]
        valid_contributors.sort(
            key=lambda contributor: (
                contributor['id'],
                contributor.get('fl_id') or 0,
            )
        )

        seen_public_names = set()
        distinct_public = []
        masked_contributor_ids = set()
        public_contributor_ids = set()
        counted_anonymous_ids = set()
        anonymous_by_type = defaultdict(
            lambda: {'count': 0, 'last_contributed_at': None}
        )

        for contributor in valid_contributors:
            if masked.should_mask(contributor):
                masked_contributor_ids.add(contributor['id'])
                continue

            is_public = (
                contributor.get('should_display_associations') is True
                and user_can_see_detail
            )
            if is_public:
                if contributor['name'] not in seen_public_names:
                    seen_public_names.add(contributor['name'])
                    distinct_public.append(contributor)
                else:
                    for public_contributor in distinct_public:
                        if public_contributor['name'] == contributor['name']:
                            self._update_max_contributed_at(
                                public_contributor,
                                contributor.get('last_contributed_at'),
                            )
                            break
                public_contributor_ids.add(contributor['id'])
            else:
                if contributor['id'] in public_contributor_ids:
                    continue

                contrib_type = contributor.get('contrib_type')
                anonymous_data = anonymous_by_type[contrib_type]

                if contributor['id'] not in counted_anonymous_ids:
                    counted_anonymous_ids.add(contributor['id'])
                    anonymous_data['count'] += 1

                self._update_max_contributed_at(
                    anonymous_data,
                    contributor.get('last_contributed_at'),
                )

        anonymous_entries = []
        for contrib_type in sorted(anonymous_by_type):
            anonymous_data = anonymous_by_type[contrib_type]
            count = anonymous_data['count']
            last_contributed_at = anonymous_data['last_contributed_at']
            entry = {
                'name': Contributor.prefix_with_count(contrib_type, count),
                'contributor_type': contrib_type,
                'count': count,
                'last_contributed_at': last_contributed_at,
            }
            anonymous_entries.append(entry)

        if masked_contributor_ids:
            anonymous_entries.append({
                'name': MASKED_CONTRIBUTOR_LABEL,
                'contributor_type': Contributor.OTHER_CONTRIB_TYPE,
                'count': len(masked_contributor_ids),
            })

        sources = distinct_public + anonymous_entries
        seen_names = set()
        result = []
        for source in sources:
            formatted = self._format_source(source)
            if formatted['name'] not in seen_names:
                seen_names.add(formatted['name'])
                result.append(formatted)
        return result

    def _get_request(self):
        if self.context is None:
            return None
        return self.context.get('request')

    def _masked_contributor_ids(self):
        """Contributor ids whose name must be anonymized for this request.

        Empty for the web client and facility profiles, so contributor names
        stay visible there; populated only for programmatic API callers.

        The masked set is the same for the whole response, so it is resolved
        once per serializer instance and reused. Without this the value would
        be re-fetched from the cache for every field of every facility (e.g.
        ``contributors``, ``extended_fields`` and ``sector`` per row of a list
        response).

        When ``masked_contributors`` is present in the serializer context it
        was already resolved by the view (avoiding a second cache round-trip);
        otherwise it is resolved lazily via ``ContributorMaskingPolicy``.
        """
        cached = getattr(self, '_masked_contributors_cache', None)
        if cached is None:
            ctx = self.context or {}
            if 'masked_contributors' in ctx:
                cached = ctx['masked_contributors']
            else:
                cached = ContributorMaskingPolicy.for_facilities_api(
                    self._get_request()
                )
            self._masked_contributors_cache = cached
        return cached

    @staticmethod
    def _date_field_to_sort(use_main_created_at):
        return (
            'created_at' if use_main_created_at else 'updated_at'
        )

    @staticmethod
    def _sort_order(item, date_field_to_sort):
        return (
            item.get('verified_count', 0),
            item.get('is_from_claim', False),
            item.get('value_count', 1),
            item.get(date_field_to_sort, None)
        )

    @staticmethod
    def _sort_order_excluding_date(item):
        return (
            item.get('verified_count', 0),
            item.get('is_from_claim', False),
            # Among otherwise-equal contributions (e.g. several with the same
            # value), the promoted contribution (the facility's created_from)
            # is attributed as the source of the canonical name/address.
            item.get('is_from_created_from', False),
            item.get('value_count', 1)
        )

    @staticmethod
    def _filter_contributor_extended_fields(extended_fields, request):
        if request is None:
            return extended_fields

        embed = request.query_params.get('embed')

        if embed != '1':
            return extended_fields

        contributor_id = request.query_params.get('contributor')

        if contributor_id is None:
            contributor_ids = request.query_params.getlist('contributors', [])
            if contributor_ids:
                contributor_id = contributor_ids[0]

        if contributor_id:
            return get_efs_associated_with_contributor(
                int(contributor_id),
                extended_fields,
            )

        return extended_fields

    @staticmethod
    def _format_source(source):
        if source.get('admin_id') is None:
            return {
                'name': source.get('name'),
                'contributor_type': source.get('contributor_type') or None,
                'count': source.get('count', 1),
                'last_contributed_at': (
                    format_date(source.get('last_contributed_at'))
                    if source.get('last_contributed_at') is not None
                    else None
                ),
            }
        return {
            'id': source.get('admin_id') or None,
            'name': source.get('name'),
            'is_verified': bool(source.get('is_verified')),
            'contributor_name': source.get('contributor_name')
            or '[Unknown Contributor]',
            'contributor_type': source.get('contrib_type') or None,
            'list_name': source.get('list_name') or None,
            'last_contributed_at': (
                format_date(source.get('last_contributed_at'))
                if source.get('last_contributed_at') is not None
                else None
            ),
            'list_uploaded_at': (
                format_date(source.get('list_uploaded_at'))
                if source.get('list_uploaded_at') is not None
                else None
            ),
            'count': 1,
        }

    @staticmethod
    def _update_max_contributed_at(target, contributed_at):
        if not contributed_at:
            return
        existing_date = target.get('last_contributed_at')
        if (existing_date is None
                or contributed_at > existing_date):
            target['last_contributed_at'] = contributed_at
