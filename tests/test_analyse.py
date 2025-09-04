import os
from filer import db
from filer.commands import analyse


def test_analyse_inserts_files(tmp_path):
    db_path = tmp_path / "analyse.sqlite3"
    conn = db.connect(str(db_path))
    rootdir = tmp_path / "r1"
    rootdir.mkdir()
    f = rootdir / "f.txt"
    f.write_text("hello")
    conn.execute("INSERT INTO roots (path,classification) VALUES (?,?)", (str(rootdir), "medium"))
    conn.commit()
    args = type("obj", (), {"db": str(db_path), "all_hashes": True})
    analyse.run(args)
    row = conn.execute("SELECT name FROM files").fetchone()
    assert row[0] == "f.txt"
    sha = conn.execute("SELECT sha256 FROM sha256").fetchone()
    assert sha is not None
