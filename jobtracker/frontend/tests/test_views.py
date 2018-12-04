"""Test for home.views module.

These test cases ensure that views.py functions as expected under all anticipated
circumstances.
"""

from django.test import TestCase
from jobtracker.tests.helpers import create_user

PASSWORD_1 = 'fleerdygort'

USERNAME_1 = 'username'

RESPONSE_OK = 200


class IndexViewTests(TestCase):
    """Tests for Index View

    Methods:
        setUp:
            Recreate data between tests
        test_response_code:
            Ensure GET requests always return 200, whether or not a user is
            authenticated.

    References:
        https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    """

    def setUp(self):
        """
        Create clean data before running each test
        """
        self.user = create_user(USERNAME_1, PASSWORD_1)

    def test_response_code(self):
        """
        GET requests to index view should return 200, whether or not a user
        is authenticated.
        """
        response = self.client.get('')
        self.assertEqual(response.status_code, RESPONSE_OK)
        self.client.login(username=USERNAME_1, password=PASSWORD_1)
        response = self.client.get('')
        self.assertEqual(response.status_code, RESPONSE_OK)
