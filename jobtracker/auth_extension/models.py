from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.urls import reverse


class UserProfile(models.Model):
    """Model to store User Profile Information.

    Fields:
        id:             randomly generated unique id (PK in database)
        user:           Creates 1-to-1 relationship with AUTH_USER_MODEL
        created_date:   Date profile was created
        slug:           Slugified username for creating urls

    References:

        * https://docs.djangoproject.com/en/1.11/ref/contrib/auth/#django.contrib.auth.models.User

    """

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='profile',
        on_delete=models.CASCADE,
    )

    created_date = models.DateTimeField(
        default=timezone.now
    )

    slug = models.SlugField()

    def __str__(self):
        """
        Calling __str__ will return something legible.
        """
        return "Profile for: {}".format(self.user.username)

    def save(self, *args, **kwargs):
        """
        Slugifies username automatically wen UserProfile is saved
        """
        self.slug = slugify(self.user.username)
        super(UserProfile, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Return url for viewing a specific profile
        """
        return reverse('userprofile-detail', args=[self.id])


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    If a User instance is created in the database, automatically create an
    associated profile.
    :param sender:
        Object Class who sends the post_save signal
    :param instance:
        Instance of object that sent signal
    :param created:
        Whether or not the object was newly created
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Update a profile when the associated User object is updated.
    :param sender:
        Object Class who sends the post_save signal
    :param instance:
        Instance of object that sent signal
    """
    instance.profile.save()
