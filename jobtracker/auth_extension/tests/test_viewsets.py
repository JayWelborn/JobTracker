from copy import deepcopy as copy

from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import (APITestCase, APIRequestFactory,
                                 force_authenticate,
                                 )

from auth_extension.models import UserProfile
from auth_extension.viewsets import UserViewset, UserProfileViewset


class UserViewsetTests(APITestCase):
    """Tests for User View Set.

    Methods:
        setUp: Create test users
        tearDown: Empty test database
        test_user_list_on_get: `GET` requests with no `pk` should return a
            response containing a list of users ordered by pk.
        test_post_with_valid_data: `POST` requests should create User and
            associated profile.
        test_post_with_valid_json: `POST` requests should create User and
            associated profile.
        test_post_with_invalid_data: `POST1 requests with invalid data should
            return appropriate error message.
        test_get_with_pk: `GET` requests with `pk` should return details of
            specified user.
        test_get_with_invalid_pk: `GET` requests with invalid pk should return
            appropriate error message.
        test_put_with_valid_data: `PUT` requests should update appropriate
            field, leaving others unaffected.
        test_put_with_invalid_data: `PUT` requests with invalid data should
            fail and return appropriate error message.
        test_unauthenticated_put: `PUT` requests from unauthenticated user
            should return permission denied status code.
        test_put_from_another_user: `PUT` requests from users other than self
            should result in permission denied.
        test_delete_with_staff: Staff should be allowed to delete all users
        test_delete_with_self: users should be allowed to dleete their own
            accounts
        test_delete_others_fails: Non staff should not be able to delete other
            accounts.

    References:
        * http://www.django-rest-framework.org/api-guide/viewsets/
        * http://www.django-rest-framework.org/api-guide/permissions/
        * http://www.django-rest-framework.org/api-guide/testing/

    """

    def setUp(self):
        """
        Create several users for testing.
        """
        self.users = []
        for i in range(3):
            user = User.objects.create_user(
                username='user-{}'.format(i),
                email='test{}@test.test'.format(i),
                password='password23234545'
            )
            self.users.append(user)
            user.save()

        self.assertEqual(len(User.objects.all()), 3)
        self.factory = APIRequestFactory()
        self.listview = UserViewset.as_view({'get': 'list', 'post': 'create'})
        self.detailview = UserViewset.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })

    def tearDown(self):
        """
        Clean test database.
        """

        for user in User.objects.all():
            user.delete()
        self.assertEqual(len(User.objects.all()), 0)

    def test_user_list_on_get(self):
        """
        `GET` request with no pk should return list of all users ordered by
        `pk`.
        """

        request = self.factory.get(reverse('user-list'))
        response = self.listview(request)
        self.assertEqual(response.status_code, 200)

        data = response.data
        users = data['results']
        self.assertEqual(data['count'], len(self.users))

        for i in range(len(self.users)):
            self.assertEqual(self.users[i].username, users[i]['username'])
            self.assertEqual(users[i]['id'], i + 1)

    def test_post_with_valid_data(self):
        """
        `POST` requests to listview should create new user object if data is
        valid.
        """
        post_data = {
            'username': 'user-11',
            'email': 'test11@test.test',
            'password': 'rubytuesday'
        }
        url = reverse('user-list')
        request = self.factory.post(url, post_data)
        response = self.listview(request)

        self.assertEqual(response.status_code, 201)

        return_data = response.data
        for key, value in post_data.items():
            if key == 'password':
                continue
            self.assertEqual(return_data[key], value)

        user = User.objects.get(id=len(self.users) + 1)

        detail_url = reverse('user-detail', args=[user.id])
        detail_url = 'http://testserver' + detail_url
        self.assertEqual(return_data['url'], detail_url)
        self.assertEqual(return_data['id'], user.id)
        self.assertEqual(return_data['email'], user.email)
        self.assertEqual(return_data['username'], user.username)

        self.assertEqual(len(self.users) + 1, len(User.objects.all()))

    def test_post_with_valid_json(self):
        """
        `POST` requests to listview should create new user object if data is
        valid.
        """
        post_data = {
            'username': 'user-11',
            'email': 'test11@test.test',
            'password': 'rubytuesday'
        }
        url = reverse('user-list')
        request = self.factory.post(url, post_data, format='json')
        response = self.listview(request)

        self.assertEqual(response.status_code, 201)

        return_data = response.data
        for key, value in post_data.items():
            if key == 'password':
                continue
            self.assertEqual(return_data[key], value)

        user = User.objects.get(id=len(self.users) + 1)

        detail_url = reverse('user-detail', args=[user.id])
        detail_url = 'http://testserver' + detail_url
        self.assertEqual(return_data['url'], detail_url)
        self.assertEqual(return_data['id'], user.id)
        self.assertEqual(return_data['email'], user.email)
        self.assertEqual(return_data['username'], user.username)

        self.assertEqual(len(self.users) + 1, len(User.objects.all()))

    def test_post_with_invalid_data(self):
        """
        `POST` should reject invalid data and return appropriate error code.
        """

        invalid_email = {
            'username': 'username',
            'email': 'notanemail',
            'password': 'password',
        }
        request = self.factory.post(reverse('user-list'), invalid_email)
        response = self.listview(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'],
                         ['Enter a valid email address.'])

        missing_username = {
            'email': 'email@e.mail',
            'password': 'password',
        }

        request = self.factory.post(reverse('user-list'), missing_username)
        response = self.listview(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'],
                         ['This field is required.'])

        missing_password = {
            'username': 'username',
        }

        request = self.factory.post(reverse('user-list'), missing_password)
        response = self.listview(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        self.assertEqual(response.data['password'],
                         ['This field is required.'])

    def test_get_with_pk(self):
        """
        GET requests that include a Primay Key should retrieve detailed
        information about a single object.
        """
        user = self.users[0]
        pk = user.pk
        request = self.factory.get(reverse('user-detail', args=[pk]))
        response = self.detailview(request, pk=pk)
        data = response.data

        self.assertEqual(response.status_code, 200)
        for key, value in data.items():
            if key in ['id', 'username', 'email']:
                self.assertEqual(value, getattr(user, key))

    def test_get_with_invalid_pk(self):
        """
        `GET` requests with invalid PK should fail loudly and return proper
        Error code.
        """

        user = self.users[-1]
        pk = user.pk + 1
        request = self.factory.get(reverse('user-detail', args=[pk]))
        response = self.detailview(request, pk=pk)

        self.assertEqual(response.status_code, 404)
        self.assertIn('Not Found', response.status_text)

    def test_put_with_valid_data(self):
        """
        `PUT` requests with valid data should be accepted and update user
        object fields as needed.
        """
        user = copy(self.users[0])
        pk = user.pk
        new_username = {
            'username': 'new-0'
        }
        username_request = self.factory.put(
            reverse('user-detail', args=[pk]),
            instance=user,
            data=new_username
        )
        force_authenticate(username_request, user=user)

        response = self.detailview(username_request, pk=pk, partial=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], new_username['username'])
        self.assertEqual(response.data['email'], user.email)
        self.assertEqual(response.data['id'], user.id)

        user = User.objects.get(id=self.users[0].id)
        pk = user.pk
        new_email = {
            'email': 'new@new.new'
        }
        email_request = self.factory.put(
            reverse('user-detail', args=[pk]),
            instance=user,
            data=new_email
        )
        force_authenticate(email_request, user=user)

        response = self.detailview(email_request, pk=pk, partial=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], new_email['email'])
        self.assertEqual(response.data['username'], user.username)
        self.assertEqual(response.data['id'], user.id)

    def test_unauthenticated_put(self):
        """
        `PUT` requests coming from unauthenticated users should return 403
        forbidden.
        """
        user = copy(self.users[0])
        pk = user.pk
        new_username = {
            'username': 'new-0'
        }
        request = self.factory.put(
            reverse('user-detail', args=[pk]),
            instance=user,
            data=new_username
        )

        response = self.detailview(request, pk=pk, partial=True)

        self.assertEqual(response.status_code, 403)
        data = response.data
        self.assertEqual(
            data['detail'],
            'Authentication credentials were not provided.')

    def test_put_from_another_user(self):
        """
        `PUT` requests from user other than self should result in permission
        denied.
        """
        user = copy(self.users[0])
        pk = user.pk
        new_username = {
            'username': 'new-0'
        }
        request = self.factory.put(
            reverse('user-detail', args=[pk]),
            instance=user,
            data=new_username
        )

        force_authenticate(request, user=self.users[1])

        response = self.detailview(request, pk=pk, partial=True)
        data = response.data
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            data['detail'],
            'You do not have permission to perform this action.')

    def test_delete_with_staff(self):
        """
        Staff should be allowed to delete any user.
        """
        user = copy(self.users[0])
        pk = user.pk
        new_username = {
            'username': 'new-0'
        }
        request = self.factory.delete(
            reverse('user-detail', args=[pk]),
            instance=user,
            data=new_username
        )
        staff = self.users[1]
        staff.is_staff = True

        force_authenticate(request, user=staff)

        response = self.detailview(request, pk=pk, partial=True)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.status_text, 'No Content')
        self.assertRaises(User.DoesNotExist, User.objects.get, pk=pk)

    def test_delete_with_self(self):
        """
        Users should be able to delete themselves.
        """
        user = copy(self.users[0])
        pk = user.pk
        new_username = {
            'username': 'new-0'
        }
        request = self.factory.delete(
            reverse('user-detail', args=[pk]),
            instance=user,
            data=new_username
        )

        force_authenticate(request, user=user)

        response = self.detailview(request, pk=pk, partial=True)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.status_text, 'No Content')
        self.assertRaises(User.DoesNotExist, User.objects.get, pk=pk)

    def test_delete_with_other_user(self):
        """
        Users should not be able to delete each other.
        """

        user = copy(self.users[0])
        pk = user.pk
        new_username = {
            'username': 'new-0'
        }
        request = self.factory.delete(
            reverse('user-detail', args=[pk]),
            instance=user,
            data=new_username
        )

        force_authenticate(request, user=self.users[1])

        response = self.detailview(request, pk=pk, partial=True)
        data = response.data
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            data['detail'],
            'You do not have permission to perform this action.')


class UserProfileViewsetTests(APITestCase):
    """Tests for User Profile API Endpoint.

    After testing Users, I have decided to only write tests for methods that
    should be affected by permissions. Many tests on the User endpoint tested
    the framework rather than my code. That took a lot of time that could have
    gone towards something else.

    Methods:
        setUp: Create test users and profiles
        tearDown: Empty test database between iterations
        unauthenticated_user_can_only_get: Unauthenticated users should only be
            able to `GET` info from this endpoint.
        wrong_user_can_only_get: Users should only be able to `GET` other users
            profile's from this endpoint.
        user_can_modify_and_delete_themselves: Users should be able to modify
            or delete their own profiles.
        staff_can_modify_or_delete_profiles: Staff should be able to modify or
            delete all profiles.

    References:

    """

    def setUp(self):
        """
        Create test data.
        """
        self.users = []
        for i in range(3):
            user = User.objects.create_user(
                username='user-{}'.format(i),
                email='test{}@test.test'.format(i),
                password='password23234545'
            )
            self.users.append(user)
            user.save()

        self.profiles = []
        for user in User.objects.all():
            profile = UserProfile.objects.get_or_create(user=user)[0]
            self.profiles.append(profile)

        self.assertEqual(len(User.objects.all()), 3)
        self.assertEqual(len(UserProfile.objects.all()), 3)

        self.factory = APIRequestFactory()
        self.listview = UserProfileViewset.as_view({
            'get': 'list',
        })
        self.detailview = UserProfileViewset.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })

    def tearDown(self):
        """
        Clear Test Database.
        """
        for user in User.objects.all():
            user.delete()

    def test_unauthenticated_user_can_only_get(self):
        """
        Unauthenticated visitors should not be able to create, modify, or
        delete profiles.
        """

        # `GET` requests
        list_url = reverse('userprofile-list')
        request = self.factory.get(list_url)
        response = self.listview(request)
        results = response.data['results']
        self.assertEqual(response.status_code, 200)

        for index, profile in enumerate(UserProfile.objects.all()):
            self.assertEqual(results[index]['slug'], profile.slug)

        user = self.users[0]
        user_id = user.profile.id
        detail_url = reverse('userprofile-detail', args=[user_id])
        request = self.factory.get(detail_url)
        response = self.detailview(request, pk=user_id)
        data = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['slug'], user.username)

        # `POST` request
        post_data = {
        }

        request = self.factory.post(list_url, post_data)
        response = self.listview(request)
        self.assertEqual(response.status_code, 403)

        # `PUT` request
        request = self.factory.put(
            detail_url,
            instance=user,
            data=post_data)
        response = self.detailview(request, pk=id, partial=True)
        self.assertEqual(response.status_code, 403)

        # `DELETE` request
        request = self.factory.delete(
            detail_url
        )
        response = self.detailview(request)
        self.assertEqual(response.status_code, 403)

    def test_wrong_user_can_only_get(self):
        """
        User should be able to `GET` any profile, but not `POST`, `PUT`, or
        `DELETE` anyone else.
        """

        user = self.users[0]
        profile = self.users[1].profile
        pk = profile.pk

        # `GET` another profile should succeed
        request = self.factory.get(
            reverse('userprofile-detail', args=[pk])
        )
        force_authenticate(request, user=user)
        response = self.detailview(request, pk=pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['slug'], profile.slug)

        # `PUT` request should fail
        data = {
        }
        request = self.factory.put(
            reverse('userprofile-detail', args=[pk]),
            data=data
        )
        force_authenticate(request, user=user)
        response = self.detailview(request, pk=pk)
        self.assertEqual(response.status_code, 403)

        # `DELETE` request should fail
        request = self.factory.delete(
            reverse('userprofile-detail', args=[pk])
        )
        force_authenticate(request, user=user)
        response = self.detailview(request, pk=pk)
        self.assertEqual(response.status_code, 403)

    def test_user_can_modify_and_delete_themselves(self):
        """
        User should be able to modify or delete their own profile.
        """

        user = self.users[0]
        profile = user.profile
        pk = profile.pk
        url = reverse('userprofile-detail', args=[pk])

        # `PUT` should work on self
        data = {
        }
        request = self.factory.put(
            url,
            data=data
        )
        force_authenticate(request, user=user)
        response = self.detailview(request, pk=pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['slug'], profile.slug)

        # `DELTE` should work on self
        request = self.factory.delete(url)
        force_authenticate(request, user=user)
        response = self.detailview(request, pk=pk)
        self.assertEqual(response.status_code, 204)
        self.assertRaises(
            UserProfile.DoesNotExist, UserProfile.objects.get, pk=pk
        )

    def test_staff_can_modify_and_delete_profiles(self):
        """
        Staff should be able to modify or delete anyone.
        """

        staff = self.users[0]
        user = self.users[1]
        pk = user.profile.id
        url = reverse('userprofile-detail', args=[pk])
        staff.is_staff = True
        data = {
        }

        # test staff can `PUT` other profile
        request = self.factory.put(
            url,
            data=data,
            partial=True
        )
        force_authenticate(request, staff)

        response = self.detailview(request, pk=pk)
        self.assertEqual(response.status_code, 200)

        # test staff can `DELETE` other profile
        request = self.factory.delete(url)
        force_authenticate(request, staff)
        response = self.detailview(request, pk=pk)
        self.assertEqual(response.status_code, 204)

    def test_user_creates_profile(self):
        """
        Test the perform_create viewset method
        """
        new_user = User.objects.create_user("beans", "beans@gmail.com",
                                            "ilovebeans")
        data = {
        }
        url = reverse('userprofile-list')
        request = self.factory.post(
            url, data=data,
        )
        force_authenticate(request, new_user)
        response = self.listview(request)
        self.assertEqual(response.status_code, 405)
        self.assertIn('detail', response.data)
        self.assertEquals(str(response.data['detail']),
                          'Method "POST" not allowed.')

