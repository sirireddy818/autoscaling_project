import sqlite3
import os
import hashlib
import secrets
import time

# ──────────────────────────────────────────────
# db.py
# Handles all database operations for user accounts.
# Uses SQLite — a lightweight database stored as a single file (cloudscale.db).
# No external database server needed.
# Responsible for: creating the DB, signing up users, logging them in.
# ──────────────────────────────────────────────

# Build the full path to cloudscale.db (located in the project root folder)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cloudscale.db")


def get_db():
    """Opens a connection to the SQLite database file."""
    conn = sqlite3.connect(DB_PATH)
    # Makes query results accessible like dicts: row['email'] instead of row[0]
    conn.row_factory = sqlite3.Row
    # WAL mode = Write-Ahead Logging → prevents data corruption if app crashes mid-write
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """
    Creates the users table if it doesn't already exist.
    Runs automatically every time the app starts (line 30).
    IF NOT EXISTS = safe to run repeatedly without wiping existing data.
    """
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- auto-increments: 1, 2, 3...
            full_name TEXT NOT NULL,                -- user's display name
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,  -- email must be unique, case-insensitive
            password_hash TEXT NOT NULL,            -- hashed password (never plain text)
            avatar_color TEXT DEFAULT '#3b82f6',    -- random color for avatar badge
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- when account was created
        );
    """)
    conn.commit()
    conn.close()

# Run init_db immediately when this file is imported
# So the table always exists before any signup/login attempt
init_db()

# 8 colors randomly assigned as avatar background when a user signs up
AVATAR_COLORS = ['#3b82f6', '#22c55e', '#a855f7', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899', '#14b8a6']


def _hash_password(password, salt=None):
    """
    Hashes a password using PBKDF2-SHA256 (military-grade hashing).
    Never stores the plain password — only this scrambled version.

    salt = random 32-character string added before hashing.
    Why salt? So two users with the same password get different hashes.
    100,000 iterations = very slow to brute-force crack.

    Returns: "salt:hashedvalue" stored as one string.
    """
    if salt is None:
        salt = secrets.token_hex(16)  # Generate new random salt
    h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{h.hex()}"  # Store salt alongside hash so we can verify later


def _verify_password(password, stored):
    """
    Verifies a login attempt by re-hashing with the original salt and comparing.
    If it matches → correct password. If not → wrong password.
    """
    salt, _ = stored.split(':')  # Extract the salt from the stored string
    return _hash_password(password, salt) == stored  # Rehash and compare


def signup(full_name, email, password):
    """
    Creates a new user account.
    Returns: (user_dict, None) on success, (None, error_message) on failure.
    """
    # ── Input validation ──
    if not full_name or not email or not password:
        return None, "All fields are required."
    if len(password) < 6:
        return None, "Password must be at least 6 characters."
    if '@' not in email or '.' not in email:
        return None, "Please enter a valid email."

    conn = get_db()

    # Check if email is already registered (emails must be unique)
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (email.lower(),)).fetchone()
    if existing:
        conn.close()
        return None, "An account with this email already exists."

    # Hash the password before saving
    pw_hash = _hash_password(password)
    # Pick a random avatar color for this user
    color = secrets.choice(AVATAR_COLORS)

    # Insert new user record into the database
    cur = conn.execute(
        "INSERT INTO users (full_name, email, password_hash, avatar_color) VALUES (?, ?, ?, ?)",
        (full_name.strip(), email.lower().strip(), pw_hash, color)
    )
    conn.commit()

    # Fetch the newly created user to return their info
    user = conn.execute(
        "SELECT id, full_name, email, avatar_color, created_at FROM users WHERE id = ?",
        (cur.lastrowid,)
    ).fetchone()
    conn.close()

    return dict(user), None  # Return user info, no error


def login(email, password):
    """
    Verifies login credentials.
    Returns: (user_dict, None) on success, (None, error_message) on failure.
    Note: Always returns the same error message whether email or password is wrong —
    this is a security best practice (don't reveal which one failed).
    """
    if not email or not password:
        return None, "Email and password are required."

    conn = get_db()
    # Look up user by email (case-insensitive)
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
    ).fetchone()
    conn.close()

    # User not found
    if not user:
        return None, "Invalid email or password."

    # Password doesn't match
    if not _verify_password(password, user['password_hash']):
        return None, "Invalid email or password."

    # Success — return user info (never include password_hash in the returned dict)
    return {
        'id': user['id'],
        'full_name': user['full_name'],
        'email': user['email'],
        'avatar_color': user['avatar_color'],
        'created_at': user['created_at'],
    }, None
