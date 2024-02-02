from rest_framework.permissions import IsAdminUser


class IsListAndAdminOrNotList(IsAdminUser):
    """
    Custom permission to only allow access to lists for admins
    """

    def has_permission(self, request, view):
        is_admin = (
            super(IsListAndAdminOrNotList, self)
            .has_permission(request, view)
        )
        return view.action != 'list' or is_admin
