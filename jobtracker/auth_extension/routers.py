from rest_framework.routers import SimpleRouter

from .viewsets import UserProfileViewset, UserViewset

auth_extension_router = SimpleRouter()
auth_extension_router.register('users', UserViewset)
auth_extension_router.register('profiles', UserProfileViewset)
