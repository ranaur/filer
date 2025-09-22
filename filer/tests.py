import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Any, Tuple
from filer import db

def run_command(args: List[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    result=subprocess.run(
        ["filer"] + args,
        capture_output=True,
        text=True,
        **kwargs
    )
    assert result.returncode == 0
    return result

def newDatabase(database: str) -> None:
    """Create a new database and add it to environment variable."""
    result = run_command([ "new", str(database) ])
    assert result.returncode == 0
    os.environ["FILER_DB"] = str(database) + ".sqlite3"
    return

def queryOne(sql: str, params: Optional[tuple] = None) -> Any:
    """Execute a query and return a single result."""
    conn = db.connect(os.environ["FILER_DB"])
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    result = cursor.fetchone()
    assert len(result)
    return result[0]

def queryAll(sql: str, params: Optional[tuple] = None) -> List[Tuple]:
    """Execute a query and return all results."""
    conn = db.connect(os.environ["FILER_DB"])
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    return cursor.fetchall()

def execute(sql: str, params: Optional[tuple] = None) -> None:
    """Execute a SQL statement with parameters."""
    conn = db.connect(os.environ["FILER_DB"])
    conn.execute(sql, params or ())
    conn.commit()

def deleteDatabase() -> None:
    """Delete a database file."""
    try:
        os.remove(os.environ["FILER_DB"])
    except FileNotFoundError:
        pass
