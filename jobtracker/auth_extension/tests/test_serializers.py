import copy

from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from auth_extension.models import UserProfile
from auth_extension.serializers import UserSerializer, UserProfileSerializer


class UserSerializerTest(APITestCase):
    """Tests for User Serializer.

    Methods:
        setUp: Create test data dictionary
        serializer_accepts_valid_data: Serializer should be valid when provided
            with username, email, and password
        user_and_profile_accepted_upon_save: Serializer should create new
            profile associated with new user
        proper_fields_included_on_retrieval: Password hash should not be sent
            when User object is serialized. Id, username, cards, profile,
            and email should be.
        user_updates_username: User should be able to update username without
            affecting other fields.
        user_updates_email: User updating email should not affect other fields.
        user_updates_username_and_email: User should be able to update any 2 of
            the three available fields without affecting the other two.
        user_updates_username_and_password: User should be able to update any 2
            of the three available fields without affecting the other two.
        user_updates_email_and_password: User should be able to update any 2 of
            the three available fields without affecting the other two.

    References:

        * http://www.django-rest-framework.org/api-guide/serializers/

    """

    def setUp(self):
        """
        Create test dictionary.
        """
        self.data = {
            'username': 'UserSerializerTest',
            'email': 'test@test.test',
            'password': 'password'
        }

        self.user = User.objects.get_or_create(
            username='retrievaltest',
            email='retrieval@retrieve.whatever'
        )[0]
        self.user.set_password('jimothy')
        self.user.save()

        self.profile = UserProfile.objects.get_or_create(
            user=self.user)[0]

    def tearDown(self):
        """
        Clean database so each test starts fresh.
        """
        for user in User.objects.all():
            user.delete()

    def test_serializer_accepts_valid_data(self):
        """
        Serializer should be valid when provided with a username, email and
        password.
        """

        serializer = UserSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_password_hashed_for_new_user(self):
        """
        Upon creation, new User's passwords should be hashed before storing
        in the database.
        """

        serializer = UserSerializer(data=self.data)
        if serializer.is_valid():
            user = serializer.save()
        else:
            self.fail("invalid data. Shouldn't happen")

        self.assertNotEqual(user.password, self.data['password'])
        self.assertNotEqual(len(user.password), len(self.data['password']))

    def test_user_and_profile_created_upon_save(self):
        serializer = UserSerializer(data=self.data)
        if serializer.is_valid():
            serializer.save()

        user = User.objects.get(username=self.data['username'])
        profile = UserProfile.objects.get_or_create(user=user)[0]
        self.assertTrue(user)
        self.assertTrue(user.profile)
        self.assertEqual(profile.user, user)
        self.assertEqual(user.profile, profile)

    def test_password_not_included_upon_retrieval(self):
        """
        Password should not be included when User is serialized
        """
        serializer = UserSerializer(self.user, context={'request': None})
        self.assertNotIn('password', serializer.data)

        included_fields = ['id', 'username', 'profile', 'email']
        for field in included_fields:
            self.assertIn(field, serializer.data)

    def test_user_updates_username(self):
        """
        User updating username should not affect other fields.
        """

        user = User.objects.get(username=self.user.username)
        email = user.email
        userid = user.id
        pk = user.pk
        profile = user.profile
        username = user.username

        update = {
            'username': 'NewUserName',
        }

        serializer = UserSerializer(user, data=update, partial=True,
                                    context={'request': None})
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertTrue(updated_user)
        self.assertEqual(updated_user.username, 'NewUserName')
        self.assertEqual(userid, updated_user.id)
        self.assertEqual(pk, updated_user.pk)
        self.assertEqual(email, updated_user.email)
        self.assertEqual(profile, updated_user.profile)

        self.assertNotEqual(username, updated_user.username)

    def test_user_updates_email(self):
        """
        User updating email should not affect other fields.
        """

        email = self.user.email
        username = self.user.username
        password = self.user.password
        userid = self.user.id
        pk = self.user.pk
        profile = self.user.profile

        update = {
            'email': 'newemail@new.new'
        }

        serializer = UserSerializer(self.user, data=update, partial=True,
                                    context={'request': None})
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertTrue(updated_user)
        self.assertEqual(updated_user.email, update['email'])
        self.assertEqual(updated_user.username, username)
        self.assertEqual(userid, updated_user.id)
        self.assertEqual(pk, updated_user.pk)
        self.assertEqual(password, updated_user.password)
        self.assertEqual(profile, updated_user.profile)
        self.assertNotEqual(email, updated_user.email)

    def test_user_updates_password(self):
        """
        User updating password should have password hashed before storage,
        and update should not affect other fields.
        """

        email = self.user.email
        username = self.user.username
        password = self.user.password
        userid = self.user.id
        pk = self.user.pk
        profile = self.user.profile

        update = {
            'password': 'newtestdude'
        }

        serializer = UserSerializer(self.user, data=update, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertTrue(updated_user)
        self.assertEqual(updated_user.email, email)
        self.assertEqual(updated_user.username, username)
        self.assertEqual(userid, updated_user.id)
        self.assertEqual(pk, updated_user.pk)
        self.assertEqual(profile, updated_user.profile)

        self.assertNotEqual(updated_user.password, update['password'])
        self.assertNotEqual(password, updated_user.password)

    def test_user_updates_username_and_email(self):
        """
        User updating any two fields should not affect the third field.
        """

        email = self.user.email
        username = self.user.username
        password = self.user.password
        userid = self.user.id
        pk = self.user.pk
        profile = self.user.profile

        update = {
            'username': 'multipletest',
            'email': 'multiple@mult.iple'
        }

        serializer = UserSerializer(self.user, data=update, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertTrue(updated_user)
        self.assertEqual(password, updated_user.password)
        self.assertEqual(userid, updated_user.id)
        self.assertEqual(pk, updated_user.pk)
        self.assertEqual(profile, updated_user.profile)

        self.assertNotEqual(updated_user.username, username)
        self.assertNotEqual(updated_user.email, email)

    def test_user_updates_username_and_password(self):
        """
        User updating any two fields should not affect the third field.
        """

        email = self.user.email
        username = self.user.username
        password = self.user.password
        userid = self.user.id
        pk = self.user.pk
        profile = self.user.profile

        update = {
            'username': 'multipletest',
            'password': 'multipleupdatepassword'
        }

        serializer = UserSerializer(self.user, data=update, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertTrue(updated_user)
        self.assertEqual(email, updated_user.email)
        self.assertEqual(userid, updated_user.id)
        self.assertEqual(pk, updated_user.pk)
        self.assertEqual(profile, updated_user.profile)

        self.assertNotEqual(updated_user.username, username)
        self.assertNotEqual(updated_user.password, password)

    def test_user_updates_email_and_password(self):
        """
        User updating any two fields should not affect the third field.
        """

        email = self.user.email
        username = self.user.username
        password = self.user.password
        userid = self.user.id
        pk = self.user.pk
        profile = self.user.profile

        update = {
            'password': 'multipletestthree',
            'email': 'multiple@mult.iple'
        }

        serializer = UserSerializer(self.user, data=update, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertTrue(updated_user)
        self.assertEqual(username, updated_user.username)
        self.assertEqual(userid, updated_user.id)
        self.assertEqual(pk, updated_user.pk)
        self.assertEqual(profile, updated_user.profile)

        self.assertNotEqual(updated_user.password, password)
        self.assertNotEqual(updated_user.email, email)


class UserProfileSerializerTest(APITestCase):
    """Tests for UserProfileSerializer

    Methods:
        setUp: Create User and Profile for testing.
        tearDown: Clean database between tests
        serializer_accepts_valid_data: `is_valid()` should return True when
            instantiated with valid data
        save_updates_correct_fields: Calling `.save()` should update correct
            fields on model
    References:
    """

    def setUp(self):
        """
        Create profile and data for tests.
        """

        self.user = User.objects.create_user(
            username='profileserializertests',
            email='profileserializer@test.com',
            password='passwordtesting'
        )

        self.profile = UserProfile.objects.get_or_create(user=self.user)[0]

        self.data = {
        }

        self.context = {'request': None}

    def tearDown(self):
        """
        Clear database between tests.
        """

        for user in User.objects.all():
            user.delete()

        self.assertEqual(len(UserProfile.objects.all()), 0)

    def test_serializer_accepts_valid_data(self):
        """
        Serializer.is_valid() should return true when instantiated with
        valid data.
        """

        serializer = UserProfileSerializer(
            data=self.data, context=self.context
        )
        self.assertTrue(serializer.is_valid())

    def test_save_updates_correct_fields(self):
        """
        Calling `.save()` should update correct fields on model.
        """
        serializer = UserProfileSerializer(
            self.profile, data=self.data, context=self.context
        )

        if serializer.is_valid():
            new_profile = serializer.save()
        else:
            self.fail("invalid data, test_update method")

        self.assertEqual(new_profile.user, self.user)

    def test_get_includes_expected_fields(self):
        """
        GET requests should include url, user, created_date, slug, picture,
        website, and about_me fields.
        """

        serializer = UserProfileSerializer(self.profile, context=self.context)
        expeted_fields = ['url', 'user', 'created_date', 'slug',]

        for field in expeted_fields:
            self.assertIn(field, serializer.data)
