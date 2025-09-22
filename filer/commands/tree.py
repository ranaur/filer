import os
from typing import Dict, Any, List
from filer import db

def print_tree(node: Dict, prefix: str = '') -> None:
    """Print directory tree structure."""
    items = sorted(node.items())
    for i, (name, value) in enumerate(items):
        is_last = i == len(items) - 1
        print(f"{prefix}{'└── ' if is_last else '├── '}{name}")
        if isinstance(value, dict):
            new_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(value, new_prefix)

def build_tree(files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a directory tree structure from a list of files."""
    tree = {}
    for file in files:
        path_parts = file['path'].split(os.sep)
        current = tree
        for part in path_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[path_parts[-1]] = {}
    return tree

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

def run(args):
    conn = db.connect(args.db)
    cur = conn.cursor()
    
    # Query to get file details
    query = """
    SELECT 
        r.path as root_path, 
        d.name as dir_name, 
        f.name as file_name
    FROM files f
    JOIN directories d ON f.directory = d.id
    JOIN roots r ON d.root = r.id
    """
    params = []
    
    if args.root:
        query += " WHERE r.path = ?"
        params.append(os.path.abspath(args.root))
    
    query += " ORDER BY r.path, d.name, f.name"
    
    files = []
    for row in cur.execute(query, params):
        rel_path = os.path.join(row['dir_name'], row['file_name'])
        files.append({
            'path': rel_path,
        })
    
    tree = build_tree(files)
    print_tree(tree)
