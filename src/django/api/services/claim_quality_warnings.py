'''
The vocabulary of claim quality warnings and the validation of the
`dismissed_warnings` a write endpoint may receive. Kept free of model
and service imports so the claim serializers can import it without
pulling the contribution pipeline into the serializer package.
'''
import json
from typing import Dict, List

from rest_framework import serializers

# Maps each verdict returned by ClaimQualityService to the warning shown
# to the claimant when it is flagged, in the order they are shown. To
# add another AI-judgable check, add a field to ClaimQualityVerdicts and
# an entry here. The titles double as the vocabulary of the warning
# `type` values a write may report as dismissed.
WARNING_TITLES = {
    'name_quality': 'Name May Not Look Like a Facility Name',
    'address_quality': 'Address May Not Look Like a Facility Address',
    'address_country_mismatch': 'Address May Not Match Selected Country',
    'multiple_locations': 'Details May Describe Multiple Locations',
    'different_location': 'Details May Describe a Different Location',
}

# The reason text of a dismissed warning is echoed back by the client
# and lands in a review note; bounded so a tampered request cannot
# stuff the note.
MAX_DISMISSED_WARNING_MESSAGE_LENGTH = 500


def validate_dismissed_warnings(value) -> List[Dict]:
    '''
    Normalize the `dismissed_warnings` a write endpoint receives into
    [{type, message}]. Accepts a list, or a JSON-encoded list (the claim
    form posts multipart form data, so its list arrives as a string).
    Missing or empty means nothing was dismissed. Raises a DRF
    ValidationError for anything else: an unknown or repeated warning
    type, a non-string or over-long message, or more entries than there
    are checks. The title is not accepted from the client; it is looked up
    from the type when the note is written.
    '''
    if value is None or value == '':
        return []
    if isinstance(value, (str, bytes)):
        try:
            value = json.loads(value)
        except ValueError as exc:
            raise serializers.ValidationError(
                'Expected a JSON-encoded list.'
            ) from exc
    if not isinstance(value, list):
        raise serializers.ValidationError('Expected a list of warnings.')
    if len(value) > len(WARNING_TITLES):
        raise serializers.ValidationError(
            f'At most {len(WARNING_TITLES)} warnings can be dismissed.'
        )

    dismissed = []
    seen = set()
    for entry in value:
        if not isinstance(entry, dict):
            raise serializers.ValidationError(
                'Each dismissed warning must be an object.'
            )
        warning_type = entry.get('type')
        if warning_type not in WARNING_TITLES:
            raise serializers.ValidationError(
                f'Unknown warning type: {warning_type!r}.'
            )
        # The check endpoint returns at most one warning per type, so a
        # repeat can only come from a tampered or buggy client. It is
        # rejected like the other malformed shapes rather than merged,
        # which would mean guessing which message the claimant saw.
        if warning_type in seen:
            raise serializers.ValidationError(
                f'Duplicate warning type: {warning_type!r}.'
            )
        seen.add(warning_type)
        # A missing key and a JSON null both mean no message.
        message = entry.get('message')
        if message is None:
            message = ''
        if not isinstance(message, str):
            raise serializers.ValidationError(
                'A dismissed warning message must be a string.'
            )
        if len(message) > MAX_DISMISSED_WARNING_MESSAGE_LENGTH:
            raise serializers.ValidationError(
                'A dismissed warning message must be at most '
                f'{MAX_DISMISSED_WARNING_MESSAGE_LENGTH} characters.'
            )
        dismissed.append({'type': warning_type, 'message': message.strip()})
    return dismissed


class DismissedWarningsField(serializers.Field):
    '''
    Serializer field for `dismissed_warnings` on the claim form's
    multipart POST; see validate_dismissed_warnings.
    '''

    def to_internal_value(self, data):
        return validate_dismissed_warnings(data)

    def to_representation(self, value):
        return value
