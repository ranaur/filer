## FILER.md

I want to develop a python command line app called filer that handle files. Is stores information about the file (creation, modify dates, size, permissions, owners, hases, etc.) in a sqllite database.

There are many subcommands to use in the app.

new => initialize a filebase (e.g. the sqllite file) normally in a local directory (~/.filer) giving it a name. The filebase is a sqllite file with the following tables:
	config => key/value pairs of strings that controls the setup. Initializing it should insert version/<version number>, creation date/<current date/time>, last update/<current date/time>
	roots => id (artificial key), full path name, default classsification (high, medium, low)
	directories => id (artificial key), dirname (only the name, not the path), parent directory (null if it was the first directory of this root), root (pointing to the roots table), classsification (excluded, high, medium, low, inherited), analysed (initialy false)
	files => id (artificial key), filename, creation date, modification date, access date, size, directory (id poiting to a record in directories table, where the tile is), and every other stat() funciotn information, analysed (initialy false).
	sha256 => file (primary key), sha256 value, processing date (current time of update/insertion)

root => add/update/delete/list the root directories to be handled by the filebase. 
	* if --list is passed, list all of the configured root directories, or if other parameters were passed, the directories passed after this parameter.
	* if --delete is passed, delete all direcectories passed after this parameter. If no diretory is passsed, shows an error message.
	* the default is to add (if the directory does not exist) or update (if exist) in the directories table. The directory must exist to be added.
	adds to "roots" table.
analyse => for each root in roots table, thansverse all its subdirectories, recording in the tables every directory in directories table and every file in files tables, with it's corresponding stat values. if there is some file or directory in the tables that does not exist anymore, remove from the table. If the stat changed, update to the new stat.
	* with --all-hashes => calculate sh256 of every file and record in the sha256 table
dir => can have the following subcomands
	* list => list classification of the dir (with -r lists all its subdirs)
	* set => change the classsification for the directory passed to the new classification (add if it does not exist)
	* add => add a new root directory (if it does not exist yet in the base). Logs an error message if there is a directory that is parent (of any level) or sibling (of any level)
	* exclude => change the classsification for the directory passed to excluded, warns if there is any subdir under with classification not "inherited" or "excluded"
check => checks for the integrity between the filebase and the directory.
	for every subdirectory of every root configured for the filebase:
		if the directory is the classification "excluded", ignore it.
		logs if the directory does not still exist anymore
		for every file in the directory:
			logs if the file exist in the filebase, but not in the directory (it was deleted)
			logs if the file exist in the directory, but not in the filebase  (it was new)
			if it exists in both the directory and the filebase:
				compare it's stat values: creation date, modification date, size, sha256. Logs if there is any mismatch
				if the filebase doesn't have a hash for this file log an error.
dedup (or deduplicate) => pass one or more filebases. If there is more than one database passed, treat all the files them as a single database for the following check:
	Group files with the same size:
		For every file with the same size, get it's sha256 hash:
			if some of the files has no hash, calculate it and save it to the sha256 database.
			show the group of files with the same size and hash to list the group, sorting by the classification (high, medium, low)
