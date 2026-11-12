from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import (
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet

from ..models.contributor.contributor import Contributor
from ..models.spotlight_field import (
    DISPLAY_NAME_RULES,
    NAME_MAX_LENGTH,
    NAME_RULES,
    SpotlightField,
    SpotlightFieldProperty,
    validate_internal_name,
)

PENDING_APPROVAL_MESSAGE = (
    'Thanks! Your new fields are inactive until the OS Hub team approves '
    'them. Once approved, you can switch them on yourself, or they will go '
    'live automatically on the date we set.'
)


def _as_drf_error(error):
    """Turn a Django validation error into one the API returns as a 400."""
    return ValidationError(error.messages)


def serialize_property(prop):
    """Describe one Spotlight field the way the dashboard needs it."""
    return {
        'name': prop.name,
        'display_name': prop.display_name,
        'approved': prop.approved,
        'active': prop.active,
    }


class SpotlightFieldsViewSet(GenericViewSet):
    """
    Lets a Spotlight partner list, add and edit their own Spotlight fields.

    There is deliberately no delete: fields can only be marked inactive.
    Every action is limited to the requesting user's own contributor, so a
    partner can never see or change another partner's fields.
    """

    swagger_schema = None
    lookup_value_regex = '[a-z][a-z0-9_]*'

    def _partner(self, request):
        """Return the requesting user's contributor if they are a partner."""
        if not request.user.is_authenticated:
            raise NotAuthenticated()
        try:
            contributor = request.user.contributor
        except Contributor.DoesNotExist as exc:
            raise PermissionDenied(
                'Spotlight fields are only available to Spotlight partners.'
            ) from exc
        if not contributor.is_spotlight_partner:
            raise PermissionDenied(
                'Spotlight fields are only available to Spotlight partners.'
            )
        return contributor

    def _summary(self, contributor):
        """Everything the Spotlight dashboard section shows."""
        spotlight = SpotlightField.objects.filter(
            contributor=contributor).first()
        properties = spotlight.properties.all() if spotlight else []
        partner_field = spotlight.partner_field if spotlight else None
        return {
            'go_live_date': (
                spotlight.go_live_date.isoformat()
                if spotlight and spotlight.go_live_date else None
            ),
            'go_live_pending': bool(spotlight and spotlight.go_live_pending),
            'can_control_visibility': (
                contributor.can_control_spotlight_visibility
            ),
            'available_in_api': (
                partner_field.available_in_api if partner_field else True
            ),
            'available_in_data_downloads': (
                partner_field.available_in_data_downloads
                if partner_field else True
            ),
            'rules': {
                'name': NAME_RULES,
                'display_name': DISPLAY_NAME_RULES,
                'max_length': NAME_MAX_LENGTH,
            },
            'fields': [serialize_property(p) for p in properties],
        }

    def list(self, request):
        """Return the partner's fields, go-live date and visibility."""
        contributor = self._partner(request)
        return Response(self._summary(contributor))

    @transaction.atomic
    def create(self, request):
        """
        Add a field. It starts unapproved and inactive; an admin approves it.
        """
        contributor = self._partner(request)
        name = (request.data.get('name') or '').strip()
        display_name = (request.data.get('display_name') or '').strip()

        errors = {}
        try:
            validate_internal_name(name)
        except DjangoValidationError as exc:
            errors['name'] = exc.messages
        if not display_name or len(display_name) > NAME_MAX_LENGTH:
            errors['display_name'] = [
                f'Invalid display name. {DISPLAY_NAME_RULES}'
            ]
        spotlight = SpotlightField.get_or_create_for(contributor)
        if 'name' not in errors and spotlight.properties.filter(
                name=name).exists():
            errors['name'] = [
                f'You already have a field named "{name}". Internal names '
                'must be unique.'
            ]
        if errors:
            raise ValidationError(errors)

        prop = SpotlightFieldProperty(
            spotlight_field=spotlight,
            name=name,
            display_name=display_name,
        )
        prop._history_user = request.user
        prop.save()
        data = self._summary(contributor)
        data['message'] = PENDING_APPROVAL_MESSAGE
        return Response(data, status=HTTP_201_CREATED)

    @transaction.atomic
    def partial_update(self, request, pk=None):
        """
        Change a field's display name and/or switch it on or off. The
        internal name cannot be changed.
        """
        contributor = self._partner(request)
        if 'name' in request.data:
            raise ValidationError(
                {'name': ['The internal name cannot be changed once saved.']}
            )
        spotlight = SpotlightField.objects.filter(
            contributor=contributor).first()
        prop = spotlight.properties.filter(
            name=pk).first() if spotlight else None
        if prop is None:
            raise ValidationError({'detail': 'Field not found.'})
        try:
            if 'display_name' in request.data:
                prop.update_display_name(
                    request.data['display_name'], request.user,
                    is_admin=False)
            if 'active' in request.data:
                prop.set_active(
                    bool(request.data['active']), request.user,
                    is_admin=False)
        except DjangoValidationError as exc:
            raise _as_drf_error(exc) from exc
        return Response(self._summary(contributor))

    @action(detail=False, methods=['patch'], url_path='visibility')
    @transaction.atomic
    def visibility(self, request):
        """
        Choose whether the fields appear in the API and in data downloads.
        Only partners an admin has granted this permission can change it.
        """
        contributor = self._partner(request)
        if not contributor.can_control_spotlight_visibility:
            raise PermissionDenied(
                'An OS Hub admin needs to grant you permission to change '
                'field visibility.'
            )
        spotlight = SpotlightField.get_or_create_for(contributor)
        partner_field = spotlight.partner_field
        for key in ('available_in_api', 'available_in_data_downloads'):
            if key in request.data:
                setattr(partner_field, key, bool(request.data[key]))
        partner_field.save()
        return Response(self._summary(contributor))
