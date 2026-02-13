# AccessControl (DCL)

1. [create](#create)
2. [read](#read)
3. [write](#write)
4. [activate](#activate)

## create

Creates a CDS access control (DCL) of the given name with the given
description in the given package.

```bash
sapcli dcl create ZMYACL "Access control description" '$PACKAGE'
```

## read

Download source code of the given access control.

```bash
sapcli dcl read ZMYACL
```

## write

Change source code of an access control without activation.

```
sapcli dcl write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors]
```

* _OBJECT\_NAME_ either access control name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

### Examples

Write from a file:

```bash
sapcli dcl write ZMYACL zmyacl.dcls
```

Write from stdin:

```bash
cat zmyacl.dcls | sapcli dcl write ZMYACL -
```

Write and activate:

```bash
sapcli dcl write ZMYACL zmyacl.dcls --activate
```

Write multiple files (object name deduced from filename):

```bash
sapcli dcl write - zmyacl.dcls zmyacl2.dcls zmyacl3.dcls
```

## activate

Activates the given access controls in the given order.

```bash
sapcli dcl activate [--ignore-errors] [--warning-errors] NAME NAME ...
```

* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

### Examples

Activate single object:

```bash
sapcli dcl activate ZMYACL
```

Activate multiple objects:

```bash
sapcli dcl activate ZMYACL ZMYACL2 ZMYACL3
```
