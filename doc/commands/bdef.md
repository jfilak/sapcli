# BehaviorDefinition (BDEF)

1. [create](#create)
2. [read](#read)
3. [write](#write)
4. [activate](#activate)

## create

Creates a CDS behavior definition (BDEF) of the given name with the given
description in the given package.

```bash
sapcli bdef create ZMYBDEF "Behavior definition description" '$PACKAGE'
```

## read

Download source code of the given behavior definition.

```bash
sapcli bdef read ZMYBDEF
```

## write

Change source code of a behavior definition without activation.

```
sapcli bdef write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors]
```

* _OBJECT\_NAME_ either behavior definition name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

### Examples

Write from a file:

```bash
sapcli bdef write ZMYBDEF zmybdef.bdef
```

Write from stdin:

```bash
cat zmybdef.bdef | sapcli bdef write ZMYBDEF -
```

Write and activate:

```bash
sapcli bdef write ZMYBDEF zmybdef.bdef --activate
```

Write multiple files (object name deduced from filename):

```bash
sapcli bdef write - zmybdef.bdef zmybdef2.bdef zmybdef3.bdef
```

## activate

Activates the given behavior definitions in the given order.

```bash
sapcli bdef activate [--ignore-errors] [--warning-errors] NAME NAME ...
```

* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

### Examples

Activate single object:

```bash
sapcli bdef activate ZMYBDEF
```

Activate multiple objects:

```bash
sapcli bdef activate ZMYBDEF ZMYBDEF2 ZMYBDEF3
```
