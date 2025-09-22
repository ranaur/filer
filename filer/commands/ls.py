import os
from filer import db

# TODO: add ls --long -l compatible output, shoing all file attributes
# TODO: add --hash option, shoying the hash value
# TODO: add --fullpath option, showing the full path
# TODO: add --tree option to show directory tree with files

def register_parser(subparsers):
    """Register the `ls` subcommand.

    Usage:
      filer ls [--long/-l] [--hash] [--fullpath] [--tree]

    List all files stored in the database.

    --long/-l shows a long listing format, like ls -l
    --hash shows the hash value of the files
    --fullpath shows the full path of the files
    --tree shows the directory tree with files

    The DB argument sets the database to use. Defaults to FILER_DB environment variable if none is given.
    """
    p = subparsers.add_parser("ls", help="List files in the database")
    p.add_argument("--db", required=True, help="Path to the database file")
    p.add_argument("--root", help="Filter by root directory")
    p.set_defaults(func=run)


def run(args):
    conn = db.connect(args.db)
    cur = conn.cursor()
    
    query = """
    SELECT r.path as root_path, d.name as dir_name, f.name as file_name
    FROM files f
    JOIN directories d ON f.directory = d.id
    JOIN roots r ON d.root = r.id
    """
    params = []
    
    if args.root or args.directory:
        conditions = []
        if args.root:
            conditions.append("r.path = ?")
            params.append(os.path.abspath(args.root))
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY r.path, d.name, f.name"
    
    for row in cur.execute(query, params):
        # Construct full path relative to root
        rel_path = os.path.join(
            #os.path.basename(row['root_path']),
            row['dir_name'],
            row['file_name']
        )
        print(rel_path)
