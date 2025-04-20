from rest_framework import permissions


class IsModerationEventContributor(permissions.BasePermission):
    """
    Permission class to check if the user is the contributor of a moderation event.
    """
    message = 'Only the contributor of this moderation event can access it.'

    def has_object_permission(self, request, view, obj):
        if obj.contributor and obj.contributor.admin:
            return request.user == obj.contributor.admin
        return False


class IsModerator(permissions.BasePermission):
    """
    Permission class to check if the user is a moderator.
    """
    message = 'Only moderators can access this resource.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if not request.user.did_register_and_confirm_email:
            return False

        return request.user.is_superuser


class IsModeratorOrContributor(permissions.BasePermission):
    """
    Permission class to check if the user is either a moderator or the contributor of a moderation event.
    """
    message = 'Only moderators or the contributor of this moderation event can access it.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        return IsModerationEventContributor().has_object_permission(request, view, obj)
