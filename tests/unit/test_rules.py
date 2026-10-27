from datetime import date

import pytest

from accounts.services import clamp_int, sanitise_css, totp_step
from api.registry import OpError, _coerce_args
from boards import services as s
from boards.models import Board, List, Task, slug_for
from boards.reminders import DUE, SOON, reminder_stage
from boards.serializers import board_data, list_data, task_data

TODAY = date(2026, 3, 10)


class TestTransitions:
    @pytest.mark.parametrize("start,end", [("open", "done"), ("done", "open"), ("done", "archived"), ("archived", "done")])
    def test_allowed(self, monkeypatch, start, end):
        task = Task(state=start)
        monkeypatch.setattr(task, "save", lambda **kw: None)
        assert s.transition(task, end).state == end

    @pytest.mark.parametrize("start,end", [("open", "archived"), ("archived", "open"), ("open", "open"), ("done", "done")])
    def test_rejected_with_409(self, start, end):
        with pytest.raises(s.Conflict) as e:
            s.transition(Task(state=start), end)
        assert e.value.status == 409


class TestDueStatus:
    @pytest.mark.parametrize("days,expected", [(-5, "now"), (0, "now"), (1, "soon"), (3, "soon"), (4, None)])
    def test_open(self, days, expected):
        assert s.due_status(date.fromordinal(TODAY.toordinal() + days), "open", TODAY) == expected

    def test_done_and_undated_have_no_warning(self):
        assert s.due_status(TODAY, "done", TODAY) is None
        assert s.due_status(None, "open", TODAY) is None


class TestReminderStage:
    def task(self, days, soon=False, due=False, state="open"):
        return Task(state=state, due_date=date.fromordinal(TODAY.toordinal() + days), reminded_soon=soon, reminded_due=due)

    def test_soon(self):
        assert reminder_stage(self.task(2), TODAY) == SOON

    def test_soon_once(self):
        assert reminder_stage(self.task(2, soon=True), TODAY) is None

    def test_due_wins_when_both_pending(self):
        assert reminder_stage(self.task(0), TODAY) == DUE

    def test_due_after_soon(self):
        assert reminder_stage(self.task(-1, soon=True), TODAY) == DUE

    def test_due_once(self):
        assert reminder_stage(self.task(-1, soon=True, due=True), TODAY) is None

    def test_not_for_done(self):
        assert reminder_stage(self.task(0, state="done"), TODAY) is None

    def test_far_future(self):
        assert reminder_stage(self.task(10), TODAY) is None


class TestSlugs:
    def test_board_slug(self):
        from accounts.models import User

        assert Board(slug="haus-garten", owner=User(username="leon")).get_absolute_url() == "/leon/haus-garten/"

    def test_unique_slug(self):
        from accounts.models import unique_slug

        assert unique_slug("Haus & Garten!", set(), "board") == "haus-garten"
        assert unique_slug("My tasks", {"my-tasks", "my-tasks-1"}, "board") == "my-tasks-2"

    def test_fallback(self):
        assert slug_for("🌼", "board") == "board"


class TestCss:
    def test_strips_forbidden(self):
        assert sanitise_css("color: red;} </style><b>{@import `x` \\ &") == "color: red; /stylebimport x"

    def test_limit(self):
        assert len(sanitise_css("a" * 3000)) == 2000

    def test_clamp(self):
        assert clamp_int("5", 30, 100, 100) == 30
        assert clamp_int("x", 30, 100, 100) == 100


class TestValidation:
    def test_name_required(self):
        with pytest.raises(s.Invalid):
            s.clean_text("   ", "Board title", 100)

    def test_name_too_long(self):
        with pytest.raises(s.Invalid):
            s.clean_text("x" * 101, "Board title", 100)

    def test_emoji(self):
        assert s.clean_emoji("🌼") == "🌼"
        with pytest.raises(s.Invalid):
            s.clean_emoji("<b>")

    def test_colour(self):
        with pytest.raises(s.Invalid):
            s.clean_colour("pink")


class TestCoercion:
    props = {"id": {"type": "integer", "minimum": 1}, "due": {"type": ["string", "null"], "format": "date"},
             "flag": {"type": "boolean"}, "ids": {"type": "array", "items": {"type": "integer", "minimum": 1}}}

    def test_strings_from_query(self):
        assert _coerce_args(self.props, (), {"id": "3", "flag": "true"}) == {"id": 3, "flag": True}

    def test_date(self):
        assert _coerce_args(self.props, (), {"due": "2026-03-10"})["due"] == TODAY
        assert _coerce_args(self.props, (), {"due": None})["due"] is None

    @pytest.mark.parametrize("raw", [{"id": 0}, {"id": "x"}, {"id": True}, {"due": "10.03.2026"},
                                     {"ids": "1"}, {"ids": [0]}, {"other": 1}, {"id": 2**40}])
    def test_rejected(self, raw):
        with pytest.raises(OpError) as e:
            _coerce_args(self.props, (), raw)
        assert e.value.status == 400

    def test_required(self):
        with pytest.raises(OpError):
            _coerce_args(self.props, ("id",), {})


class TestSerializers:
    def test_task(self):
        task = Task(id=5, list_id=2, title="Seeds", state="done", position=1, due_date=TODAY, colour="blue", note="n")
        assert task_data(task) == {"id": 5, "list_id": 2, "title": "Seeds", "state": "done", "position": 1,
                                   "due_date": "2026-03-10", "colour": "blue", "note": "n"}

    def test_list_with_tasks(self):
        lst = List(id=2, board_id=1, title="", is_default=True, position=0)
        assert list_data(lst, [])["tasks"] == []
        assert "tasks" not in list_data(lst)

    def test_board(self):
        from accounts.models import User

        board = Board(id=1, title="Home", slug="home", emoji="🏡", owner=User(id=3, display_name="Leon", username="leon"))
        board.role = "owner"
        data = board_data(board, [])
        assert data["owner"] == {"id": 3, "display_name": "Leon"}
        assert data["url"] == "/leon/home/" and data["lists"] == [] and data["role"] == "owner"
        assert data["description"] == ""


class TestTotp:
    def test_window_and_reuse(self):
        import pyotp

        secret = pyotp.random_base32()
        now = 1_800_000_000
        step = now // 30
        code = pyotp.TOTP(secret).at(now)
        assert totp_step(secret, code, None, now) == step
        assert totp_step(secret, code, step, now) is None
        assert totp_step(secret, pyotp.TOTP(secret).at(now - 30), None, now) == step - 1
        assert totp_step(secret, pyotp.TOTP(secret).at(now - 60), None, now) is None
        assert totp_step(secret, "abc", None, now) is None
