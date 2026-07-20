"""
test_login.py
Testcase Selenium untuk modul login.php.
Elemen form (dari source): input#username, input#InputPassword, button[name=submit]
"""

import pytest
from selenium.webdriver.common.by import By

from db_stub import STUB_USER


def _fill_login_form(driver, base_url, username, password):
    driver.get(f"{base_url}/login.php")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "InputPassword").send_keys(password)
    driver.find_element(By.NAME, "submit").click()


# TC01 - Login sukses dengan kredensial valid
def test_login_sukses(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, STUB_USER["username"], STUB_USER["password_plain"])
    assert "index.php" in driver.current_url, "Login sukses harus redirect ke index.php"


# TC02 - Username tidak terdaftar
def test_login_username_tidak_terdaftar(driver, base_url, empty_db):
    _fill_login_form(driver, base_url, "usertidakada", "sembarangpassword")
    error = driver.find_element(By.CLASS_NAME, "alert-danger").text
    assert "Gagal" in error
    assert "login.php" in driver.current_url


# TC03 - Password salah untuk username valid
def test_login_password_salah(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, STUB_USER["username"], "PasswordSalah123")
    # BUG DITEMUKAN: $error tidak di-set saat password_verify() gagal,
    # sehingga tidak ada alert-danger yang muncul. Assert ini akan gagal
    # dan menjadi bukti bug pada laporan.
    pytest.xfail("Bug aplikasi: login.php tidak mengatur $error saat password salah")
    alerts = driver.find_elements(By.CLASS_NAME, "alert-danger")
    assert len(alerts) > 0, "BUG: tidak ada pesan error saat password salah"
    assert "login.php" in driver.current_url


# TC04 - Username kosong
def test_login_username_kosong(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, "", STUB_USER["password_plain"])
    error = driver.find_element(By.CLASS_NAME, "alert-danger").text
    assert "tidak boleh kosong" in error


# TC05 - Password kosong
def test_login_password_kosong(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, STUB_USER["username"], "")
    error = driver.find_element(By.CLASS_NAME, "alert-danger").text
    assert "tidak boleh kosong" in error


# TC06 - Username dan password kosong
def test_login_semua_kosong(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, "", "")
    error = driver.find_element(By.CLASS_NAME, "alert-danger").text
    assert "tidak boleh kosong" in error


# TC07 - Percobaan SQL Injection di username
def test_login_sql_injection(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, "' OR '1'='1", "sembarangpassword")
    # Diharapkan gagal login (mysqli_real_escape_string sudah melindungi)
    assert "index.php" not in driver.current_url


# TC08 - Session aktif auto-redirect ke index.php
def test_login_session_aktif_redirect(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, STUB_USER["username"], STUB_USER["password_plain"])
    assert "index.php" in driver.current_url
    # Akses ulang login.php seharusnya langsung redirect karena session sudah aktif
    driver.get(f"{base_url}/login.php")
    assert "index.php" in driver.current_url


# LG-09 - Spasi di sekitar username tidak boleh menjadi bypass autentikasi
def test_login_username_dengan_spasi(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, f" {STUB_USER['username']} ", STUB_USER["password_plain"])
    assert "index.php" not in driver.current_url


# LG-10 - Username bersifat case-sensitive pada implementasi saat ini
def test_login_username_case_sensitive(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, STUB_USER["username"].upper(), STUB_USER["password_plain"])
    assert "index.php" not in driver.current_url


# LG-11 - Password bersifat case-sensitive
def test_login_password_case_sensitive(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, STUB_USER["username"], STUB_USER["password_plain"].lower())
    assert "index.php" not in driver.current_url


# LG-12 - Username sangat panjang tidak boleh menyebabkan bypass atau crash
def test_login_username_sangat_panjang(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, "u" * 200, STUB_USER["password_plain"])
    assert "index.php" not in driver.current_url


# LG-13 - Markup username tidak boleh dieksekusi sebagai HTML
def test_login_username_markup_aman(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, "<b>testuser</b>", "wrong")
    assert "index.php" not in driver.current_url
    assert len(driver.find_elements(By.TAG_NAME, "b")) == 0


# LG-14 - Refresh setelah login mempertahankan session
def test_login_refresh_mempertahankan_session(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, STUB_USER["username"], STUB_USER["password_plain"])
    assert "index.php" in driver.current_url
    driver.refresh()
    assert "index.php" in driver.current_url


# LG-15 - Cookie session tersedia setelah autentikasi
def test_login_membuat_cookie_session(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, STUB_USER["username"], STUB_USER["password_plain"])
    assert any(c["name"] == "PHPSESSID" for c in driver.get_cookies())


# LG-16 - Login ulang tidak menghapus session
def test_login_submit_ulang(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, STUB_USER["username"], STUB_USER["password_plain"])
    assert "index.php" in driver.current_url
    driver.get(f"{base_url}/login.php")
    assert "index.php" in driver.current_url


# LG-17 - Password SQL injection tidak boleh lolos
def test_login_password_sql_injection(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, STUB_USER["username"], "' OR '1'='1")
    assert "index.php" not in driver.current_url


# LG-18 - Apostrophe pada username diperlakukan sebagai teks
def test_login_username_apostrof(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, "test'user", "wrong")
    assert "index.php" not in driver.current_url


# LG-19 - Username Unicode tidak boleh membypass autentikasi
def test_login_username_unicode(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, "测试用户", "wrong")
    assert "index.php" not in driver.current_url


# LG-20 - Spasi pada password harus dianggap bagian password
def test_login_password_dengan_spasi(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, STUB_USER["username"], f" {STUB_USER['password_plain']} ")
    assert "index.php" not in driver.current_url


# LG-21 - Sebelum login, cookie PHP session belum berisi autentikasi
def test_login_cookie_sebelum_autentikasi(driver, base_url, seeded_db):
    driver.get(f"{base_url}/login.php")
    assert not any(c["name"] == "username" for c in driver.get_cookies())


# LG-22 - Login gagal tetap berada di halaman login
def test_login_gagal_tetap_di_login(driver, base_url, seeded_db):
    _fill_login_form(driver, base_url, "unknown", "wrong")
    assert "login.php" in driver.current_url


# LG-23 - Link register dari halaman login dapat digunakan
def test_login_link_ke_register(driver, base_url, seeded_db):
    driver.get(f"{base_url}/login.php")
    driver.find_element(By.LINK_TEXT, "Register").click()
    assert "register.php" in driver.current_url
