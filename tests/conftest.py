"""
conftest.py
Fixture pytest: menyiapkan Selenium WebDriver (driver) dan stub data DB
sebelum tiap testcase dijalankan, lalu membersihkannya setelah selesai.
"""

import os
import shutil
from pathlib import Path
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from db_stub import reset_users_table, seed_default_user

BASE_URL = os.environ.get("BASE_URL", "http://localhost/quiz-pengupil-main")
ARTIFACT_DIR = Path(os.environ.get("TEST_ARTIFACT_DIR", "artifacts"))


@pytest.fixture
def driver():
    """Driver: Selenium WebDriver yang mengendalikan browser untuk tiap testcase."""
    options = Options()
    if os.environ.get("CI"):
        # Headless wajib di GitHub Actions (tidak ada display)
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,900")

    # CI installs chromedriver explicitly. Local development falls back to
    # Selenium Manager when no chromedriver executable is on PATH.
    driver_binary = shutil.which("chromedriver")
    if driver_binary:
        drv = webdriver.Chrome(service=Service(driver_binary), options=options)
    else:
        drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(5)

    yield drv

    drv.quit()


@pytest.fixture
def seeded_db():
    """Stub: reset tabel users lalu isi 1 user dummy sebelum testcase jalan."""
    reset_users_table()
    seed_default_user()
    yield
    reset_users_table()


@pytest.fixture
def empty_db():
    """Stub: tabel users kosong total, dipakai untuk testcase register (username belum ada)."""
    reset_users_table()
    yield
    reset_users_table()


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Save browser evidence for every failed test (including strict xfail checks)."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return
    driver = item.funcargs.get("driver")
    if driver:
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        suffix = "FAIL" if report.failed else "PASS"
        driver.save_screenshot(str(ARTIFACT_DIR / f"{item.name}_{suffix}.png"))
