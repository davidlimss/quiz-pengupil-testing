# Desain dan Hasil Testcase Login & Register

Status aktual diisi dari eksekusi terbaru pada `artifacts/report.xml`. `XFAIL` berarti bug aplikasi yang sudah dikonfirmasi dan sengaja dicatat sebagai expected failure; perubahan menjadi `XPASS` akan menggagalkan CI agar baseline diperbarui.

| ID | Modul | Deskripsi | Prasyarat/Stub Data | Langkah | Input | Expected Output | Actual Output | Status |
|---|---|---|---|---|---|---|---|---|
| LG-01 | Login | Login valid | Seed `testuser` | Isi dan submit form | `testuser` / `Test123!` | Redirect `index.php` | Dari JUnit | Belum dijalankan |
| LG-02 | Login | Username tidak ada | DB kosong | Isi dan submit | `usertidakada` | Tetap di login, pesan gagal | Dari JUnit | Belum dijalankan |
| LG-03 | Login | Password salah | Seed `testuser` | Isi dan submit | password salah | Pesan autentikasi gagal | Tidak ada pesan (bug) | XFAIL |
| LG-04 | Login | Username kosong | Seed | Submit tanpa username | username kosong | Pesan data kosong | Dari JUnit | Belum dijalankan |
| LG-05 | Login | Password kosong | Seed | Submit tanpa password | password kosong | Pesan data kosong | Dari JUnit | Belum dijalankan |
| LG-06 | Login | Semua kosong | Seed | Submit form kosong | kosong | Pesan data kosong | Dari JUnit | Belum dijalankan |
| LG-07 | Login | SQL injection | Seed | Kirim payload | `' OR '1'='1` | Login ditolak | Dari JUnit | Belum dijalankan |
| LG-08 | Login | Session aktif | Seed; login dahulu | Buka ulang login | session cookie | Redirect `index.php` | Dari JUnit | Belum dijalankan |
| RG-01 | Register | Data valid | DB kosong | Isi semua field | data Budi | User dibuat dan redirect | Nama kosong akibat bug `$nama` | Diuji terpisah RG-06 |
| RG-02 | Register | Username duplikat | Seed `testuser` | Register username sama | `testuser` | Pesan sudah terdaftar | Dari JUnit | Belum dijalankan |
| RG-03 | Register | Password berbeda | DB kosong | Isi password berbeda | `Password1!` / `Password2!` | Pesan password tidak sama | Dari JUnit | Belum dijalankan |
| RG-04 | Register | Field kosong | DB kosong | Kosongkan email | email kosong | Pesan data kosong | Dari JUnit | Belum dijalankan |
| RG-05 | Register | Email invalid | DB kosong | Bypass HTML5 lalu submit | `bukan-email-valid` | Server menolak | Server menerima (bug) | XFAIL |
| RG-06 | Register | Verifikasi kolom nama | DB kosong | Register lalu query DB | `Budi Santoso` | Nama tersimpan utuh | Nama kosong (bug `$nama`) | XFAIL |
| RG-07 | Register | Payload XSS nama | DB kosong | Register payload lalu query DB | `<script>alert(1)</script>` | Ditolak/disanitasi aman | Tertutup bug `$nama`; kode tidak punya sanitasi output | Risiko ditemukan |

## Metodologi

Setiap test menggunakan Selenium WebDriver untuk mensimulasikan interaksi browser terhadap UI PHP. Fixture database menghapus tabel `users` dan menanam satu akun bcrypt yang tetap sebelum skenario terkait, sehingga test repeatable dan tidak bergantung pada data sebelumnya. Assertion memeriksa redirect, pesan UI, atau isi database melalui `mysql-connector-python`. Screenshot otomatis disimpan untuk kegagalan, sedangkan seluruh hasil tersedia sebagai JUnit XML.
