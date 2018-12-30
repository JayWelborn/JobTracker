from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import (APITestCase, APIRequestFactory,
                                 force_authenticate,
                                 )

from jobapplication.models import Company, JobReference, JobApplication
from jobapplication.viewsets import (CompanyViewset, JobReferenceViewset,
                                     JobApplicationViewset,
                                     )

# Status codes
STATUS_OK = 200
STATUS_CREATED = 201
STATUS_NO_CONTENT = 204
STATUS_BAD_REQUEST = 400
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404

# DRF url domain
DOMAIN = 'http://testserver'


class BaseJobapplicationViewsetTests(APITestCase):
    """Setup and teardown methods for all Job Application app Viewsets.

    Methods:
        setUp: Create test objects
        tearDown: Empty test database
    """

    USERNAME = "normaluser"
    EMAIL = "normal@norm.al"
    PASSWORD = "pfa;23po4u2oidfsj;lkjf"

    SUPERUSERNAME = "superuser"
    SUPEREMAIL = "super@su.per"
    SUPERPASSWORD = "pfa23po4u2oidfsjlkjf"

    COMPANY_NAME = "Normal Company"
    COMPANY_WEBSITE = "www.website.com"

    REFERENCE_NAME = "user's friend"
    REFERENCE_EMAIL = "friend@gmail.com"

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

        self.normal_reference = JobReference.objects.get_or_create(
            name="Normal " + self.REFERENCE_NAME,
            email="normal" + self.REFERENCE_EMAIL, company=self.normal_company,
            creator=self.non_super_user
        )[0]

        self.super_user_reference = JobReference.objects.get_or_create(
            name="Super " + self.REFERENCE_NAME,
            email="super" + self.REFERENCE_EMAIL,
            company=self.normal_company, creator=self.super_user
        )[0]

        self.factory = APIRequestFactory()
        self.company_listview = CompanyViewset.as_view({
            'get': 'list',
            'post': 'create'
        })
        self.company_detailview = CompanyViewset.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })

        self.reference_listview = JobReferenceViewset.as_view({
            'get': 'list',
            'post': 'create'
        })
        self.reference_detailview = JobReferenceViewset.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })

        self.application_listview = JobApplicationViewset.as_view({
            'get': 'list',
            'post': 'create'
        })
        self.application_detailview = JobApplicationViewset.as_view({
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


class CompanyViewsetTests(BaseJobapplicationViewsetTests):
    """Tests for Company Viewset.

    Methods:
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
        superuser_get_own: Superuser should be allowed to GET Company created by
            themselves.
        superuser_get_list: Superuser GET on listview should return all Company
            objects in the database, regardless of creator

        authenticated_post: Regardless of user type, POST requests should create
            a new object if they contain complete, correct data.
        invalid_post: If the data is incomplete or incorrect, the POST should
            fail with status 400 BAD REQUEST.
        unauthenticated_post: Unauthenticated users attempting POST request
            should return 403

        authenticated_put: Correctly formed PUT requests should completely
            overwrite old Company object data.
        normal_user_put_other: Non superuser should not be able to send PUT
            requests to url of object created by another user
        invalid put: Incomplete PUT requests or PUT requests with invalid data
            should fail with status 400 Bad Request
        unauthenticated_put: PUT requests without authentication should return
            403 Forbidden.

        valid_patch: Normal users should be able to PATCH their own objects.
            Superusers should be able to PATCH all objects.
        normal_user_patch_other: Normal users should not be able to PATCH
            objects made by others. These objects should not be queryable, and
            so should return 404 Not Found.
        invalid_patch: PATCH requests with invalid data should fail with status
            400 Bad Request

        user_deletes_own:Both normal user and superuser should be able to delete
            objects they created.
        superuser_delete_other: Superuser should be able to DELETE objects
            created by others
        normal_user_delete_other: Non-superusers should not be able to DELETE
            objects created by others. Requests should return 404 Not Found, as
            those items won't be in that user's queryset
        unauthenticated_user_delete: Unauthenticated requests to DELETE anything
            should return 403 Forbidden.

    """

    def test_unauthenticated_get(self):
        """
        Unauthenticated GET requests should return 403 forbidden
        """
        request = self.factory.get(reverse('company-list'))
        response = self.company_listview(request)
        self.assertEqual(response.status_code, STATUS_FORBIDDEN)

    def test_normal_user_get_other(self):
        """
        Non super-user should not be able to GET a different user's company's
        details. Should return 404 so user doesn't know object exists at all.
        """
        pk = self.super_user_company.pk
        request = self.factory.get(reverse('company-detail', args=[pk]))
        force_authenticate(request, user=self.non_super_user)

        response = self.company_detailview(request, pk=pk)
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
        response = self.company_detailview(request, pk=pk)
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
        response = self.company_listview(request)
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

        response = self.company_detailview(request, pk=pk)
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

        response = self.company_detailview(request, pk=pk)
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
        response = self.company_listview(request)
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

    def test_authenticated_post(self):
        """
        Regardless of user type, POST requests should create a new object if
        they contain complete, correct data.
        """
        # Try POST with normal user
        url = reverse('company-list')
        complete_data = {
            'name': 'Complete Data',
            'website': 'https://www.complete.com',
        }
        request = self.factory.post(url, complete_data)
        force_authenticate(request, user=self.non_super_user)
        response = self.company_listview(request)
        self.assertEqual(response.status_code, STATUS_CREATED)
        company = Company.objects.get(name='Complete Data')
        self.assertEqual(company.name, complete_data['name'])
        self.assertEqual(company.website, complete_data['website'])
        self.assertEqual(company.creator_id, self.non_super_user.id)

        # Try POST with superuser
        complete_data = {
            'name': 'Superuser Complete',
            'website': 'https://www.superuser.complete.com'
        }
        request = self.factory.post(url, complete_data)
        force_authenticate(request, user=self.super_user)
        response = self.company_listview(request)
        self.assertEqual(response.status_code, STATUS_CREATED)
        company = Company.objects.get(name='Superuser Complete')
        self.assertEqual(company.name, complete_data['name'])
        self.assertEqual(company.website, complete_data['website'])
        self.assertEqual(company.creator_id, self.super_user.id)

    def test_invalid_post(self):
        """
        If the data is incomplete or incorrect, the POST should fail with status
        400 BAD REQUEST
        """
        # Missing name
        url = reverse('company-list')
        missing_name = {
            'website': 'https://www.missingname.com'
        }
        request = self.factory.post(url, missing_name)
        force_authenticate(request, user=self.non_super_user)
        response = self.company_listview(request)
        self.assertEqual(response.status_code, STATUS_BAD_REQUEST)

        request = self.factory.post(url, missing_name)
        force_authenticate(request, user=self.super_user)
        response = self.company_listview(request)
        self.assertEqual(response.status_code, STATUS_BAD_REQUEST)

        # Missing website
        missing_website = {
            'name': 'Missing Website'
        }
        request = self.factory.post(url, missing_website)
        force_authenticate(request, user=self.super_user)
        response = self.company_listview(request)
        self.assertEqual(response.status_code, STATUS_BAD_REQUEST)

        request = self.factory.post(url, missing_website)
        force_authenticate(request, user=self.non_super_user)
        response = self.company_listview(request)
        self.assertEqual(response.status_code, STATUS_BAD_REQUEST)

        # Incorrect url
        incorrect_url = {
            'name': 'Valid Name',
            'website': 'notaurl'
        }
        request = self.factory.post(url, incorrect_url)
        force_authenticate(request, user=self.super_user)
        response = self.company_listview(request)
        self.assertEqual(response.status_code, STATUS_BAD_REQUEST)

        request = self.factory.post(url, incorrect_url)
        force_authenticate(request, user=self.non_super_user)
        response = self.company_listview(request)
        self.assertEqual(response.status_code, STATUS_BAD_REQUEST)

    def test_unauthenticated_post(self):
        """
        Unauthenticated POST requests should be rejected with 403 FORBIDDEN
        """
        url = reverse('company-list')
        complete_data = {
            'name': 'Complete Data',
            'website': 'https://www.complete.com',
        }
        request = self.factory.post(url, complete_data)
        response = self.company_listview(request)
        self.assertEqual(response.status_code, STATUS_FORBIDDEN)

    def test_authenticated_put(self):
        """
        Correctly formed PUT requests should completely overwrite old Company
        object data.
        """
        # Normal user PUT own object
        pk = self.normal_company.pk
        url = reverse('company-detail', args=[pk])
        data = {
            'name': 'Updated Company',
            'website': 'https://www.updated.com'
        }
        request = self.factory.put(url, data)
        force_authenticate(request, self.non_super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_OK)
        company = Company.objects.filter(creator=self.non_super_user)[0]
        self.assertEqual(company.name, data['name'])
        self.assertEqual(company.website, data['website'])
        self.assertEqual(company.creator_id, self.non_super_user.id)

        # Superuser PUT own object
        pk = self.super_user_company.pk
        url = reverse('company-detail', args=[pk])
        data = {
            'name': 'Updated Company',
            'website': 'https://www.updated.com'
        }
        request = self.factory.put(url, data)
        force_authenticate(request, self.super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_OK)
        company = Company.objects.filter(creator=self.super_user)[0]
        self.assertEqual(company.name, data['name'])
        self.assertEqual(company.website, data['website'])
        self.assertEqual(company.creator_id, self.super_user.id)

        # Superuser PUT other object
        pk = self.normal_company.pk
        url = reverse('company-detail', args=[pk])
        data = {
            'name': 'Updated Company Again',
            'website': 'https://www.updatedagain.com'
        }
        request = self.factory.put(url, data)
        force_authenticate(request, self.super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_OK)
        company = Company.objects.filter(creator=self.non_super_user)[0]
        self.assertEqual(company.name, data['name'])
        self.assertEqual(company.website, data['website'])
        self.assertEqual(company.creator_id, self.non_super_user.id)

    def test_normal_user_put_other(self):
        """
        Non superuser should not be able to send PUT requests to url of object
        created by another user.
        """
        pk = self.super_user_company.pk
        url = reverse('company-detail', args=[pk])
        data = {
            'name': 'Updated Company',
            'website': 'https://www.updated.com'
        }
        request = self.factory.put(url, data)
        force_authenticate(request, self.non_super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_NOT_FOUND)
        company = Company.objects.filter(creator=self.super_user)[0]
        self.assertNotEqual(company.name, data['name'])
        self.assertNotEqual(company.website, data['website'])
        self.assertNotEqual(company.creator_id, self.non_super_user.id)

    def test_invalid_put(self):
        """
        Incomplete PUT requests or PUT requests with invalid data should fail
        with status 400 Bad Request
        """
        pk = self.super_user_company.pk
        url = reverse('company-detail', args=[pk])
        missing_name = {
            'website': 'https://www.missingname.com'
        }
        request = self.factory.put(url, missing_name)
        force_authenticate(request, self.super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_BAD_REQUEST)

        missing_website = {
            'name': 'Missing Website'
        }
        request = self.factory.put(url, missing_website)
        force_authenticate(request, self.super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_BAD_REQUEST)

        invalid_website = {
            'name': 'Invalid Website',
            'website': 'notaurl'
        }
        request = self.factory.put(url, invalid_website)
        force_authenticate(request, self.super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_BAD_REQUEST)

    def test_unauthenticated_put(self):
        """
        PUT requests without authentication should return 403 Forbidden.
        """
        pk = self.normal_company.pk
        url = reverse('company-detail', args=[pk])
        data = {
            'name': 'Updated Company',
            'website': 'https://www.updated.com'
        }
        request = self.factory.put(url, data)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_FORBIDDEN)

    def test_valid_patch(self):
        """
        Normal users should be able to PATCH their own objects. Superusers
        should be able to PATCH all objects.
        """
        # Normal user PATCH own object
        pk = self.normal_company.pk
        url = reverse('company-detail', args=[pk])
        data = {
            'name': 'Patched Company',
        }
        request = self.factory.patch(url, data)
        force_authenticate(request, self.non_super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_OK)
        company = Company.objects.filter(creator=self.non_super_user)[0]
        self.assertEqual(company.name, data['name'])
        self.assertEqual(company.creator_id, self.non_super_user.id)

        # Superuser PATCH own object
        pk = self.super_user_company.pk
        url = reverse('company-detail', args=[pk])
        data = {
            'website': 'https://www.updated.com'
        }
        request = self.factory.patch(url, data)
        force_authenticate(request, self.super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_OK)
        company = Company.objects.filter(creator=self.super_user)[0]
        self.assertEqual(company.website, data['website'])
        self.assertEqual(company.creator_id, self.super_user.id)

        # Superuser PATCH other object
        pk = self.normal_company.pk
        url = reverse('company-detail', args=[pk])
        data = {
            'name': 'Patched Company Again',
        }
        request = self.factory.patch(url, data)
        force_authenticate(request, self.super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_OK)
        company = Company.objects.filter(creator=self.non_super_user)[0]
        self.assertEqual(company.name, data['name'])
        self.assertEqual(company.creator_id, self.non_super_user.id)

    def test_normal_user_patch_other(self):
        """
        Normal users should not be able to PATCH objects made by others. These
        objects should not be queryable, and so should return 404 Not Found.
        """
        pk = self.super_user_company.pk
        url = reverse('company-detail', args=[pk])
        data = {
            'name': 'Patched Company',
        }
        request = self.factory.patch(url, data)
        force_authenticate(request, self.non_super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_NOT_FOUND)
        company = Company.objects.filter(creator=self.super_user)[0]
        self.assertNotEqual(company.name, data['name'])
        self.assertNotEqual(company.creator_id, self.non_super_user.id)

    def test_invalid_patch(self):
        """
        PATCH requests with invalid data should fail with status 400 Bad Request
        """
        pk = self.super_user_company.pk
        url = reverse('company-detail', args=[pk])
        invalid_website = {
            'website': 'notaurl'
        }
        request = self.factory.patch(url, invalid_website)
        force_authenticate(request, self.super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_BAD_REQUEST)

    def test_user_deletes_own(self):
        """
        Both normal user and superuser should be able to DELETE objects they
        created.
        """
        # Superuser
        pk = self.super_user_company.pk
        url = reverse('company-detail', args=[pk])
        request = self.factory.delete(url)
        force_authenticate(request, self.super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_NO_CONTENT)
        self.assertNotIn(self.super_user_company, Company.objects.all())

        # Normal user
        pk = self.normal_company.pk
        url = reverse('company-detail', args=[pk])
        request = self.factory.delete(url)
        force_authenticate(request, self.non_super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_NO_CONTENT)
        self.assertNotIn(self.normal_company, Company.objects.all())

    def test_superuser_delete_other(self):
        """
        Superuser should be able to DELETE objects created by others
        """
        pk = self.normal_company.pk
        url = reverse('company-detail', args=[pk])
        request = self.factory.delete(url)
        force_authenticate(request, self.super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_NO_CONTENT)
        self.assertNotIn(self.normal_company, Company.objects.all())

    def test_normal_user_delete_other(self):
        """
        Non-superusers should not be able to DELETE objects created by others.
        Requests should return 404 Not Found, as those items won't be in that
        user's queryset
        """
        pk = self.super_user_company.pk
        url = reverse('company-detail', args=[pk])
        request = self.factory.delete(url)
        force_authenticate(request, self.non_super_user)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_NOT_FOUND)
        self.assertIn(self.super_user_company, Company.objects.all())

    def test_unauthenticated_user_delete(self):
        """
        Unauthenticated requests to DELETE objects should return 403 Forbidden.
        """
        pk = self.super_user_company.pk
        url = reverse('company-detail', args=[pk])
        request = self.factory.delete(url)
        response = self.company_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_FORBIDDEN)
        self.assertIn(self.super_user_company, Company.objects.all())


class JobReferenceViewsetTests(BaseJobapplicationViewsetTests):
    """Tests for Job Reference Viewset.

    Methods:
        unauthenticated_get: Unauthenticated GET requests should return 403
            Forbidden
        normal_user_get_other: User should not be able to GET a reference
            created by another user. Should return 404 so user doesn't know
            object exists at all.
        normal_user_get_own: User should be able to get details about a job
            reference object they've created
        normal_user_get_list: User should receive a list of all the JobReference
            objects they've created if issuing a GET request to listview
        superuser_get_other: Superuser should be allowed to GET JobReference
            created by another user.
        superuser_get_own: Superuser should be allowed to GET JobReference
            cretaed by themselves.
        superuser_get_list: Superuser GET on listview should return all
            JobReference objects in the database, regardless of creator.

    TODO
        authenticated_post: Regardless of user type, POST requests should create
            a new object if they contain complete, correct data.
        invalid_post: If the data is incomplete or incorrect, the POST should
            fail with status 400 BAD REQUEST.
        unauthenticated_post: Unauthenticated users attempting POST request
            should return 403
        authenticated_put: Correctly formed PUT requests should completely
            overwrite old Company object data.
        normal_user_put_other: Non superuser should not be able to send PUT
            requests to url of object created by another user
        invalid put: Incomplete PUT requests or PUT requests with invalid data
            should fail with status 400 Bad Request
        unauthenticated_put: PUT requests without authentication should return
            403 Forbidden.
        valid_patch: Normal users should be able to PATCH their own objects.
            Superusers should be able to PATCH all objects.
        normal_user_patch_other: Normal users should not be able to PATCH
            objects made by others. These objects should not be queryable, and
            so should return 404 Not Found.
        invalid_patch: PATCH requests with invalid data should fail with status
            400 Bad Request
        user_deletes_own:Both normal user and superuser should be able to delete
            objects they created.
        superuser_delete_other: Superuser should be able to DELETE objects
            created by others
        normal_user_delete_other: Non-superusers should not be able to DELETE
            objects created by others. Requests should return 404 Not Found, as
            those items won't be in that user's queryset
        unauthenticated_user_delete: Unauthenticated requests to DELETE anything
            should return 403 Forbidden.

        """

    def test_unauthenticated_get(self):
        """
        Unauthenticated GET requests should return 403 forbidden
        """
        request = self.factory.get(reverse('jobreference-list'))
        response = self.reference_listview(request)
        self.assertEqual(response.status_code, STATUS_FORBIDDEN)

    def test_normal_user_get_other(self):
        """
        Non super-user should not be able to GET a different user's company's
        details. Should return 404 so user doesn't know object exists at all.
        """
        pk = self.super_user_reference.pk
        request = self.factory.get(reverse('jobreference-detail', args=[pk]))
        force_authenticate(request, user=self.non_super_user)

        response = self.reference_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_NOT_FOUND)
        data = response.data
        self.assertEqual(str(data['detail']),
                         'Not found.')

    def test_normal_user_get_own(self):
        """
        Non superuser should be able to GET their own reference's details
        """
        pk = self.normal_reference.pk
        request = self.factory.get(reverse('jobreference-detail', args=[pk]))
        force_authenticate(request, user=self.non_super_user)
        response = self.reference_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_OK)

        # Ensure data is the expected data
        data = response.data
        actual_url = data['url']
        expected_url = DOMAIN + reverse('jobreference-detail', args=[pk])
        self.assertEqual(actual_url, expected_url)

        self.assertEqual(data['id'], str(self.normal_reference.pk))
        self.assertEqual(data['name'], self.normal_reference.name)
        self.assertEqual(data['email'], self.normal_reference.email)

        actual_url = data['creator']
        expected_url = DOMAIN + reverse('user-detail',
                                        args=[self.non_super_user.pk])
        self.assertEqual(actual_url, expected_url)

    def test_normal_user_get_list(self):
        """
        When there are more than one JobReference record in the database, a GET
        request should return all JobReferences created by the current user
        """
        JobReference.objects.get_or_create(
            name="throwaway", email="normalthrow@gmail.com",
            company=self.normal_company, creator=self.non_super_user
        )

        JobReference.objects.get_or_create(
            name="throwaway super", email="superthrow@gmail.com",
            creator=self.super_user, company=self.super_user_company
        )

        request = self.factory.get(reverse('jobreference-list'))
        force_authenticate(request, user=self.non_super_user)
        response = self.reference_listview(request)
        self.assertEqual(response.status_code, STATUS_OK)

        # Ensure the correct number of records are present
        returned_references = response.data['results']
        db_references = JobReference.objects.filter(
            creator=self.non_super_user).order_by('name')
        self.assertEqual(len(returned_references), len(db_references))

        for ret_ref, db_ref in zip(returned_references, db_references):
            self.assertEqual(ret_ref['id'], str(db_ref.id))
            self.assertEqual(ret_ref['name'], db_ref.name)
            self.assertEqual(ret_ref['email'], db_ref.email)
            act_url = ret_ref['creator']
            exp_url = DOMAIN + reverse('user-detail', args=[db_ref.creator_id])
            self.assertEqual(act_url, exp_url)

    def test_superuser_get_other(self):
        """
        Superuser should be allowed to GET JobReference created
        by another user.
        """
        pk = self.normal_reference.pk
        request = self.factory.get(reverse('jobreference-detail', args=[pk]))
        force_authenticate(request, user=self.super_user)

        response = self.reference_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_OK)
        reference = response.data
        self.assertEqual(reference['name'], self.normal_reference.name)
        self.assertEqual(reference['email'],
                         self.normal_reference.email)
        act_url = reference['creator']
        exp_url = DOMAIN + reverse('user-detail',
                                   args=[self.non_super_user.id])
        self.assertEqual(act_url, exp_url)

    def test_superuser_get_own(self):
        """
        Superuser should be allowed to GET their own JobReference records
        """
        pk = self.super_user_reference.pk
        request = self.factory.get(reverse('jobreference-detail', args=[pk]))
        force_authenticate(request, user=self.super_user)

        response = self.reference_detailview(request, pk=pk)
        self.assertEqual(response.status_code, STATUS_OK)
        reference = response.data
        self.assertEqual(reference['name'], self.super_user_reference.name)
        self.assertEqual(reference['email'], self.super_user_reference.email)
        act_url = reference['creator']
        exp_url = DOMAIN + reverse('user-detail', args=[self.super_user.id])
        self.assertEqual(act_url, exp_url)

    def test_superuser_get_list(self):
        """
        Superuser GET on listview should return all JobReference objects in the
        database, regardless of creator
        """
        JobReference.objects.get_or_create(
            name="throwaway", email="throw@away.com",
            creator=self.non_super_user, company=self.normal_company,
        )

        JobReference.objects.get_or_create(
            name="throwaway super", email="throwaway@super.com",
            creator=self.super_user, company=self.super_user_company,
        )

        request = self.factory.get(reverse('jobreference-list'))
        force_authenticate(request, user=self.super_user)
        response = self.reference_listview(request)
        self.assertEqual(response.status_code, STATUS_OK)

        # Ensure the correct number of records are present
        returned_references = response.data['results']
        db_references = JobReference.objects.all().order_by('name')
        self.assertEqual(len(returned_references), len(db_references))

        for ret_ref, db_ref in zip(returned_references, db_references):
            self.assertEqual(ret_ref['id'], str(db_ref.id))
            self.assertEqual(ret_ref['name'], db_ref.name)
            self.assertEqual(ret_ref['email'], db_ref.email)
            act_url = ret_ref['creator']
            exp_url = DOMAIN + reverse('user-detail', args=[db_ref.creator_id])
            self.assertEqual(act_url, exp_url)
