from datetime import date, timedelta

from django.test import TestCase

from jobapplication.models import Company, JobApplication, JobReference
from jobtracker.tests.helpers import create_user

USERNAME_1 = "fleerdygort"
PASSWORD_1 = "poiuPOIU0987)(*&"


class CompanyTestCase(TestCase):
    """Test cases for Company model

    Methods:
        setUp: Create clean data between tests
        test_str: Ensure companies are converted to strings as expected

    References:
    """

    def setUp(self):
        """
        Create test users/objects so each test case starts with clean data
        """

        self.user = create_user(USERNAME_1, PASSWORD_1)
        self.company = Company.objects.get_or_create(
            name="Test Company INC.",
            website="www.testcompany.com",
            creator=self.user
        )[0]

    def test_str(self):
        """
        Companies should be converted to strings as follows:
            Company: {COMPANY NAME}
            Created By: {CREATOR'S USERNAME}
        """

        self.assertEquals("Company: Test Company INC.\nCreated By: fleerdygort",
                          str(self.company))


class JobReferenceTestCase(TestCase):
    """Test cases for JobReference model

    Methods:
        setUp: Create clean data between tests
        test_str: Ensure references are converted to strings as expected

    References:
    """

    def setUp(self):
        """
        Create clean objects between test cases
        """
        self.user = create_user(USERNAME_1, PASSWORD_1)
        self.company = Company.objects.get_or_create(
            name="Test Company INC.",
            website="www.testcompany.com",
            creator=self.user
        )[0]

        self.reference = JobReference.objects.get_or_create(
            name="Jimothy",
            company=self.company,
            creator=self.user,
        )[0]

    def test_str(self):
        """
        Job References should be converted to strings as follows:
            Reference: {NAME} at {COMPANY}
            Created By: {CREATOR'S USERNAME}
        """

        self.assertEqual(
            "Reference: Jimothy at Test Company INC.\nCreated By: fleerdygort",
            str(self.reference)
        )


class JobApplicationTests(TestCase):
    """Tests for the Job Application model

    Methods:
        setUp: Start each test with clean data
        test_create_new_model: new models should be created in the 'submitted'
            state, and each of the datefields for the followon states should
            be None.

        test_submitted_to_followup_send: sending followup should update the
            applications status to 'followup_sent' and set it's followup_date
            to the current date

        test_submitted_to_rejected: models should be able to transition from
            'submitted' to 'rejected' status. Reason message provided in reject
            method should be saved to models "rejected_reason" field.
            rejected_date should be today, but all other date fields should be
            none

    References:

    """

    def setUp(self):
        """
        Start each test with clean data
        """
        self.user = create_user(USERNAME_1, PASSWORD_1)
        self.company = Company.objects.get_or_create(
            name="Test Company INC.",
            website="www.testcompany.com",
            creator=self.user
        )[0]
        self.jobapp = JobApplication.objects.get_or_create(
            company=self.company,
            position="Software Engineer",
            city="Raleigh",
            state="North Carolina",
            creator=self.user,
        )[0]

        # Useful Dates
        self.dates = []
        for i in range(7):
            self.dates.append(date.today() - timedelta(days=i))

        # Ensure fixture object was created in the pas
        self.jobapp.submitted_date = self.dates[6]
        self.jobapp.save()

    def test_create_new_model(self):
        """
        New models should be created in the 'submitted' state
        """
        # Check state
        self.assertEqual(self.jobapp.status, "submitted")
        # Check date fields
        self.assertEquals(self.jobapp.submitted_date, self.dates[6])
        self.assertIsNone(self.jobapp.updated_date)
        self.assertIsNone(self.jobapp.rejected_date)

    def test_submitted_to_followup_sent(self):
        """
        Sending a followup should set the state to 'followup sent' and should
        set the followup_date to today
        """
        # Send followup
        self.jobapp.send_followup()
        # Check status
        self.assertEqual(self.jobapp.status, "followup_sent")
        self.assertEqual(self.jobapp.updated_date, date.today())

    def test_followup_sent_to_phone_screen(self):
        """
        Completing a Phone Screen should set the state to
        'phone_screen_complete' and should set the phone_screen_date to today
        """
        # Move fixture object through state pattern and hard set dates
        self.jobapp.send_followup()
        self.assertEqual(self.jobapp.updated_date, self.dates[0])

        self.jobapp.phone_screen()
        self.assertEqual(self.jobapp.status, "phone_screen_complete")
        self.assertEqual(self.jobapp.updated_date, self.dates[0])

    def test_submitted_to_rejected(self):
        """
        Calling 'reject' method should set status to 'rejected' and set
        rejected date to date provided as argument to `reject` method
        """
        # Reject the application
        self.jobapp.reject("No reason")
        # Check Status and rejected_reason
        self.assertEqual(self.jobapp.status, "rejected", self.dates[6])
        self.assertEqual(self.jobapp.rejected_reason, "No reason")
        # Check previous state
        self.assertEquals(self.jobapp.rejected_state, "submitted")
        # Check the model's date fields
        self.assertEquals(self.jobapp.rejected_date, date.today())
        self.assertIsNone(self.jobapp.updated_date)
