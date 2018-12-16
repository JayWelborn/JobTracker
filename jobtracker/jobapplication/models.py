from datetime import date
from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models, transaction

from django_fsm import FSMField, transition

from .exceptions import IncompatibleDateException


class Company(models.Model):
    """Model to represent a company with a job opening

    Fields:
        id: randomly generated unique id (used as PK in database)
        Name: name of the company with job opening
        Website: company's website


    References:
    """

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=128
    )

    website = models.URLField()

    creator = models.ForeignKey(
        User,
        related_name="companies",
        on_delete=models.CASCADE,
        editable=False,
    )

    def __str__(self) -> str:
        """
        Create a human-readable string representation of a company
        """
        return "Company: {}\nCreated By: {}".format(self.name,
                                                    self.creator.username)


class JobApplication(models.Model):
    """Model for a Job Application

    Model uses django-fsm package to implement a simple finite state machine to
    represent the progression of a job application from 'submitted' to
    'offer_accepted'.

    The typical progression of a job application is:
        submitted
        followup_sent
        phone_screen_complete
        interview_scheduled
        interview_complete
        offer_recieved
        offer_accepted

        rejected

    Any state can lead to the 'rejected' state, but otherwise the progression is
    linear. The model's methods define the side effects of each transition,
    including how the database should be updated on each state change.

    Fields:
        id:                 randomly generated unique id (PK in database)
        Company:            Company with the job opening
        Position:           Title of job position
        City:               City where job is located
        State/Region:       State where job is located
        status:             Current state of job application
        creator:            User who created this job application
        submitted_date:     Date application was submitted
        updated_date:       Date of last update to application status
        interview_date:     Date of the interview
        rejected_date:      Date rejection was received
        rejected_reason:    Reason application was rejected

    Methods:
        reject:             Transition to represent a rejected application
        send_followup:      Transition to represent sending followup email
        phone_screen:       Transition to represent completing a phone screen


    References:
        https://www.worldatlas.com/articles/the-10-longest-place-names-in-the-world.html
        https://github.com/viewflow/django-fsm
    """

    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False
    )

    company = models.ForeignKey(
        Company,
        related_name="job_applications",
        on_delete=models.CASCADE
    )

    position = models.CharField(
        max_length=128,
    )

    city = models.CharField(
        max_length=85,
    )

    # This is the state in which the job is located, not the `state` of the FSM
    state = models.CharField(
        max_length=85,
    )

    status = FSMField(
        default="submitted"
    )

    creator = models.ForeignKey(
        User,
        related_name="job_applications",
        on_delete=models.CASCADE,
        editable=False,
    )

    submitted_date = models.DateField(
        auto_now_add=True,
    )

    updated_date = models.DateField(
        blank=True,
        null=True
    )

    interview_date = models.DateField(
        blank=True,
        null=True
    )

    rejected_date = models.DateField(
        blank=True,
        null=True
    )

    rejected_reason = models.TextField(
        blank=True,
        null=True
    )

    rejected_state = models.CharField(
        max_length=12,
        blank=True,
        null=True
    )

    @transition(field=status, source="*", target="rejected")
    def reject(self, reason: str) -> None:
        """
        Set application's state to 'Rejected'.
        :param: reason
            Reason application was rejected
        """
        # Raise exception if dates are suspicious
        today = date.today()
        if today < self.submitted_date:
            raise IncompatibleDateException(
                "Rejected date cannot predate submission"
            )
        self.rejected_reason = reason
        self.rejected_date = today
        self.rejected_state = self.status

    @transition(field=status, source="submitted", target="followup_sent")
    def send_followup(self) -> None:
        """
        Set application's state to 'followup_sent' and set the followup_date
        to current date.
        """
        today = date.today()
        # Raise exception if dates are suspicious
        if today < self.submitted_date:
            raise IncompatibleDateException(
                "Followup date cannot predate submission"
            )
        self.updated_date = today

    @transition(field=status, source="followup_sent",
                target="phone_screen_complete")
    def phone_screen(self) -> None:
        """
        Set application's state to 'phone_screen_complete'
        """
        # Raise exception if dates are suspicious
        today = date.today()
        if today < self.submitted_date:
            raise IncompatibleDateException(
                "Phone Screen date cannot predate submission"
            )
        self.updated_date = today


    @transition(field=status, source="phone_screen_complete",
                target="interview_scheduled")
    def schedule_interview(self, interview_date: date) -> None:
        """
        Set application's state to 'interview_scheduled' and update
        interview_date field with provided date.
        """
        today = date.today()
        if today > interview_date:
            raise IncompatibleDateException(
                "Interview date cannot be in the past"
            )
        self.updated_date = today
        self.interview_date = interview_date


    @transition(field=status, source="interview_scheduled",
                target="interview_complete")
    def complete_interview(self) -> None:
        """
        Set application's state to 'interview_complete' and set updated_date to
        current date
        """
        today = date.today()
        if today < self.interview_date:
            raise IncompatibleDateException(
                "Interview cannot be completed before scheduled date"
            )
        self.updated_date = today
        with transaction.atomic():
            self.save()

    @transition(field=status, source="interview_complete",
                target="offer_received")
    def receive_offer(self) -> None:
        """
        Set application's state to 'offer_received' and set updated_date to
        current date.
        """
        today = date.today()
        if today < self.submitted_date:
            raise IncompatibleDateException(
                "Offer cannot predate Application Submission"
            )
        self.updated_date = today
        with transaction.atomic():
            self.save()


class JobReference(models.Model):
    """Person working for a compnay who may serve as a reference

    Fields:
        id: randomly generated unique id (PK)
        Name: name of individual
        Email: individual's email address

    Methods:
        __str__: provide human-readable if object is printed

    References:
    """

    class Meta:
        verbose_name = "Job Reference"
        verbose_name_plural = "Job References"

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=128
    )

    email = models.EmailField(
        blank=True,
    )

    company = models.ForeignKey(
        Company,
        related_name="references",
        on_delete=models.CASCADE,
    )

    creator = models.ForeignKey(
        User,
        related_name="references",
        on_delete=models.CASCADE,
        editable=False,
    )

    def __str__(self) -> str:
        """
        Provide a human-readable string representation of object. String
        contains name of person to use as a reference, along with the name
        of the company they work for.

        :return: String representing Job reference object
        """
        reference = "Reference: {} at {}\n".format(self.name, self.company.name)
        created = "Created By: {}".format(self.creator.username)
        return reference + created
