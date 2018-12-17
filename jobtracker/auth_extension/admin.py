from django.contrib import admin


# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    """Admin inteface for UserProfiles.

    Fields:
        user: Creates one to one relationship with Django's built-in User
        created_date: Date profile was created
        slug: slug for pretty url purposes
        id: unique user id *THIS FIELD IS MARKED AS READ ONLY*

    References:
        * https://docs.djangoproject.com/en/1.11/ref/contrib/auth/#django.contrib.auth.models.User

    """

    readonly_fields = ('id',)

    fieldsets = [
        ('User', {'fields': ['user']}),
        ('Profile Information', {
            'fields': ['slug', 'id'],
        }),
        ('Control Info', {'fields': ['created_date', ]})
    ]

    list_display = ['user', 'created_date', ]
    list_filter = ['created_date']
