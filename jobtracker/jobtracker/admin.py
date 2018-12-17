from django.contrib.admin import sites
from django.contrib.auth.models import User, Group

from auth_extension.admin import UserProfileAdmin
from auth_extension.models import UserProfile


class JobTrackerAdmin(sites.AdminSite):
    """Admin Site with customized header and title bar.

    References:

        * https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#customizing-the-adminsite-class

    """
    site_header = 'Job Application Tracker Administration'
    site_title = 'Job Application Tracker Administration'


jobtracker_admin_site = JobTrackerAdmin(name='admin')
jobtracker_admin_site.register(User)
jobtracker_admin_site.register(Group)
jobtracker_admin_site.register(UserProfile, UserProfileAdmin)
