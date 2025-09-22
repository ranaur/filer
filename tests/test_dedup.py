import os
import subprocess
import sys
from filer import db


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
    
    # First run analyse to populate the database
    result1 = subprocess.run([
        "filer",
        "analyse", "--db", str(db_path), "--all-hashes"
    ], capture_output=True, text=True)
    assert result1.returncode == 0
    
    # Then run dedup to find duplicates
    result2 = subprocess.run([
        "filer.cli",
        "dedup", str(db_path)
    ], capture_output=True, text=True)
    
    assert result2.returncode == 0
    assert "Duplicates" in result2.stdout
