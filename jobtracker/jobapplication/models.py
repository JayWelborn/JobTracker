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

    def __str__(self):
        """
        Create a human-readable string representation of a company
        """
        return "Company: {}\nCreated By: {}".format(self.name,
                                                    self.creator.username)


class JobApplication(models.Model):
    """Model for a Job Application

    Fields:
        id:                 randomly generated unique id (PK in database)
        Company:            Company with the job opening
        Position:           Title of job position
        City:               City where job is located
        State/Region:       State where job is located
        status:             Current state of job application
        creator:            User who created this job application
        submitted_date:     Date application was submitted
        followup_date:      Date followup email/phonecall was sent/made
        phone_screen_date:  Date of the phone screening
        interview_date:     Date of the interview
        offer_date:         Date job offer was received
        rejected_date:      Date rejection was received
        rejected_reason:    Reason application was rejected

    Methods:
        reject:             Transition to represent a rejected application
        send_followup:      Transition to represent sending followup email
        phone_screen:       Transition to represent completing a phone screen


    References:
        https://www.worldatlas.com/articles/the-10-longest-place-names-in-the-world.html
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
    def reject(self, reason):
        """
        Set application's state to 'Rejected'.
        :param: reason
            Reason application was rejected
        """
        # Raise exception if dates are suspicious
        if date.today() < self.submitted_date:
            raise IncompatibleDateException(
                "Rejected date cannot predate submission"
            )
        self.rejected_reason = reason
        self.rejected_date = date.today()
        self.rejected_state = self.status
        # avoid concurrent db operations
        with transaction.atomic():
            self.save()

    @transition(field=status, source="submitted", target="followup_sent")
    def send_followup(self):
        """
        Set application's state to 'followup_sent' and set the followup_date
        to current date.
        """
        # Raise exception if dates are suspicious
        if date.today() < self.submitted_date:
            raise IncompatibleDateException(
                "Followup date cannot predate submission"
            )
        self.updated_date = date.today()
        # avoid concurrent db operations
        with transaction.atomic():
            self.save()

    @transition(field=status, source="followup_sent",
                target="phone_screen_complete")
    def phone_screen(self):
        """
        Set application's state to 'phone_screen_complete'
        """
        # Raise exception if dates are suspicious
        if date.today() < self.submitted_date:
            raise IncompatibleDateException(
                "Followup date cannot predate submission"
            )
        self.updated_date = date.today()
        # avoid concurrent db operations
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

    def __str__(self):
        """
        Provide a human-readable string representation of object. String
        contains name of person to use as a reference, along with the name
        of the company they work for.

        :return: String representing Job reference object
        """
        return "Reference: {} at {}\nCreated By: {}".format(self.name,
                                                            self.company.name,
                                                            self.creator.username)
