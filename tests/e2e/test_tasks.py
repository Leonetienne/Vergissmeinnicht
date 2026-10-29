import datetime
import json
import time

from selenium.webdriver.common.keys import Keys

from .conftest import BASE, PAUSE, mailpit_messages, manage

LINGER = 1.0


def set_date(ui, value):
    field = ui.css(".vm-pop input[type=date]")
    ui.d.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'))", field, value)
    time.sleep(PAUSE)


def test_quick_entry_check_uncheck_order(ui, owner):
    ui.create_board("Tasks")
    for title in ["One", "Two", "Three"]:
        ui.add_task(title)
    entry = ui.d.switch_to.active_element
    assert entry.get_attribute("aria-label") == "New task"
    assert entry.get_attribute("enterkeyhint") == "enter"
    assert ui.titles() == ["One", "Two", "Three"]
    ui.click(ui.css(".vm-check", ui.card("One")))
    assert "vm-card--done" in ui.card("One").get_attribute("class")
    assert ui.titles() == ["One", "Two", "Three"]
    time.sleep(LINGER)
    assert ui.titles() == ["Two", "Three", "One"]
    ui.click(ui.css(".vm-check", ui.card("One")))
    assert "vm-card--done" not in ui.card("One").get_attribute("class")
    assert ui.titles() == ["Two", "Three", "One"]
    time.sleep(LINGER)
    assert ui.titles() == ["One", "Two", "Three"]
    ui.d.refresh()
    time.sleep(PAUSE)
    assert ui.titles() == ["One", "Two", "Three"]


def test_tick_taken_back_in_time_keeps_place(ui, owner):
    ui.create_board("Linger")
    for title in ["One", "Two"]:
        ui.add_task(title)
    check = ui.css(".vm-check", ui.card("One"))
    check.click()
    time.sleep(0.2)
    check.click()
    time.sleep(LINGER)
    assert ui.titles() == ["One", "Two"]
    assert "vm-card--done" not in ui.card("One").get_attribute("class")
    ui.d.refresh()
    time.sleep(PAUSE)
    assert ui.titles() == ["One", "Two"]
    assert "vm-card--done" not in ui.card("One").get_attribute("class")


def test_tap_opens_details_and_delete_with_confirm(ui, owner):
    ui.create_board("Edit")
    ui.add_task("Typo")
    ui.open_card("Typo")
    field = ui.css(".vm-pop input:not([type=date])")
    ui.d.execute_script("arguments[0].select()", field)
    field.send_keys("Fixed")
    ui.keys(Keys.ESCAPE)
    ui.click(ui.css("button[aria-label='Delete task']", ui.card("Fixed")))
    ui.confirm(ok=False)
    assert ui.titles() == ["Fixed"]
    ui.click(ui.css("button[aria-label='Delete task']", ui.card("Fixed")))
    ui.confirm()
    assert ui.titles() == []
    ui.d.refresh()
    time.sleep(PAUSE)
    assert ui.titles() == []


def test_enter_in_singleview_title_saves_and_closes(ui, owner):
    ui.create_board("Enter")
    ui.add_task("Draft")
    ui.open_card("Draft")
    field = ui.css(".vm-pop input:not([type=date])")
    ui.d.execute_script("arguments[0].select()", field)
    field.send_keys("Final")
    field.send_keys(Keys.ENTER)
    time.sleep(PAUSE)
    assert not ui.all(".vm-pop[aria-label=Task]")
    assert ui.titles() == ["Final"]
    ui.d.refresh()
    time.sleep(PAUSE)
    assert ui.titles() == ["Final"]


def test_singleview_colour_due_note_and_export(ui, owner):
    ui.create_board("Details")
    ui.add_task("Renew passport")
    ui.open_card("Renew passport")
    ui.click(ui.css(".vm-pop button[aria-label=Blue]"))
    set_date(ui, (datetime.date.today() + datetime.timedelta(days=2)).isoformat())
    note = ui.css(".vm-pop textarea")
    note.send_keys("Line one\nline two\nline three\nline four\nline five")
    time.sleep(1.2)
    export = ui.css(".vm-pop a").get_attribute("href")
    ui.keys(Keys.ESCAPE)
    assert not ui.css(".vm-pop[aria-label=Task]").is_displayed() if ui.all(".vm-pop[aria-label=Task]") else True
    card = ui.card("Renew passport")
    assert card.get_attribute("data-colour") == "blue"
    assert "vm-due--soon" in ui.css(".vm-due", card).get_attribute("class")
    note_el = ui.css(".vm-card__note", card)
    assert note_el.size["height"] <= 18 * 3 + 2
    ui.d.refresh()
    time.sleep(PAUSE)
    assert ui.card("Renew passport").get_attribute("data-colour") == "blue"
    data = ui.session().get(export).json()
    assert data["colour"] == "blue" and data["note"].startswith("Line one")

    ui.open_card("Renew passport")
    set_date(ui, datetime.date.today().isoformat())
    ui.click(ui.css(".vm-pop button[aria-label=Close]"))
    assert "vm-due--now" in ui.css(".vm-due", ui.card("Renew passport")).get_attribute("class")


def test_dropped_task_flashes(ui, owner):
    ui.create_board("Flash")
    ui.add_task("First")
    ui.add_task("Second")
    ui.d.execute_script("""
        window.flashed = [];
        new MutationObserver((records) => records.forEach((r) => {
          if (r.target.classList.contains('vm-flash')) window.flashed.push(r.target.getAttribute('aria-label'));
        })).observe(document.body, { subtree: true, attributeFilter: ['class'] });
    """)
    ui.drag(ui.card("Second"), ui.card("First"), dy=2)
    assert ui.titles() == ["Second", "First"]
    assert ui.d.execute_script("return [...new Set(window.flashed)]") == ["Second"]
    assert "vm-flash" not in ui.card("Second").get_attribute("class")


def test_lists_create_rename_drag_delete(ui, owner):
    ui.create_board("Kanban")
    ui.add_task("Loose")
    ui.add_task("Bread")
    create = ui.button("+ Create list")
    ui.click(create)
    assert ui.d.switch_to.active_element.get_attribute("enterkeyhint") == "enter"
    ui.type(ui.d.switch_to.active_element, "Groceries" + Keys.ENTER)
    assert ui.button("+ Create another list").is_displayed()
    ui.click(ui.button("+ Create another list"))
    assert ui.d.switch_to.active_element.get_attribute("aria-label") == "List title"
    ui.type(ui.d.switch_to.active_element, Keys.ESCAPE)
    assert len(ui.all(".vm-list")) == 2
    assert not ui.all(".vm-list--default .vm-list__header")

    ui.drag(ui.card("Bread"), ui.css(".vm-list__cards", ui.list_section("Groceries")))
    assert ui.titles("Groceries") == ["Bread"]
    assert not ui.all("[role=dialog][aria-label=Task]")
    ui.d.refresh()
    time.sleep(PAUSE)
    assert ui.titles("Groceries") == ["Bread"] and ui.titles() == ["Loose"]
    entry = ui.css("input[aria-label='New task']", ui.list_section("Groceries"))
    assert entry.location["y"] < ui.card("Bread").location["y"]

    ui.click(ui.css(".vm-list__header .vm-inline"))
    field = ui.d.switch_to.active_element
    ui.select_all(field)
    ui.type(field, "Shop" + Keys.ENTER)
    ui.click(ui.css("button[aria-label='Delete list']", ui.list_section("Shop")))
    assert "Its tasks move to the default list" in ui.text("[role=alertdialog]")
    ui.confirm()
    assert ui.titles() == ["Loose", "Bread"] and len(ui.all(".vm-list")) == 1

    ui.click(ui.css(".vm-footer span"))
    ui.chord("z")
    assert ui.titles("Shop") == ["Bread"]
    ui.chord("z", shift=True)
    assert len(ui.all(".vm-list")) == 1


def test_undo_redo_delete_and_text_input(ui, owner):
    ui.create_board("Undo")
    ui.add_task("Keep me")
    ui.click(ui.css("button[aria-label='Delete task']", ui.card("Keep me")))
    ui.confirm()
    ui.chord("z")
    assert ui.titles() == ["Keep me"] and "Undo: delete task" in ui.toast()
    ui.chord("y")
    assert ui.titles() == []
    ui.chord("z")
    ui.click(ui.css(".vm-check", ui.card("Keep me")))
    ui.chord("z")
    assert "vm-card--done" not in ui.card("Keep me").get_attribute("class")

    entry = ui.css("input[aria-label='New task']")
    entry.send_keys("abc")
    ui.chord("z")
    assert ui.titles() == ["Keep me"]


def test_archive_flow(ui, owner):
    ui.create_board("Archive me")
    for t in ["Done one", "Done two", "Open one"]:
        ui.add_task(t)
    ui.click(ui.css(".vm-check", ui.card("Done one")))
    ui.click(ui.css(".vm-check", ui.card("Done two")))
    ui.click(ui.button("Archive what's done"))
    ui.confirm(ok=False)
    assert sorted(ui.titles()) == ["Done one", "Done two", "Open one"]
    ui.click(ui.button("Archive what's done"))
    ui.confirm()
    assert ui.titles() == ["Open one"]
    ui.click(ui.xpath("//a[normalize-space()='Open archive']"))
    assert ui.d.current_url.endswith("/archive/")
    assert sorted(c.text.split("\n")[0] for c in ui.all(".vm-card")) == ["Done one", "Done two"]
    ui.click(ui.css(".vm-check", ui.card("Done one")))
    ui.click(ui.button("Unarchive selected"))
    ui.confirm(ok=False)
    assert sorted(c.text.split("\n")[0] for c in ui.all(".vm-card")) == ["Done one", "Done two"]
    ui.click(ui.button("Unarchive selected"))
    ui.confirm()
    assert [c.text.split("\n")[0] for c in ui.all(".vm-card")] == ["Done two"]
    ui.click(ui.xpath("//a[normalize-space()='Leave archive']"))
    assert sorted(ui.titles()) == ["Done one", "Open one"]


def test_search_popup(ui, owner):
    ui.create_board("Paperwork")
    ui.add_task("Renew passport")
    ui.add_task("Passport photos")
    ui.click(ui.css(".vm-check", ui.card("Passport photos")))
    ui.go("/")
    ui.chord("f")
    field = ui.d.switch_to.active_element
    assert field.get_attribute("aria-label") == "Search"
    ui.type(field, "pass")
    rows = ui.all(".vm-result")
    assert any("Renew passport" in r.text and r.text.endswith("Paperwork") for r in rows) and any("done" in r.text for r in rows)
    ui.keys(Keys.ESCAPE)
    assert not ui.css("[role=dialog][aria-label=Search]").is_displayed()
    ui.click(ui.css("input[aria-label='New board']"))
    ui.chord("f")
    field = ui.d.switch_to.active_element
    assert field.get_attribute("aria-label") == "Search"
    assert ui.d.execute_script("return arguments[0].selectionEnd - arguments[0].selectionStart", field) == 4
    ui.keys(Keys.ESCAPE)
    ui.click(ui.css("button[aria-label=Search]"))
    ui.type(ui.d.switch_to.active_element, "renew")
    ui.keys(Keys.ENTER)
    assert "#task-" in ui.d.current_url
    assert "vm-card--highlight" in ui.card("Renew passport").get_attribute("class")


def test_anchor_change_on_open_board_highlights_task(ui, owner):
    ui.create_board("Anchors")
    for title in ["First", "Second"]:
        ui.add_task(title)
    second = ui.card("Second")
    assert "vm-card--highlight" not in second.get_attribute("class")
    ui.d.execute_script("location.hash = arguments[0]", second.get_attribute("id"))
    time.sleep(PAUSE)
    assert "vm-card--highlight" in second.get_attribute("class")
    assert "vm-card--highlight" not in ui.card("First").get_attribute("class")
    time.sleep(3)
    assert "vm-card--highlight" not in second.get_attribute("class")


def test_anchored_task_lands_below_header(ui, owner):
    ui.create_board("Long board")
    for i in range(40):
        ui.add_task(f"Task {i}")
    card = ui.card("Task 10")
    ui.d.execute_script("arguments[0].scrollIntoView({ block: 'start' })", card)
    time.sleep(PAUSE)
    assert ui.d.execute_script("return window.scrollY") > 0
    top = ui.d.execute_script("return arguments[0].getBoundingClientRect().top", card)
    assert top >= ui.css(".vm-header").rect["height"]


def test_leftmost_card_ring_fits_inside_board(ui, owner):
    ui.create_board("Edges")
    ui.add_task("Edge task")
    board = ui.css(".vm-board").rect
    card = ui.card("Edge task").rect
    title = ui.css(".vm-page-title").rect
    assert card["x"] - board["x"] >= 4
    assert card["x"] == title["x"]


def test_exports_hidden_without_tasks(ui, owner):
    ui.create_board("Empty export board")
    shown = lambda: [a for a in ui.all("a") if a.text == "Json export"]
    assert shown() == []
    ui.add_task("First")
    time.sleep(PAUSE)
    assert len(shown()) == 2


def test_exports(ui, owner):
    ui.create_board("Export board")
    ui.add_task("Exported")
    links = [a.get_attribute("href") for a in ui.all("a") if a.text == "Json export"]
    assert len(links) == 2
    http = ui.session()
    board = http.get(links[-1])
    assert board.headers["Content-Disposition"] == 'attachment; filename="export-board.json"'
    assert board.json()["lists"][0]["tasks"][0]["title"] == "Exported"
    listing = http.get(links[0])
    assert listing.json()["tasks"][0]["title"] == "Exported"
    assert listing.headers["Content-Disposition"] == 'attachment; filename="export-board-list.json"'
    board_link = ui.css(".vm-page-export a")
    assert board_link.location["x"] < 60


def test_reminder_email(ui, owner):
    ui.create_board("Due board")
    ui.add_task("Pay the bill")
    ui.open_card("Pay the bill")
    set_date(ui, datetime.date.today().isoformat())
    ui.keys(Keys.ESCAPE)
    manage("send_due_reminders")
    messages = mailpit_messages(owner)
    assert messages and messages[0]["Subject"].endswith("due")
    detail = json.loads(__import__("requests").get(f"http://localhost:8030/api/v1/message/{messages[0]['ID']}").text)
    assert "Pay the bill" in detail["Text"] and "#task-" in detail["Text"] and BASE in detail["Text"]


def test_done_tasks_drag_and_default_list_hides(ui, owner):
    ui.create_board("Flow")
    ui.add_task("Wash")
    ui.add_task("Dry")
    ui.click(ui.css(".vm-check", ui.card("Wash")))
    ui.click(ui.css(".vm-check", ui.card("Dry")))
    time.sleep(LINGER)
    ui.drag(ui.card("Dry"), ui.card("Wash"), dy=2)
    assert ui.titles() == ["Dry", "Wash"]
    assert all("vm-card--done" in c.get_attribute("class") for c in ui.all(".vm-card"))

    ui.click(ui.button("+ Create list"))
    ui.type(ui.d.switch_to.active_element, "Laundry" + Keys.ENTER)
    ui.drag(ui.card("Wash"), ui.css(".vm-list__cards", ui.list_section("Laundry")))
    ui.drag(ui.card("Dry"), ui.css(".vm-list__cards", ui.list_section("Laundry")))
    assert sorted(ui.titles("Laundry")) == ["Dry", "Wash"]
    assert not ui.all(".vm-list--default")

    page = ui.css(".vm-page-export")
    ui.drag(ui.card("Wash"), page, dy=10)
    assert ui.titles() == ["Wash"] and ui.titles("Laundry") == ["Dry"]
    ui.d.refresh()
    time.sleep(PAUSE)
    assert ui.titles() == ["Wash"]


def test_search_shows_list_name(ui, owner):
    ui.create_board("Vacation")
    ui.click(ui.button("+ Create list"))
    ui.type(ui.d.switch_to.active_element, "Packing" + Keys.ENTER)
    ui.add_task("Sunscreen", "Packing")
    ui.click(ui.css("button[aria-label=Search]"))
    ui.type(ui.d.switch_to.active_element, "sunscreen")
    assert ui.text(".vm-result .vm-result__where") == "Vacation: Packing"


def test_archive_looks_like_board(ui, owner):
    ui.create_board("Kanban archive")
    ui.click(ui.button("+ Create list"))
    ui.type(ui.d.switch_to.active_element, "Later" + Keys.ENTER)
    ui.add_task("Old", "Later")
    ui.click(ui.css(".vm-check", ui.card("Old")))
    ui.click(ui.button("Archive what's done"))
    ui.confirm()
    ui.click(ui.xpath("//a[normalize-space()='Open archive']"))
    assert ui.titles("Later") == ["Old"]
    assert not ui.all("input[aria-label='New task']") and not ui.all("button[aria-label='Delete list']")


def test_card_title_inline_edit_and_drag_from_any_surface(ui, owner):
    ui.create_board("Surfaces")
    for title in ["First", "Second", "Third"]:
        ui.add_task(title)
    ui.click(ui.css(".vm-card__title .vm-inline", ui.card("Second")))
    assert not ui.all("[role=dialog][aria-label=Task]") or not ui.css("[role=dialog][aria-label=Task]").is_displayed()
    field = ui.d.switch_to.active_element
    assert field.get_attribute("aria-label") == "task title"
    ui.select_all(field)
    ui.type(field, "Renamed" + Keys.ENTER)
    assert ui.titles() == ["First", "Renamed", "Third"]

    ui.drag(ui.css(".vm-card__title .vm-inline", ui.card("Third")), ui.card("First"), dy=2)
    assert ui.titles() == ["Third", "First", "Renamed"]
    assert ui.d.switch_to.active_element.get_attribute("aria-label") != "task title"

    ui.drag(ui.css(".vm-check", ui.card("Renamed")), ui.card("Third"), dy=2)
    assert ui.titles() == ["Renamed", "Third", "First"]
    assert "vm-card--done" not in ui.card("Renamed").get_attribute("class")
    assert not ui.css("[role=dialog][aria-label=Task]").is_displayed() if ui.all("[role=dialog][aria-label=Task]") else True
    ui.d.refresh()
    time.sleep(PAUSE)
    assert ui.titles() == ["Renamed", "Third", "First"]


def add_task_elsewhere(ui, title):
    """Create a task through the REST API, past the page's own state, as another tab would."""
    ui.d.execute_async_script("""
        const [title, done] = arguments;
        const [, template] = JSON.parse(document.getElementById("vm-api-routes").textContent).task_create;
        const list = JSON.parse(document.getElementById("vm-page-data").textContent).lists.find((l) => l.is_default);
        const csrf = document.cookie.match(/csrftoken=([^;]+)/)[1];
        fetch(template.replace("{list_id}", list.id), {method: "POST", credentials: "same-origin",
              headers: {"Content-Type": "application/json", "X-CSRFToken": csrf}, body: JSON.stringify({title})})
            .then(done);
    """, title)


def show_tab(ui):
    ui.d.execute_script("document.dispatchEvent(new Event('visibilitychange'))")


def test_returning_to_tab_shows_changes_from_elsewhere(ui, owner):
    ui.create_board("Refresh")
    ui.add_task("Here")
    ui.d.execute_script("document.activeElement.blur()")
    add_task_elsewhere(ui, "Elsewhere")
    time.sleep(PAUSE)
    assert ui.titles() == ["Here"]
    show_tab(ui)
    time.sleep(PAUSE)
    assert ui.titles() == ["Here", "Elsewhere"]


def test_refresh_waits_for_lingering_tick(ui, owner):
    ui.create_board("Refresh linger")
    for title in ["One", "Two"]:
        ui.add_task(title)
    ui.d.execute_script("document.activeElement.blur()")
    ui.css(".vm-check", ui.card("One")).click()
    add_task_elsewhere(ui, "Three")
    show_tab(ui)
    time.sleep(0.3)
    assert ui.titles() == ["One", "Two"]
    time.sleep(LINGER + PAUSE * 2)
    assert ui.titles() == ["Two", "Three", "One"]


def test_refresh_waits_for_open_text_field(ui, owner):
    ui.create_board("Refresh field")
    ui.add_task("Here")
    add_task_elsewhere(ui, "Elsewhere")
    show_tab(ui)
    time.sleep(PAUSE)
    assert ui.titles() == ["Here"]
    ui.d.execute_script("document.activeElement.blur()")
    time.sleep(PAUSE * 2)
    assert ui.titles() == ["Here", "Elsewhere"]
