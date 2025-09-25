import os
from typing import Dict, Any, List
from filer import db

def walk_roots(cur, initial_state={}, start_root_cb = None, end_root_cb = None, start_directory_cb = None, end_directory_cb = None, file_cb = None):
    """Transverse directories in the database.
    
    start_directory_cb(state, dir_name) => callback that is called before any directory is processed
    end_directory_cb(state, dir_name) => callback that is called after any directory is processed
    file_cb(state, file_name) => callback that is called for each file
    state => state that is passed to the callbacks
    
    Traverse directories in the database.
    
    The function is a recursive function that traverses the directories in the database.
    For each directory, it calls the `start_directory_cb` function before traversing the subdirectories,
    and the `end_directory_cb` function after traversing the subdirectories.
    For each file, it calls the `file_cb` function.
    
    The `state` parameter is an optional parameter that is passed to the callbacks.
    It can be used to pass additional information to the callbacks.
    
    Example:
        def start_directory_cb(state, dir_name):
            print(f"Entering directory {dir_name}")
    
        def end_directory_cb(state, dir_name):
            print(f"Leaving directory {dir_name}")
    
        def file_cb(state, file_name):
            print(f"Found file {file_name}")
    
        traverse_directories(start_directory_cb, end_directory_cb, file_cb, state=["a", "b", "c"])
    
    This will traverse the directories in the database and call the callbacks for each directory and file.
    The `state` parameter is passed to the callbacks, and its value is `["a", "b", "c"]`.
    """
    
    cur.execute("""
    SELECT id, path, classification from roots
    """)
    root_dirs = cur.fetchall()
    
    for root in root_dirs:
        if start_root_cb is not None:
            start_root_cb(initial_state, root) 

        walk_directories(cur, initial_state, root["id"], None, start_directory_cb, end_directory_cb, file_cb)

        if end_root_cb is not None:
            end_root_cb(initial_state, root) 

def walk_directories(cur, state, root_id, directory_id = None, start_directory_cb = None, end_directory_cb = None, file_cb = None, depth = 1):
    if start_directory_cb is not None:
        start_directory_cb(state, directory_id, depth)

    cur.execute("""
    SELECT files.id id, directories.id directory_id, files.name name, classification, files.ctime, files.mtime, files.size, files.mode, files.uid, files.gid, files.inode, files.dev, files.nlink, "file" type
    FROM files 
    JOIN directories ON files.directory = directories.id
    WHERE files.directory is ? and roots.id is ?
    UNION ALL
    SELECT "", directories.id directory_id, directories.name name, directories.classification, "", "", "", "", "", "", "", "", "", "directory" type
    FROM directories WHERE parent is ? and roots.id is ?
    ORDER BY name""", (directory_id, root_id, directory_id, root_id))
    files = cur.fetchall()

    pos=1
    for file in files:
        if pos == len(files):
            state[depth]="last"
        else:
            state[depth]="not last"

        if file_cb is not None:     
            file_cb(state, file, depth)

        if file["type"] == "directory":
            _walk_directories(cur, start_directory_cb, end_directory_cb, file_cb, file["directory_id"], state, depth + 1)
        pos = pos + 1

    if end_directory_cb is not None:
        end_directory_cb(state, directory_id, depth)
    
    
def register_parser(subparsers):
    """Register the `tree` subcommand.

    Usage:
      filer tree [--root ROOT]

    Show directory tree structure of files in the database.
    """
    p = subparsers.add_parser("tree", help="Show directory tree structure")
    p.add_argument("--db", default=os.environ.get("FILER_DB"), help="Path to database file or use FILER_DB if omitted")
    p.add_argument("--root", help="Filter by root directory")
    p.set_defaults(func=run)


def tree_file_cb(state, file, depth):
    prefix = ""
    for level in range(1, depth):
        if state[level] == "last":
            prefix = prefix + " "
        else:
            prefix = prefix + "│"

        prefix = prefix + "   "
    if state[depth] == "last":
        prefix = prefix + "└── "
    else:
        prefix = prefix + "├── "

    if file["type"] == "directory":
        suffix="/"
    else:
        suffix=""

    print(f"{prefix}{file['name']}{suffix}")

def tree_start_root_cb(state, root):
    print(f"{root['path']}/")

def run(args):
    conn = db.connect(args.db)
    cur = conn.cursor()

    walk_roots(cur, start_root_cb=tree_start_root_cb, file_cb=tree_file_cb)