from __future__ import annotations

from filer import db
import os


def register_parser(subparsers):
    """Register the `new` subcommand.

    Usage:
      filer new NAME [--dir /path/to/store]

    Creates a SQLite filebase named `NAME.sqlite3` inside the given directory
    If the DB already exists gives an error.
    """
    p = subparsers.add_parser("new", help="Initialize a new filebase (SQLite DB)")
    p.add_argument("name", help="Name for the filebase (no extension)")
    p.set_defaults(func=run)


def run(args):
    db_path = f"{args.name}.sqlite3"

    if os.path.exists(db_path):
        print(f"Error: {db_path} already exists")
        return 1

    # Connect will create and initialize schema on first use
    conn = db.connect(str(db_path))

    # Ensure config timestamps are up-to-date
    db.touch_update(conn)

    print(f"Initialized filebase at {db_path}")

    return 0