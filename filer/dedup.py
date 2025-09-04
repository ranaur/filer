from filer import db, utils

def register_parser(subparsers):
    p = subparsers.add_parser("dedup", help="Find duplicates")
    p.add_argument("--db", nargs="+", required=True)
    p.set_defaults(func=run)

def run(args):
    conns = [db.connect(path) for path in args.db]
    files = []
    for conn in conns:
        cur = conn.cursor()
        rows = cur.execute("SELECT f.id,f.name,f.size,f.directory,d.classification FROM files f JOIN directories d ON f.directory=d.id").fetchall()
        for r in rows:
            files.append(r)
    groups = {}
    for fid,fname,size,dirid,classif in files:
        groups.setdefault(size,[]).append((fid,fname,classif))
    for size,g in groups.items():
        if len(g)>1:
            hashes = {}
            for fid,fname,classif in g:
                for conn in conns:
                    cur = conn.cursor()
                    hrow = cur.execute("SELECT sha256 FROM sha256 WHERE file=?", (fid,)).fetchone()
                    if hrow:
                        sha = hrow[0]
                    else:
                        sha = None
                if not sha:
                    continue
                hashes.setdefault(sha,[]).append((fname,classif))
            for sha,flist in hashes.items():
                if len(flist)>1:
                    print(f"Duplicates size={size} sha={sha}:")
                    for f,c in sorted(flist,key=lambda x: x[1]):
                        print(f"  {f} ({c})")
