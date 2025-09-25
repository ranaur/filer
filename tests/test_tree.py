from filer import tests

def test_tree_displays_directory_structure(tmp_path):
    database = tmp_path / "test_tree_structure"

    # 1. Create a new database
    tests.newDatabase(database)

    # 2. Create a directory
    root_dir = tmp_path / "test_root"
    root_dir.mkdir()

    # 3. Create a subdirectory
    sub_dir = root_dir / "subdir"
    sub_dir.mkdir()

    # 4. Put different files in both directories
    (root_dir / "file1.txt").write_text("content1")
    (root_dir / "file2.py").write_text("print('hello')")
    (sub_dir / "file3.md").write_text("# Markdown")
    (sub_dir / "file4.json").write_text('{"key": "value"}')

    # 5. Add the directory as root
    tests.run_command(["root", str(root_dir)])

    # 6. Run analyse command
    tests.run_command(["analyse", "--all-hashes"])

    # 7. Run tree command and assert the output
    result = tests.run_command(["tree"])

    # Expected tree structure:
    # test_root/
    # ├── file1.txt
    # ├── file2.py
    # └── subdir/
    #     ├── file3.md
    #     └── file4.json

    expected_output = f"""├── file1.txt
├── file2.py
└── subdir
    ├── file3.md
    └── file4.json
"""

    assert result.stdout.strip() == expected_output.strip()

    tests.deleteDatabase()

def test_tree_displays_directory_structure2(tmp_path):
    database = tmp_path / "test_tree_structure"

    # 1. Create a new database
    tests.newDatabase(database)

    # 2. Create a directory
    root_dir = tmp_path / "test_root"
    root_dir.mkdir()

    # 3. Create two subdirectories
    sub_dir = root_dir / "subdir"
    sub_dir.mkdir()

    sub_dir2 = root_dir / "subdir2"
    sub_dir2.mkdir()

    # 4. Put different files in both directories
    (root_dir / "file1.txt").write_text("content1")
    (root_dir / "file2.py").write_text("print('hello')")
    (sub_dir / "file3.md").write_text("# Markdown")
    (sub_dir / "file4.json").write_text('{"key": "value"}')
    (sub_dir2 / "file5.md").write_text("# Markdown")
    (sub_dir2 / "file6.json").write_text('{"key": "value"}')

    # 5. Add the directory as root
    tests.run_command(["root", str(root_dir)])

    # 6. Run analyse command
    tests.run_command(["analyse", "--all-hashes"])

    # 7. Run tree command and assert the output
    result = tests.run_command(["tree"])

    # Expected tree structure:
    # test_root/
    # ├── file1.txt
    # ├── file2.py
    # └── subdir/
    #     ├── file3.md
    #     └── file4.json

    expected_output = f"""
├── file1.txt
├── file2.py
├── subdir
│   ├── file3.md
│   └── file4.json
└── subdir2
    ├── file5.md
    └── file6.json
"""

    assert result.stdout.strip() == expected_output.strip()

    tests.deleteDatabase()

