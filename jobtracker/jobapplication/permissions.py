from rest_framework import permissions
from django.contrib.auth.models import User


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Only return True if User === Request.user, or if request is coming from a
    superuser
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user == obj


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Only return True if object's creator === Request.user, or if request is
    coming from a superuser
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user == obj.creator
