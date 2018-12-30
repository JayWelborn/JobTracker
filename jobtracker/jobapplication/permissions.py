from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Only return True if object's creator === Request.user, or if request is
    coming from a superuser
    """

    def has_object_permission(self, request, view, obj):
        """
        Determine if the user making request has permission to see the requested
        object. Currently, the application filters all objects not created by
        the requester out of the queryset before they can be retrieved.

        This renders this permission somewhat unnecessary. If non-creators are
        allowed to view objects in the future, replace the method body with the
        following:
            if request.user.is_superuser or request.user == obj.creator:
                return True
            raise PermissionDenied({
                "message": "Access Forbidden"
            })

        :param request: HTTP request
        :param view: View responsible for returning response
        :param obj: Object to check permission
        :return: True if user is superuser, or the object's creator
        """
        return request.user.is_superuser or request.user == obj.creator
