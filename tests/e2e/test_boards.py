import time

from selenium.webdriver.common.keys import Keys

from .conftest import BASE, PAUSE, new_user


def test_board_list_create_rename_reorder_undo(ui, owner):
    ui.go("/")
    entry = ui.css("input[aria-label='New board']")
    for name in ["Alpha", "Beta", "Gamma"]:
        ui.type(entry, name + Keys.ENTER)
    assert ui.d.switch_to.active_element == entry
    names = lambda: [a.text for a in ui.all(".vm-board-entry__name")]
    assert names() == ["Alpha", "Beta", "Gamma"]
    assert ui.all(".vm-emoji--empty")

    ui.click(ui.all("button[aria-label='Rename board name']")[1])
    field = ui.d.switch_to.active_element
    field.send_keys(Keys.CONTROL, "a")
    ui.type(field, "Bravo" + Keys.ENTER)
    assert names()[1] == "Bravo"

    ui.drag(ui.all(".vm-board-entry")[2], ui.all(".vm-board-entry")[0], dy=-10)
    assert names() == ["Gamma", "Alpha", "Bravo"]

    ui.click(ui.css(".vm-footer span"))
    ui.chord("z")
    assert "Undo: move board" in ui.toast()
    assert names() == ["Alpha", "Bravo", "Gamma"]
    ui.chord("z", shift=True)
    ui.go("/")
    assert names() == ["Gamma", "Alpha", "Bravo"]


def test_emoji_picker(ui, owner):
    ui.create_board("Household")
    ui.click(ui.css(".vm-page-title button.vm-emoji--empty"))
    ui.type(ui.d.switch_to.active_element, "house with garden")
    ui.click(ui.css(".vm-page-title .vm-emoji-grid button"))
    assert ui.text(".vm-page-title .vm-emoji") == "🏡"
    ui.go("/")
    assert ui.text(".vm-board-entry .vm-emoji") == "🏡"
    ui.click(ui.css(".vm-board-entry .vm-emoji"))
    ui.click(ui.button("Remove"))
    assert ui.all(".vm-board-entry .vm-emoji--empty")


def test_board_rename_slug_and_delete(ui, owner):
    ui.create_board("Old name")
    ui.click(ui.css(".vm-page-title .vm-inline"))
    field = ui.d.switch_to.active_element
    field.send_keys(Keys.CONTROL, "a")
    ui.type(field, "New name" + Keys.ENTER)
    assert ui.d.current_url.endswith("-new-name/")
    ui.click(ui.css("button[aria-label='Delete board']"))
    assert "Delete board New name" in ui.text("[role=alertdialog]")
    ui.confirm()
    assert ui.d.current_url == BASE + "/" and "New name" not in ui.text(".vm-boards")


def test_inline_edit_escape_and_empty_restore(ui, owner):
    ui.create_board("Keep")
    ui.click(ui.css(".vm-page-title .vm-inline"))
    field = ui.d.switch_to.active_element
    field.send_keys(Keys.CONTROL, "a")
    ui.type(field, "Changed" + Keys.ESCAPE)
    assert ui.text(".vm-page-title h1") == "Keep"
    ui.click(ui.css(".vm-page-title .vm-inline"))
    field = ui.d.switch_to.active_element
    field.send_keys(Keys.CONTROL, "a", Keys.BACKSPACE)
    ui.type(field, Keys.ENTER)
    assert ui.text(".vm-page-title h1") == "Keep"


def test_sharing_roles_and_leave(ui):
    member = new_user("Mara Member")
    owner = new_user("Leon Owner")
    ui.login(owner)
    ui.create_board("Shared board")
    board_url = ui.d.current_url
    ui.add_task("Visible task")
    ui.click(ui.button("Share"))
    ui.type(ui.css("input[aria-label='Add user']"), member.split("@")[0])
    ui.click(ui.css(".vm-pop .vm-result"))
    assert "Mara Member" in ui.text(".vm-share")

    ui.login(member)
    assert "Shared board" in ui.text() and "Leon Owner · Observer" in ui.text()
    ui.go(board_url.replace(BASE, ""))
    assert "Visible task" in ui.text()
    assert not ui.all("input[aria-label='New task']") and not ui.all("button[aria-label='Delete task']")
    assert not ui.css(".vm-card .vm-check").is_enabled()
    assert not ui.all("button[aria-label='Choose emoji']") and not ui.all("button[aria-label='Delete board']")
    assert not ui.all(".vm-page-title__actions button.vm-btn--primary")

    ui.login(owner)
    ui.go(board_url.replace(BASE, ""))
    ui.click(ui.button("Share"))
    ui.css(".vm-share select").send_keys("Editor")
    time.sleep(PAUSE)

    ui.login(member)
    ui.go(board_url.replace(BASE, ""))
    ui.add_task("From editor")
    assert "From editor" in ui.titles()
    assert not ui.all("button[aria-label='Delete board']")
    ui.click(ui.button("Leave board"))
    ui.confirm()
    assert ui.d.current_url == BASE + "/" and "Shared board" not in ui.text()
    ui.go(board_url.replace(BASE, ""))
    assert "Not Found" in ui.text() or "404" in ui.d.title or "not found" in ui.text().lower()


def test_mobile_stacks_lists(ui, owner):
    ui.create_board("Phone")
    ui.click(ui.button("+ Create list"))
    ui.type(ui.d.switch_to.active_element, "Second" + Keys.ENTER)
    ui.d.set_window_size(375, 800)
    time.sleep(PAUSE)
    try:
        lists = ui.all(".vm-list")
        assert lists[1].location["y"] > lists[0].location["y"]
        assert ui.d.execute_script("return document.documentElement.scrollWidth <= window.innerWidth")
    finally:
        ui.d.set_window_size(1280, 900)
