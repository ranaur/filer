# filer/db.py
import os
import sqlite3
import datetime

SCHEMA_VERSION = "0.1.0"

SCHEMA = """
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS roots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    classification TEXT DEFAULT 'medium'
);

CREATE TABLE IF NOT EXISTS directories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent INTEGER,
    root INTEGER NOT NULL,
    classification TEXT DEFAULT 'inherited',
    path TEXT NOT NULL,
    analysed INTEGER DEFAULT 0,
    FOREIGN KEY(root) REFERENCES roots(id),
    FOREIGN KEY(parent) REFERENCES directories(id),
    UNIQUE (name, parent, root),
    UNIQUE (root, path)
);

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    ctime REAL,
    mtime REAL,
    size INTEGER,
    directory INTEGER,
    mode INTEGER,
    uid INTEGER,
    gid INTEGER,
    inode INTEGER,
    dev INTEGER,
    nlink INTEGER,
    analysed INTEGER DEFAULT 0,
    FOREIGN KEY(directory) REFERENCES directories(id),
    UNIQUE (name, directory)
);

CREATE TABLE IF NOT EXISTS sha256 (
    file INTEGER PRIMARY KEY,
    sha256 TEXT NOT NULL,
    processed_at TEXT NOT NULL,
    FOREIGN KEY(file) REFERENCES files(id)
);

CREATE INDEX IF NOT EXISTS idx_files_directory ON files(directory);
CREATE INDEX IF NOT EXISTS idx_sha256_hash ON sha256(sha256);
"""


def connect(db_path: str) -> sqlite3.Connection:
    """Connect to the SQLite database (creates it if missing)."""
    first_time = not os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    if first_time:
        initialize(conn)
    return conn


def initialize(conn: sqlite3.Connection) -> None:
    """Initialize schema and insert default config."""
    conn.executescript(SCHEMA)
    now = datetime.datetime.utcnow().isoformat()
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?,?)",
                 ("version", SCHEMA_VERSION))
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?,?)",
                 ("creation_date", now))
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?,?)",
                 ("last_update", now))
    conn.commit()


def touch_update(conn: sqlite3.Connection) -> None:
    """Update the last_update field in config."""
    now = datetime.datetime.utcnow().isoformat()
    conn.execute("UPDATE config SET value=? WHERE key='last_update'", (now,))
    conn.commit()

def upsert_directory(conn: sqlite3.Connection, root_id: int, name: str, parent_id: int, path: str, classification: str) -> int:
    #print(f"DEBUG: upsert_directory: root_id={root_id}, name={name!r}, parent_id={parent_id}, path={path!r}, classification={classification!r}")
    """Upsert a directory in the directories table."""
    conn.execute("""
        INSERT OR REPLACE INTO directories (name, parent, root, path, classification, analysed)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (name, parent_id, root_id, path, classification))

def get_directory_by_path(conn: sqlite3.Connection, root_id: int, path: str) -> int:
    #print(f"DEBUG: get_directory_by_path: root_id={root_id}, path={path!r}")
    """Get the ID of a directory in the directories table by path."""
    # todo: get the path by the parent ID, not the path
    row = conn.execute("""
        SELECT id FROM directories WHERE root=? AND path=?
    """, (root_id, path)).fetchone()
    return row[0] if row else None