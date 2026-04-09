from api.models import ExtendedField
from api.models.facility.facility_claim import FacilityClaim
from api.helpers.helpers import prefix_a_an, parse_download_date


def format_download_date(date):
    return date.strftime("%Y-%m-%d")


def get_download_contribution(source, match_is_active, user_can_see_detail):
    contribution = '[Unknown Contributor]'
    is_visible = source.is_active and source.is_public and match_is_active
    source_name = "API" if source.source_type == "SINGLE" else "List"

    if source and source.contributor:
        if user_can_see_detail and is_visible:
            if source.facility_list is not None:
                source_name = source.facility_list.name
            contribution = "{} ({})".format(
                source.contributor.name,
                source_name
            )
        else:
            contribution = "{} ({})".format(
                prefix_a_an(source.contributor.contrib_type),
                source_name
            )

    return contribution


def get_download_claim_contribution(claim, user_can_see_detail):
    contribution = '[Unknown Contributor]'
    if claim and claim.contributor:
        if user_can_see_detail:
            contribution = "{} (Claimed)".format(
                claim.contributor.name
            )
        else:
            contribution = prefix_a_an(claim.contributor.contrib_type)
    return contribution


def format_download_extended_fields(fields, extended_fields):
    for field in fields:
        field_name = field.get('field_name', None)
        value = field.get('value', None)
        if value is None:
            continue
        if field_name == ExtendedField.NUMBER_OF_WORKERS:
            min = value.get('min', 0)
            max = value.get('max', 0)
            result = str(max) if max == min \
                else "{}-{}".format(min, max)
            extended_fields[0].append(result)
        elif field_name == ExtendedField.PARENT_COMPANY:
            contributor_name = value.get('contributor_name', None)
            name = value.get('name', None)
            result = contributor_name \
                if contributor_name is not None else name
            extended_fields[1].append(result)
        elif field_name == ExtendedField.FACILITY_TYPE:
            raw_values = value.get('raw_values', [])
            result = combine_raw_values(raw_values, extended_fields[2])
            extended_fields[2] = result

            matched_values = value.get('matched_values', [])
            result = [m_value[2]
                      for m_value in matched_values
                      if m_value[2] is not None]
            extended_fields[3].extend(result)
        elif field_name == ExtendedField.PROCESSING_TYPE:
            raw_values = value.get('raw_values', [])
            result = combine_raw_values(raw_values, extended_fields[2])
            extended_fields[2] = result

            matched_values = value.get('matched_values', [])
            result = [m_value[3]
                      for m_value in matched_values
                      if m_value[3] is not None]
            extended_fields[4].extend(result)
        elif field_name == ExtendedField.PRODUCT_TYPE:
            raw_values = value.get('raw_values', [])
            result = value_to_set(raw_values)
            extended_fields[5].extend(result)

    return extended_fields


CLAIMED_DOWNLOAD_FIELDS = [
    'created_at',
    'contact_person',
    'job_title',
    'company_name',
    'facility_name_native_language',
    'facility_website',
    'website',
    'facility_phone_number',
    'point_of_contact_person_name',
    'linkedin_profile',
    'office_official_name',
    'office_address',
    'office_country_code',
    'office_phone_number',
    'facility_description',
    'facility_certifications',
    'facility_affiliations',
    'facility_minimum_order_quantity',
    'facility_average_lead_time',
    'facility_female_workers_percentage',
    'sector',
    'facility_type',
    'other_facility_type',
    'facility_product_types',
    'facility_production_types',
    'parent_company_name',
    'facility_workers_count',
]


class _ClaimVisibilityProxy:
    def __init__(self, claim):
        self._claim = claim

    def __getattr__(self, name):
        return self._claim.get(name)


def format_download_claimed_fields(claim, output):
    proxy = _ClaimVisibilityProxy(claim)
    serializers = FacilityClaim.change_value_serializers

    for i, field in enumerate(CLAIMED_DOWNLOAD_FIELDS):
        if field == 'created_at':
            raw = claim.get('created_at')
            output[i] = parse_download_date(raw) if raw else ''
            continue

        if not FacilityClaim.change_conditions[field](proxy):
            output[i] = ''
            continue

        raw = claim.get(field)
        if raw is None:
            output[i] = ''
            continue

        formatted = serializers[field](raw)
        if isinstance(formatted, list):
            formatted = ', '.join(str(v) for v in formatted)
        output[i] = str(formatted) if formatted is not None else ''

    return output


def value_to_set(value):
    if isinstance(value, str):
        return set(value.split('|') if '|' in value else [value])
    return set(value)


def combine_raw_values(new_values, old_values):
    old_set = set()
    if len(old_values) != 0:
        old_set = value_to_set(old_values)
    return value_to_set(new_values).union(old_set)
