# Panduan Bukti Screenshot Pengujian

Identitas: **David Sam Limbong — III RPLK — 2322101894**

## 1. Persiapan

1. Buka XAMPP Control Panel.
2. Start **Apache** dan **MySQL**.
3. Pastikan database `quiz_pengupil` sudah di-import dari `db/quiz_pengupil.sql`.
4. Buka PowerShell pada folder project.

Screenshot yang diambil: XAMPP menampilkan Apache/MySQL hijau dan phpMyAdmin menampilkan database `quiz_pengupil`.

## 2. Jalankan aplikasi

```powershell
cd C:\xampp\htdocs\quiz-pengupil-main
php -S 127.0.0.1:8000
```

Buka `http://127.0.0.1:8000/login.php` di Chrome. Ambil screenshot halaman Login dan Register sebelum test.

## 3. Jalankan seluruh testcase

Buka PowerShell kedua:

```powershell
cd C:\xampp\htdocs\quiz-pengupil-main
$env:CI="true"
pytest tests/ -v --junitxml=artifacts/report.xml
```

Fixture akan reset/seed database otomatis. Selenium akan menyimpan screenshot setiap testcase ke folder `artifacts/` dengan nama `test_nama_PASS.png` atau `test_nama_FAIL.png`.

Ambil screenshot terminal yang menampilkan ringkasan `passed`, `xfailed`, atau `failed`, serta screenshot isi folder `artifacts`.

## 4. Bukti manual yang disarankan

- Login valid: tampilkan redirect URL `index.php`.
- Password salah: tampilkan pesan yang hilang sebagai bukti bug.
- SQL injection: tampilkan tetap di login dan tidak masuk.
- Register valid: buka phpMyAdmin dan screenshot baris user baru.
- Bug `$nama` vs `$name`: screenshot kolom `name` kosong setelah register.
- Email invalid: screenshot form berhasil terkirim/diterima sebagai bukti validasi server belum ada.
- XSS: screenshot payload tidak boleh dieksekusi; simpan screenshot dan catat risiko escaping.

## 5. Bukti GitHub Actions

1. Push repository ke GitHub.
2. Buka tab **Actions**.
3. Buka workflow **Selenium CI - Login & Register Testing**.
4. Screenshot status hijau, detail job, dan artifact `selenium-test-report`.

## 6. Penempatan bukti di laporan

Gunakan caption: `Gambar 1 — XAMPP aktif`, `Gambar 2 — halaman login`, `Gambar 3 — hasil pytest`, `Gambar 4 — artifact screenshot`, dan `Gambar 5 — GitHub Actions berhasil`.
