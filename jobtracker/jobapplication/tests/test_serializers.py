from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from ..models import Company, JobReference, JobApplication
from ..serializers import CompanySerializer, JobReferenceSerializer


class CompanySerializerTests(APITestCase):
    """Tests for Company Serializer

    Company serializer should be able to create, update, and delete company
    objects with all Model fields.

    Fields:
        USERNAME: username to include in tests
        PASSWORD: password to include in tests
        USER_EMAIL: user email address to include in tests
        COMP_NAME: company name to include in tests
        COMP_SITE: company website to include in tests

    Methods:
        setUp: Create clean data before each testcase
        tearDown: Clear test database between tests
        company_serializes_expected_fields: Serializer should return key-value
            pairs for all of the fields on the model. Values for missing fields
            should be empty.
        update_company_name: Serializer should update object in database with
            new name when "update" method is called.
        update_company_website: Serializer should update object in database with
            new website when "update" method is called.
        update_invalid_data: Serializer.is_valid() should return false if data
            is invalid. Invalid data includes non-url values for website, and
            empty company names.
    """

    USERNAME = "lazertagR0cks"
    PASSWORD = "IOPU@#Y$MbSDF"
    USER_EMAIL = "lazertag@hotness.mailcom"
    COMP_NAME = "TESTNAME"
    COMP_SITE = "https://www.testsite.com"

    def setUp(self):
        """
        Create clean data between each test case
        """
        self.user = User.objects.create_user(
            username=self.USERNAME,
            email=self.USER_EMAIL,
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

    def test_update_company_name(self):
        """
        Serializer should update object in database when "update" method is
        called.
        """
        creator = self.company.creator
        id = self.company.id
        name = self.company.name
        new_name = "New Name"
        website = self.company.website

        update = {
            'name': new_name,
        }

        serializer = CompanySerializer(self.company, data=update, partial=True,
                                       context=self.context)
        self.assertTrue(serializer.is_valid())
        updated_company = serializer.save()

        self.assertTrue(updated_company)
        self.assertEqual(new_name, updated_company.name)
        self.assertEqual(creator, updated_company.creator)
        self.assertEqual(id, updated_company.id)
        self.assertEqual(website, updated_company.website)
        self.assertNotEqual(name, updated_company.name)

    def test_update_company_website(self):
        """
        Serializer should update object in database when "update" method is
        called.
        """
        creator = self.company.creator
        company_id = self.company.id
        name = self.company.name
        website = self.company.website
        new_website = "https://www.new.com"

        update = {
            'website': new_website,
        }

        serializer = CompanySerializer(self.company, data=update, partial=True,
                                       context=self.context)
        self.assertTrue(serializer.is_valid())
        updated_company = serializer.save()

        self.assertTrue(updated_company)
        self.assertEqual(new_website, updated_company.website)
        self.assertNotEqual(website, updated_company.website)
        self.assertEqual(creator, updated_company.creator)
        self.assertEqual(company_id, updated_company.id)
        self.assertEqual(name, updated_company.name)

    def test_update_invalid_data(self):
        """
        Serializer.is_valid() should return false if data is invalid.
        Invalid data includes non-url values for website, and empty company
        names.
        """

        # Test invalid website URL
        invalid_website = 'notAUrl'

        update = {
            'website': invalid_website
        }

        serializer = CompanySerializer(self.company, data=update, partial=True,
                                       context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn('website', serializer.errors)
        website_error = serializer.errors['website'][0]
        self.assertEqual(website_error.code, 'invalid')
        self.assertEqual(str(website_error), 'Enter a valid URL.')

        # Test empty company name
        invalid_company = ""

        update = {
            'name': invalid_company
        }

        serializer = CompanySerializer(self.company, data=update, partial=True,
                                       context=self.context)
        self.assertFalse(serializer.is_valid())
        name_error = serializer.errors['name'][0]
        self.assertEqual(name_error.code, 'blank')
        self.assertEqual(str(name_error), 'This field may not be blank.')


class JobReferenceSerializerTests(APITestCase):
    """Tests for the Job Reference Serializer

    Job Reference serializer should create, update, and delete JobReference
    objects with all model fields.

    Fields:
        USERNAME: username to include in tests
        PASSWORD: password to include in tests
        USER_EMAIL: user email address to include in tests
        COMP_NAME: company name to include in tests
        COMP_SITE: company website to include in tests

    Methods:
        setUp: Create clean test data
        tearDown: Empty database between tests
        jobreference_serializes_expected_fields: Serializer should return
            key-value pairs for all fields on the model.
        update_name: Attempting to update name with string up to 128 characters
            should succeed. Empty string or 129+ characters should fail.
        update_email: Updating email field with valid email address should
            succeed. Invalid emails should fail. Blank emails are allowed, and
            should succeed.
    """

    USERNAME = "lazertagR0cks"
    PASSWORD = "IOPU@#Y$MbSDF"
    USER_EMAIL = "lazertag@hotness.mailcom"
    COMP_NAME = "TESTNAME"
    COMP_SITE = "www.testsite.com"
    REF_NAME = "Jimothy"
    REF_EMAIL = "jimothy@jim.othy"

    def setUp(self):
        """
        Create clean data between each test case
        """
        self.user = User.objects.create_user(
            username=self.USERNAME,
            email=self.USER_EMAIL,
            password=self.PASSWORD,
        )

        self.company = Company.objects.get_or_create(
            name=self.COMP_NAME,
            website=self.COMP_SITE,
            creator=self.user,
        )[0]

        self.reference = JobReference.objects.get_or_create(
            creator=self.user,
            company=self.company,
            name=self.REF_NAME,
            email=self.REF_EMAIL
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
        for reference in JobReference.objects.all():
            reference.delete()

    def test_jobreference_serializes_expected_fields(self):
        """
        Serializer should return JSON object with keys for every field on the
        model.
        """
        reference_fields = [f.name for f in self.reference._meta.get_fields()]
        serializer = JobReferenceSerializer(self.reference,
                                            context=self.context)

        for field in reference_fields:
            self.assertIn(field, serializer.data)

    def test_update_name(self):
        """
        If updating name field to any string up to 128 characters, is_valid()
        should return True.
        Attempting to update to an empty string or to > 128 character should
        return false.
        """
        valid = "Valid name"
        longest = "poiuytrewqwertyuiopoiuytrewqwert" + \
                  "poiuytrewqwertyuiopoiuytrewqwert" + \
                  "poiuytrewqwertyuiopoiuytrewqwert" + \
                  "poiuytrewqwertyuiopoiuytrewqwert"
        self.assertEqual(len(longest), 128)
        too_long = longest + "!"
        empty = ""

        # test the valid names
        for name in [valid, longest]:
            data = {
                'name': name
            }
            serializer = JobReferenceSerializer(self.reference, data=data,
                                                partial=True,
                                                context=self.context)
            self.assertTrue(serializer.is_valid())
            updated_reference = serializer.save()
            self.assertEqual(name, updated_reference.name)

        # test invalid names
        for index, name in enumerate([too_long, empty]):
            data = {
                'name': name
            }
            serializer = JobReferenceSerializer(self.reference, data=data,
                                                partial=True,
                                                context=self.context)
            self.assertFalse(serializer.is_valid())
            self.assertNotEqual(name, updated_reference.name)
            error = serializer.errors['name'][0]
            self.assertEqual(error.code, ['max_length', 'blank'][index])

    def test_update_email(self):
        """
        Updating email field with valid email address should succeed. Invalid
        emails should fail. Blank emails are allowed, and should succeed.
        """
        valid = "newemail@em.ail"
        empty = ""
        invalid_no_ampersand = "not.an.email"
        invalid_no_tld = "email@gmail"

        # Test valid email
        for index, email in enumerate([valid, empty]):
            data = {
                'email': email
            }
            serializer = JobReferenceSerializer(self.reference, data=data,
                                                partial=True,
                                                context=self.context)
            self.assertTrue(serializer.is_valid())
            updated_reference = serializer.save()
            self.assertEqual(email, updated_reference.email)

        # test invalid email
        invalids = [invalid_no_ampersand, invalid_no_tld]
        for index, email in enumerate(invalids):
            data = {
                'email': email
            }
            serializer = JobReferenceSerializer(self.reference, data=data,
                                                partial=True,
                                                context=self.context)
            self.assertFalse(serializer.is_valid())
            error = serializer.errors['email'][0]
            self.assertTrue(error.code)


class JobApplicationSerializerTests(APITestCase):
    """Tests for the Job Application Serializer

    Fields:
        USERNAME: username to include in tests
        PASSWORD: password to include in tests
        USER_EMAIL: user email address to include in tests
        COMP_NAME: company name to include in tests
        COMP_SITE: company website to include in tests

    Methods:
        setUp: Create clean data between tests
        tearDown: Empty database between tests

    References:

    """

    USERNAME = "lazertagR0cks"
    PASSWORD = "IOPU@#Y$MbSDF"
    USER_EMAIL = "lazertag@hotness.mailcom"
    COMP_NAME = "TESTNAME"
    COMP_SITE = "www.testsite.com"
    REF_NAME = "Jimothy"
    REF_EMAIL = "jimothy@jim.othy"

    def setUp(self):
        """
        Create clean test data between tests
        """
        self.user = User.objects.create_user(
            username=self.USERNAME,
            email=self.USER_EMAIL,
            password=self.PASSWORD,
        )

        self.company = Company.objects.get_or_create(
            name=self.COMP_NAME,
            website=self.COMP_SITE,
            creator=self.user,
        )[0]

        self.reference = JobReference.objects.get_or_create(
            creator=self.user,
            company=self.company,
            name=self.REF_NAME,
            email=self.REF_EMAIL
        )[0]

        self.context = {'request': None}

    def tearDown(self):
        """
        Empty database between tests
        """
        for user in User.objects.all():
            user.delete()
        self.assertFalse(Company.objects.all())
        self.assertFalse(JobApplication.objects.all())
