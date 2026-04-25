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
sapcli structure write [STRUCTURE_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [-a|--activate] [--ignore-errors] [--warning-errors] [--skip-check]
```

* _STRUCTURE\_NAME_ specifying the name of the structure or `-` to deduce it from the file name specified by FILE\_PATH
* _FILE\_PATH_ if TABLE\_NAME is not `-`, single file path or `-` for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number **(optional)**
* _--ignore-errors_ continue activating objects ignoring errors **(optional)**
* _--warning-errors_ treat activation warnings as errors **(optional)**
* _--skip-check_ skip the ADT `abapCheckRun` performed before the source is written; the global env-var `SAPCLI_CHECK_BEFORE_SAVE=false` disables the check for every invocation **(optional)**

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
