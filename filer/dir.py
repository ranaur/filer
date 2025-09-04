import os
from filer import db

def register_parser(subparsers):
    p = subparsers.add_parser("dir", help="Directory operations")
    sub = p.add_subparsers(dest="subcmd", required=True)

    listp = sub.add_parser("list", help="List classification")
    listp.add_argument("--db", required=True)
    listp.add_argument("path")
    listp.add_argument("-r", action="store_true")
    listp.set_defaults(func=run_list)

    setp = sub.add_parser("set", help="Set classification")
    setp.add_argument("--db", required=True)
    setp.add_argument("path")
    setp.add_argument("classification", choices=["excluded","high","medium","low","inherited"])
    setp.set_defaults(func=run_set)

    addp = sub.add_parser("add", help="Add new root directory")
    addp.add_argument("--db", required=True)
    addp.add_argument("path")
    addp.set_defaults(func=run_add)

    exclp = sub.add_parser("exclude", help="Exclude directory")
    exclp.add_argument("--db", required=True)
    exclp.add_argument("path")
    exclp.set_defaults(func=run_exclude)


def run_list(args):
    conn = db.connect(args.db)
    cur = conn.cursor()
    path = os.path.basename(args.path)
    row = cur.execute("SELECT classification FROM directories WHERE name=?", (path,)).fetchone()
    if row:
        print(f"{args.path}: {row[0]}")

def run_set(args):
    conn = db.connect(args.db)
    cur = conn.cursor()
    name = os.path.basename(args.path)
    cur.execute("INSERT OR REPLACE INTO directories (name,classification,analysed) VALUES (?,?,1)", (name,args.classification))
    conn.commit()

def run_add(args):
    conn = db.connect(args.db)
    cur = conn.cursor()
    path = os.path.abspath(args.path)
    row = cur.execute("SELECT id FROM roots WHERE path=?", (path,)).fetchone()
    if row:
        print("Error: already exists")
    else:
        cur.execute("INSERT INTO roots (path,classification) VALUES (?,?)", (path,"medium"))
        conn.commit()

def run_exclude(args):
    conn = db.connect(args.db)
    cur = conn.cursor()
    name = os.path.basename(args.path)
    cur.execute("UPDATE directories SET classification='excluded' WHERE name=?", (name,))
    conn.commit()
