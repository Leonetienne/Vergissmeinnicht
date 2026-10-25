from django.core.management.base import BaseCommand, CommandError

from accounts.models import User
from accounts.services import check_email_free, clean_email
from boards.services import ServiceError, clean_text

from ._common import valid_password


class Command(BaseCommand):
    help = "Create an account, regardless of ENABLE_REGISTRATION."

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("-p", "--password")
        parser.add_argument("--name")

    def handle(self, email, password, name, **options):
        try:
            email = clean_email(email)
            check_email_free(email)
            name = clean_text(name or email.split("@")[0], "Display name", 100)
        except ServiceError as e:
            raise CommandError(e.message)
        password = valid_password(password, User(email=email, display_name=name))
        User.objects.create_user(email, password, display_name=name)
        self.stdout.write(f"Created {email}")
