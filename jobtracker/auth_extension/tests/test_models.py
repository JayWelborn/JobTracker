from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.test import TestCase
from django.urls import reverse

from auth_extension.models import UserProfile


class UserProfileModelTests(TestCase):
    """Tests for Contact Model

    Methods:
        setUp: Creates sample UserProfile object for testing
        test_creating_user_creates_profile: Ensures creating a User object
            also creates a related UserProfile object
        test_profile_links_to_user: Ensures User and UserProfile objects are
            linked as expected
        test_slugify_for_user_profile: Ensures username is correctly slugified
            when UserProfile instance is saved
        test_get_absolute_url: define url for viewing object instances

    References:
        * https://docs.djangoproject.com/en/1.11/topics/testing/

    """

    def setUp(self):
        """
        Create instance(s) for tests
        """
        self.test_user_one = User.objects.create(username='test one',
                                                 password='password',
                                                 email='test@test.com', )

        self.test_user_two = User.objects.create(username='test two',
                                                 password='password1',
                                                 email='test2@test.com')

        self.test_profile = UserProfile.objects.get_or_create(
            user=self.test_user_one)[0]

    def test_creating_user_creates_profile(self):
        """
        Test to ensure creating a new user also creates a new UserProfile
        linked to that user.
        """
        new_user = User.objects.create_user(
            username="modeltest",
            email="model@te.st",
            password="passwordmodeltest")
        new_profile = UserProfile.objects.get(user=new_user)

        self.assertTrue(new_profile)
        self.assertEqual(new_profile, new_user.profile)

    def test_profile_links_to_user(self):
        """
        Test to ensure UserProfile object is linked to a User upon creation
        """
        self.assertEqual(self.test_profile.user, self.test_user_one)
        self.assertEqual(self.test_user_one.profile, self.test_profile)

    def test_slugify_for_user_profile(self):
        """
        Test to ensure username slug is stored as expected when UserProfile
        instance is created
        """
        test_slug = slugify(self.test_user_one.username)
        self.assertEqual(self.test_profile.slug, test_slug)
        self.assertEqual(self.test_profile.slug, 'test-one')

    def test_get_absolute_url(self):
        """
        Absolute url should match the regex pattern from app-level urlconf
        """
        self.assertEqual(self.test_profile.get_absolute_url(),
                         '/api/profiles/{}/'.format(self.test_profile.id))

    def test_str(self):
        """
        Calling str() on profile instance should return this user's username.
        """
        self.assertEqual("Profile for: test one", str(self.test_profile))
