from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import (APITestCase, APIRequestFactory,
                                 force_authenticate,
                                 )

from jobapplication.models import Company
from jobapplication.viewsets import CompanyViewset

# Status codes
STATUS_OK = 200
STATUS_FORBIDDEN = 403

# DRF url domain
DOMAIN = 'http://testserver'


class CompanyViewsetTests(APITestCase):
    """Tests for Company Viewset.

    Methods:
        setUp: Create test objects
        tearDown: Empty test database
        unauthenticated_get: Unauthenticated GET requests should return 403
            Forbidden
        normal_user_get_other: User should not be able to GET a company created
            by another user
        normal_user_get_own: User should be able to get details about a company
            object they've created

    TODO - superuser GET, all user types POST, PUT, PATCH, DELETE

    """

    USERNAME = "normaluser"
    EMAIL = "normal@norm.al"
    PASSWORD = "pfa;23po4u2oidfsj;lkjf"
    SUPERUSERNAME = "superuser"
    SUPEREMAIL = "super@su.per"
    SUPERPASSWORD = "pfa23po4u2oidfsjlkjf"
    COMPANY_NAME = "Normal Company"
    COMPANY_WEBSITE = "www.website.com"

    def setUp(self):
        """
        Create test objects in database, and test factories and views
        """
        self.non_super_user = User.objects.create_user(
            self.USERNAME, self.EMAIL, self.PASSWORD)

        self.super_user = User.objects.create_superuser(
            self.SUPERUSERNAME, self.SUPEREMAIL, self.SUPERPASSWORD)

        self.normal_company = Company.objects.get_or_create(
            name=self.COMPANY_NAME, website=self.COMPANY_WEBSITE,
            creator=self.non_super_user)[0]

        self.super_user_company = Company.objects.get_or_create(
            name=self.COMPANY_NAME, website=self.COMPANY_WEBSITE,
            creator=self.super_user
        )[0]

        self.factory = APIRequestFactory()
        self.listview = CompanyViewset.as_view({
            'get': 'list',
            'post': 'create'
        })
        self.detailview = CompanyViewset.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })

    def tearDown(self):
        """
        Empty database between tests
        """
        for user in User.objects.all():
            user.delete()

    def test_unauthenticated_get(self):
        """
        Unauthenticated GET requests should return 403 forbidden
        """
        request = self.factory.get(reverse('company-list'))
        response = self.listview(request)
        self.assertEqual(response.status_code, STATUS_FORBIDDEN)

    def test_normal_user_get_other(self):
        """
        Non super-user should not be able to GET a different user's company's
        details
        """
        pk = self.super_user_company.pk
        request = self.factory.get(reverse('company-detail', args=[pk]))
        force_authenticate(request, user=self.non_super_user)

        response = self.detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_FORBIDDEN)
        data = response.data
        self.assertEqual(str(data['detail']),
                         'You do not have permission to perform this action.')

    def test_normal_user_get_own(self):
        """
        Non superuser should be able to GET their own company's details
        """
        pk = self.normal_company.pk
        request = self.factory.get(reverse('company-detail', args=[pk]))
        force_authenticate(request, user=self.non_super_user)
        response = self.detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_OK)

        # Ensure data is the expected data
        data = response.data
        actual_url = data['url']
        expected_url = DOMAIN + reverse('company-detail', args=[pk])
        self.assertEqual(actual_url, expected_url)

        self.assertEqual(data['id'], str(self.normal_company.pk))
        self.assertEqual(data['name'], self.COMPANY_NAME)
        self.assertEqual(data['website'], self.COMPANY_WEBSITE)

        actual_url = data['creator']
        expected_url = DOMAIN + reverse('user-detail',
                                        args=[self.non_super_user.pk])
        self.assertEqual(actual_url, expected_url)
