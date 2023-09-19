# Structure

- [Structure](#structure)
  - [create](#create)
  - [write](#write)
  - [activate](#activate)
  - [read](#read)

## create

Create ABAP DDIC structure.

```bash
sapcli structure create [--corrnr TRANSPORT] "STRUCTURE_NAME" "Description" "PACKAGE_NAME"
```

* _--corrnr TRANSPORT_ specifies CTS Transport Request Number **(optional)**

## write

Change the definition of ABAP DDIC structure.

```bash
sapcli structure write [STRUCTURE_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [-a|--activate] [--ignore-errors] [--warning-errors]
```

* _STRUCTURE\_NAME_ specifying the name of the structure or `-` to deduce it from the file name specified by FILE\_PATH
* _FILE\_PATH_ if TABLE\_NAME is not `-`, single file path or `-` for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number **(optional)**
* _--ignore-errors_ continue activating objects ignoring errors **(optional)**
* _--warning-errors_ treat activation warnings as errors **(optional)**

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
