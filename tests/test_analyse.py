from filer import tests


def test_analyse_inserts_files(tmp_path):
    database = str(tmp_path / "test_analyse_inserts_files")

    tests.newDatabase(database)

    # Create test directory and file
    root_path = tmp_path / "files"
    root_path.mkdir()
    (root_path / "f.txt").write_text("hello")
    
    # Add root and analyse
    tests.run_command(["root", str(root_path)])
    tests.run_command(["analyse", "--all-hashes"])
    
    # Check if file was added to the database
    file = tests.queryOne("SELECT name FROM files")
    assert "f.txt" == file
    
    # Check if hash was calculated
    hashes = tests.queryOne("SELECT sha256 FROM sha256 LIMIT 1")
    assert hashes == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    
    result = tests.run_command(["analyse", "--all-hashes"])
    result.stdout = """

Analysis complete!
Files inserted: 0
Files updated:  0
Files deleted:  0

"""
    
    (root_path / "f.txt").write_text("hello 2")
    
    result = tests.run_command(["analyse", "--all-hashes"])
    result.stdout = """

Analysis complete!
Files inserted: 0
Files updated:  1
Files deleted:  0

"""
    (root_path / "f1.txt").write_text("hello 1")
    
    result = tests.run_command(["analyse", "--all-hashes"])
    result.stdout = """

Analysis complete!
Files inserted: 1
Files updated:  0
Files deleted:  0

"""
    
    (root_path / "f1.txt").unlink()
    result = tests.run_command(["analyse", "--all-hashes"])
    result.stdout = """

Analysis complete!
Files inserted: 0
Files updated:  0
Files deleted:  1

"""
    
    result = tests.run_command(["analyse", "--all-hashes"])
    result.stdout = """

Analysis complete!
Files inserted: 0
Files updated:  0
Files deleted:  0

"""
    tests.deleteDatabase()

# test with two roots