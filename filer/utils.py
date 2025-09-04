import hashlib
import os
import time

def file_sha256(path, chunk_size=8192):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def file_stat(path):
    st = os.stat(path, follow_symlinks=False)
    return {
        "ctime": getattr(st, "st_birthtime", st.st_ctime),
        "mtime": st.st_mtime,
        "atime": st.st_atime,
        "size": st.st_size,
        "mode": st.st_mode,
        "uid": getattr(st, "st_uid", 0),
        "gid": getattr(st, "st_gid", 0),
        "inode": getattr(st, "st_ino", 0),
        "dev": getattr(st, "st_dev", 0),
        "nlink": getattr(st, "st_nlink", 1)
    }

def now():
    return time.time()
