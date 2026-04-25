# Structure

- [Structure](#structure)
  - [create](#create)
  - [write](#write)
  - [activate](#activate)
  - [read](#read)
  - [delete](#delete)
  - [whereused](#whereused)

## create

Create ABAP DDIC structure.

```bash
sapcli structure create [--corrnr TRANSPORT] "STRUCTURE_NAME" "Description" "PACKAGE_NAME"
```

* _--corrnr TRANSPORT_ specifies CTS Transport Request Number **(optional)**

## write

Change the definition of ABAP DDIC structure.

```bash
sapcli structure write [STRUCTURE_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [-a|--activate] [--ignore-errors] [--warning-errors] [--check|--no-check]
```

* _STRUCTURE\_NAME_ specifying the name of the structure or `-` to deduce it from the file name specified by FILE\_PATH
* _FILE\_PATH_ if TABLE\_NAME is not `-`, single file path or `-` for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number **(optional)**
* _--ignore-errors_ continue activating objects ignoring errors **(optional)**
* _--warning-errors_ treat activation warnings as errors **(optional)**
* _--check_ run the ADT `abapCheckRun` before the source is written and abort with readable findings on errors **(optional, off by default)**
* _--no-check_ skip the ADT `abapCheckRun` even when `SAPCLI_CHECK_BEFORE_SAVE=true` enables it globally **(optional)**

Failed PUTs (with or without the flag) are always re-run through `abapCheckRun` so the user gets a readable diagnostic instead of the cryptic ADT save error. Set `SAPCLI_CHECK_BEFORE_SAVE=true` once to make every `write`/`checkin` invocation run the check up front - this is the agentic-workflow opt-in.

## activate

Activate ABAP DDIC structure.

```bash
sapcli structure activate [--ignore-errors] [--warning-errors] STRUCTURE_NAME ...
```

* _--ignore-errors_ continue activating objects ignoring errors **(optional)**
* _--warning-errors_ treat activation warnings as errors **(optional)**

## read

Get the definition of ABAP DDIC structure.

```bash
sapcli structure read STRUCTURE_NAME
```

## delete

Delete structure

```bash
sapcli structure delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given structure

```bash
sapcli structure whereused STRUCTURE_NAME
```
