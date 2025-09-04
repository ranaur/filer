import os
from filer import db
from filer.commands import new


def test_new_creates_filebase(tmp_path):
    args = type("obj", (), {"name": "testbase"})
    new.run(args)
    base_dir = os.path.expanduser("~/.filer")
    db_path = os.path.join(base_dir, "testbase.sqlite3")
    assert os.path.exists(db_path)
    conn = db.connect(db_path)
    row = conn.execute("SELECT value FROM config WHERE key='version'").fetchone()
    assert row[0] == "0.1.0"
