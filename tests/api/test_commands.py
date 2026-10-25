from datetime import date, timedelta

import pytest
from django.core import mail
from django.core.management import CommandError, call_command

from accounts.models import RecoveryCode, User
from boards import services as s
from boards.models import Board, Task
from boards.reminders import send_due_reminders


def test_create_user(db):
    call_command("create_user", "New@Example.org", "-p", "Forget-me-not-1")
    user = User.objects.get(email="new@example.org")
    assert user.display_name == "new"
    call_command("create_user", "b@example.org", "-p", "Forget-me-not-1", "--name", "Bee")
    assert User.objects.get(email="b@example.org").display_name == "Bee"


def test_create_user_validates(db, people):
    with pytest.raises(CommandError):
        call_command("create_user", "c@example.org", "-p", "123")
    with pytest.raises(CommandError):
        call_command("create_user", "owner@example.org", "-p", "Forget-me-not-1")


def test_set_password(people):
    call_command("set_user_password", "owner@example.org", "-p", "Brand-new-pass-3")
    assert User.objects.get(email="owner@example.org").check_password("Brand-new-pass-3")


def test_delete_user(people, board):
    call_command("delete_user", "owner@example.org", "--yes")
    assert not Board.objects.exists() and not User.objects.filter(email="owner@example.org").exists()


def test_remove_2fa(people):
    owner = people[0]
    owner.totp_secret = "ABC"
    owner.save()
    RecoveryCode.objects.create(user=owner, code_hash="x")
    call_command("remove_user_2fa", "owner@example.org")
    owner.refresh_from_db()
    assert not owner.has_totp and not RecoveryCode.objects.exists()


@pytest.mark.parametrize("args", [
    ["set_user_password", "ghost@example.org", "-p", "Forget-me-not-1"],
    ["delete_user", "ghost@example.org", "--yes"],
    ["remove_user_2fa", "ghost@example.org"],
])
def test_unknown_account(db, args):
    with pytest.raises(CommandError, match="No account"):
        call_command(*args)


class TestReminders:
    TODAY = date(2026, 3, 10)

    def due(self, days):
        return self.TODAY + timedelta(days=days)

    def test_command_without_email(self, settings, people, board, default_list, capsys):
        settings.EMAIL_CONFIGURED = False
        s.create_task(people[0], default_list.id, "A", due_date=date.today())
        call_command("send_due_reminders")
        assert mail.outbox == [] and "not configured" in capsys.readouterr().out

    def test_digest_recipients_and_stages(self, settings, people, board, default_list):
        owner, editor, observer, _ = people
        soon = s.create_task(owner, default_list.id, "Soon", due_date=self.due(2))
        now = s.create_task(owner, default_list.id, "Now", due_date=self.due(0))
        s.create_task(owner, default_list.id, "Later", due_date=self.due(10))
        done = s.create_task(owner, default_list.id, "Done", due_date=self.due(0))
        s.transition_task(owner, done.id, "done")
        assert send_due_reminders(self.TODAY) == 2
        assert sorted(m.to[0] for m in mail.outbox) == ["editor@example.org", "owner@example.org"]
        body = mail.outbox[0].body
        assert "Soon" in body and "Now" in body and "Later" not in body and "Done" not in body
        assert f"/{board.id}-household/#task-{now.id}" in body
        assert mail.outbox[0].subject == "2 tasks due"
        assert Task.objects.get(pk=now.id).reminded_due and Task.objects.get(pk=now.id).reminded_soon
        assert Task.objects.get(pk=soon.id).reminded_soon and not Task.objects.get(pk=soon.id).reminded_due

    def test_each_stage_once(self, people, board, default_list):
        s.create_task(people[0], default_list.id, "Soon", due_date=self.due(2))
        send_due_reminders(self.TODAY)
        mail.outbox.clear()
        assert send_due_reminders(self.TODAY) == 0
        assert send_due_reminders(self.TODAY + timedelta(days=2)) == 2
        mail.outbox.clear()
        assert send_due_reminders(self.TODAY + timedelta(days=3)) == 0

    def test_opt_out(self, people, board, default_list):
        people[1].reminders_enabled = False
        people[1].save()
        s.create_task(people[0], default_list.id, "Now", due_date=self.due(0))
        send_due_reminders(self.TODAY)
        assert [m.to[0] for m in mail.outbox] == ["owner@example.org"]
