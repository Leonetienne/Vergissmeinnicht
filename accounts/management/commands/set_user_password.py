from django.core.management.base import BaseCommand

from ._common import get_user, valid_password


class Command(BaseCommand):
    help = "Set a new password for an account."

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("-p", "--password")

    def handle(self, email, password, **options):
        user = get_user(email)
        user.set_password(valid_password(password, user))
        user.save()
        self.stdout.write(f"Password set for {user.email}")
