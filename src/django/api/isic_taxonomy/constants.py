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
