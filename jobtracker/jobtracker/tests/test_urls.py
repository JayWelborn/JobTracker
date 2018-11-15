from django.test import TestCase


class BaseUrlConfTests(TestCase):
    """ Test for base url conf.

    These tests ensure that urls referred to by the base URLConf point to valid
    urls. These tests only ensure that a non-empty repsonse is returned
    from each of the urls pointed to in the base URLConf, not that those
    requests contain expected data.

    Methods:
        test_home: Tests that the catch-all url is routed to 'home' app
            for processing.
    References:
    """

    def test_home(self):
        """
        Test that requests without url parameters are referred to app 'HOME'
        and 'HOME' returns a valid response.
        """

        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
