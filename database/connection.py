"""Database connection management with WAL mode for concurrency."""

import sqlite3
import os
import streamlit as st

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "ctms.db")


@st.cache_resource
def get_connection() -> sqlite3.Connection:
    """Return a cached SQLite connection with WAL mode and foreign keys enabled."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def get_db() -> sqlite3.Connection:
    """Get database connection from cache."""
    return get_connection()


def init():
    """Initialize DB schema + run migrations + seed on first start."""
    from database.schema import init_db, migrate
    from database.seed import seed
    conn = get_db()
    init_db(conn)
    migrate(conn)
    seed(conn)
