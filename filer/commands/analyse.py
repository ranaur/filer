import os
from filer import db, utils


def register_parser(subparsers):
    """Register the `analyse` subcommand.

    Usage:
      filer [--db database] analyse [--all-hashes]

    Analyse all files under registered roots. The analysis updates the database with file
    metadata and optionally calculates SHA-256 hashes for all files.

    The DB argument sets the database to use. Defaults to FILER_DB environment variable if none is given.
    """
    p = subparsers.add_parser("analyse", help="Analyse filesystem and update DB")
    p.add_argument("--db", default=os.environ.get("FILER_DB"))
    p.add_argument("--all-hashes", action="store_true", 
                  help="Calculate SHA-256 hashes for all files (can be slow)")
    p.set_defaults(func=run)


def run(args):
    if not args.db:
        print("Error: No database specified. Use --db option or set FILER_DB environment variable.")
        return 1
    
    if not os.path.exists(args.db):
        print(f"Error: Database '{args.db}' does not exist. Please create it first using 'filer new' command.")
        return 1

    try:
        conn = db.connect(args.db)
        cur = conn.cursor()
        
        # Initialize counters
        files_inserted = 0
        files_updated = 0
        files_deleted = 0
        files_skipped = 0
        
        # clear analysed flag
        cur.execute("""
            UPDATE files set analysed=0
            """)

        roots = cur.execute("SELECT id, path FROM roots").fetchall()
        if not roots:
            print("No root directories found. Add directories using 'filer root' command.")
            return 0

        # Process each root directory
        for root_id, root_path in roots:
            #print(f'ROOT: id = {root_id} path = {root_path}')
            if not os.path.exists(root_path):
                print(f"Warning: Root directory '{root_path}' does not exist, skipping...")
                continue
            
            dir_id = None
            for dirpath, dirnames, filenames in os.walk(root_path):
                dirlocalpath = os.path.relpath(dirpath, root_path)
                if dirlocalpath == '.':
                    dirlocalpath = ''
                #print(f'DIR: path = {dirpath}  dirnames = {dirnames} filenames = {filenames} dirlocalpath = {dirlocalpath}')

                # Find parent directory ID if it exists
                dir_id = db.get_directory_by_path(conn, root_id, dirlocalpath)
                #if dir_id is None:
                #   print(f"Warning: Directory '{dirlocalpath}' does not exist, skipping...")
                #   continue

                # insert subdirectories
                for dirname in dirnames:
                    db.upsert_directory(conn, root_id, os.path.basename(dirname), dir_id, os.path.join(dirlocalpath, dirname), "inherited")
                
                # Process files in the current directory
                for fname in filenames:
                    #print(f"FILE: name = {fname}")
                    fpath = os.path.join(dirpath, fname)
                    try:
                        st = utils.file_stat(fpath)
                    except FileNotFoundError:
                        continue
                        
                    # Update or insert file metadata
                    # Check if file exists and if any values have changed
                    existing = cur.execute("""
                        SELECT ctime, mtime, size, mode, uid, gid, inode, dev, nlink
                        FROM files WHERE name=? AND directory=?
                    """, (fname, dir_id)).fetchone()
                        
                    file_state = 0
                    if existing is None:
                        # File doesn't exist, insert it
                        cur.execute("""
                            INSERT INTO files 
                            (name, ctime, mtime, size, directory, mode, 
                             uid, gid, inode, dev, nlink, analysed)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                        """, (
                            fname, st['ctime'], st['mtime'], st['size'], dir_id,
                            st['mode'], st['uid'], st['gid'], st['inode'], st['dev'], st['nlink']
                        ))
                        file_state = 1 # inserted
                    else:
                        # Check if any values have changed
                        if (existing[0] != st['ctime'] or existing[1] != st['mtime'] or 
                            existing[2] != st['size'] or
                            existing[3] != st['mode'] or existing[4] != st['uid'] or
                            existing[5] != st['gid'] or existing[6] != st['inode'] or
                            existing[7] != st['dev'] or existing[8] != st['nlink']):
                            # Values have changed, update the record
                            cur.execute("""
                                UPDATE files SET 
                                    ctime=?, mtime=?, size=?, mode=?,
                                    uid=?, gid=?, inode=?, dev=?, nlink=?, analysed=1
                                WHERE name=? AND directory=?
                            """, (
                                st['ctime'], st['mtime'], st['size'], st['mode'],
                                st['uid'], st['gid'], st['inode'], st['dev'], st['nlink'],
                                fname, dir_id
                            ))
                            file_state = 2 # updated
                        else:
                            # Values are the same, just mark as analysed
                            cur.execute("""
                                UPDATE files SET analysed=1 WHERE name=? AND directory=?
                            """, (fname, dir_id))
                            file_state = 3 # analysed, but skipped
                   
                    # Calculate hash if requested
                    if args.all_hashes:
                        file_id = cur.execute(
                            "SELECT id FROM files WHERE name=? AND directory=?",
                            (fname, dir_id)
                        ).fetchone()[0]
                        
                        # Check if hash already exists
                        existing_hash = cur.execute(
                            "SELECT sha256 FROM sha256 WHERE file=?",
                            (file_id,)
                        ).fetchone()
                        
                        # TODO: compare the hash and update if different
                        if not existing_hash:
                            file_state = 2 # updated
                            sha = utils.file_sha256(fpath)
                            cur.execute(
                                "INSERT INTO sha256 (file, sha256, processed_at) VALUES (?, ?, ?)",
                                (file_id, sha, utils.now())
                            )
                    if file_state == 1:
                        files_inserted += 1
                    elif file_state == 2:
                        files_updated += 1
                    elif file_state == 3:
                        files_skipped += 1
        
        # Delete files that were not analysed (no longer exist on disk)
        deleted_files = cur.execute("""
            SELECT id, name, directory FROM files WHERE analysed = 0
        """).fetchall()
        
        for file_id, file_name, dir_id in deleted_files:
            # Delete associated hashes first due to foreign key constraint
            cur.execute("DELETE FROM sha256 WHERE file = ?", (file_id,))
            # Delete the file
            cur.execute("DELETE FROM files WHERE id = ?", (file_id,))
            files_deleted += 1
            #print(f"DELETED: {file_name} (ID: {file_id}) from directory ID {dir_id}")
        
        # Update the database timestamp
        db.touch_update(conn)
        conn.commit()
        
        # Print summary
        print("\nAnalysis complete!")
        print(f"Files inserted: {files_inserted}")
        print(f"Files updated:  {files_updated}")
        print(f"Files deleted:  {files_deleted}")
        
        return 0
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        conn.rollback()
        return 1
    finally:
        if 'conn' in locals():
            conn.close()
