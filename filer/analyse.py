import os
from filer import db, utils

def register_parser(subparsers):
    p = subparsers.add_parser("analyse", help="Analyse filesystem and update DB")
    p.add_argument("--db", required=True)
    p.add_argument("--all-hashes", action="store_true")
    p.set_defaults(func=run)

def run(args):
    conn = db.connect(args.db)
    cur = conn.cursor()
    roots = cur.execute("SELECT id,path FROM roots").fetchall()
    for root_id, root_path in roots:
        for dirpath, dirnames, filenames in os.walk(root_path):
            dirname = os.path.basename(dirpath)
            parent = os.path.dirname(dirpath)
            parent_id = None
            if parent and parent != dirpath:
                row = cur.execute("SELECT id FROM directories WHERE name=?", (os.path.basename(parent),)).fetchone()
                if row:
                    parent_id = row[0]
            cur.execute("INSERT OR IGNORE INTO directories (name,parent,root,classification,analysed) VALUES (?,?,?,?,1)", (dirname,parent_id,root_id,"inherited"))
            dir_id = cur.execute("SELECT id FROM directories WHERE name=? AND root=?", (dirname,root_id)).fetchone()[0]
            # files
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                try:
                    st = utils.file_stat(fpath)
                except FileNotFoundError:
                    continue
                cur.execute("INSERT OR REPLACE INTO files (name,ctime,mtime,atime,size,directory,mode,uid,gid,inode,dev,nlink,analysed) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1)",
                    (fname,st['ctime'],st['mtime'],st['atime'],st['size'],dir_id,st['mode'],st['uid'],st['gid'],st['inode'],st['dev'],st['nlink']))
                fid = cur.execute("SELECT id FROM files WHERE name=? AND directory=?", (fname,dir_id)).fetchone()[0]
                if args.all_hashes:
                    sha = utils.file_sha256(fpath)
                    cur.execute("INSERT OR REPLACE INTO sha256 (file,sha256,processed) VALUES (?,?,?)", (fid,sha,utils.now()))
    conn.commit()
