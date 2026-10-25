import time
import uuid

import pyotp
from selenium.webdriver.common.keys import Keys

from .conftest import BASE, PASSWORD, PAUSE, new_user


def test_login_redirect_next_and_logout(ui):
    email = new_user()
    ui.d.delete_all_cookies()
    ui.go("/settings/")
    assert ui.d.current_url == BASE + "/login?next=/settings/"
    ui.css("input[name=email]").send_keys(email.upper())
    ui.css("input[name=password]").send_keys(PASSWORD + Keys.ENTER)
    time.sleep(PAUSE)
    assert ui.d.current_url == BASE + "/settings/"
    ui.click(ui.css("button[aria-label=Menu]"))
    ui.click(ui.button("Logout"))
    assert ui.d.current_url.startswith(BASE + "/login")


def test_theme_menu(ui, owner):
    html = ui.css("html")
    ui.click(ui.css("button[aria-label=Theme]"))
    ui.click(ui.xpath("//button[normalize-space()='OLED']"))
    ui.click(ui.xpath("//button[normalize-space()='Dark']"))
    time.sleep(PAUSE)
    assert (html.get_attribute("data-theme"), html.get_attribute("data-mode")) == ("oled", "dark")
    ui.go("/settings/")
    html = ui.css("html")
    assert (html.get_attribute("data-theme"), html.get_attribute("data-mode")) == ("oled", "dark")
    assert ui.d.execute_script("return getComputedStyle(document.body).backgroundColor") == "rgb(0, 0, 0)"


def test_wrong_password_message(ui):
    ui.login(new_user(), "wrong-password")
    assert "Email or password is wrong" in ui.text()


def test_registration(ui):
    ui.d.delete_all_cookies()
    ui.go("/login")
    ui.click(ui.xpath("//a[normalize-space()='Create account']"))
    ui.css("input[name=display_name]").send_keys("Ann")
    ui.css("input[name=email]").send_keys(f"ann-{uuid.uuid4().hex[:6]}@example.org")
    ui.css("input[name=password]").send_keys(PASSWORD + Keys.ENTER)
    time.sleep(PAUSE)
    assert ui.d.current_url == BASE + "/" and "My boards" in ui.text()


def test_footer(ui):
    ui.go("/login")
    assert "Open Source on Github" in ui.text(".vm-footer") and "dev" in ui.text(".vm-footer")


def test_two_factor_setup_login_and_recovery(ui):
    email = new_user()
    ui.login(email)
    ui.go("/settings/")
    ui.click(ui.button("Set up"))
    assert ui.css(".vm-qr svg").is_displayed()
    secret = ui.text("#second-factor code")
    ui.type(ui.css("#second-factor input[name=code]"), pyotp.TOTP(secret).now() + Keys.ENTER)
    codes = ui.text(".vm-codes").split()
    assert len(codes) == 10

    ui.login(email)
    assert "Second factor" in ui.text()
    time.sleep(31)
    ui.type(ui.css("input[name=code]"), pyotp.TOTP(secret).now() + Keys.ENTER)
    assert ui.d.current_url == BASE + "/"

    ui.login(email)
    ui.type(ui.css("input[name=code]"), codes[0] + Keys.ENTER)
    assert "Second factor removed" in ui.toast()
    ui.go("/settings/")
    assert "Not set up." in ui.text("#second-factor")


def test_keys_shown_once(ui, owner):
    ui.go("/settings/")
    ui.click(ui.css("#api-key").find_element("xpath", ".//button[normalize-space()='Generate']"))
    key = ui.text("[data-new-key]")
    assert key.startswith("vmk_")
    assert ui.session().get(BASE + "/api/v1/boards/", headers={"Authorization": f"Bearer {key}"}).status_code == 200
    ui.go("/settings/")
    assert key not in ui.text() and "Never used" not in ui.text("#api-key")
    ui.click(ui.css("#api-key").find_element("xpath", ".//button[normalize-space()='Revoke']"))
    assert "No key." in ui.text("#api-key")


def test_ui_opacity_previews_live(ui, owner):
    ui.go("/settings/")
    slider = ui.css("input[name=ui_opacity]")
    ui.d.execute_script("arguments[0].value = 40; arguments[0].dispatchEvent(new Event('input'))", slider)
    time.sleep(PAUSE)
    value = ui.d.execute_script("return document.documentElement.style.getPropertyValue('--ui-alpha')")
    assert value.strip() == "40%"


def test_delete_account(ui):
    email = new_user()
    ui.login(email)
    ui.create_board("Doomed")
    ui.go("/settings/")
    ui.click(ui.button("Delete account"))
    assert "All boards and tasks you own are deleted" in ui.text("[role=alertdialog]")
    ui.confirm()
    assert "/login" in ui.d.current_url
    ui.login(email)
    assert "Email or password is wrong" in ui.text()
