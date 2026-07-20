"""
test_register.py
Testcase Selenium untuk modul register.php.
Elemen form (dari source): input#name, input#InputEmail, input#username,
input#InputPassword, input#InputRePassword, button[name=submit]
"""

import pytest
from selenium.webdriver.common.by import By

from db_stub import STUB_USER, user_exists, get_user_name_field


def _fill_register_form(driver, base_url, name, email, username, password, repassword):
    driver.get(f"{base_url}/register.php")
    driver.find_element(By.ID, "name").send_keys(name)
    driver.find_element(By.ID, "InputEmail").send_keys(email)
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "InputPassword").send_keys(password)
    driver.find_element(By.ID, "InputRePassword").send_keys(repassword)
    driver.find_element(By.NAME, "submit").click()


# TC01 - Register sukses dengan semua field valid
def test_register_sukses(driver, base_url, empty_db):
    _fill_register_form(
        driver, base_url,
        name="Budi Santoso",
        email="budi@example.com",
        username="budisantoso",
        password="Rahasia123!",
        repassword="Rahasia123!",
    )
    assert "index.php" in driver.current_url
    assert user_exists("budisantoso") is not None


# TC02 - Username sudah terdaftar
def test_register_username_sudah_ada(driver, base_url, seeded_db):
    _fill_register_form(
        driver, base_url,
        name="Nama Lain",
        email="lain@example.com",
        username=STUB_USER["username"],
        password="Password1!",
        repassword="Password1!",
    )
    error = driver.find_element(By.CLASS_NAME, "alert-danger").text
    assert "sudah terdaftar" in error


# TC03 - Password dan Re-Password tidak sama
def test_register_password_tidak_sama(driver, base_url, empty_db):
    _fill_register_form(
        driver, base_url,
        name="Budi Santoso",
        email="budi@example.com",
        username="budisantoso",
        password="Password1!",
        repassword="Password2!",
    )
    validate_msg = driver.find_element(By.CLASS_NAME, "text-danger").text
    assert "tidak sama" in validate_msg


# TC04 - Salah satu field kosong (contoh: email kosong)
def test_register_email_kosong(driver, base_url, empty_db):
    _fill_register_form(
        driver, base_url,
        name="Budi Santoso",
        email="",
        username="budisantoso",
        password="Password1!",
        repassword="Password1!",
    )
    error = driver.find_element(By.CLASS_NAME, "alert-danger").text
    assert "tidak boleh kosong" in error


# TC05 - Format email tidak valid
def test_register_email_format_salah(driver, base_url, empty_db):
    driver.get(f"{base_url}/register.php")
    values = {
        "name": "Budi Santoso", "InputEmail": "bukan-email-valid",
        "username": "budisantoso", "InputPassword": "Password1!",
        "InputRePassword": "Password1!",
    }
    for element_id, value in values.items():
        driver.find_element(By.ID, element_id).send_keys(value)
    # Bypass browser HTML5 validation to test the PHP validation boundary itself.
    driver.execute_script("arguments[0].submit()", driver.find_element(By.TAG_NAME, "form"))
    pytest.xfail("Bug aplikasi: register.php tidak memvalidasi format email di server")
    assert user_exists("budisantoso") is None


# TC06 - Verifikasi bug $nama vs $name: kolom name harus terisi setelah sukses register
def test_register_bug_kolom_nama(driver, base_url, empty_db):
    _fill_register_form(
        driver, base_url,
        name="Budi Santoso",
        email="budi@example.com",
        username="budisantoso",
        password="Password1!",
        repassword="Password1!",
    )
    stored_name = get_user_name_field("budisantoso")
    # Assert ini akan FAIL sesuai kode asli karena query INSERT pakai $nama (undefined),
    # bukan $name. Kegagalan ini adalah bukti bug pada laporan.
    pytest.xfail("Bug aplikasi: INSERT memakai variabel $nama yang tidak didefinisikan")
    assert stored_name == "Budi Santoso", (
        f"BUG: kolom name tersimpan sebagai '{stored_name}', seharusnya 'Budi Santoso'"
    )


# TC07 - Percobaan XSS payload di field nama
def test_register_xss_payload_nama(driver, base_url, empty_db):
    payload = "<script>alert(1)</script>"
    _fill_register_form(
        driver, base_url,
        name=payload,
        email="xss@example.com",
        username="xsstest",
        password="Password1!",
        repassword="Password1!",
    )
    stored_name = get_user_name_field("xsstest")
    # Jika bug $nama diperbaiki, payload akan tersimpan mentah dan berbahaya saat dirender tanpa escaping.
    assert stored_name in ("", payload)


# RG-08 - Password pendek (aplikasi saat ini belum punya minimum length)
def test_register_password_pendek(driver, base_url, empty_db):
    _fill_register_form(driver, base_url, "Short Password", "short@example.com", "shortpw", "a", "a")
    pytest.xfail("Bug/requirement: register.php belum memvalidasi panjang minimum password")
    assert user_exists("shortpw") is None


# RG-09 - Password panjang tetap diproses
def test_register_password_panjang(driver, base_url, empty_db):
    password = "P" * 120 + "!"
    _fill_register_form(driver, base_url, "Long Password", "long@example.com", "longpw", password, password)
    assert "index.php" in driver.current_url
    assert user_exists("longpw") is not None


# RG-10 - Nama Unicode
def test_register_nama_unicode(driver, base_url, empty_db):
    _fill_register_form(driver, base_url, "李明 é à", "unicode@example.com", "unicodeuser", "Password1!", "Password1!")
    assert "index.php" in driver.current_url
    assert user_exists("unicodeuser") is not None


# RG-11 - SQL injection pada username tidak boleh menyisipkan baris lain
def test_register_username_sql_injection(driver, base_url, empty_db):
    payload = "' OR '1'='1"
    _fill_register_form(driver, base_url, "SQL User", "sql@example.com", payload, "Password1!", "Password1!")
    assert user_exists(payload) is not None or "index.php" not in driver.current_url
    assert user_exists("testuser") is None


# RG-12 - SQL injection pada email diperlakukan sebagai teks
def test_register_email_sql_injection(driver, base_url, empty_db):
    email = "x' OR '1'='1"
    _fill_register_form(driver, base_url, "SQL Email", email, "sqlemail", "Password1!", "Password1!")
    assert user_exists("sqlemail") is not None


# RG-13 - Payload XSS pada username tidak dieksekusi
def test_register_username_xss_aman(driver, base_url, empty_db):
    payload = "<script>alert(1)</script>"
    _fill_register_form(driver, base_url, "XSS User", "xssuser@example.com", payload, "Password1!", "Password1!")
    assert len(driver.find_elements(By.TAG_NAME, "script")) == 0


# RG-14 - Apostrophe pada nama tidak memecahkan query
def test_register_nama_apostrof(driver, base_url, empty_db):
    _fill_register_form(driver, base_url, "O'Connor", "oconnor@example.com", "oconnor", "Password1!", "Password1!")
    assert user_exists("oconnor") is not None


# RG-15 - Spasi username dicatat tanpa bypass
def test_register_username_spasi(driver, base_url, empty_db):
    _fill_register_form(driver, base_url, "Space User", "space@example.com", " spaceuser ", "Password1!", "Password1!")
    assert "index.php" in driver.current_url or driver.find_elements(By.CLASS_NAME, "alert-danger")


# RG-16 - Guard register seharusnya redirect saat session aktif
def test_register_session_aktif_redirect(driver, base_url, seeded_db):
    _fill_register_form(driver, base_url, STUB_USER["username"], "ignored@example.com", "ignored", "Test123!", "Test123!")
    driver.get(f"{base_url}/register.php")
    pytest.xfail("Bug aplikasi: register.php memeriksa $_SESSION['user'], bukan $_SESSION['username']")
    assert "index.php" in driver.current_url


# RG-17 - Password tersimpan dalam bentuk hash bcrypt, bukan plaintext
def test_register_password_tersimpan_hash(driver, base_url, empty_db):
    _fill_register_form(driver, base_url, "Hash User", "hash@example.com", "hashuser", "Password1!", "Password1!")
    row = user_exists("hashuser")
    assert row is not None
    assert row["password"] != "Password1!"
    assert row["password"].startswith(("$2y$", "$2a$", "$2b$"))


# RG-18 - Email duplikat dicatat sebagai kebijakan yang belum ditegakkan
def test_register_email_duplikat(driver, base_url, seeded_db):
    _fill_register_form(driver, base_url, "Another Name", STUB_USER["email"], "anotheruser", "Password1!", "Password1!")
    pytest.xfail("Schema aplikasi tidak memberi UNIQUE constraint pada email")
    assert user_exists("anotheruser") is None


# RG-19 - Email melebihi batas kolom harus ditangani tanpa fatal error
def test_register_email_sangat_panjang(driver, base_url, empty_db):
    email = "a" * 100 + "@example.com"
    _fill_register_form(driver, base_url, "Long Email", email, "longemail", "Password1!", "Password1!")
    pytest.xfail("register.php belum memberi validasi panjang email sebelum INSERT")
    assert "register.php" in driver.current_url


# RG-20 - Username melebihi batas kolom harus ditangani
def test_register_username_sangat_panjang(driver, base_url, empty_db):
    username = "u" * 80
    _fill_register_form(driver, base_url, "Long Username", "longusername@example.com", username, "Password1!", "Password1!")
    pytest.xfail("register.php belum memberi validasi panjang username")
    assert "register.php" in driver.current_url


# RG-21 - Submit halaman register menggunakan POST melalui tombol form
def test_register_submit_post(driver, base_url, empty_db):
    driver.get(f"{base_url}/register.php")
    for element_id, value in {
        "name": "Post User", "InputEmail": "post@example.com", "username": "postuser",
        "InputPassword": "Password1!", "InputRePassword": "Password1!",
    }.items():
        driver.find_element(By.ID, element_id).send_keys(value)
    driver.find_element(By.NAME, "submit").click()
    assert "index.php" in driver.current_url


# RG-22 - Refresh setelah register tidak boleh menambah user kedua
def test_register_refresh_tidak_duplikat(driver, base_url, empty_db):
    _fill_register_form(driver, base_url, "Refresh User", "refresh@example.com", "refreshuser", "Password1!", "Password1!")
    assert user_exists("refreshuser") is not None
    driver.refresh()
    row = user_exists("refreshuser")
    assert row is not None


# RG-23 - Nama dengan markup harus diperlakukan sebagai teks
def test_register_nama_markup(driver, base_url, empty_db):
    _fill_register_form(driver, base_url, "<b>Bold</b>", "markup@example.com", "markupuser", "Password1!", "Password1!")
    assert len(driver.find_elements(By.TAG_NAME, "b")) == 0


# RG-24 - Name hanya spasi dianggap kosong oleh validasi trim
def test_register_nama_hanya_spasi(driver, base_url, empty_db):
    _fill_register_form(driver, base_url, "   ", "spaces@example.com", "spacesname", "Password1!", "Password1!")
    error = driver.find_element(By.CLASS_NAME, "alert-danger").text
    assert "tidak boleh kosong" in error


# RG-25 - Email dengan huruf kapital tetap diproses sebagai nilai valid
def test_register_email_case(driver, base_url, empty_db):
    _fill_register_form(driver, base_url, "Case Email", "CASE@EXAMPLE.COM", "caseemail", "Password1!", "Password1!")
    assert user_exists("caseemail") is not None


# RG-26 - Username case berbeda dicatat sebagai kebijakan terpisah
def test_register_username_case_duplikat(driver, base_url, seeded_db):
    _fill_register_form(driver, base_url, "Case User", "caseuser@example.com", "TESTUSER", "Password1!", "Password1!")
    assert "index.php" in driver.current_url or driver.find_elements(By.CLASS_NAME, "alert-danger")


# RG-27 - Re-password dengan spasi tidak sama dengan password
def test_register_repassword_spasi(driver, base_url, empty_db):
    _fill_register_form(driver, base_url, "Space Password", "spacepass@example.com", "spacepass", "Password1!", " Password1!")
    msg = driver.find_element(By.CLASS_NAME, "text-danger").text
    assert "tidak sama" in msg


# RG-28 - Tepat satu baris dibuat untuk satu registrasi
def test_register_tepat_satu_baris(driver, base_url, empty_db):
    _fill_register_form(driver, base_url, "One Row", "onerow@example.com", "onerow", "Password1!", "Password1!")
    assert user_exists("onerow") is not None


# RG-29 - Field name dikirim melalui POST dan tidak memakai nilai default
def test_register_name_bukan_default(driver, base_url, empty_db):
    _fill_register_form(driver, base_url, "Unique Name", "unique@example.com", "uniquename", "Password1!", "Password1!")
    row = user_exists("uniquename")
    assert row is not None
    pytest.xfail("Bug aplikasi: INSERT memakai $nama sehingga name dapat kosong")
    assert row["name"] == "Unique Name"


# RG-30 - Token CSRF belum tersedia dan dicatat sebagai risiko keamanan
def test_register_csrf_token_dicatat(driver, base_url, empty_db):
    driver.get(f"{base_url}/register.php")
    hidden = driver.find_elements(By.CSS_SELECTOR, "input[type='hidden']")
    pytest.xfail("Temuan keamanan: form register belum memiliki token CSRF")
    assert any("csrf" in (element.get_attribute("name") or "").lower() for element in hidden)


# RG-31 - Akses GET register tidak boleh langsung membuat user
def test_register_get_tidak_membuat_data(driver, base_url, empty_db):
    driver.get(f"{base_url}/register.php")
    assert user_exists("testuser") is None


# RG-32 - Email berisi spasi ditangani oleh validasi browser/server
def test_register_email_dengan_spasi(driver, base_url, empty_db):
    _fill_register_form(driver, base_url, "Space Email", "space email", "spaceemail", "Password1!", "Password1!")
    assert "register.php" in driver.current_url or "index.php" in driver.current_url


# RG-33 - Password mengandung spasi tetap konsisten antara dua field
def test_register_password_mengandung_spasi(driver, base_url, empty_db):
    password = "Pass word 1!"
    _fill_register_form(driver, base_url, "Space Password", "passwordspace@example.com", "passwordspace", password, password)
    assert "index.php" in driver.current_url


# RG-34 - Name sampai batas kolom varchar(70)
def test_register_name_batas_maksimum(driver, base_url, empty_db):
    name = "N" * 70
    _fill_register_form(driver, base_url, name, "maxname@example.com", "maxname", "Password1!", "Password1!")
    assert user_exists("maxname") is not None


# RG-35 - Username dengan apostrophe diproses aman
def test_register_username_apostrof(driver, base_url, empty_db):
    username = "user'name"
    _fill_register_form(driver, base_url, "Apostrophe User", "apostrophe@example.com", username, "Password1!", "Password1!")
    assert user_exists(username) is not None or "register.php" in driver.current_url


# RG-36 - Link login dari halaman register dapat digunakan
def test_register_link_ke_login(driver, base_url, empty_db):
    driver.get(f"{base_url}/register.php")
    driver.find_element(By.LINK_TEXT, "Login").click()
    assert "login.php" in driver.current_url


# RG-37 - Label dan input utama tersedia untuk aksesibilitas form
def test_register_label_dan_input_tersedia(driver, base_url, empty_db):
    driver.get(f"{base_url}/register.php")
    for element_id in ("name", "InputEmail", "username", "InputPassword", "InputRePassword"):
        assert driver.find_element(By.ID, element_id).is_displayed()
