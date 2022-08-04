# Table

1. [create](#create)
2. [write](#write)
3. [activate](#activate)
4. [read](#read)

## create

Create ABAP DDIC transparent table.

```bash
sapcli table create [--corrnr TRANSPORT] "TABLE_NAME" "Description" "PACKAGE_NAME"
```

* _--corrnr TRANSPORT_ specifies CTS Transport Request Number **(optional)**

## write

Change the definition of ABAP DDIC transparent table.

```bash
saplci table write [TABLE_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [-a|--activate] [--ignore-errors] [--warning-errors]
```

* _TABLE\_NAME_ specifying the name of the table or `-` to deduce it from the file name specified by FILE\_PATH
* _FILE\_PATH_ if TABLE\_NAME is not `-`, single file path or `-` for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number **(optional)**
* _--ignore-errors_ continue activating objects ignoring errors **(optional)**
* _--warning-errors_ treat activation warnings as errors **(optional)**

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
