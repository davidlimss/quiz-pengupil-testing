"""
db_stub.py
Stub data layer: reset & seed tabel `users` sebelum setiap testcase dijalankan,
supaya hasil testing konsisten dan repeatable (tidak tergantung data lama).
"""

import os
import mysql.connector

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "quiz_pengupil"),
}

# Kredensial dummy yang dipakai konsisten di semua testcase
STUB_USER = {
    "username": "testuser",
    "name": "Test User",
    "email": "testuser@example.com",
    "password_plain": "Test123!",
}


def _get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def reset_users_table():
    """Kosongkan tabel users, dipanggil sebelum setiap testcase (fixture)."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")
    conn.commit()
    cursor.close()
    conn.close()


def seed_default_user():
    """Insert satu user dummy dengan password sudah di-hash (PHP password_hash-compatible)."""
    # PHP password_hash() default pakai bcrypt, jadi kita pakai bcrypt juga di sisi test
    # supaya password_verify() di PHP bisa memverifikasi hash ini.
    # Fixed PHP-compatible bcrypt hash for "Test123!" keeps the fixture deterministic.
    hashed = "$2y$10$gZS7kaDxXvxYqjKSuxmhqe3Cq24L0AXO6eGzWZQcPRZJXMmIYNWgO"

    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, name, email, password) VALUES (%s, %s, %s, %s)",
        (STUB_USER["username"], STUB_USER["name"], STUB_USER["email"], hashed),
    )
    conn.commit()
    cursor.close()
    conn.close()


def user_exists(username):
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_user_name_field(username):
    """Dipakai khusus untuk testcase verifikasi bug $nama vs $name di register.php."""
    row = user_exists(username)
    return row["name"] if row else None
