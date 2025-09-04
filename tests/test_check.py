import os
from filer import db
from filer.commands import check


def test_check_detects_missing_file(tmp_path, capsys):
    db_path = tmp_path / "check.sqlite3"
    conn = db.connect(str(db_path))
    rootdir = tmp_path / "root"
    rootdir.mkdir()
    f = rootdir / "f.txt"
    f.write_text("data")
    conn.execute("INSERT INTO roots (path,classification) VALUES (?,?)", (str(rootdir), "medium"))
    conn.execute("INSERT INTO directories (name,root,classification,analysed) VALUES (?,?,?,1)", ("root",1,"medium"))
    conn.execute("INSERT INTO files (name,ctime,mtime,atime,size,directory,mode,uid,gid,inode,dev,nlink,analysed) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1)", ("f.txt",1,1,1,4,1,0,0,0,0,0,0,1))
    conn.commit()
    f.unlink()
    args = type("obj", (), {"db": str(db_path)})
    check.run(args)
    captured = capsys.readouterr()
    assert "File deleted" in captured.out
