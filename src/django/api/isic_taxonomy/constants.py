import re

REQUIRED_HEADERS = (
    'section',
    'section_label',
    'division',
    'division_label',
    'group',
    'group_label',
    'class',
    'full_code',
    'description',
    '4-digits',
    '4-digits classification',
)

ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.ods', '.odt'}

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
# An ODS file is a zip: cap the unpacked sheet and the cells read per row
# too, so a small upload cannot expand into gigabytes. Real rows have 11
# columns.
MAX_ODS_CONTENT_BYTES = 50 * 1024 * 1024
MAX_ODS_ROW_CELLS = 64

ISIC_TAXONOMY_SWITCH = 'enable_isic_taxonomy'

TAXONOMY_S3_PREFIX = 'taxonomy/isic4'

STAGING_PREFIX = f'{TAXONOMY_S3_PREFIX}/staging'

SECTION_CODE_PATTERN = re.compile(r'^[A-U]$')

# Unicode-aware word chars plus punctuation used in official ISIC labels.
LABEL_CHAR_PATTERN = re.compile(r"^[\w\s,;\"'\-()./’]+$", re.UNICODE)

JSON_ARTIFACT_NAME = 'isic_rev4.json'
JS_ARTIFACT_NAME = 'isicRev4Taxonomy.js'
SOURCE_ARTIFACT_NAME = 'source'

# Browser cache TTL for GET /api/taxonomy/isic4/?v=<version>. The query param
# changes on publish, so immutable + long max-age is safe.
ISIC4_TAXONOMY_BROWSER_CACHE_MAX_AGE_SECONDS = 31_536_000
ISIC4_TAXONOMY_BROWSER_CACHE_CONTROL = (
    f'public, max-age={ISIC4_TAXONOMY_BROWSER_CACHE_MAX_AGE_SECONDS}, '
    'immutable'
)
