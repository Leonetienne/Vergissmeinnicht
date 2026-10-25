import io
import json

import pyotp
import pytest
from django.test import Client
from PIL import Image

from accounts.models import RecoveryCode, User
from accounts.services import verify_second_factor
from boards import services as s
from boards.models import Board

from .conftest import make_user


@pytest.fixture
def owner(people):
    return people[0]


def login(client, email="owner@example.org", password="Forget-me-not-1", next_url=""):
    return client.post("/login", {"email": email, "password": password, "next": next_url})


class TestLogin:
    def test_redirects_with_next(self, client, people):
        response = client.get("/settings/")
        assert response.status_code == 302 and response["Location"] == "/login?next=/settings/"

    def test_login_case_insensitive_and_next(self, client, people):
        response = login(client, "OWNER@Example.org", next_url="/settings/")
        assert response["Location"] == "/settings/"

    def test_foreign_next(self, client, people):
        assert login(client, next_url="https://evil.example/")["Location"] == "/"

    def test_wrong_password(self, client, people):
        response = login(client, password="nope")
        assert response.status_code == 400 and b"Email or password is wrong" in response.content

    def test_rate_limit(self, client, people):
        for _ in range(5):
            login(client, password="nope")
        response = login(client)
        assert response.status_code == 429 and b"Too many attempts" in response.content

    def test_logout(self, client, people):
        login(client)
        response = client.post("/logout")
        assert response["Location"] == "/login"
        assert client.get("/")["Location"].startswith("/login")

    def test_api_is_not_redirected(self, client, people):
        assert client.get("/api/v1/boards/").status_code == 401


class TestRegistration:
    def test_disabled_is_404(self, client, settings, db):
        settings.ENABLE_REGISTRATION = False
        assert client.get("/register").status_code == 404
        assert b"Create account" not in client.get("/login").content

    def test_register(self, client, settings, db):
        settings.ENABLE_REGISTRATION = True
        response = client.post("/register", {"display_name": "Ann", "email": "Ann@Example.org", "password": "Forget-me-not-1"})
        assert response["Location"] == "/"
        assert User.objects.get(email="ann@example.org").display_name == "Ann"

    @pytest.mark.parametrize("data,message", [
        ({"display_name": "", "email": "a@example.org", "password": "Forget-me-not-1"}, b"Display name is required"),
        ({"display_name": "A", "email": "OWNER@example.org", "password": "Forget-me-not-1"}, b"already in use"),
        ({"display_name": "A", "email": "nope", "password": "Forget-me-not-1"}, b"Email is not valid"),
        ({"display_name": "A", "email": "b@example.org", "password": "123"}, b"too short"),
    ])
    def test_rejected(self, client, settings, people, data, message):
        settings.ENABLE_REGISTRATION = True
        response = client.post("/register", data)
        assert response.status_code == 400 and message in response.content


class TestTwoFactor:
    def activate(self, client, user):
        client.force_login(user)
        client.post("/settings/", {"action": "totp_start"})
        secret = client.session["pending_totp_secret"]
        page = client.get("/settings/")
        assert b"<svg" in page.content and secret.encode() in page.content
        response = client.post("/settings/", {"action": "totp_activate", "code": pyotp.TOTP(secret).now()})
        return secret, response.context["recovery_codes"]

    def test_setup_requires_valid_code(self, client, owner):
        client.force_login(owner)
        client.post("/settings/", {"action": "totp_start"})
        response = client.post("/settings/", {"action": "totp_activate", "code": "000000"})
        assert b"Code is wrong" in response.content
        owner.refresh_from_db()
        assert not owner.has_totp

    def test_activation_stores_hashed_codes(self, client, owner):
        secret, codes = self.activate(client, owner)
        assert len(codes) == 10 and RecoveryCode.objects.filter(user=owner).count() == 10
        assert not RecoveryCode.objects.filter(code_hash__in=codes).exists()

    def test_login_challenge(self, client, owner):
        secret, _ = self.activate(Client(), owner)
        response = login(client)
        assert response["Location"] == "/login/2fa"
        assert client.get("/").status_code == 302
        owner.refresh_from_db()
        code = pyotp.TOTP(secret).at(owner.totp_last_step * 30 + 30)
        response = client.post("/login/2fa", {"code": code})
        assert response["Location"] == "/"

    def test_recovery_code_removes_factor(self, client, owner):
        _, codes = self.activate(Client(), owner)
        login(client)
        response = client.post("/login/2fa", {"code": codes[0]}, follow=True)
        assert b"Second factor removed" in response.content
        owner.refresh_from_db()
        assert not owner.has_totp and not RecoveryCode.objects.exists()

    def test_wrong_code(self, client, owner):
        self.activate(Client(), owner)
        login(client)
        assert client.post("/login/2fa", {"code": "123456"}).status_code == 400

    def test_reused_code_rejected(self, client, owner):
        secret, _ = self.activate(Client(), owner)
        owner.refresh_from_db()
        used = pyotp.TOTP(secret).at(owner.totp_last_step * 30)
        assert verify_second_factor(owner, used) is None

    def test_remove_in_settings(self, client, owner):
        _, codes = self.activate(client, owner)
        client.post("/settings/", {"action": "totp_remove", "code": codes[1]})
        owner.refresh_from_db()
        assert not owner.has_totp


class TestSettings:
    def test_sections(self, client, owner, settings):
        settings.EMAIL_CONFIGURED = True
        client.force_login(owner)
        content = client.get("/settings/").content.decode()
        for section in ["Profile", "Password", "Notifications", "Second factor", "API key", "MCP key", "Appearance", "Delete account"]:
            assert f">{section}</h2>" in content
        settings.EMAIL_CONFIGURED = False
        assert ">Notifications</h2>" not in client.get("/settings/").content.decode()

    def test_profile(self, client, owner):
        client.force_login(owner)
        client.post("/settings/", {"action": "profile", "display_name": "Leo", "email": "leo@example.org"})
        owner.refresh_from_db()
        assert (owner.display_name, owner.email) == ("Leo", "leo@example.org")

    def test_password_keeps_session(self, client, owner):
        client.force_login(owner)
        response = client.post("/settings/", {"action": "password", "current_password": "Forget-me-not-1", "new_password": "Another-pass-2"})
        assert response.status_code == 302 and client.get("/settings/").status_code == 200
        owner.refresh_from_db()
        assert owner.check_password("Another-pass-2")

    def test_password_wrong_current(self, client, owner):
        client.force_login(owner)
        response = client.post("/settings/", {"action": "password", "current_password": "x", "new_password": "Another-pass-2"})
        assert b"Current password is wrong" in response.content

    def test_notifications(self, client, owner):
        client.force_login(owner)
        client.post("/settings/", {"action": "notifications"})
        owner.refresh_from_db()
        assert owner.reminders_enabled is False

    def test_key_shown_once(self, client, owner):
        client.force_login(owner)
        response = client.post("/settings/", {"action": "api_generate"})
        key = response.context["new_key"]["value"]
        assert key.startswith("vmk_") and key.encode() in response.content
        page = client.get("/settings/").content
        assert key.encode() not in page and b"Never used" in page
        client.post("/settings/", {"action": "api_revoke"})
        assert b"No key." in client.get("/settings/").content

    def test_appearance_sanitised(self, client, owner):
        client.force_login(owner)
        client.post("/settings/", {"action": "appearance", "backdrop_mode": "fit", "backdrop_opacity": "150",
                                   "backdrop_css": "filter: blur(2px);}</style>", "backdrop_css_mobile": "", "ui_opacity": "10"})
        owner.refresh_from_db()
        assert (owner.backdrop_mode, owner.backdrop_opacity, owner.ui_opacity) == ("fit", 100, 30)
        assert owner.backdrop_css == "filter: blur(2px);/style"
        assert b"--ui-alpha: 30%" in client.get("/").content

    def test_backdrop_upload_private_and_removed(self, client, owner, people):
        client.force_login(owner)
        image = io.BytesIO()
        Image.new("RGB", (4, 4), "blue").save(image, "PNG")
        image.name = "b.png"
        image.seek(0)
        client.post("/settings/", {"action": "appearance", "backdrop": image, "ui_opacity": "100"})
        owner.refresh_from_db()
        assert owner.backdrop.endswith(".png")
        assert client.get("/settings/backdrop").status_code == 200
        other = Client()
        other.force_login(people[1])
        assert other.get("/settings/backdrop").status_code == 404
        client.post("/settings/", {"action": "backdrop_remove"})
        owner.refresh_from_db()
        assert owner.backdrop == "" and client.get("/settings/backdrop").status_code == 404

    def test_backdrop_rejects_non_image(self, client, owner):
        client.force_login(owner)
        fake = io.BytesIO(b"<html>")
        fake.name = "x.png"
        response = client.post("/settings/", {"action": "appearance", "backdrop": fake})
        assert b"not a valid image" in response.content

    def test_delete_account(self, client, owner, board, people):
        own = s.create_board(people[1], "Mara board")
        s.add_share(people[1], own.id, owner.id)
        client.force_login(owner)
        response = client.post("/settings/", {"action": "delete_account"})
        assert response["Location"] == "/login"
        assert not User.objects.filter(pk=owner.pk).exists()
        assert list(Board.objects.values_list("name", flat=True)) == ["Mara board"]
        assert not own.shares.exists()


class TestBoardPages:
    def test_home_sections(self, client, people, board):
        client.force_login(people[1])
        data = client.get("/").context["page_data"]
        assert data["shared"][0]["name"] == "Household"

    def test_board_slug_redirect(self, client, people, board):
        client.force_login(people[0])
        assert client.get(f"/{board.id}-wrong/")["Location"] == f"/{board.id}-household/"
        assert client.get(f"/{board.id}-wrong/archive/")["Location"] == f"/{board.id}-household/archive/"

    def test_board_hidden_from_strangers(self, client, people, board, default_list):
        client.force_login(people[3])
        task = s.create_task(people[0], default_list.id, "A")
        for url in [board.get_absolute_url(), board.get_absolute_url() + "archive/", f"/export/board/{board.id}.json",
                    f"/export/list/{default_list.id}.json", f"/export/task/{task.id}.json"]:
            assert client.get(url).status_code == 404, url

    def test_board_page_hides_archived(self, client, people, board, default_list):
        owner = people[0]
        task = s.create_task(owner, default_list.id, "Gone")
        s.transition_task(owner, task.id, "done")
        s.transition_task(owner, task.id, "archived")
        client.force_login(owner)
        data = client.get(board.get_absolute_url()).context["page_data"]
        assert data["lists"][0]["tasks"] == []
        archive = client.get(board.get_absolute_url() + "archive/").context["page_data"]
        assert archive["lists"][0]["tasks"][0]["title"] == "Gone"

    def test_embedded_json_is_escaped(self, client, people, board, default_list):
        owner = people[0]
        s.create_task(owner, default_list.id, "</script><script>alert(1)</script>&")
        client.force_login(owner)
        content = client.get(board.get_absolute_url()).content.decode()
        assert "</script><script>alert(1)" not in content
        assert "\\u003C/script\\u003E" in content and "\\u0026" in content

    def test_exports(self, client, people, board, default_list):
        owner = people[0]
        lst = s.create_list(owner, board.id, "Groceries")
        task = s.create_task(owner, lst.id, "Oat milk")
        client.force_login(people[2])
        response = client.get(f"/export/board/{board.id}.json")
        assert response["Content-Disposition"] == 'attachment; filename="household.json"'
        api = Client()
        api.force_login(owner)
        assert json.loads(response.content) == api.get(f"/api/v1/boards/{board.id}/").json() | {"role": "observer"}
        assert client.get(f"/export/list/{lst.id}.json")["Content-Disposition"].endswith('"groceries.json"')
        assert json.loads(client.get(f"/export/task/{task.id}.json").content)["title"] == "Oat milk"
        assert 'filename="oat-milk.json"' in client.get(f"/export/task/{task.id}.json")["Content-Disposition"]

    def test_footer(self, client, settings, db):
        settings.APP_VERSION = "1.4.0"
        content = client.get("/login").content.decode()
        assert "1.4.0" in content and "Open Source on Github" in content


def settings_with(env):
    import subprocess
    import sys

    env = {"PATH": "/usr/bin:/bin", "DJANGO_SETTINGS_MODULE": "vergissmeinnicht.settings", **env}
    script = (
        "import django; django.setup(); from django.conf import settings as s; "
        "print(s.SESSION_COOKIE_SECURE, s.CSRF_COOKIE_SECURE, getattr(s, 'SECURE_SSL_REDIRECT', False), "
        "getattr(s, 'SECURE_HSTS_SECONDS', 0), getattr(s, 'SECURE_PROXY_SSL_HEADER', None))"
    )
    return subprocess.run([sys.executable, "-c", script], env=env, capture_output=True, text=True)


def test_transport_settings():
    production = settings_with({"DJANGO_SECRET_KEY": "x", "ALLOWED_HOSTS": "x"})
    assert production.stdout.split() == ["True", "True", "False", "0", "None"]
    assert settings_with({"DEBUG": "TRUE"}).stdout.split()[:2] == ["False", "False"]


def test_misconfiguration_refuses_start():
    for env, name in [({"ALLOWED_HOSTS": "x"}, "DJANGO_SECRET_KEY"), ({"DJANGO_SECRET_KEY": "x"}, "ALLOWED_HOSTS")]:
        result = settings_with(env)
        assert result.returncode != 0 and f"{name} is required" in result.stderr


def test_make_user_helper(db):
    assert make_user("z@example.org").display_name == "z"
