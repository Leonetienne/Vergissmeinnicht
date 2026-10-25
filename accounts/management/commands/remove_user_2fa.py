from django.core.management.base import BaseCommand

from accounts.services import remove_totp

from ._common import get_user


class Command(BaseCommand):
    help = "Remove the second factor of an account."

    def add_arguments(self, parser):
        parser.add_argument("email")

    def handle(self, email, **options):
        user = get_user(email)
        remove_totp(user)
        self.stdout.write(f"Second factor removed for {user.email}")
