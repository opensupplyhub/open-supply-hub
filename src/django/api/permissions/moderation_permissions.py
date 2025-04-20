from api.permissions import IsRegisteredAndConfirmed, IsSuperuser
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


class IsModerator(IsSuperuser):
    """
    Permission class to check if the user is a moderator.
    Inherits from IsSuperuser which already checks if the user is a superuser.
    """
    message = 'Only moderators can access this resource.'


class IsModeratorOrContributor(permissions.BasePermission):
    """
    Permission class to check if the user is either a moderator or the contributor of a moderation event.
    """
    message = 'Only moderators or the contributor of this moderation event can access it.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        if obj.contributor and obj.contributor.admin:
            return request.user == obj.contributor.admin
        
        return False
