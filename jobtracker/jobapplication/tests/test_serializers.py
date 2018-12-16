from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from ..models import Company
from ..serializers import CompanySerializer


class CompanySerializerTests(APITestCase):
    """Tests for Company Serializer

    Company serializer should be able to create, update, and delete company
    objects with all Model fields.

    Methods:
        setUp: Create clean data before each testcase
        tearDown: Clear test database between tests
        company_serializes_expected_fields: Serializer should return key-value
            pairs for all of the fields on the model. Values for missing fields
            should be empty.
    """

    USERNAME = "lazertagR0cks"
    PASSWORD = "IOPU@#Y$MbSDF"
    EMAIL = "lazertag@hotness.mailcom"
    COMP_NAME = "TESTNAME"
    COMP_SITE = "www.testsite.com"

    def setUp(self):
        """
        Create clean data between each test case
        """
        self.user = User.objects.create_user(
            username=self.USERNAME,
            email=self.EMAIL,
            password=self.PASSWORD,
        )

        self.company = Company.objects.get_or_create(
            name=self.COMP_NAME,
            website=self.COMP_SITE,
            creator=self.user,
        )[0]

        self.context = {'request': None}

    def tearDown(self):
        """
        Empty database between tests
        """
        for company in Company.objects.all():
            company.delete()
        for user in User.objects.all():
            user.delete()

    def test_company_serializes_expected_fields(self):
        """
        Serializer should return JSON object with keys for every field on the
        model.
        """
        company_fields = [f.name for f in self.company._meta.get_fields()]
        serializer = CompanySerializer(self.company, context=self.context)

        for field in company_fields:
            self.assertIn(field, serializer.data)

        #print(serializer.data['creator'])
