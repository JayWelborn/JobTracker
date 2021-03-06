from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from django_fsm import TransitionNotAllowed

from jobapplication.models import Company, JobApplication, JobReference
from jobapplication.exceptions import IncompatibleDateException
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

        test_create_new_model: New models should be created in the 'submitted'
            state, and its updated_date should be None.

        test_submitted_to_followup_sent: Sending followup should update the
            applications status to 'followup_sent' and set its updated_date
            to the current date

        test_followup_sent_to_phone_screen: Setting the phone screen as complete
            should update the status to 'phone_screen_complete' and set its
            updated_date ot the current date

        test_phone_screen_to_interview_scheduled: Scheduling the interview
            should update status to 'interview_scheduled', set updated_date to
            current date, and set interview_date to provided date

        test_attempt_to_schedule_interview_invalid_date: Attempting to schedule
            an interview for a date in the past should throw an
            IncompatibleDateException with the message "Interview date cannot
            be in the past"

        test_interview_complete: Completing the interview should set status to
            interview_complete and set updated_date to current date

        test_attempt_to_complete_interview_before_scheduled: Attempting to
            complete an interview before its scheduled date should raise an
            IncompatibleDateException

        test_offer_received: Receiving an offer should set the status to
            "offer_received" and set the updated_date to today

        test_submitted_to_rejected: Models should be able to transition from
            'submitted' to 'rejected' status. Reason message provided in reject
            method should be saved to models "rejected_reason" field.
            rejected_date should be today, but updated_date should be None.

        test_followup_sent_to_rejected: Models rejected after a followup should
            have rejected_reason, rejected_state, and rejected_date fields set
            to provided reason, followup_sent, and today.

        test_phone_screen_to_rejected: Rejecting application after completing a
            phone screen should set rejected_reason, rejected_state, and
            rejected_date fields to provided reason, phone_screen_complete, and
            today, respectively.

        test_interview_scheduled_to_rejected: Rejection application after
            scheduling an interview should set rejected reason, rejected_state,
            and rejected_date to provided reason, interview_scheduled, and
            today, respectively. interview_date should remain unchanged

        test_interview_complete_to_rejected: Rejecting application after
            completing interview should set rejected_reason, rejected_state,
            and rejected_date to provided reason, interview_complete, and today,
            respectively.

        test_invalid_transitions: Attempting state transitions that aren't
            explicitly allowed should result in TransitionNotAllowed exception

        test_invalid_dates: Attempting any state transition that would alter the
            updated_date to be before the submitted_date should raise an
            IncompatibleDateException.

    References:
        https://github.com/viewflow/django-fsm

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

    def tearDown(self):
        """
        Empty database between tests
        """
        for user in User.objects.all():
            user.delete()

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
        'phone_screen_complete' and should set the updated_date to today
        """
        # Move fixture object through state pattern and hard set dates
        self.jobapp.send_followup()
        self.assertEqual(self.jobapp.updated_date, self.dates[0])
        self.jobapp.updated_date = self.dates[3]
        self.jobapp.save()

        # Complete phone screen and check application status and updated date
        self.jobapp.phone_screen()
        self.assertEqual(self.jobapp.status, "phone_screen_complete")
        self.assertEqual(self.jobapp.updated_date, self.dates[0])

    def test_phone_screen_to_interview_scheduled(self):
        """
        Scheduling an interview should set the state to 'interview_scheduled'
        and should updated_date to today, and the interview_date to some date
        in the future
        """
        # Move object through state pattern and hard set date to day in the past
        self.jobapp.send_followup()
        self.jobapp.phone_screen()
        self.jobapp.updated_date = self.dates[5]
        self.jobapp.save()

        # Schedule interview for 7 days in the future
        next_week = self.dates[0] + timedelta(days=7)
        self.jobapp.schedule_interview(next_week)

        # Check application status
        self.assertEqual(self.jobapp.status, 'interview_scheduled')
        self.assertEqual(self.jobapp.updated_date, self.dates[0])
        self.assertEqual(self.jobapp.interview_date, next_week)

    def test_attempt_to_schedule_interview_invalid_date(self):
        """
        Attempting to schedule an interview in the past should throw an
        IncompatibleDateException with the message "Interview date cannot be
        in the past".
        """
        # Move object through state pattern
        self.jobapp.send_followup()
        self.jobapp.phone_screen()

        # Attempt to schedule interview for the past
        try:
            self.jobapp.schedule_interview(self.dates[1])
        except IncompatibleDateException as e:
            self.assertEqual(str(e), "Interview date cannot be in the past")

    def test_interview_complete(self):
        """
        Completing interview should set state to 'interview_complete' and set
        updated_date to today
        """
        # Move object through state pattern and hard set updated_date and
        # interview_date to a day in the past
        self.jobapp.send_followup()
        self.jobapp.phone_screen()
        # Schedule interview for today (should be acceptable)
        self.jobapp.schedule_interview(self.dates[0])
        # Reset updated date to be in the past
        self.jobapp.updated_date = self.dates[4]
        self.jobapp.save()

        # Complete interview
        self.jobapp.complete_interview()
        self.assertEqual(self.jobapp.status, "interview_complete")
        self.assertEqual(self.jobapp.updated_date, self.dates[0])

    def test_attempt_to_complete_interview_before_scheduled(self):
        """
        Attempting to complete an interview before its scheduled date should
        raise an IllegalDateExcetion
        """
        # Move object through state pattern and hard set date to day in the past
        self.jobapp.send_followup()
        self.jobapp.phone_screen()
        self.jobapp.updated_date = self.dates[5]
        self.jobapp.save()

        # Schedule interview for 7 days in the future
        next_week = self.dates[0] + timedelta(days=7)
        self.jobapp.schedule_interview(next_week)

        # Attempt to complete interview
        try:
            self.jobapp.complete_interview()
        except IncompatibleDateException as e:
            self.assertEqual(
                str(e),
                "Interview cannot be completed before scheduled date"
            )

    def test_offer_received(self):
        """
        Should set status to 'offer received' and set 'updated_date' to today
        """
        # Move object through state pattern
        self.jobapp.send_followup()
        self.jobapp.phone_screen()
        self.jobapp.updated_date = self.dates[5]
        self.jobapp.save()
        # Schedule interview for today (should be acceptable)
        self.jobapp.schedule_interview(self.dates[0])
        self.jobapp.complete_interview()

        # Call jobapp.offer_received
        self.jobapp.receive_offer()
        # Check updated_date
        self.assertEqual(self.jobapp.updated_date, self.dates[0])
        # Check status
        self.assertEqual(self.jobapp.status, "offer_received")

    def test_submitted_to_rejected(self):
        """
        Calling 'reject' method should set status to 'rejected' and set
        rejected date to today. 'rejected_state' should be set to 'submitted'
        """
        # Reject the application
        self.jobapp.reject("No reason")
        # Check Status and rejected_reason
        self.assertEqual(self.jobapp.status, "rejected")
        self.assertEqual(self.jobapp.rejected_reason, "No reason")
        # Check previous state
        self.assertEqual(self.jobapp.rejected_state, "submitted")
        # Check the model's date fields
        self.assertEqual(self.jobapp.rejected_date, self.dates[0])
        self.assertIsNone(self.jobapp.updated_date)

    def test_followup_sent_to_rejected(self):
        """
        Calling 'reject' method should set status to 'rejected' and set
        rejected date to today. rejected_state should be set to 'followup_sent'
        """
        # Advance application to 'followup_sent' state
        self.jobapp.send_followup()
        # Reject the application
        self.jobapp.reject("Bad Followup")
        # Check status and rejected reason
        self.assertEqual(self.jobapp.status, "rejected")
        self.assertEqual(self.jobapp.rejected_reason, "Bad Followup")
        # Check previous state
        self.assertEqual(self.jobapp.rejected_state, "followup_sent")
        # Check model's date fields
        self.assertEqual(self.jobapp.rejected_date, self.dates[0])
        self.assertEqual(self.jobapp.updated_date, self.dates[0])

    def test_phone_screen_to_rejected(self):
        """
        Calling 'reject' should set status to 'rejected' and set rejected date
        to today. rejected_state should be set to 'phone_screen_complete
        """
        # Advance application to 'phone_screen_complete' status
        self.jobapp.send_followup()
        self.jobapp.phone_screen()
        # Reset updated_date to earlier date
        self.jobapp.updated_date = self.dates[1]
        self.jobapp.save()
        # Reject the application
        self.jobapp.reject("Bad Phone Screen")
        # Check status and rejected reason
        self.assertEqual(self.jobapp.status, "rejected")
        self.assertEqual(self.jobapp.rejected_reason, "Bad Phone Screen")
        # Check previous state
        self.assertEqual(self.jobapp.rejected_state, "phone_screen_complete")
        # Check model's date fields
        self.assertEqual(self.jobapp.rejected_date, self.dates[0])
        self.assertEqual(self.jobapp.updated_date, self.dates[1])

    def test_interview_scheduled_to_rejected(self):
        """
        Calling 'reject' should set status to 'rejected' and set rejected date
        to today. rejected_state should be 'interview_scheduled'
        """
        # Advance application to 'interview_scheduled' status
        self.jobapp.send_followup()
        self.jobapp.phone_screen()
        # Schedule interview for 7 days in the future
        next_week = self.dates[0] + timedelta(days=7)
        self.jobapp.schedule_interview(next_week)
        # Reject the application
        self.jobapp.reject("Unknown")
        # Check status and rejected reason
        self.assertEqual(self.jobapp.status, "rejected")
        self.assertEqual(self.jobapp.rejected_reason, "Unknown")
        # Check previous state
        self.assertEqual(self.jobapp.rejected_state, "interview_scheduled")
        # Check model's date fields
        self.assertEqual(self.jobapp.rejected_date, self.dates[0])
        self.assertEqual(self.jobapp.updated_date, self.dates[0])
        self.assertEqual(self.jobapp.interview_date, next_week)

    def test_interview_complete_to_rejected(self):
        """
        Calling 'reject' should set status to 'rejected' and set rejected date
        to today. rejected_state should be 'interview_scheduled'
        """
        # Advance application to the 'interview_complete' state
        self.jobapp.send_followup()
        self.jobapp.phone_screen()
        self.jobapp.schedule_interview(self.dates[0])
        self.jobapp.complete_interview()

        # Reject application
        self.jobapp.reject("Your Interview Sucked and you're stupid.")
        # Check status and rejected reason
        self.assertEqual(self.jobapp.status, "rejected")
        self.assertEqual(self.jobapp.rejected_reason,
                         "Your Interview Sucked and you're stupid.")
        # Check previous state
        self.assertEqual(self.jobapp.rejected_state, "interview_complete")
        # Check model's date fields
        self.assertEqual(self.jobapp.rejected_date, self.dates[0])
        self.assertEqual(self.jobapp.updated_date, self.dates[0])

    def test_invalid_transitions(self):
        """
        Attempting to make any transitions other than those explicitly allowed
        should fail.
        """
        # TransitionNotAllowed string
        tnl = "Can't switch from state {} using method {}"
        # Submitted to phone_screen
        try:
            self.jobapp.phone_screen()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'submitted'", "'phone_screen'"))
        # Submitted to interview_scheduled
        try:
            self.jobapp.schedule_interview()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'submitted'", "'schedule_interview'"))
        # Submitted to interview_complete
        try:
            self.jobapp.complete_interview()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'submitted'", "'complete_interview'"))
        # Submitted to offer_received
        try:
            self.jobapp.receive_offer()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'submitted'",
                                        "'receive_offer'"))

        # Followup_sent to followup_sent
        self.jobapp.send_followup()
        try:
            self.jobapp.send_followup()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'followup_sent'",
                                        "'send_followup'"))
        # Followup_sent to interview_scheduled
        try:
            self.jobapp.schedule_interview()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'followup_sent'",
                                        "'schedule_interview'"))
        # Followup_sent to interview_complete
        try:
            self.jobapp.complete_interview()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'followup_sent'",
                                        "'complete_interview'"))
        # Followup_sent to offer_received
        try:
            self.jobapp.receive_offer()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'followup_sent'",
                                        "'receive_offer'"))

        # Phone_screen to followup_sent
        self.jobapp.phone_screen()
        try:
            self.jobapp.send_followup()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'phone_screen_complete'",
                                        "'send_followup'"))
        # Phone screen to phone screen
        try:
            self.jobapp.phone_screen()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'phone_screen_complete'",
                                        "'phone_screen'"))
        # Phone screen to interview_complete
        try:
            self.jobapp.complete_interview()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'phone_screen_complete'",
                                        "'complete_interview'"))
        # Phone screen to offer_received
        try:
            self.jobapp.receive_offer()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'phone_screen_complete'",
                                        "'receive_offer'"))

        # Interview scheduled to followup_sent
        self.jobapp.schedule_interview(self.dates[0])
        try:
            self.jobapp.send_followup()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'interview_scheduled'",
                                        "'send_followup'"))
        # Interview scheduled to phone screen
        try:
            self.jobapp.phone_screen()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'interview_scheduled'",
                                        "'phone_screen'"))
        # Interview scheduled to interview_complete
        try:
            self.jobapp.schedule_interview()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'interview_scheduled'",
                                        "'schedule_interview'"))
        # Interview scheduled to offer_received
        try:
            self.jobapp.receive_offer()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'interview_scheduled'",
                                        "'receive_offer'"))

        # Interview complete to followup_sent
        self.jobapp.complete_interview()
        try:
            self.jobapp.send_followup()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'interview_complete'",
                                        "'send_followup'"))
        # Interview complete to phone screen
        try:
            self.jobapp.phone_screen()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'interview_complete'",
                                        "'phone_screen'"))
        # Interview complete to interview_scheduled
        try:
            self.jobapp.schedule_interview(self.dates[0])
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'interview_complete'",
                                        "'schedule_interview'"))
        # Interview complete to interview complete
        try:
            self.jobapp.complete_interview()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'interview_complete'",
                                        "'complete_interview'"))

        # Offer received to followup_sent
        self.jobapp.receive_offer()
        try:
            self.jobapp.send_followup()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'offer_received'",
                                        "'send_followup'"))
        # Offer received to phone screen
        try:
            self.jobapp.phone_screen()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'offer_received'",
                                        "'phone_screen'"))
        # Offer received to interview_scheduled
        try:
            self.jobapp.schedule_interview(self.dates[0])
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'offer_received'",
                                        "'schedule_interview'"))
        # Offer received to interview complete
        try:
            self.jobapp.receive_offer()
        except TransitionNotAllowed as t:
            self.assertEqual(str(t),
                             tnl.format("'offer_received'",
                                        "'receive_offer'"))

    def test_invalid_dates(self):
        """
        Attempting any state transition that would alter the updated_date to be
        before the submitted_date should raise an IncompatibleDateException.
        """
        # Check reject and send_followup
        self.assertEqual(self.jobapp.status, "submitted")
        self.jobapp.submitted_date = date.today() + timedelta(days=7)
        self.assertRaises(IncompatibleDateException, self.jobapp.send_followup)
        self.assertRaises(IncompatibleDateException, self.jobapp.reject, "none")

        # Check phone screen
        self.jobapp.submitted_date = date.today()
        self.jobapp.send_followup()
        self.jobapp.submitted_date = date.today() + timedelta(days=7)
        self.assertRaises(IncompatibleDateException, self.jobapp.phone_screen)

        # Check receive_offer
        self.jobapp.submitted_date = date.today()
        self.jobapp.phone_screen()
        self.jobapp.schedule_interview(date.today())
        self.jobapp.complete_interview()
        self.jobapp.submitted_date = date.today() + timedelta(days=7)
        self.assertRaises(IncompatibleDateException, self.jobapp.receive_offer)
