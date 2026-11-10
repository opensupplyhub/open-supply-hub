from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    BooleanField,
    CharField,
    ChoiceField,
    FloatField,
    IntegerField,
    Serializer,
)

from api.serializers.v1.candidates_bbox_query_param_serializer import (
    parse_bbox,
)
from api.services import candidate_validation

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 500

# The sort keys the list accepts. Nearby keys are computed on read by
# api/services/candidate_listing.py; the rest are columns.
NEARBY_SORT_FIELDS = frozenset({'nearby_count', 'nearest_m'})
SORT_FIELDS = (
    'id',
    'confidence',
    'created_at',
    'nearby_count',
    'nearest_m',
)
SORT_CHOICES = tuple(
    choice
    for field in SORT_FIELDS
    for choice in (field, f'-{field}')
)

STATE_CHOICES = (
    candidate_validation.UNVERIFIED,
    candidate_validation.DISPUTED,
    candidate_validation.CONFIRMED,
    candidate_validation.RETIREMENT_PENDING,
)

# The query params that make up a legacy (map viewport) request. A request
# carrying only these keeps the OSDEV-3249 contract; anything else, or no
# bbox at all, is the paged list mode (OSDEV-3754).
LEGACY_BBOX_PARAMS = frozenset({'bbox', 'limit'})


def is_legacy_bbox_request(query_params):
    keys = set(query_params.keys())
    return 'bbox' in keys and keys <= LEGACY_BBOX_PARAMS


class CommaSeparatedChoiceField(CharField):
    '''
    ``?state=unverified,disputed`` -> ``['unverified', 'disputed']``.
    Repeats are dropped; an unknown value is a validation error naming it.
    '''

    def __init__(self, choices, **kwargs):
        self.choices = tuple(choices)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        raw = super().to_internal_value(data)
        values = []
        for part in raw.split(','):
            part = part.strip()
            if not part:
                continue
            if part not in self.choices:
                raise ValidationError(
                    f"'{part}' is not one of: {', '.join(self.choices)}."
                )
            if part not in values:
                values.append(part)
        if not values:
            raise ValidationError(
                f"Expected one or more of: {', '.join(self.choices)}."
            )
        return values


class CandidatesListQueryParamSerializer(Serializer):
    '''
    Query parameters of the paged list mode of
    ``GET /api/v1/production-locations/candidates/`` (OSDEV-3754).

    Every parameter is optional. ``bbox`` has the map mode's format but
    no size cap; ``limit`` is clamped to ``MAX_PAGE_SIZE`` rather than
    rejected, as in the map mode. ``state`` and ``country`` accept a
    comma-separated list.
    '''
    bbox = CharField(required=False)
    page = IntegerField(
        required=False,
        default=1,
        min_value=1,
        error_messages={
            'invalid': 'page must be a positive integer.',
            'min_value': 'page must be a positive integer.',
        },
    )
    limit = IntegerField(
        required=False,
        default=DEFAULT_PAGE_SIZE,
        min_value=1,
        error_messages={
            'invalid': 'limit must be a positive integer.',
            'min_value': 'limit must be a positive integer.',
        },
    )
    sort = ChoiceField(required=False, default='id', choices=SORT_CHOICES)
    confidence_min = FloatField(
        required=False, min_value=0.0, max_value=1.0
    )
    confidence_max = FloatField(
        required=False, min_value=0.0, max_value=1.0
    )
    state = CommaSeparatedChoiceField(required=False, choices=STATE_CHOICES)
    country = CharField(required=False)
    source = CharField(required=False, max_length=200)
    has_nearby = BooleanField(required=False, allow_null=True, default=None)

    def validate_bbox(self, value):
        return parse_bbox(value, max_side_degrees=None)

    def validate_limit(self, value):
        return min(value, MAX_PAGE_SIZE)

    def validate_country(self, value):
        codes = []
        for part in value.split(','):
            part = part.strip().upper()
            if not part:
                continue
            if len(part) != 2 or not part.isalpha():
                raise ValidationError(
                    'country must be one or more ISO 3166-1 alpha-2 codes, '
                    'comma-separated.'
                )
            if part not in codes:
                codes.append(part)
        if not codes:
            raise ValidationError(
                'country must be one or more ISO 3166-1 alpha-2 codes, '
                'comma-separated.'
            )
        return codes

    def validate(self, attrs):
        low = attrs.get('confidence_min')
        high = attrs.get('confidence_max')
        if low is not None and high is not None and low > high:
            raise ValidationError({
                'confidence_min':
                    'confidence_min must not exceed confidence_max.'
            })
        return attrs
