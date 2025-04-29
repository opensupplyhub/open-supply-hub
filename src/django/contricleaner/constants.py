MAX_PRODUCT_TYPE_COUNT = 50
DEFAULT_SECTOR_NAME = 'Unspecified'

# Validation errors will include field names as keys in the response. If the
# error isn’t field-specific, ContriCleaner will use the non_field_errors key
# for issues spanning multiple fields or related to the overall data object.
NON_FIELD_ERRORS_KEY = 'non_field_errors'


class AdditionalIDs:
    DUNS_ID = 'duns_id'
    LEI_ID = 'lei_id'
    RBA_ID = 'rba_id'

    ALLOWED_KEYS = {DUNS_ID, LEI_ID, RBA_ID}
