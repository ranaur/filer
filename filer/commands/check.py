import os
from filer import db, utils

def register_parser(subparsers):
    p = subparsers.add_parser("check", help="Check integrity")
    p.add_argument("--db", required=True)
    p.set_defaults(func=run)

def run(args):
    conn = db.connect(args.db)
    cur = conn.cursor()
    roots = cur.execute("SELECT id,path FROM roots").fetchall()
    for root_id, root_path in roots:
        for dirpath, _, filenames in os.walk(root_path):
            dname = os.path.basename(dirpath)
            drow = cur.execute("SELECT id,classification FROM directories WHERE name=?", (dname,)).fetchone()
            if not drow:
                print(f"Missing dir in DB: {dirpath}")
                continue
            did, classification = drow
            if classification == "excluded":
                continue
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                row = cur.execute("SELECT id,ctime,mtime,size FROM files WHERE name=? AND directory=?", (fname,did)).fetchone()
                if not os.path.exists(fpath):
                    if row:
                        print(f"File deleted on disk: {fpath}")
                    continue
                if not row:
                    print(f"File new on disk: {fpath}")
                    continue
                st = utils.file_stat(fpath)
                fid, ctime, mtime, size = row
                if abs(ctime - st['ctime'])>1 or abs(mtime - st['mtime'])>1 or size!=st['size']:
                    print(f"Mismatch: {fpath}")
                hrow = cur.execute("SELECT sha256 FROM sha256 WHERE file=?", (fid,)).fetchone()
                if not hrow:
                    print(f"Missing hash: {fpath}")
