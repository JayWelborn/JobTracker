from rest_framework import routers


class DefaultRouter(routers.DefaultRouter):
    """Extends 'DefaultRouter' to add method for extending other routers

    Methods:
        extend: Add another router's urls to this router
    """

    def extend(self, router):
        """
        Extend the routes with url routes of the passed in router.

        Args:
             router: SimpleRouter instance containing route definitions.
        """
        self.registry.extend(router.registry)
