import os
from filer import db


def register_parser(subparsers):
    p = subparsers.add_parser("root", help="Manage root directories")
    p.add_argument("--db", required=True)
    p.add_argument("--list", action="store_true")
    p.add_argument("--delete", action="store_true")
    p.add_argument("--classification", choices=["high","medium","low"], default="medium")
    p.add_argument("paths", nargs="*")
    p.set_defaults(func=run)

def run(args):
    conn = db.connect(args.db)
    cur = conn.cursor()
    if args.list:
        if args.paths:
            for path in args.paths:
                row = cur.execute("SELECT * FROM roots WHERE path=?", (os.path.abspath(path),)).fetchone()
                print(row)
        else:
            for row in cur.execute("SELECT * FROM roots").fetchall():
                print(row)
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
