"""
Candidate-aware detail payloads (OSDEV-3249).

A candidate is an unnamed satellite detection that holds an OS ID but has
no ``api_facilityindex`` row and no OpenSearch document (OSDEV-3243), so
both detail endpoints used to answer 404 for it. This module is the one
place that shapes a candidate for those two endpoints, so the
brand/CSO-facing contract can be reviewed in a single file:

* ``candidate_production_location`` -- the body
  ``GET /api/v1/production-locations/{os_id}/`` returns for a candidate.
* ``FacilityCandidateDetailsSerializer`` -- the GeoJSON Feature
  ``GET /api/facilities/{os_id}/`` returns for a candidate, shaped like
  ``FacilityIndexDetailsSerializer`` output with safe empties so the
  existing React detail page renders it without changes.

Both carry the same labeling: ``is_candidate``, ``source``,
``external_id``, ``confidence``, the detected ``polygon`` and the
``validation`` block (derived state, live tally, the caller's own vote
and whether voting is open; see ``api/services/candidate_validation``).
Confirmed facilities never pass through here, so their responses are
untouched.
"""
import json

from rest_framework.fields import DateTimeField

from api.models.extended_field import ExtendedField
from api.models.facility.facility_candidate_vote import FacilityCandidateVote
from api.services import candidate_validation
from api.services.candidate_matches import suggested_matches
from countries.lib.countries import COUNTRY_NAMES

# Candidate detail responses must not be indexed by search engines: the
# SPA has no server-rendered <head>, so the header is the only signal.
NOINDEX_HEADER = 'X-Robots-Tag'
NOINDEX_VALUE = 'noindex'

_datetime_field = DateTimeField()


def geometry_geojson(geometry):
    """A GEOS geometry as a GeoJSON geometry dict, or None."""
    if geometry is None:
        return None
    return json.loads(geometry.geojson)


def _format_datetime(value):
    return _datetime_field.to_representation(value) if value else None


def your_vote(facility, user):
    """The caller's vote on ``facility`` (``None`` when anonymous/unvoted)."""
    if user is None or not user.is_authenticated:
        return None
    return (
        FacilityCandidateVote.objects
        .filter(facility=facility, user=user)
        .values_list('vote', flat=True)
        .first()
    )


def validation_block(facility, user, vote_tally=None):
    """
    ``{"state", "tally", "your_vote", "voting_open"}`` for a candidate.

    ``state`` is the public state (``retirement_pending`` at consensus-no
    under the moderation gate); ``voting_open`` is False only once the
    candidate is confirmed, exactly when the vote endpoint answers 409.
    """
    if vote_tally is None:
        vote_tally = candidate_validation.tally(facility)
    state = candidate_validation.derive_state(vote_tally)
    return {
        'state': candidate_validation.public_state(state),
        'tally': vote_tally,
        'your_vote': your_vote(facility, user),
        'voting_open': not candidate_validation.voting_is_closed(state),
    }


def provenance_block(facility):
    """``{"source", "external_id", "confidence", "polygon"}``."""
    return {
        'source': facility.source,
        'external_id': facility.external_id,
        'confidence': facility.confidence,
        'polygon': geometry_geojson(facility.polygon),
    }


def candidate_production_location(facility, user):
    """
    The v1 detail body for a candidate. Key names follow the OpenSearch
    production-location document where the concept exists (``os_id``,
    ``name``, ``address``, ``country.alpha_2``/``name``,
    ``coordinates.lat``/``lng``, ``created_at``/``updated_at``); the rest
    is the candidate labeling.
    """
    location = facility.location
    return {
        'os_id': facility.id,
        'is_candidate': True,
        'name': facility.name,
        'address': facility.address,
        'country': {
            'alpha_2': facility.country_code,
            'name': COUNTRY_NAMES.get(facility.country_code, ''),
        },
        'coordinates': {
            'lat': location.y if location else None,
            'lng': location.x if location else None,
        },
        **provenance_block(facility),
        'created_at': _format_datetime(facility.created_at),
        'updated_at': _format_datetime(facility.updated_at),
        'validation': validation_block(facility, user),
        'suggested_matches': suggested_matches(facility),
    }


class FacilityCandidateDetailsSerializer:
    """
    GeoJSON Feature for a candidate on the legacy
    ``GET /api/facilities/{os_id}/`` endpoint.

    Mirrors the key set of ``FacilityIndexDetailsSerializer`` (the shape
    ``src/react`` reads) with empty/neutral values where a candidate has
    nothing: no contributors, claims, activity reports or extended
    fields. The candidate-specific data sits under ``properties.candidate``
    next to ``properties.is_candidate: true``. Not a DRF serializer: it is
    built from a ``Facility`` row, not an index row, and has no model
    fields to declare; the ``(instance, context=...).data`` call shape is
    kept so the view reads the same as the confirmed path.
    """

    def __init__(self, facility, context=None):
        self.facility = facility
        self.context = context or {}

    @property
    def data(self):
        facility = self.facility
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        created_from = facility.created_from
        source = created_from.source if created_from else None
        contributor = source.contributor if source else None

        candidate = {
            **validation_block(facility, user),
            **provenance_block(facility),
            'suggested_matches': suggested_matches(facility),
        }

        return {
            'id': facility.id,
            'type': 'Feature',
            'geometry': geometry_geojson(facility.location),
            'properties': {
                'name': facility.name,
                'address': facility.address,
                'country_code': facility.country_code,
                'country_name': COUNTRY_NAMES.get(facility.country_code, ''),
                'os_id': facility.id,
                'is_candidate': True,
                'candidate': candidate,
                'other_names': [],
                'other_addresses': [],
                'contributors': [],
                'claim_info': None,
                'other_locations': [],
                'is_closed': None,
                'activity_reports': [],
                'contributor_fields': [],
                'new_os_id': None,
                'has_inexact_coordinates': False,
                'extended_fields': {
                    field_name: []
                    for field_name, _ in ExtendedField.FIELD_CHOICES
                },
                'created_from': {
                    'created_at': _format_datetime(facility.created_at),
                    'contributor': contributor.name if contributor else None,
                },
                'sector': [],
                'is_claimed': False,
                'partner_fields': {},
                'is_data_center': False,
            },
        }
