import math

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import CharField, IntegerField, Serializer

# A bbox side longer than this is refused outright rather than paged: the
# endpoint exists to paint candidate footprints on a zoomed-in map, not to
# bulk-export candidates (which stay out of every download surface).
MAX_BBOX_SIDE_DEGREES = 2.0
DEFAULT_LIMIT = 200
MAX_LIMIT = 500

BBOX_FORMAT = 'minLng,minLat,maxLng,maxLat'


class CandidatesBboxQueryParamSerializer(Serializer):
    '''
    Query parameters of ``GET /api/v1/production-locations/candidates/``
    (OSDEV-3249). ``bbox`` is validated into a ``(min_lng, min_lat,
    max_lng, max_lat)`` tuple of floats; ``limit`` is clamped to
    ``MAX_LIMIT`` rather than rejected so a consumer that asks for more
    simply gets the cap.
    '''
    bbox = CharField(
        required=True,
        error_messages={
            'required': f'bbox is required: {BBOX_FORMAT}.',
            'blank': f'bbox is required: {BBOX_FORMAT}.',
        },
    )
    limit = IntegerField(
        required=False,
        default=DEFAULT_LIMIT,
        min_value=1,
        error_messages={
            'invalid': 'limit must be a positive integer.',
            'min_value': 'limit must be a positive integer.',
        },
    )

    def validate_bbox(self, value):
        parts = value.split(',')
        if len(parts) != 4:
            raise ValidationError(
                f'bbox must be four comma-separated numbers: {BBOX_FORMAT}.'
            )
        try:
            min_lng, min_lat, max_lng, max_lat = (
                float(part) for part in parts
            )
        except ValueError:
            raise ValidationError(
                f'bbox must be four comma-separated numbers: {BBOX_FORMAT}.'
            )
        if not all(
            math.isfinite(v) for v in (min_lng, min_lat, max_lng, max_lat)
        ):
            raise ValidationError(
                f'bbox must be four comma-separated numbers: {BBOX_FORMAT}.'
            )
        if not (-180 <= min_lng < max_lng <= 180
                and -90 <= min_lat < max_lat <= 90):
            raise ValidationError(
                'bbox coordinates must be within -180..180 longitude and '
                '-90..90 latitude, with min strictly less than max.'
            )
        if (max_lng - min_lng > MAX_BBOX_SIDE_DEGREES
                or max_lat - min_lat > MAX_BBOX_SIDE_DEGREES):
            raise ValidationError(
                'bbox is too large: each side must be at most '
                f'{MAX_BBOX_SIDE_DEGREES:g} degrees. Zoom in and retry.'
            )
        return (min_lng, min_lat, max_lng, max_lat)

    def validate_limit(self, value):
        return min(value, MAX_LIMIT)
