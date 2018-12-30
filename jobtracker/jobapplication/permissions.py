from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Only return True if object's creator === Request.user, or if request is
    coming from a superuser
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user == obj.creator:
            return True
        raise PermissionDenied({
            "message": "Access Forbidden"
        })
