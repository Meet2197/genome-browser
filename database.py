import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).parent / "genome_browser.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30)  # wait up to 30s for locks instead of failing instantly
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")     # allows concurrent readers + one writer
    conn.execute("PRAGMA busy_timeout = 30000")   # extra safety: 30s busy timeout at SQLite level
    return conn


@contextmanager
def db_session():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def is_empty() -> bool:
    conn = get_connection()
    cur = conn.execute("SELECT COUNT(*) AS c FROM genomes")
    n = cur.fetchone()["c"]
    conn.close()
    return n == 0