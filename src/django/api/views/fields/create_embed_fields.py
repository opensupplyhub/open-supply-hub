from rest_framework.exceptions import ValidationError
from ...models.embed_field import EmbedField
from ...models.facility.facility_list_item import FacilityListItem
from ...models.transactions.index_facilities_new import index_facilities_new


def clean_explanations(field_data):
    """
    The contributor's explanations for a field, checked and tidied: what
    the field means, and what each of its values means. They are shown to
    visitors as plain text. Empty explanations are dropped.
    """
    limit = EmbedField.MAX_DESCRIPTION_LENGTH
    description = field_data.get('description') or ''
    value_descriptions = field_data.get('value_descriptions') or {}

    if not isinstance(description, str) or not isinstance(
        value_descriptions, dict
    ):
        raise ValidationError('Field explanations are not in a valid form.')
    if len(value_descriptions) > EmbedField.MAX_VALUE_DESCRIPTIONS:
        raise ValidationError(
            'A field can have at most {} value explanations.'.format(
                EmbedField.MAX_VALUE_DESCRIPTIONS
            )
        )
    cleaned = {}
    for value, text in value_descriptions.items():
        if not isinstance(value, str) or not isinstance(text, str):
            raise ValidationError(
                'Field explanations are not in a valid form.'
            )
        if text.strip():
            cleaned[value.strip()] = text.strip()
    if any(len(text) > limit for text in [description, *cleaned.values()]):
        raise ValidationError(
            'An explanation can be at most {} characters.'.format(limit)
        )
    return {
        'description': description.strip(),
        'value_descriptions': cleaned,
    }


def create_embed_fields(fields_data, embed_config, previously_searchable=None):
    if previously_searchable is None:
        previously_searchable = list()

    if len(fields_data) != len(set([f['order'] for f in fields_data])):
        raise ValidationError('Fields cannot have the same order.')

    # The rows are created straight from the request data, so the model's
    # choices are not checked for us.
    display_as_values = [value for value, _ in EmbedField.DISPLAY_AS_CHOICES]
    if any(
        f.get('display_as', EmbedField.TEXT) not in display_as_values
        for f in fields_data
    ):
        raise ValidationError(
            'Fields must be displayed as one of: {}.'.format(
                ', '.join(display_as_values)
            )
        )

    # Every field is checked before any row is created.
    fields_data = [
        {**field_data, **clean_explanations(field_data)}
        for field_data in fields_data
    ]

    for field_data in fields_data:
        EmbedField.objects.create(embed_config=embed_config, **field_data)

    searchable = [
        f.get('column_name') for f in fields_data if f.get('searchable', None)
    ]

    if set(searchable) != set(previously_searchable):
        contributor = embed_config.contributor
        f_ids = (
            FacilityListItem
            .objects
            .filter(source__contributor=contributor, facility__isnull=False)
            .distinct('facility__id')
            .values_list('facility__id', flat=True)
        )
        if len(f_ids) > 0:
            index_facilities_new(list(f_ids))
