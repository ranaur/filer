from filer import tests


def test_root_add_and_list(tmp_path):
    database = tmp_path / "test_root_add_and_list"

    tests.newDatabase(database)

    d = tmp_path / "subdir"
    d.mkdir()
    
    result = tests.run_command([ "root", str(d)])
    assert result.returncode == 0
    
    result = tests.run_command([ "root", "--list"])
    assert result.returncode == 0
    assert result.stdout.strip() == str(d)

    tests.deleteDatabase()


def test_root_delete(tmp_path):
    database = tmp_path / "test_root_delete"

    tests.newDatabase(database)

    d = tmp_path / "subdir"
    d.mkdir()
    
    tests.run_command([ "root", d])
    tests.run_command([ "root", "--delete", d])

    row = tests.queryAll("SELECT * FROM roots")
    assert row == []

    tests.deleteDatabase()

def test_root_add_delete(tmp_path):
    database = tmp_path / "test_root_add_delete"
    tests.newDatabase(database)

    d = tmp_path / "subdir"
    d.mkdir()
    
    d2 = tmp_path / "subdir2"
    d2.mkdir()
    
    tests.run_command([ "root", str(d)])
    tests.run_command([ "root", str(d2)])
    tests.run_command([ "root", "--delete", str(d2)])

    row = tests.queryAll("SELECT * FROM roots")
    assert len(row) == 1

    result = tests.run_command([ "root", "--list"])
    assert result.returncode == 0
    assert result.stdout.strip() == str(d)

    tests.deleteDatabase()
