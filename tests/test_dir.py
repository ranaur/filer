import os
import subprocess

from filer import db


def test_dir_set_and_list(tmp_path, capsys):
    db_path = tmp_path / "dir.sqlite3"
    conn = db.connect(str(db_path))
    d = tmp_path / "sub"
    d.mkdir()
    conn.execute("INSERT INTO directories (name,root,classification,analysed) VALUES (?,?,?,1)", ("sub",1,"medium"))
    conn.commit()
    
    result = subprocess.run([
        "filer",
        "dir", "set", "--db", str(db_path),
        "--path", str(d), "--classification", "high"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
    row = conn.execute("SELECT classification FROM directories WHERE name=?", ("sub",)).fetchone()
    assert row[0] == "high"


def test_dir_exclude(tmp_path):
    db_path = tmp_path / "dir.sqlite3"
    conn = db.connect(str(db_path))
    d = tmp_path / "sub"
    d.mkdir()
    conn.execute("INSERT INTO directories (name,root,classification,analysed) VALUES (?,?,?,1)", ("sub",1,"medium"))
    conn.commit()
    
    result = subprocess.run([
        "filer",
        "dir", "exclude", "--db", str(db_path),
        "--path", str(d)
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
    row = conn.execute("SELECT classification FROM directories WHERE name=?", ("sub",)).fetchone()
    assert row[0] == "excluded"