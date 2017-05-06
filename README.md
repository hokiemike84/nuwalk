# tskwalk
An alternative to fiwalk that utilizes The Sleuth Kit to generate a DFXML for file information

## Usage
Tskwalk is a python script that operates off of a TSK sqlite database.  The database can be generated using tsk_loaddb.exe from The Sleuth Kit.
Tskwalk will query file data from the database to build a DFXML similar to those produced by fiwalk.

```
python tskwalk.py <path to tsk database file> <output xml file name>
```

