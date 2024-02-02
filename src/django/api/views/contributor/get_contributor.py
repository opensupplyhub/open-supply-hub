from rest_framework.exceptions import ValidationError

from ...models import Contributor


def get_contributor(request):
    try:
        contributor_id = request.user.contributor.id
        return Contributor.objects.get(id=contributor_id)

    except Contributor.DoesNotExist as exc:
        raise ValidationError(
            'Contributor not found for requesting user.'
        ) from exc
