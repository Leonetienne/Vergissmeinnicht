from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from boards.reminders import send_due_reminders


class Command(BaseCommand):
    help = "Send due date reminder emails. Run once a day by cron."

    def handle(self, **options):
        if not settings.EMAIL_CONFIGURED:
            self.stdout.write("Email is not configured, no reminders sent")
            return
        sent = send_due_reminders(timezone.localdate())
        self.stdout.write(f"Sent {sent} reminder email(s)")
