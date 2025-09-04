Awesome project. I dropped a full working filer.py into the canvas with:

SQLite schema (config, roots, directories, files, sha256) + indices

Subcommands: new, root (list/add/update/delete), analyse (optional --all-hashes), dir (list/set/add/exclude), check, and dedup

Cross-platform stat capture (ctime/mtime/size/mode/uid/gid/inode/dev/nlink), safe hashing, incremental scans, and cleanup of deleted entries

Dedup across one or more databases, grouped by size then sha256, sorted by classification

Here’s how to use it:

Create a filebase

python filer.py new myfiles            # creates ~/.filer/myfiles.sqlite3


Add/list roots

python filer.py root --db ~/.filer/myfiles.sqlite3 --list
python filer.py root --db ~/.filer/myfiles.sqlite3 ~/Documents ~/Pictures
python filer.py root --db ~/.filer/myfiles.sqlite3 --classification high ~/Documents
python filer.py root --db ~/.filer/myfiles.sqlite3 --delete ~/Pictures


Scan filesystem into DB

python filer.py analyse --db ~/.filer/myfiles.sqlite3
python filer.py analyse --db ~/.filer/myfiles.sqlite3 --all-hashes


Directory tools

# show classification (use -r to recurse)
python filer.py dir --db ~/.filer/myfiles.sqlite3 list ~/Documents -r

# set/override classification
python filer.py dir --db ~/.filer/myfiles.sqlite3 set ~/Documents/Work high

# add a new root with conflict checks
python filer.py dir --db ~/.filer/myfiles.sqlite3 add ~/Videos

# exclude a directory
python filer.py dir --db ~/.filer/myfiles.sqlite3 exclude ~/Downloads/tmp


Integrity check

python filer.py check --db ~/.filer/myfiles.sqlite3


Deduplicate (one or many DBs)

python filer.py dedup --db ~/.filer/myfiles.sqlite3
python filer.py dedup --db ~/.filer/myfiles.sqlite3 ~/.filer/other.sqlite3


Notes & assumptions:

“Creation time” uses st_birthtime if available; otherwise falls back to st_ctime (inode change time on Unix).

Owner/group fields are best-effort on Windows.

The script avoids third-party dependencies and uses WAL mode for decent concurrency.

analyse is idempotent: it flips an analysed flag during the walk and removes anything not seen (deleted on disk).

If you want, I can split this into a tiny package with tests and a pyproject.toml, or add multi-threaded hashing for a big speed-up.