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
STATUS_NOT_FOUND = 404

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
            by another user. Should return 404 so user doesn't know object
            exists at all.
        normal_user_get_own: User should be able to get details about a company
            object they've created
        normal_user_get_list: User should receive a list of all the Company
            objects they've created if issuing a GET request to listview
        superuser_get_other: Superuser should be allowed to GET Company created
            by another user.
        superuser_get_list: Superuser GET on listview should return all Company
            objects in the database, regardless of creator

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
            name=self.COMPANY_NAME + 'su', website=self.COMPANY_WEBSITE + 'su',
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
        details. Should return 404 so user doesn't know object exists at all.
        """
        pk = self.super_user_company.pk
        request = self.factory.get(reverse('company-detail', args=[pk]))
        force_authenticate(request, user=self.non_super_user)

        response = self.detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_NOT_FOUND)
        data = response.data
        self.assertEqual(str(data['detail']),
                         'Not found.')

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

    def test_normal_user_get_list(self):
        """
        When there are more than one Company record in the database, a GET
        request should return all Companies created by the current user
        """
        Company.objects.get_or_create(
            name="throwaway", website="https://test.com",
            creator=self.non_super_user
        )

        Company.objects.get_or_create(
            name="throwaway super", website="https://testsuper.com",
            creator=self.super_user
        )

        request = self.factory.get(reverse('company-list'))
        force_authenticate(request, user=self.non_super_user)
        response = self.listview(request)
        self.assertEqual(response.status_code, STATUS_OK)

        # Ensure the correct number of records are present
        returned_companies = response.data['results']
        db_companies = Company.objects.filter(
            creator=self.non_super_user).order_by('name')
        self.assertEqual(len(returned_companies), len(db_companies))

        for ret_comp, db_comp in zip(returned_companies, db_companies):
            self.assertEqual(ret_comp['id'], str(db_comp.id))
            self.assertEqual(ret_comp['name'], db_comp.name)
            self.assertEqual(ret_comp['website'], db_comp.website)
            act_url = ret_comp['creator']
            exp_url = DOMAIN + reverse('user-detail', args=[db_comp.creator_id])
            self.assertEqual(act_url, exp_url)

    def test_superuser_get_other(self):
        """
        Superuser should be allowed to GET Company created
        by another user.
        """
        pk = self.normal_company.pk
        request = self.factory.get(reverse('company-detail', args=[pk]))
        force_authenticate(request, user=self.super_user)

        response = self.detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_OK)
        company = response.data
        self.assertEqual(company['name'], self.normal_company.name)
        self.assertEqual(company['website'], self.normal_company.website)
        act_url = company['creator']
        exp_url = DOMAIN + reverse('user-detail', args=[self.non_super_user.id])
        self.assertEqual(act_url, exp_url)

    def test_superuser_get_own(self):
        """
        Superuser should be allowed to GET their own Company records
        """
        pk = self.super_user_company.pk
        request = self.factory.get(reverse('company-detail', args=[pk]))
        force_authenticate(request, user=self.super_user)

        response = self.detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_OK)
        company = response.data
        self.assertEqual(company['name'], self.super_user_company.name)
        self.assertEqual(company['website'], self.super_user_company.website)
        act_url = company['creator']
        exp_url = DOMAIN + reverse('user-detail', args=[self.super_user.id])
        self.assertEqual(act_url, exp_url)

    def test_superuser_get_list(self):
        """
        Superuser GET on listview should return all Company objects in the
        database, regardless of creator
        """
        Company.objects.get_or_create(
            name="throwaway", website="https://test.com",
            creator=self.non_super_user
        )

        Company.objects.get_or_create(
            name="throwaway super", website="https://testsuper.com",
            creator=self.super_user
        )

        request = self.factory.get(reverse('company-list'))
        force_authenticate(request, user=self.super_user)
        response = self.listview(request)
        self.assertEqual(response.status_code, STATUS_OK)

        # Ensure the correct number of records are present
        returned_companies = response.data['results']
        db_companies = Company.objects.all().order_by('name')
        self.assertEqual(len(returned_companies), len(db_companies))

        for ret_comp, db_comp in zip(returned_companies, db_companies):
            self.assertEqual(ret_comp['id'], str(db_comp.id))
            self.assertEqual(ret_comp['name'], db_comp.name)
            self.assertEqual(ret_comp['website'], db_comp.website)
            act_url = ret_comp['creator']
            exp_url = DOMAIN + reverse('user-detail', args=[db_comp.creator_id])
            self.assertEqual(act_url, exp_url)
