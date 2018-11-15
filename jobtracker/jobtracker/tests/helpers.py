from django.contrib.auth.models import User


def create_user(username: str, password: str):
    """Create a new User object.

    Args:
        username: Username to assign to new User instance
        password: Password to assign to new User instance

    Returns:
        user: New instance of django's User object with provided username and
              password.
    """

    # create User
    user = User.objects.get_or_create(
        username=username,
        email='{}@gmail.com'.format(username)
    )[0]
    user.set_password(password)

    user.save()

    return user
