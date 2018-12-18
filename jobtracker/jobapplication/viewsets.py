from rest_framework import permissions, viewsets

from jobapplication.models import Company, JobReference
from jobapplication.serializers import CompanySerializer, JobReferenceSerializer


class CompanyViewset(viewsets.ModelViewSet):
    """Viewset for Company objects.

    Company views should only be accessible by authenticated users

    Fields:
        queryset: list of companies ordered by name
        serializer_class: serializer to use to represent companies
        permission_classes: restrictions on who can access company endpoints

    """

    queryset = Company.objects.all().order_by('name', )
    serializer_class = CompanySerializer
    permission_classes = (permissions.IsAuthenticated,)


class JobReferenceViewset(viewsets.ModelViewSet):
    """Viewset for JobReference objects.

    JobReference views should only be accessible by authenticated users

    Fields:
        queryset: list of companies ordered by name
        serializer_class: serializer to use to represent companies
        permission_classes: restrictions on who can access company endpoints
    """

    queryset = JobReference.objects.all().order_by('name', )
    serializer_class = JobReferenceSerializer
    permission_classes = (permissions.IsAuthenticated,)
