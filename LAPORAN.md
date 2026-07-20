# Laporan Pengujian Modul Login dan Register

## Pendahuluan

Pengujian mencakup autentikasi pada `login.php` dan pendaftaran pada `register.php` di aplikasi PHP/MySQL quiz-pengupil.

## Metodologi

Stub database mereset dan menanam data dummy sebelum test. Selenium Chrome bertindak sebagai automation driver untuk mengisi dan mengirim form seperti pengguna. Pemeriksaan hasil dilakukan melalui URL, pesan halaman, dan query database langsung. Rincian skenario tersedia di `TESTCASES.md`.

## Eksekusi dan Bukti

Jalankan `pytest tests/ -v --junitxml=artifacts/report.xml`. Screenshot test gagal tersimpan otomatis dalam `artifacts/`. Pipeline GitHub Actions mengunggah folder tersebut walaupun job gagal. Setelah repository dipush, tambahkan screenshot run Actions ke bagian ini sebelum ekspor PDF.

## Cuplikan Penting

- `tests/conftest.py`: lifecycle Chrome, fixture stub, screenshot kegagalan.
- `tests/db_stub.py`: reset, seed bcrypt, dan query verifikasi.
- `tests/test_login.py` dan `tests/test_register.py`: skenario UI dan assertion.
- `.github/workflows/selenium-ci.yml`: MySQL service, PHP server, Chrome, pytest, dan artifact.

## Kesimpulan

Analisis dan test mengonfirmasi tiga cacat utama: password login salah tidak menghasilkan pesan; register memakai `$nama` alih-alih `$name`; dan format email tidak divalidasi server. Guard session register juga memeriksa key yang berbeda (`user` vs `username`). Input nama belum memiliki kebijakan sanitasi/escaping yang aman untuk pemakaian kembali.

## Repository

Repository GitHub: https://github.com/davidlimss/quiz-pengupil-testing
