from rest_framework import permissions, viewsets

from jobapplication.models import Company, JobReference, JobApplication
from jobapplication.permissions import IsOwnerOrAdmin
from jobapplication.serializers import (CompanySerializer,
                                        JobReferenceSerializer,
                                        JobApplicationSerializer,
                                        )


class BaseViewset(viewsets.ModelViewSet):
    """Base Class for filtering querysets based on current user.

    This viewset's queryset will only contian objects created by the current
    user, unless they are a superuser. If they are a superuser, it will return
    all objects of that class.

    Fields:
        model_class: Class open which to build queryset for serializing
        order_by_field: Object field by which queryset will be ordered
        permission_classes: restrictions on who can access endpoints

    Methods:
        get_queryset: Get a queryset of objects of type defined in `model_class`
            ordered by field defined in `order_by_field`. If user is a
            superuser, include all object records. If user is not a superuser,
            only get objects created by currently authenticated user.
    """

    model_class = None
    order_by_field = None
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdmin)


    def get_queryset(self):
        """
        Return a list of objects created by the current user. If they are a
        superuser, return all Object records
        :return: Queryset of Objects
        """
        if self.request.user.is_superuser:
            return self.model_class.objects.all().order_by(self.order_by_field)
        else:
            return self.model_class.objects.filter(
                creator=self.request.user).order_by(self.order_by_field)


class CompanyViewset(BaseViewset):
    """Viewset for Company objects.

    Company views should only be accessible by authenticated users

    Fields:
        serializer_class: serializer to use to represent companies
        model_class: class of model used in View
        order_by_field: field by which to order queryset

     Methods:
        perform_create: Assign the user associated with the current request to
            the Company being created before saving.

    """

    serializer_class = CompanySerializer
    model_class = Company
    order_by_field = 'name'

    def perform_create(self, serializer):
        """
        Add currently authenticated user as creator of this company object
        :param serializer: Serializer generated using the data from current
            request
        """
        serializer.save(creator=self.request.user)


class JobReferenceViewset(BaseViewset):
    """Viewset for JobReference objects.

    JobReference views should only be accessible by authenticated users

    Fields:
        serializer_class: serializer to use to represent job references
        model_class: class of model used in View
        order_by_field: field by which to order queryset

    Methods:
        get_queryset: Only get records created by the current user if they are
            a normal user. If they are a superuser, return all records.
        perform_create: Assign currently authenticated user as the object's
            creator
    """

    serializer_class = JobReferenceSerializer
    model_class = JobReference
    order_by_field = 'name'

    def perform_create(self, serializer):
        """
       Add currently authenticated user as creator of this JobReference object
       :param serializer: Serializer generated using the data from current
           request
       """
        serializer.save(creator=self.request.user)


class JobApplicationViewset(BaseViewset):
    """Viewset for JobApplication objects.

    JobApplication views should only be accessible by authenticated users.

    Fields:
        serializer_class: Serializer to use to render/save objects
        model_class: class of model used in View
        order_by_field: field by which to order queryset

    References:
        https://github.com/27medkamal/djangorestframework-fsm

    """

    serializer_class = JobApplicationSerializer
    model_class = JobApplication
    order_by_field = 'submitted_date'
