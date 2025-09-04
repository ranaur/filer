import os
from filer import db
from filer.commands import dedup, analyse


def test_dedup_finds_duplicates(tmp_path, capsys):
    db_path = tmp_path / "dedup.sqlite3"
    conn = db.connect(str(db_path))
    rootdir = tmp_path / "root"
    rootdir.mkdir()
    f1 = rootdir / "a.txt"
    f2 = rootdir / "b.txt"
    f1.write_text("same")
    f2.write_text("same")
    conn.execute("INSERT INTO roots (path,classification) VALUES (?,?)", (str(rootdir), "medium"))
    conn.commit()
    args = type("obj", (), {"db": str(db_path), "all_hashes": True})
    analyse.run(args)
    args2 = type("obj", (), {"db": [str(db_path)]})
    dedup.run(args2)
    captured = capsys.readouterr()
    assert "Duplicates" in captured.out
