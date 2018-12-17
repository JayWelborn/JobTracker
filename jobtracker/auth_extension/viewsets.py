from django.contrib.auth.models import User
from rest_framework import permissions, viewsets

from auth_extension.models import UserProfile
from auth_extension.permissions import IsSelfOrAdmin, IsUserOrReadOnly
from auth_extension.serializers import UserSerializer, UserProfileSerializer


class UserViewset(viewsets.ModelViewSet):
    """
    Read only viewset class for User objects.

    Fields:
        queryset: list of users ordered by pk
        serializer_class: serializer used to represent users
        permission_classes: restrictions on who can access detail view
    """

    queryset = User.objects.all().order_by('pk')
    serializer_class = UserSerializer
    permission_classes = (IsSelfOrAdmin,)


class UserProfileViewset(viewsets.ModelViewSet):
    """
    Viewset for User Profiles.
    """

    queryset = UserProfile.objects.all().order_by('created_date')
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsUserOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
