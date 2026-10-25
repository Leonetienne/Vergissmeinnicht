from django.core.management.base import BaseCommand, CommandError

from accounts.services import delete_account

from ._common import get_user


class Command(BaseCommand):
    help = "Delete an account with every board it owns."

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("--yes", action="store_true", help="Skip the confirmation")

    def handle(self, email, yes, **options):
        user = get_user(email)
        if not yes and input(f"Delete {user.email} and all boards it owns? [y/N] ").strip().lower() != "y":
            raise CommandError("Aborted")
        delete_account(user)
        self.stdout.write(f"Deleted {email}")
