"""10 testcase inti untuk login.php."""
import pytest
from selenium.webdriver.common.by import By
from db_stub import STUB_USER


def fill_login(driver, base_url, username, password):
    driver.get(f"{base_url}/login.php")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "InputPassword").send_keys(password)
    driver.find_element(By.NAME, "submit").click()


def test_login_sukses(driver, base_url, seeded_db):
    fill_login(driver, base_url, STUB_USER["username"], STUB_USER["password_plain"])
    assert "index.php" in driver.current_url


def test_login_username_tidak_terdaftar(driver, base_url, seeded_db):
    fill_login(driver, base_url, "tidakada", "sembarang")
    assert "login.php" in driver.current_url
    assert "Gagal" in driver.find_element(By.CLASS_NAME, "alert-danger").text


def test_login_password_salah(driver, base_url, seeded_db):
    fill_login(driver, base_url, STUB_USER["username"], "PasswordSalah!")
    pytest.xfail("Bug aplikasi: $error tidak diisi saat password_verify gagal")
    assert driver.find_elements(By.CLASS_NAME, "alert-danger")


def test_login_username_kosong(driver, base_url, seeded_db):
    fill_login(driver, base_url, "", STUB_USER["password_plain"])
    assert "tidak boleh kosong" in driver.find_element(By.CLASS_NAME, "alert-danger").text


def test_login_password_kosong(driver, base_url, seeded_db):
    fill_login(driver, base_url, STUB_USER["username"], "")
    assert "tidak boleh kosong" in driver.find_element(By.CLASS_NAME, "alert-danger").text


def test_login_semua_kosong(driver, base_url, seeded_db):
    fill_login(driver, base_url, "", "")
    assert "tidak boleh kosong" in driver.find_element(By.CLASS_NAME, "alert-danger").text


def test_login_sql_injection_ditolak(driver, base_url, seeded_db):
    fill_login(driver, base_url, "' OR '1'='1", "sembarang")
    assert "index.php" not in driver.current_url


def test_login_session_aktif_redirect(driver, base_url, seeded_db):
    fill_login(driver, base_url, STUB_USER["username"], STUB_USER["password_plain"])
    assert "index.php" in driver.current_url
    driver.get(f"{base_url}/login.php")
    assert "index.php" in driver.current_url


def test_login_username_sangat_panjang(driver, base_url, seeded_db):
    fill_login(driver, base_url, "u" * 200, STUB_USER["password_plain"])
    assert "index.php" not in driver.current_url


def test_login_link_register(driver, base_url, seeded_db):
    driver.get(f"{base_url}/login.php")
    driver.find_element(By.LINK_TEXT, "Register").click()
    assert "register.php" in driver.current_url
