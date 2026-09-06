"""
LocalLink - Database Module
Handles SQLite initialization and all DB operations
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "locallink.db")


def get_db():
    """Open a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    # Users table — pre-registered by admin
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            full_name   TEXT NOT NULL,
            role        TEXT DEFAULT 'student',
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Sessions table — tracks who is currently online
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT UNIQUE NOT NULL,
            device_ip   TEXT NOT NULL,
            mac_address TEXT,
            logged_in   TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(student_id)
        )
    """)

    # Messages table — stores chat history
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT NOT NULL,
            full_name   TEXT NOT NULL,
            content     TEXT NOT NULL,
            msg_type    TEXT DEFAULT 'text',
            timestamp   TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(student_id)
        )
    """)

    # Files table — tracks uploaded files
    c.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            filename     TEXT NOT NULL,
            original_name TEXT NOT NULL,
            uploaded_by  TEXT NOT NULL,
            file_size    INTEGER,
            file_type    TEXT,
            auto_push    INTEGER DEFAULT 0,
            uploaded_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed default admin account if not exists
    c.execute("SELECT * FROM users WHERE student_id = 'admin'")
    if not c.fetchone():
        c.execute("""
            INSERT INTO users (student_id, password, full_name, role)
            VALUES ('admin', 'admin2026', 'Administrator', 'admin')
        """)

    conn.commit()
    conn.close()


# ── User Operations ───────────────────────────────────────────────

def get_user(student_id):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE student_id = ?", (student_id,)
    ).fetchone()
    conn.close()
    return user


def get_all_users():
    conn = get_db()
    users = conn.execute(
        "SELECT * FROM users WHERE role = 'student' ORDER BY student_id"
    ).fetchall()
    conn.close()
    return users


def add_user(student_id, password, full_name):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (student_id, password, full_name) VALUES (?, ?, ?)",
            (student_id, password, full_name)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def delete_user(student_id):
    conn = get_db()
    conn.execute("DELETE FROM users WHERE student_id = ?", (student_id,))
    conn.execute("DELETE FROM sessions WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()


# ── Session Operations ────────────────────────────────────────────

def create_session(student_id, device_ip):
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO sessions (student_id, device_ip, logged_in) VALUES (?, ?, ?)",
        (student_id, device_ip, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def delete_session(student_id):
    conn = get_db()
    conn.execute("DELETE FROM sessions WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()


def is_session_active(student_id):
    conn = get_db()
    session = conn.execute(
        "SELECT * FROM sessions WHERE student_id = ?", (student_id,)
    ).fetchone()
    conn.close()
    return session is not None


def get_active_sessions():
    conn = get_db()
    sessions = conn.execute("""
        SELECT s.student_id, s.device_ip, s.logged_in, u.full_name
        FROM sessions s
        JOIN users u ON s.student_id = u.student_id
        ORDER BY s.logged_in DESC
    """).fetchall()
    conn.close()
    return sessions


def force_logout(student_id):
    delete_session(student_id)


# ── Message Operations ────────────────────────────────────────────

def save_message(student_id, full_name, content, msg_type="text"):
    conn = get_db()
    conn.execute(
        "INSERT INTO messages (student_id, full_name, content, msg_type) VALUES (?, ?, ?, ?)",
        (student_id, full_name, content, msg_type)
    )
    conn.commit()
    conn.close()


def get_recent_messages(limit=50):
    conn = get_db()
    messages = conn.execute(
        "SELECT * FROM messages ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return list(reversed(messages))


# ── File Operations ───────────────────────────────────────────────

def save_file_record(filename, original_name, uploaded_by, file_size, file_type, auto_push=0):
    conn = get_db()
    conn.execute("""
        INSERT INTO files (filename, original_name, uploaded_by, file_size, file_type, auto_push)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (filename, original_name, uploaded_by, file_size, file_type, auto_push))
    conn.commit()
    conn.close()


def get_all_files():
    conn = get_db()
    files = conn.execute(
        "SELECT * FROM files ORDER BY uploaded_at DESC"
    ).fetchall()
    conn.close()
    return files


def delete_file_record(file_id):
    conn = get_db()
    file = conn.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()
    conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
    conn.commit()
    conn.close()
    return file
