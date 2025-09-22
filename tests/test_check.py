from pathlib import Path
import pytest
from filer import tests


def test_check_detects_missing_file(tmp_path):
    # Setup
    database = "test_check"
    tests.newDatabase(database)
    
    # Create test environment
    test_path, root_id = tests.create_test_environment(database, tmp_path, "test_check")
    
    # Create a test file
    test_file = test_path / "f.txt"
    test_file.write_text("data")
    
    
    # Delete the file to simulate it going missing
    test_file.unlink()
    
    # Run check command
    result = tests.run_command(["check", "--db", database])
    
    # Verify
    assert result.returncode == 0
    assert "File deleted" in result.stdout
    
    # Cleanup
    tests.deleteDatabase(database)
