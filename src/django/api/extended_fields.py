import re
from api.models import Contributor, ExtendedField, ProductType
from api.facility_type_processing_type import (
    get_facility_and_processing_type,
)


def extract_int_range_value(value):
    """
    Excel workbooks mat contain decimal values for number_of_workers. Matching
    the decimal in the regex then using int(float(x)) ensures that a plain
    integer is extracted.
    """
    values = [int(float(x)) for x
              in re.findall(r'([0-9.]+)', str(value).replace(',', ''))]
    return {"min": min(values, default=0), "max": max(values, default=0)}


MAX_PRODUCT_TYPE_COUNT = 50


def get_matched_values(field_value, sector):
    results = []
    for value in field_value:
        result = get_facility_and_processing_type(value, sector)
        results.append(result)
    return results


def get_facility_and_processing_type_extendfield_value(
    field_value, sector,
    is_claim_edit=False
):
    if is_claim_edit:
        field_value_capitalized = (
            [value.capitalize() for value in field_value]
        )
        raw_values = '|'.join(field_value_capitalized)
        results = get_matched_values(field_value_capitalized, sector)
    else:
        processed_values = field_value.get('processed_values')
        raw_values = field_value.get('raw_values')
        results = get_matched_values(processed_values, sector)

    return {
        'raw_values': raw_values,
        'matched_values': results,
    }


def get_parent_company_extendedfield_value(field_value):
    matches = Contributor.objects.filter_by_name(field_value)

    if matches.exists():
        return {
            'raw_value': field_value,
            'contributor_name': matches[0].name,
            'contributor_id': matches[0].id
        }
    else:
        return {
            'raw_value': field_value,
            'name': field_value
        }


def get_parent_company_os_id_extendedfield_value(field_value):

    return {
        'raw_values':  field_value,
    }


def get_product_type_extendedfield_value(field_value):

    return {
        'raw_values':  field_value,
    }


def all_values_empty(value):
    if value is not None:
        if isinstance(value, list):
            return all(v in (None, "") for v in value)
        if isinstance(value, dict):
            return all(v in (None, "") for v in value.values())

    return False


def create_extendedfield(field, field_value, item, contributor):
    if field_value is not None and field_value != "" \
            and not all_values_empty(field_value):
        if field == ExtendedField.NUMBER_OF_WORKERS:
            field_value = extract_int_range_value(field_value)
        elif field == ExtendedField.PARENT_COMPANY:
            field_value = get_parent_company_extendedfield_value(field_value)
        elif field == ExtendedField.PARENT_COMPANY_OS_ID:
            field_value = get_parent_company_os_id_extendedfield_value(
                field_value
            )
        elif field == ExtendedField.PRODUCT_TYPE:
            field_value = get_product_type_extendedfield_value(field_value)
        elif (field == ExtendedField.FACILITY_TYPE or
              field == ExtendedField.PROCESSING_TYPE):
            field_value = (
                get_facility_and_processing_type_extendfield_value(
                    field_value,
                    item.sector
                )
            )
        elif (
            field == ExtendedField.DUNS_ID
            or field == ExtendedField.LEI_ID
            or field == ExtendedField.RBA_ID
        ):
            field_value = {
                'raw_value': field_value,
            }
        elif field == ExtendedField.ISIC_4:
            if isinstance(field_value, list):
                normalized_value = (
                    field_value[0] if len(field_value) == 1 else field_value
                )
            else:
                normalized_value = field_value
            field_value = {
                'raw_value': normalized_value,
            }

        ExtendedField.objects.create(
            contributor=contributor,
            facility_list_item=item,
            field_name=field,
            value=field_value
        )


OBJECT_FIELD_TYPE = "object"


def create_partner_extendedfield(
        field,
        field_value,
        field_type,
        item,
        contributor
):
    if field_value is not None and field_value != "" \
            and not all_values_empty(field_value):
        if field_type == OBJECT_FIELD_TYPE:
            field_value = {
                'raw_values': field_value,
            }
        else:
            field_value = {
                'raw_value': field_value,
            }

        ExtendedField.objects.create(
            contributor=contributor,
            facility_list_item=item,
            field_name=field,
            value=field_value
        )


RAW_DATA_FIELDS = (
    ExtendedField.NUMBER_OF_WORKERS,
    ExtendedField.NATIVE_LANGUAGE_NAME,
    ExtendedField.PARENT_COMPANY,
    ExtendedField.PARENT_COMPANY_OS_ID,
    ExtendedField.PRODUCT_TYPE,
    ExtendedField.FACILITY_TYPE,
    ExtendedField.PROCESSING_TYPE,
    ExtendedField.DUNS_ID,
    ExtendedField.LEI_ID,
    ExtendedField.RBA_ID,
    ExtendedField.ISIC_4,
)


def create_extendedfields_for_single_item(
        item,
        raw_data
):
    if item.id is None:
        return False
    contributor = item.source.contributor

    for field in RAW_DATA_FIELDS:
        field_value = raw_data.get(field)
        create_extendedfield(field, field_value, item, contributor)


def create_partner_extendedfields_for_single_item(
    item,
    raw_data
):
    if item.id is None:
        return False

    contributor = item.source.contributor

    for partner_field in item.source.contributor \
            .partner_fields.all():
        field = partner_field.name
        field_type = partner_field.type
        field_value = raw_data.get(field)

        create_partner_extendedfield(
            field,
            field_value,
            field_type,
            item,
            contributor
        )


def update_extendedfields_for_list_item(list_item):
    for extended_field in ExtendedField.objects.filter(
            facility_list_item=list_item):
        extended_field.facility = list_item.facility
        extended_field.save()


CLAIM_FIELDS = (
    ('facility_name_english', ExtendedField.NAME),
    ('facility_address', ExtendedField.ADDRESS),
    ('facility_workers_count', ExtendedField.NUMBER_OF_WORKERS),
    ('facility_name_native_language', ExtendedField.NATIVE_LANGUAGE_NAME),
    ('facility_production_types', ExtendedField.PROCESSING_TYPE),
    ('facility_type', ExtendedField.FACILITY_TYPE),
    ('parent_company', ExtendedField.PARENT_COMPANY),
    ('parent_company_name', ExtendedField.PARENT_COMPANY),
    ('facility_product_types', ExtendedField.PRODUCT_TYPE),
)


def create_extendedfields_for_claim(claim):
    if claim.id is None:
        return False
    c = claim.contributor
    f = claim.facility

    for claim_field, extended_field in CLAIM_FIELDS:
        if extended_field == ExtendedField.FACILITY_TYPE:
            # We have unified the facility type and processing type in the UI
            # into a single processing type field but we still want to create a
            # facility type extended field based on processing types selected
            field_value = getattr(claim, 'facility_production_types')
        else:
            field_value = getattr(claim, claim_field)
        if field_value is not None and field_value != "":
            if extended_field == ExtendedField.NUMBER_OF_WORKERS:
                field_value = extract_int_range_value(field_value)
            elif extended_field == ExtendedField.PARENT_COMPANY:
                field_value = get_parent_company_extendedfield_value(
                    field_value.name
                    if claim_field == "parent_company" else field_value
                )
            elif extended_field in [ExtendedField.PROCESSING_TYPE,
                                    ExtendedField.FACILITY_TYPE]:
                field_value = (
                    get_facility_and_processing_type_extendfield_value(
                       field_value, claim.sector, True
                    )
                )
            elif extended_field == ExtendedField.PRODUCT_TYPE:
                field_value = get_product_type_extendedfield_value(field_value)

            try:
                field = ExtendedField.objects.get(facility_claim=claim,
                                                  field_name=extended_field)
                field.value = field_value
                field.save()
            except ExtendedField.DoesNotExist:
                ExtendedField.objects.create(contributor=c,
                                             facility=f,
                                             facility_claim=claim,
                                             field_name=extended_field,
                                             value=field_value)
        else:
            ExtendedField.objects.filter(facility_claim=claim,
                                         field_name=extended_field).delete()


def get_product_types():
    product_types = list(ProductType.objects.all()
                         .values_list('value', flat=True))
    ef_values = (ExtendedField.objects.filter(field_name='product_type')
                 .values_list('value__raw_values', flat=True))
    flat_ef_value_titles = [item.title() for sublist in
                            ef_values for item in sublist]
    product_types.extend(flat_ef_value_titles)
    # Converting to a set and back removes duplicates
    product_types = list(set(product_types))
    product_types.sort()
    return product_types
