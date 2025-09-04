import os
from filer import db
from filer.commands import dir


def test_dir_set_and_list(tmp_path, capsys):
    db_path = tmp_path / "dir.sqlite3"
    conn = db.connect(str(db_path))
    d = tmp_path / "sub"
    d.mkdir()
    conn.execute("INSERT INTO directories (name,root,classification,analysed) VALUES (?,?,?,1)", ("sub",1,"medium"))
    conn.commit()
    args = type("obj", (), {"db": str(db_path), "path": str(d), "classification": "high"})
    dir.run_set(args)
    row = conn.execute("SELECT classification FROM directories WHERE name=?", ("sub",)).fetchone()
    assert row[0] == "high"


def test_dir_exclude(tmp_path):
    db_path = tmp_path / "dir.sqlite3"
    conn = db.connect(str(db_path))
    d = tmp_path / "sub"
    d.mkdir()
    conn.execute("INSERT INTO directories (name,root,classification,analysed) VALUES (?,?,?,1)", ("sub",1,"medium"))
    conn.commit()
    args = type("obj", (), {"db": str(db_path), "path": str(d)})
    dir.run_exclude(args)
    row = conn.execute("SELECT classification FROM directories WHERE name=?", ("sub",)).fetchone()
    assert row[0] == "excluded"