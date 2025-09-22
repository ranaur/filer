import os
from filer import db


def register_parser(subparsers):
    """Register the `root` subcommand.

    Usage:
      filer [--db database] root [dir1 [...]]
      filer [--db database] root --list
      filer [--db database] root --delete [dir1 [...]]

    In the first form, adds the directories to an existing database, or the current directory if none is given.
    --list lists all registered directories from the database.
    --delete deletes the directories from the database.
    --classification sets the classification of the directories.

    The DB argument sets the database to use. Defaults to FILER_DB environment variable if none is given.
    """
    p = subparsers.add_parser("root", help="Manage root directories")
    p.add_argument("--db", default=os.environ.get("FILER_DB"))
    p.add_argument("--list", action="store_true")
    p.add_argument("--delete", action="store_true")
    p.add_argument("--classification", choices=["high","medium","low"], default="medium")
    p.add_argument("paths", nargs="*")
    p.set_defaults(func=run)

def run(args):
    if not args.db:
        print("Error: No database specified. Use --db option or set FILER_DB environment variable.")
        return 1
    
    if not os.path.exists(args.db):
        print(f"Error: Database '{args.db}' does not exist. Please create it first using 'filer new' command.")
        return 1
    
    conn = db.connect(args.db)
    cur = conn.cursor()
    if args.list:
        if args.paths:
            for path in args.paths:
                row = cur.execute("SELECT path FROM roots WHERE path=?", (os.path.abspath(path),)).fetchone()
                print(row['path'])
        else:
            for row in cur.execute("SELECT path FROM roots").fetchall():
                print(row['path'])
    elif args.delete:
        if not args.paths:
            print("Error: must specify directories to delete")
            return
        for path in args.paths:
            cur.execute("DELETE FROM roots WHERE path=?", (os.path.abspath(path),))
        conn.commit()
    else:
        for path in args.paths:
            full = os.path.abspath(path)
            if not os.path.isdir(full):
                print(f"Error: {full} not a directory")
                continue
            cur.execute("INSERT INTO roots (path,classification) VALUES (?,?) ON CONFLICT(path) DO UPDATE SET classification=excluded.classification", (full, args.classification))
        conn.commit()
