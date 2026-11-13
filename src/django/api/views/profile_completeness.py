from django.http import Http404
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from waffle import flag_is_active

from api.models import FacilityProfileCompleteness
from api.profile_completeness import (
    COMPONENTS,
    MAX_LEVEL,
    PROFILE_COMPLETENESS_FLAG,
)


def _serialize_score(run):
    if run is None:
        return None
    return {
        'value': run.score,
        'level': run.level,
        'max_level': MAX_LEVEL,
        'components': [
            {
                'key': key,
                'label': label,
                'value': run.components.get(key),
            }
            for key, label in COMPONENTS
        ],
        'scorer_version': run.scorer_version,
        'run_date': run.run_date,
    }


def _serialize_classifier(run):
    if run is None:
        return None
    return {
        'tier': run.classifier_tier,
        'level': run.classifier_level,
        'agreement_tier': run.classifier_agreement_tier,
        'field_tier': run.classifier_field_tier,
        'model': run.classifier_model,
        'run_date': run.run_date,
    }


@api_view(['GET'])
@throttle_classes([])
def profile_completeness(request, os_id):
    """
    Returns the latest profile completeness score and the latest
    model-backed classification stored for a production location, for
    users the `show_profile_completeness` flag is on for. Everyone else,
    and a location with neither, gets a 404.

    This is deliberately not part of `GET /api/facilities/{os_id}/`: that
    response is cached and shared between callers, and this one must
    never be.

    ## Sample Response

        {
            "os_id": "IN20190866W0EJK",
            "score": {
                "value": 0.63,
                "level": 2,
                "max_level": 3,
                "components": [
                    {
                        "key": "claimed_status",
                        "label": "Claimed status",
                        "value": 1.0
                    }
                ],
                "scorer_version": "v111126",
                "run_date": "2026-11-11"
            },
            "classifier": {
                "tier": "high",
                "level": 3,
                "agreement_tier": "high",
                "field_tier": "high",
                "model": "model-name-1.0",
                "run_date": "2026-11-12"
            }
        }
    """
    if not flag_is_active(request._request, PROFILE_COMPLETENESS_FLAG):
        raise Http404()

    runs = FacilityProfileCompleteness.objects.filter(facility_id=os_id)
    score_run = runs.filter(score__isnull=False).first()
    classifier_run = runs.exclude(classifier_tier='').first()

    if score_run is None and classifier_run is None:
        raise Http404()

    response = Response({
        'os_id': os_id,
        'score': _serialize_score(score_run),
        'classifier': _serialize_classifier(classifier_run),
    })
    response['Cache-Control'] = 'private, no-store'
    return response
