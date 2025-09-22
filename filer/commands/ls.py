import os
import stat
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

# For UID/GID to name mapping
try:
    import pwd
    import grp
except ImportError:
    # Windows doesn't have pwd/grp modules
    pwd = None
    grp = None

from filer import db

# TODO: add ls --long -l compatible output, showing all file attributes
# TODO: add --hash option, showing the hash value
# TODO: add --fullpath option, showing the full path

def format_mode(st_mode: int) -> str:
    """Convert file mode to a string like 'drwxr-xr-x'."""
    mode = []
    # File type
    if stat.S_ISDIR(st_mode):
        mode.append('d')
    elif stat.S_ISLNK(st_mode):
        mode.append('l')
    else:
        mode.append('-')
    # Permissions
    for who in 'USR', 'GRP', 'OTH':
        for what in 'R', 'W', 'X':
            if st_mode & getattr(stat, f'S_I{what}{who}'):
                mode.append(what.lower())
            else:
                mode.append('-')
    return ''.join(mode)

def format_size(size: int) -> str:
    return f"{size}"

def format_sizeOld(size: int) -> str:
    """Format file size in human readable format."""
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if size < 1024:
            return f"{size:>4}{unit}"
        size /= 1024.0
    return f"{size:.1f}P"

def format_mtime(mtime: float) -> str:
    """Format modification time like 'Dec 12 15:30'."""
    dt = datetime.fromtimestamp(mtime)
    now = datetime.now()
    if dt.year == now.year:
        return dt.strftime('%b %d %H:%M')
    return dt.strftime('%b %d  %Y')

def get_username(uid: int) -> str:
    """Get username from UID."""
    if pwd is None or uid is None:
        return str(uid) if uid is not None else '?'
    try:
        return pwd.getpwuid(uid).pw_name
    except (KeyError, TypeError):
        return str(uid)

def get_groupname(gid: int) -> str:
    """Get group name from GID."""
    if grp is None or gid is None:
        return str(gid) if gid is not None else '?'
    try:
        return grp.getgrgid(gid).gr_name
    except (KeyError, TypeError):
        return str(gid)

def register_parser(subparsers):
    """Register the `ls` subcommand.

    Usage:
      filer ls [--long/-l] [--hash] [--fullpath]

    List all files stored in the database.

    --long/-l shows a long listing format, like ls -l
    --hash shows the hash value of the files
    --fullpath shows the full path of the files

    The DB argument sets the database to use. Defaults to FILER_DB environment variable if none is given.
    """
    p = subparsers.add_parser("ls", help="List files in the database")
    p.add_argument("--db", default=os.environ.get("FILER_DB"), help="Path to database file or use FILER_DB if ommited")
    p.add_argument("--root", help="Filter by root directory")
    p.add_argument("-l", "--long", action="store_true", help="Use a long listing format")
    p.add_argument("--hash", action="store_true", help="Show hash values")
    p.add_argument("--fullpath", action="store_true", help="Show full paths")
    p.set_defaults(func=run)

def run(args):
    conn = db.connect(args.db)
    cur = conn.cursor()
    
    # Query to get file details including size, mtime, and mode
    query = """
    SELECT 
        r.path as root_path, 
        d.name as dir_name, 
        f.name as file_name,
        f.size as file_size,
        f.mtime as mtime,
        f.mode as mode,
        f.uid as uid,
        f.gid as gid,
        f.nlink as nlink,
        s.sha256 as file_hash
    FROM files f
    JOIN directories d ON f.directory = d.id
    JOIN roots r ON d.root = r.id
    LEFT OUTER JOIN sha256 s ON f.id = s.file
    """
    params = []
    
    if args.root:
        query += " WHERE r.path = ?"
        params.append(os.path.abspath(args.root))
    
    query += " ORDER BY r.path, d.name, f.name"
    
    files = []
    for row in cur.execute(query, params):
        full_path = os.path.join(row['root_path'], row['dir_name'], row['file_name'])
        rel_path = os.path.join(row['dir_name'], row['file_name'])
        
        files.append({
            'root': row['root_path'],
            'dir': row['dir_name'],
            'name': row['file_name'],
            'path': rel_path,
            'fullpath': full_path,
            'size': row['file_size'],
            'mtime': row['mtime'],
            'mode': row['mode'],
            'uid': row['uid'],
            'gid': row['gid'],
            'nlink': row['nlink'],
            'hash': row['file_hash']
        })
    
    # Sort files by path
    files.sort(key=lambda x: x['path'])
    
    for file in files:
        if args.long:
            mode = format_mode(file['mode']) if file['mode'] is not None else '?' * 10
            nlink = str(file['nlink']) if file['nlink'] is not None else '?'
            size = format_size(file['size']) if file['size'] is not None else '?'
            mtime = format_mtime(file['mtime']) if file['mtime'] else '?'
            username = get_username(file['uid'])
            groupname = get_groupname(file['gid'])
            
            path = file['fullpath'] if args.fullpath else file['path']
            hash_str = f"  {file['hash']}" if args.hash and file['hash'] else ""
            
            print(f"{mode} {nlink:>3} {username:<8} {groupname:<8} {size:>8} {mtime} {path}{hash_str}")
        else:
            path = file['fullpath'] if args.fullpath else file['path']
            hash_str = f"  {file['hash']}" if args.hash and file['hash'] else ""
            print(f"{path}{hash_str}")
