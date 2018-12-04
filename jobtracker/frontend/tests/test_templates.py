"""Test for home.views module.

These test cases ensure that views.py functions as expected under all anticipated
circumstances.
"""

from django.test import TestCase
from jobtracker.tests.helpers import create_user

PASSWORD_1 = 'fleerdygort'

USERNAME_1 = 'username'

RESPONSE_OK = 200


class IndexTemplateTests(TestCase):
    """Tests for frontend/index.html template

    Methods:

        setUp:
            recreate test data between tests

        test_authenticated_user_loads_react_app:
            If a user is authenticated, the react app shoud load. If no user
            is authenticated, it should not.

    References:

    """

    def setUp(self):
        """
        Create clean data before running each test
        """
        self.user = create_user(USERNAME_1, PASSWORD_1)

    def test_authenticated_user_loads_react_app(self):
        """
        If User is authenticated, the react script should load. If user is not
        authenticated, script should not load.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, RESPONSE_OK)
        self.assertContains(response, 'Log In')
        self.assertNotContains(response, 'frontend/main.js')

        self.client.login(username=USERNAME_1, password=PASSWORD_1)
        response = self.client.get('/')
        self.assertEqual(response.status_code, RESPONSE_OK)
        self.assertContains(response, 'frontend/main.js')
        self.assertNotContains(response, 'Log In')
