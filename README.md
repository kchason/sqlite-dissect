# DC3 SQLite Dissect

#### Version 0.0.6

usage:<br>

    sqlite_dissect [-h] [-v] [-d OUTPUT_DIRECTORY] [-p FILE_PREFIX]
                   [-e EXPORT_TYPE] [-n | -w WAL | -j ROLLBACK_JOURNAL] [-r | EXEMPTED_TABLES]
                   [-s | -t] [-g] [-c] [-f] [-k] [-l LOG_LEVEL] [-i LOG_FILE] [--warnings]
                   SQLITE_FILE`

SQLite Dissect is a SQLite parser with recovery abilities over SQLite databases
and their accompanying journal files. If no options are set other than the file
name, the default behaviour will be to check for any journal files and print to
the console the output of the SQLite files.  The directory of the SQLite file
specified will be searched through to find the associated journal files.  If 
they are not in the same directory as the specified file, they will not be found
and their location will need to be specified in the command.  SQLite carving
will not be done by default.  Please see the options below to enable carving.

#### positional arguments:

SQLITE_FILE
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;
The SQLite database file
<br><br>

#### optional arguments:

-h, --help
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
show this help message and exit
<br>

-v, --version
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
display the version of SQLite Dissect
<br>

-d OUTPUT_DIRECTORY, --directory OUTPUT_DIRECTORY
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
directory to write output to (must be specified for outputs other than console text)
<br>

-p FILE_PREFIX, --file-prefix FILE_PREFIX
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
the file prefix to use on output files, default is the name of the SQLite file
(the directory for output must be specified)
<br>

-e EXPORT_TYPE, --export EXPORT_TYPE
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
the format to export to {text, csv, sqlite, xlsx}
(text written to console if -d is not specified)
<br>

-n, --no-journal
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
turn off automatic detection of journal files
<br>

-w WAL, --wal WAL
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
the WAL file to use instead of searching the SQLite file directory by default
<br>

-j ROLLBACK_JOURNAL, --rollback-journal ROLLBACK_JOURNAL
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
the rollback journal file to use instead of searching the SQLite file directory by default
(under development, currently only outputs to csv, output directory needs to be specified)
<br>

-r EXEMPTED_TABLES, --exempted-tables EXEMPTED_TABLES
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
comma-delimited string of tables \[table1,table2,table3\] to exempt 
(only implemented and allowed for rollback journal parsing currently) ex.) table1,table2,table3
<br>

-s, --schema
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
output the schema to console, the initial schema found in the main database file
<br>

-t, --schema-history
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
output the schema history to console, prints the --schema information and write-head log changes
<br>

-g, --signatures
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
output the signatures generated to console
<br>

-c, --carve
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
carves and recovers table data
<br>

-f, --carve-freelists
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
carves freelist pages (carving must be enabled, under development)
<br>

-b TABLES, --tables TABLES
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
specified comma-delimited string of tables \[table1,table2,table3\] to carve
ex.) table1,table2,table3
<br>

-k, --disable-strict-format-checking
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
disable strict format checks for SQLite databases
(this may result in improperly parsed SQLite files)
<br>

-l LOG_LEVEL, --log-level LOG_LEVEL
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
level to log messages at {critical, error, warning, info, debug, off}
<br>

-i LOG_FILE, --log-file LOG_FILE
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
log file to write too, default is to write to console, ignored 
if log level set to off (appends if file already exists)
<br>

--warnings
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
enable runtime warnings
<br><br>

### Example Usage:

1. Print the version:


    sqlite_dissect --version

2. Parse a SQLite database and print the outputs to the screen:


    sqlite_dissect [SQLITE_FILE]


3. Parse a SQLite database and print schema history to a SQLite output file:


    sqlite_dissect [SQLITE_FILE] --schema-history -d [OUTPUT_DIRECTORY] -e sqlite

4. Parse a SQLite database and print the output to a SQLite file along with printing signatures and carving entries:


    sqlite_dissect [SQLITE_FILE] --signatures -d [OUTPUT_DIRECTORY] -e sqlite --carve

5. Parse a SQLite database and print the output to a SQLite file and carving entries, including freelists, for specific tables:


    sqlite_dissect [SQLITE_FILE] -d [OUTPUT_DIRECTORY] -e sqlite --carve --carve-freelists -b [TABLES]

6. Parse a SQLite database file and print the output to a xlsx workbook along with generating signatures and 
   carving entries.  The schema history (schema updates throughout the WAL included if a WAL file detected) and 
   signatures will be printed to standard output.  The log level will be set to debug and all log messages will be
   output to the specified log file.


    sqlite_dissect [SQLITE_FILE] -d [OUTPUT_DIRECTORY] -e xlsx --schema-history --carve --signatures --log-level debug -i [LOG_FILE]

7. Parse a SQLite database file along with a specified rollback journal file and send the output to CSV files.  
   (CSV is the only output option currently implemented for rollback journal files.)
   

    sqlite_dissect [SQLITE_FILE] -d [OUTPUT_DIRECTORY] -e csv --carve -j [ROLLBACK_JOURNAL]

### Description

This application focuses on carving by analyzing the allocated content within each of the SQLite
database tables and creating signatures.  Where there is no content in the table, the signature
is based off of analyzing the create table statement in the master schema table.  The signature
contains the series of possible serial types that can be stored within the file for that table.  
This signature is then applied to the unallocated content and freeblocks of the table b-tree in
the file.  This includes both interior and leaf table b-tree pages for that table.  The signatures 
are only applied to the pages belonging to the particular b-tree page it was generated from due
to initial research showing that the pages when created or pulled from the freelist set are
overwritten with zeros for the unallocated portions.  Fragments within the pages can be reported
on but due to the size (<4 bytes), are not carved.  Due to the fact that entries are added into
tables in SQLite from the end of the page and moving toward the beginning, the carving works
in the same manner in order to detect previously partial overwritten entries better.  This 
carving can also be applied to the set of freelist pages within the SQLite file if specified
but the freelist pages are treated as sets of unallocated data currently with the exception 
of the freelist page metadata.

The carving process does not currently account for index b-trees as the more pertinent information
is included in the table b-trees.  Additionally, there are some table b-trees that are not currently
supported.  This includes tables that are "without row_id", virtual, or internal schema objects.
These are unique cases which are slightly more rare use cases or don't offer as much as the
main tables do.  By default all tables will be carved if they do not fall into one of these cases.
You can send in a specific list of tables to be carved.

This application is written in the hopes that many of these use cases can be addressed in the future
and is scalable to those use cases.  Although one specific type of signature is preferred by default
in the application, SQLite Dissect generates multiple versions of a signature and can eventually
support carving by specifying other signatures or providing your own.  Since SQLite Dissect generates
the signature based off of existing data within the SQLite files automatically there is no need to
supply SQLite Dissect a signature for a particular schema or application.  This could be implemented
though to allow possibly more specific/targeted carving of SQLite files through this application.

Journal carving is supported primarily for WAL files.  If a WAL file is found, this application will
parse through each of the commit records in sequence and assign a version to them.  This is the same
as timelining that some applications use to explain this.  Rollback journals are treated as a full
unallocated block currently and only support export to csv files.

SQLite Dissect can support output to various forms: text, csv, xlsx, and sqlite.  Due to certain
constraints on what can be written to some file types, certain modifications need to be made.  For
instance, when writing SQLite columns such as row_id that are already going to pre-exist in the table
for export to a SQLite file.  In cases like these, we need to preface the columns with "sd_" so
they will not conflict with the actual row_id column.  This also applies to internal schema objects, 
so if certain SQLite tables are requested to be written to a SQLite file, than these will be prefaced
with a "iso_" so they will not conflict with similar internal schema objects that may already exist
in the SQLite file bring written to.  In xlsx or csv, due to a "=" symbol indicating a type of equation,
these are prefaced with a " " character to avoid this issue.  More details can be found in the
code documentation of the export classes themselves.

SQLite Dissect opens the file as read only and acts as a read only interpreter when parsing and carving
the SQLite file.  This is to ensure no changes are made to the files being analyzed.  The only use
of the sqlite3 libraries in python are to write the output to a SQLite file if that option is
specified for output.

#### Additional Notes:
1. SQLite Dissect currently only works on a SQLite database or a SQLite database along with a journal
   (WAL or rollback) file.  Journal files by themselves are not supported yet.

#### Currently not implemented:
1. Signatures and carving are not implemented for "without rowid" tables or indexes.  This will not cause an error 
   but will skip signature generation and carving processes.
2. Signatures and carving are not implemented for virtual tables.  This will not cause an error but will skip 
   signature generation and carving processes.  `Note:  Even though virtual tables are skipped, virtual tables may 
   create other non-virtual tables which are not skipped.  Currently nothing ties back these tables back to the 
   virtual table that created them.`
3. Invalidated frames in WAL files are currently skipped and not parsed.  `Note:  This applies to previous WAL records
   that were previously written to the SQLite database.`
4. Signatures generated are only reflective of the base/initial schema in the SQLite database.

#### Known issues and errors:
1. A use case may occur on generating a very small signature due to a table with very few columns resulting in many 
   false positives and longer parsing time.
2. Due to current handling queuing of data objects to be printed in addition to #1 above, a memory issue may occur with
   carving some tables.

#### Future implementation:
1. Export binary objects to separate files during export instead of being written to text files.
2. Print out sets of data that were unallocated or in freeblocks that did not have successful carvings.
3. Fix issues with schemas with comments.
4. Handle "altered column" table signatures where detected.
5. Implement handling of invalidated WAL frames.
6. The ability to de-dupe carved entries to those in allocated space (in cases such as those where the b-tree was migrated).

# Library Scripts

High level scripts that are used to access the rest of the library from and provide the base application for executing
SQLite Dissect when built.

- api_usage.py
- example.py
- setup.py
- sqlite_dissect.py

<br>

### api_usage.py

This script shows an example of the api usage for a specific test file.

TODO:
- [ ] Documentation improvements.

<br>

### example.py

This script shows examples of how this library can be used.

TODO:
- [ ] Documentation improvements.
- [ ] Implement additional export methods.

<br>

### setup.py

This script will be used to setup the sqlite_dissect package for use in python environments.

>Note:  To compile a distribution for the project run "python setup.py sdist" in the directory this file is located in.

>Note: openpyxl is needed for the xlsx export and will install jdcal, et-xmlfile \["openpyxl>=2.4.0b1"\]

>Note: PyInstaller is used for generation of executables but not included in this setup.py script and will
>      install altgraph, dis3, macholib, pefile, pypiwin32, pywin32 as dependencies. \[pyinstaller==3.6 needs to be used
>      for Python 2.7 since the newer versions of PyInstaller of 4.0+ require Python 3.6\]  Information on how to run
>      PyInstaller is included in the spec files under the pyinstaller directory.  Four files are here, two for windows
>      and two for linux, both for x64 platforms.  The two different files for each allow you to build it as one single
>      file or a directory of decompressed files.  Since the one file extracts to a temp directory in order to run, on
>      some systems this may be blocked and therefore the directory of files is preferred.

<br>

### sqlite_dissect.py

This script will act as the command line script to run this library as a stand-alone application.

TODO:
- [ ] Documentation improvements.
- [ ] Implement append, overwrite, etc. options for the log file if specified.
- [ ] Incorporate signature generation input and output files once implemented.
- [ ] Incorporate "store in memory" arguments (currently set to False, more in depth operations may want it True).
- [ ] Support for multiple export types simultaneously.
- [ ] Implement multiple passes/depths.
- [ ] Update string comparisons.
- [ ] Test use cases for exempted tables with rollback journal and when combined with specified tables.  
- [ ] Check on name vs table_name properties of the master schema entry.  
- [ ] Test cases where the schema changes throughout the WAL file.
- [ ] Investigate handling of virtual and "without rowid" tables when creating table signatures through the interface.
- [ ] Documentation on "without rowid" tables and indexes in references to carving in help documentation.
- [ ] Make sure to address/print unallocated space (especially uncarved) from updated page numbers in commit records.
- [ ] Research if there can be journal files with a zero length database file or zero-length journal files.
- [ ] Research if there can be combinations and of multiple rollback journal and WAL files with the SQLite database.
- [ ] Validate initial research that allocation of freelist pages to a b-tree results in a wipe of the page data.
- [ ] Add additional logging messages to the master schema entries skipped in signature generation. 
- [ ] Integrate in the SQLite Forensic Corpus into tests.
- [ ] Look into updating terminology for versioning to timelining.
- [ ] Update code for compatibility with Python 3.
- [ ] Create a pip distribution.  
- [ ] Create PyUnit tests.
- [ ] Create a GUI.