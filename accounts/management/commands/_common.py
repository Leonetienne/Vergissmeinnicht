import getpass

from django.core.management.base import CommandError

from accounts.models import User
from accounts.services import check_password
from boards.services import ServiceError


def get_user(email):
    try:
        return User.objects.get_by_email(email)
    except User.DoesNotExist:
        raise CommandError(f"No account with email {email}")


def valid_password(password, user):
    if password is None:
        password = getpass.getpass("Password: ")
    try:
        check_password(password, user)
    except ServiceError as e:
        raise CommandError(e.message)
    return password
