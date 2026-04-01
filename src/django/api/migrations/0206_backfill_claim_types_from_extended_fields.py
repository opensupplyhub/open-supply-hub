from django.db import migrations
from django.utils import timezone


FACILITY_TYPE_FIELD_NAME = 'facility_type'
PROCESSING_TYPE_FIELD_NAME = 'processing_type'


def _get_non_empty_matched_values(matched_values, match_value_index):
    return [
        value[match_value_index]
        for value in matched_values
        if (
            isinstance(value, (list, tuple))
            and len(value) > match_value_index
            and value[match_value_index]
        )
    ]


def backfill_claim_types_from_extended_fields(apps, schema_editor):
    FacilityClaim = apps.get_model('api', 'FacilityClaim')
    ExtendedField = apps.get_model('api', 'ExtendedField')

    claim_updates = {}

    extended_fields = ExtendedField.objects.filter(
        facility_claim_id__isnull=False,
        field_name__in=[FACILITY_TYPE_FIELD_NAME, PROCESSING_TYPE_FIELD_NAME],
    ).values_list('facility_claim_id', 'field_name', 'value')

    for claim_id, field_name, value in extended_fields.iterator():
        matched_values = []
        if isinstance(value, dict):
            matched_values = value.get('matched_values', [])

        claim_update = claim_updates.setdefault(claim_id, {})

        if field_name == PROCESSING_TYPE_FIELD_NAME:
            processing_types = list(dict.fromkeys(
                _get_non_empty_matched_values(matched_values, 3)
            ))
            claim_update['facility_production_types'] = (
                processing_types if processing_types else None
            )

        if field_name == FACILITY_TYPE_FIELD_NAME:
            facility_types = list(dict.fromkeys(
                _get_non_empty_matched_values(matched_values, 2)
            ))
            claim_update['facility_type'] = (
                '|'.join(facility_types) if facility_types else None
            )

    if not claim_updates:
        return

    claims_to_update = []
    current_time = timezone.now()

    for claim in FacilityClaim.objects.filter(
        id__in=claim_updates.keys(),
    ).iterator():
        update_data = claim_updates[claim.id]
        has_changes = False

        next_processing_types = update_data.get('facility_production_types')
        if claim.facility_production_types != next_processing_types:
            claim.facility_production_types = next_processing_types
            has_changes = True

        next_facility_type = update_data.get('facility_type')
        if claim.facility_type != next_facility_type:
            claim.facility_type = next_facility_type
            has_changes = True

        if has_changes:
            claim.updated_at = current_time
            claims_to_update.append(claim)

    if claims_to_update:
        FacilityClaim.objects.bulk_update(
            claims_to_update,
            ['facility_production_types', 'facility_type', 'updated_at'],
            batch_size=1000,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0205_add_facilitylistitem_moderation_event'),
    ]

    operations = [
        migrations.RunPython(
            backfill_claim_types_from_extended_fields,
            migrations.RunPython.noop,
        ),
    ]
