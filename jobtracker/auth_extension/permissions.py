from rest_framework import permissions


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Custom Permission to only allow users to edit their own profiles. Allows
    staff to eit all profiles
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # write permission are only allowed to User who owns profile or staff
        return obj.user == request.user or request.user.is_staff


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Only return True if User === Request.user, or if request is coming from
    an admin.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ['DELETE', 'PUT', 'PATCH']:
            return request.user.is_staff or request.user == obj

        return super(IsSelfOrAdmin, self).has_object_permission(request, view, obj)
