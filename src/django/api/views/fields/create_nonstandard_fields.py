from typing import KeysView

from api.models.contributor.contributor import Contributor
from api.models.nonstandard_field import NonstandardField


def create_nonstandard_fields(
    fields: KeysView[str], contributor: Contributor
) -> None:
    unique_fields = list(set(fields))

    existing_fields = NonstandardField.objects.filter(
        contributor=contributor
    ).values_list('column_name', flat=True)
    new_fields = filter(lambda f: f not in existing_fields, unique_fields)
    standard_fields = [
        'sector',
        'country',
        'name',
        'address',
        'lat',
        'lng',
        'additional_ids',
    ]
    nonstandard_fields = filter(
        lambda f: f.lower() not in standard_fields, new_fields
    )

    for field in nonstandard_fields:
        (
            NonstandardField.objects.create(
                contributor=contributor, column_name=field
            )
        )
