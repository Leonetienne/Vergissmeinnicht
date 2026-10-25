import datetime
import json
import time

from selenium.webdriver.common.keys import Keys

from .conftest import BASE, PAUSE, mailpit_messages, manage


def set_date(ui, value):
    field = ui.css(".vm-pop input[type=date]")
    ui.d.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'))", field, value)
    time.sleep(PAUSE)


def test_quick_entry_check_uncheck_order(ui, owner):
    ui.create_board("Tasks")
    for title in ["One", "Two", "Three"]:
        ui.add_task(title)
    assert ui.d.switch_to.active_element.get_attribute("aria-label") == "New task"
    assert ui.titles() == ["One", "Two", "Three"]
    ui.click(ui.css(".vm-check", ui.card("One")))
    assert ui.titles() == ["Two", "Three", "One"]
    assert "vm-card--done" in ui.card("One").get_attribute("class")
    ui.click(ui.css(".vm-check", ui.card("One")))
    assert ui.titles() == ["One", "Two", "Three"]
    ui.d.refresh()
    time.sleep(PAUSE)
    assert ui.titles() == ["One", "Two", "Three"]


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


def test_lists_create_rename_drag_delete(ui, owner):
    ui.create_board("Kanban")
    ui.add_task("Loose")
    ui.add_task("Bread")
    create = ui.button("+ Create list")
    ui.click(create)
    ui.type(ui.d.switch_to.active_element, "Groceries" + Keys.ENTER)
    assert ui.button("+ Create another list").is_displayed()
    ui.click(ui.button("+ Create another list"))
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
    field.send_keys(Keys.CONTROL, "a")
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
    assert ui.titles() == ["Open one"]
    ui.click(ui.xpath("//a[normalize-space()='Open archive']"))
    assert ui.d.current_url.endswith("/archive/")
    assert sorted(c.text.split("\n")[0] for c in ui.all(".vm-card")) == ["Done one", "Done two"]
    ui.click(ui.css(".vm-check", ui.card("Done one")))
    ui.click(ui.button("Unarchive selected"))
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
    ui.click(ui.css("button[aria-label=Search]"))
    ui.type(ui.d.switch_to.active_element, "renew")
    ui.keys(Keys.ENTER)
    assert "#task-" in ui.d.current_url
    assert "vm-card--highlight" in ui.card("Renew passport").get_attribute("class")


def test_exports(ui, owner):
    ui.create_board("Export board")
    ui.add_task("Exported")
    links = [a.get_attribute("href") for a in ui.all("a") if a.text == "Json export"]
    assert len(links) == 2
    http = ui.session()
    board = http.get(links[-1])
    assert board.headers["Content-Disposition"] == 'attachment; filename="export-board.json"'
    assert board.json()["lists"][0]["tasks"][0]["title"] == "Exported"
    assert http.get(links[0]).json()["tasks"][0]["title"] == "Exported"


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
    ui.click(ui.xpath("//a[normalize-space()='Open archive']"))
    assert ui.titles("Later") == ["Old"]
    assert not ui.all("input[aria-label='New task']") and not ui.all("button[aria-label='Delete list']")
