from __future__ import annotations

import os
from pathlib import Path
from filer import db


def register_parser(subparsers):
    """Register the `new` subcommand.

    Usage:
      filer new NAME [--dir /path/to/store]

    Creates a SQLite filebase named `NAME.sqlite3` inside the given directory
    (defaults to ~/.filer). If the DB already exists it will be opened.
    """
    p = subparsers.add_parser("new", help="Initialize a new filebase (SQLite DB)")
    p.add_argument("name", help="Name for the filebase (no extension)")
    p.add_argument("--dir", default=None, help="Directory to store DB (default: ~/.filer)")
    p.set_defaults(func=run)


def run(args):
    base_dir = Path(args.dir) if args.dir else Path.home() / ".filer"
    base_dir.mkdir(parents=True, exist_ok=True)

    db_path = base_dir / f"{args.name}.sqlite3"

    # Connect will create and initialize schema on first use
    conn = db.connect(str(db_path))

    # Ensure config timestamps are up-to-date
    db.touch_update(conn)

    print(f"Initialized filebase at {db_path}")
