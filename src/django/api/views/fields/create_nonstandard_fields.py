from ...models.nonstandart_field import NonstandardField


def create_nonstandard_fields(fields, contributor):
    unique_fields = list(set(fields))

    existing_fields = (
        NonstandardField
        .objects
        .filter(contributor=contributor)
        .values_list('column_name', flat=True)
    )
    new_fields = filter(
        lambda f: f not in existing_fields, unique_fields
    )
    standard_fields = [
        'sector', 'country', 'name', 'address', 'lat', 'lng',
        'ppe_contact_phone', 'ppe_website',
        'ppe_contact_email', 'ppe_product_types'
    ]
    nonstandard_fields = filter(
        lambda f: f.lower() not in standard_fields, new_fields
    )

    for field in nonstandard_fields:
        (
            NonstandardField
            .objects
            .create(
                contributor=contributor,
                column_name=field
            )
        )
