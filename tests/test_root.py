import os
from filer import db
from filer.commands import root


def test_root_add_and_list(tmp_path):
    db_path = tmp_path / "root.sqlite3"
    conn = db.connect(str(db_path))
    d = tmp_path / "subdir"
    d.mkdir()
    args = type("obj", (), {"db": str(db_path), "list": False, "delete": False, "classification": "high", "paths": [str(d)]})
    root.run(args)
    rows = conn.execute("SELECT path,classification FROM roots").fetchall()
    assert (str(d), "high") in rows


def test_root_delete(tmp_path):
    db_path = tmp_path / "root.sqlite3"
    conn = db.connect(str(db_path))
    d = tmp_path / "subdir"
    d.mkdir()
    conn.execute("INSERT INTO roots (path,classification) VALUES (?,?)", (str(d), "medium"))
    conn.commit()
    args = type("obj", (), {"db": str(db_path), "list": False, "delete": True, "classification": "medium", "paths": [str(d)]})
    root.run(args)
    row = conn.execute("SELECT * FROM roots").fetchone()
    assert row is None
