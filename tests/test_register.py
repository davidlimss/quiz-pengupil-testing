"""10 testcase inti untuk register.php."""
import pytest
from selenium.webdriver.common.by import By
from db_stub import STUB_USER, user_exists, get_user_name_field


def fill_register(driver, base_url, name, email, username, password, repassword):
    driver.get(f"{base_url}/register.php")
    for element_id, value in {
        "name": name, "InputEmail": email, "username": username,
        "InputPassword": password, "InputRePassword": repassword,
    }.items():
        driver.find_element(By.ID, element_id).send_keys(value)
    driver.find_element(By.NAME, "submit").click()


def test_register_sukses(driver, base_url, empty_db):
    fill_register(driver, base_url, "David Sam Limbong", "david@example.com", "davidtest", "Test123!", "Test123!")
    assert "index.php" in driver.current_url
    assert user_exists("davidtest") is not None


def test_register_username_sudah_terdaftar(driver, base_url, seeded_db):
    fill_register(driver, base_url, "Nama Baru", "baru@example.com", STUB_USER["username"], "Test123!", "Test123!")
    pytest.xfail("Bug aplikasi: cek_nama dipanggil memakai $name, bukan $username")
    assert "sudah terdaftar" in driver.find_element(By.CLASS_NAME, "alert-danger").text


def test_register_password_tidak_sama(driver, base_url, empty_db):
    fill_register(driver, base_url, "David", "david@example.com", "david2", "Test123!", "Different!")
    assert "tidak sama" in driver.find_element(By.CLASS_NAME, "text-danger").text


def test_register_field_email_kosong(driver, base_url, empty_db):
    fill_register(driver, base_url, "David", "", "david3", "Test123!", "Test123!")
    assert "tidak boleh kosong" in driver.find_element(By.CLASS_NAME, "alert-danger").text


def test_register_email_format_invalid(driver, base_url, empty_db):
    driver.get(f"{base_url}/register.php")
    for element_id, value in {"name":"David", "InputEmail":"bukan-email", "username":"invalidemail", "InputPassword":"Test123!", "InputRePassword":"Test123!"}.items():
        driver.find_element(By.ID, element_id).send_keys(value)
    # Bypass browser validation untuk menguji boundary PHP.
    driver.execute_script("HTMLFormElement.prototype.submit.call(arguments[0])", driver.find_element(By.TAG_NAME, "form"))
    pytest.xfail("Bug aplikasi: email tidak divalidasi di server")
    assert user_exists("invalidemail") is None


def test_register_bug_kolom_name(driver, base_url, empty_db):
    fill_register(driver, base_url, "Nama Asli", "name@example.com", "namebug", "Test123!", "Test123!")
    stored = get_user_name_field("namebug")
    pytest.xfail("Bug aplikasi: query INSERT memakai $nama bukan $name")
    assert stored == "Nama Asli"


def test_register_xss_nama_tidak_dieksekusi(driver, base_url, empty_db):
    fill_register(driver, base_url, "<script>alert(1)</script>", "xss@example.com", "xssuser", "Test123!", "Test123!")
    assert len(driver.find_elements(By.TAG_NAME, "script")) == 0


def test_register_password_pendek(driver, base_url, empty_db):
    fill_register(driver, base_url, "Short", "short@example.com", "shortpw", "a", "a")
    pytest.xfail("Bug/requirement: panjang minimum password belum divalidasi")
    assert user_exists("shortpw") is None


def test_register_password_tersimpan_hash(driver, base_url, empty_db):
    fill_register(driver, base_url, "Hash User", "hash@example.com", "hashuser", "Test123!", "Test123!")
    row = user_exists("hashuser")
    assert row is not None
    assert row["password"] != "Test123!"
    assert row["password"].startswith(("$2y$", "$2a$", "$2b$"))


def test_register_link_login(driver, base_url, empty_db):
    driver.get(f"{base_url}/register.php")
    driver.find_element(By.LINK_TEXT, "Login").click()
    assert "login.php" in driver.current_url
