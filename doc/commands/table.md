# Table

1. [create](#create)
2. [write](#write)
3. [activate](#activate)
4. [read](#read)
5. [delete](#delete)
6. [whereused](#whereused)

## create

Create ABAP DDIC transparent table.

```bash
sapcli table create [--corrnr TRANSPORT] "TABLE_NAME" "Description" "PACKAGE_NAME"
```

* _--corrnr TRANSPORT_ specifies CTS Transport Request Number **(optional)**

## write

Change the definition of ABAP DDIC transparent table.

```bash
saplci table write [TABLE_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [-a|--activate] [--ignore-errors] [--warning-errors] [--check|--no-check]
```

* _TABLE\_NAME_ specifying the name of the table or `-` to deduce it from the file name specified by FILE\_PATH
* _FILE\_PATH_ if TABLE\_NAME is not `-`, single file path or `-` for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number **(optional)**
* _--ignore-errors_ continue activating objects ignoring errors **(optional)**
* _--warning-errors_ treat activation warnings as errors **(optional)**
* _--check_ run the ADT `abapCheckRun` before the source is written and abort with readable findings on errors **(optional, off by default)**
* _--no-check_ skip the ADT `abapCheckRun` even when `SAPCLI_CHECK_BEFORE_SAVE=true` enables it globally **(optional)**

Failed PUTs (with or without the flag) are always re-run through `abapCheckRun` so the user gets a readable diagnostic instead of the cryptic ADT save error. Set `SAPCLI_CHECK_BEFORE_SAVE=true` once to make every `write`/`checkin` invocation run the check up front - this is the agentic-workflow opt-in.

## activate

Activate ABAP DDIC transparent table.

```bash
sapcli table activate [--ignore-errors] [--warning-errors] TABLE_NAME ...
```

* _--ignore-errors_ continue activating objects ignoring errors **(optional)**
* _--warning-errors_ treat activation warnings as errors **(optional)**

## read

Get the definition of ABAP DDIC transparent table.

```bash
sapcli table read TABLE_NAME
```

## delete

Delete table

```bash
sapcli table delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given table

```bash
sapcli table whereused TABLE_NAME
```
