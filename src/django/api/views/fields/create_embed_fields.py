from rest_framework.exceptions import ValidationError
from ...models.embed_field import EmbedField
from ...models.facility.facility_list_item import FacilityListItem
from ...models.transactions.index_facilities_new import index_facilities_new


def create_embed_fields(fields_data, embed_config, previously_searchable=None):
    if previously_searchable is None:
        previously_searchable = list()

    if len(fields_data) != len(set([f['order'] for f in fields_data])):
        raise ValidationError('Fields cannot have the same order.')

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
