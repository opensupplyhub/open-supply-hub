from urllib.parse import urlparse

from django.conf import settings
from django.utils.http import is_same_domain
from rest_framework import permissions


def _report_warning_to_rollbar(message, extra_data=None):
    ROLLBAR = getattr(settings, 'ROLLBAR', {})
    if ROLLBAR:
        import rollbar
        rollbar.report_message(message, level='warning', extra_data=extra_data)


def referring_host(request):
    referer = urlparse(request.META.get('HTTP_REFERER', ''))
    return referer.netloc.split(':')[0]


def referring_host_is_allowed(host):
    for pattern in settings.ALLOWED_HOSTS:
        if is_same_domain(host, pattern):
            return True
    return False


class IsAuthenticatedOrWebClient(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return True

        if settings.OAR_CLIENT_KEY == '':
            return True

        if request.path.startswith("/api/info"):
            return True

        client_key = request.META.get('HTTP_X_OAR_CLIENT_KEY')
        if client_key == settings.OAR_CLIENT_KEY:
            host = referring_host(request)
            if referring_host_is_allowed(host):
                return True
            else:
                _report_warning_to_rollbar(
                    'Unallowed referring host passed with API request',
                    extra_data={'host': host})
        else:
            _report_warning_to_rollbar(
                'Incorrect client key submitted with API request',
                extra_data={'client_key': client_key})

        return False


class IsAllowedHost(permissions.BasePermission):
    def has_permission(self, request, view):
        host = referring_host(request)
        if referring_host_is_allowed(host):
            return True
        else:
            _report_warning_to_rollbar(
                'Unallowed referring host passed with API request',
                extra_data={'host': host})


class IsRegisteredAndConfirmed(permissions.BasePermission):
    message = ('User must be registered and have confirmed their email to '
               'access.')

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if not request.user.did_register_and_confirm_email:
            return False

        return True


class IsSuperuser(IsRegisteredAndConfirmed):
    message = 'Only the moderator can perform this action.'

    def has_permission(self, request, view):
        is_registered = super().has_permission(request, view)
        return is_registered and request.user.is_superuser


def _get_organization_membership(request, view):
    """
    The requesting user's active membership of the organization named in
    the URL, cached on the request so the view can reuse it.
    """
    # Imported lazily: the service imports models, and this module is
    # imported while the views that the models' serializers pull in load.
    from api.services.organization_service import get_active_membership

    if not hasattr(request, 'organization_membership'):
        membership = get_active_membership(request.user)
        organization_uuid = str(view.kwargs.get('organization_uuid', ''))
        if (
            membership is not None
            and str(membership.organization.uuid) != organization_uuid
        ):
            membership = None
        request.organization_membership = membership

    return request.organization_membership


class IsOrganizationMember(IsRegisteredAndConfirmed):
    message = 'You are not a member of this organization.'

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        return _get_organization_membership(request, view) is not None


class IsOrganizationAdmin(IsOrganizationMember):
    message = 'Only an Admin of this organization can perform this action.'

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        return _get_organization_membership(request, view).is_admin
