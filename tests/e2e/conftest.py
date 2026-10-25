"""End-to-end tests against the running dev stack (docker-compose up -d)."""
import subprocess
import time
import uuid
from pathlib import Path

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

ROOT = Path(__file__).resolve().parents[2]
BASE = "http://localhost:8080"
MAILPIT = "http://localhost:8030"
PASSWORD = "Forget-me-not-1"
PAUSE = 0.6


def manage(*args):
    result = subprocess.run(["docker-compose", "exec", "-T", "web", "python", "manage.py", *args],
                            cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout


def new_user(name="Tester"):
    email = f"{name.split()[0].lower()}-{uuid.uuid4().hex[:8]}@example.org"
    manage("create_user", email, "-p", PASSWORD, "--name", name)
    return email


@pytest.fixture(scope="session")
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


class UI:
    def __init__(self, driver):
        self.d = driver

    def go(self, path):
        self.d.get(BASE + path)
        time.sleep(PAUSE)

    def login(self, email, password=PASSWORD):
        self.d.delete_all_cookies()
        self.go("/login")
        self.css("input[name=email]").send_keys(email)
        self.css("input[name=password]").send_keys(password + Keys.ENTER)
        time.sleep(PAUSE)

    def css(self, selector, root=None):
        return (root or self.d).find_element(By.CSS_SELECTOR, selector)

    def all(self, selector, root=None):
        return (root or self.d).find_elements(By.CSS_SELECTOR, selector)

    def xpath(self, path):
        return self.d.find_element(By.XPATH, path)

    def button(self, text):
        return self.xpath(f"//button[normalize-space()=\"{text}\"]")

    def click(self, element):
        element.click()
        time.sleep(PAUSE)

    def type(self, element, text):
        element.send_keys(text)
        time.sleep(PAUSE)

    def keys(self, *keys):
        ActionChains(self.d).send_keys(*keys).perform()
        time.sleep(PAUSE)

    def chord(self, key, shift=False):
        """Ctrl+key through CDP, so the host keyboard layout cannot remap the key."""
        modifiers = 2 | (8 if shift else 0)
        event = {"modifiers": modifiers, "key": key.upper() if shift else key, "code": f"Key{key.upper()}",
                 "windowsVirtualKeyCode": ord(key.upper())}
        for kind in ("rawKeyDown", "keyUp"):
            self.d.execute_cdp_cmd("Input.dispatchKeyEvent", {"type": kind, **event})
        time.sleep(PAUSE)

    def confirm(self, ok=True):
        dialog = self.css("[role=alertdialog]")
        assert dialog.is_displayed()
        self.click(self.button("OK" if ok else "Cancel"))

    def text(self, selector="body"):
        return self.css(selector).text

    def toast(self):
        return " ".join(t.text for t in self.all(".vm-toast"))

    def create_board(self, name):
        self.go("/")
        self.type(self.css("input[aria-label='New board']"), name + Keys.ENTER)
        self.click(self.xpath(f"//a[normalize-space()='{name}']"))

    def list_section(self, title=None):
        if title is None:
            return self.css(".vm-list--default")
        return self.xpath(f"//section[contains(@class,'vm-list--custom')][.//span[normalize-space()='{title}']]")

    def add_task(self, title, list_title=None):
        entry = self.css("input[aria-label='New task']", self.list_section(list_title))
        self.type(entry, title + Keys.ENTER)

    def card(self, title):
        return self.xpath(f"//article[contains(@class,'vm-card')][.//*[normalize-space()='{title}']]")

    def titles(self, list_title=None):
        return [c.text.split("\n")[0] for c in self.all(".vm-card", self.list_section(list_title))]

    def drag(self, source, target, dy=4):
        """Pointer drag in small steps from the source centre, as SortableJS fallback mode needs real moves."""
        src, tgt = source.rect, target.rect
        x, y = src["x"] + src["width"] / 2, src["y"] + src["height"] / 2
        tx, ty = tgt["x"] + 20, tgt["y"] + dy
        chain = ActionChains(self.d, duration=50).click_and_hold(source)
        for _ in range(10):
            chain = chain.move_by_offset((tx - x) / 10, (ty - y) / 10)
        chain.release().perform()
        time.sleep(PAUSE * 2)

    def session(self):
        cookies = {c["name"]: c["value"] for c in self.d.get_cookies()}
        http = requests.Session()
        http.cookies.update(cookies)
        return http


@pytest.fixture
def ui(browser):
    return UI(browser)


@pytest.fixture
def owner(ui):
    email = new_user("Leon Owner")
    ui.login(email)
    return email


def mailpit_messages(to):
    data = requests.get(f"{MAILPIT}/api/v1/search", params={"query": f"to:{to}"}).json()
    return data.get("messages", [])
