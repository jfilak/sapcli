# MyObject (CLAS/OC)

1. [create](#create)
2. [read](#read)
3. [write](#write)
4. [activate](#activate)
5. [delete](#delete)
6. [whereused](#whereused)

## create

Creates a MyObject (CLAS/OC) of the given name with the given
description in the given package.

```bash
sapcli myobject create ZMYOBJECT "MyObject description" '$PACKAGE'
```

## read

Download source code of the given MyObject (CLAS/OC).

```bash
sapcli myobject read ZMYOBJECT
```

## write

Change the given MyObject.

```
sapcli myboject write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors]
```

* _OBJECT\_NAME_ either MyObject name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

### Examples

Write from a file:

```bash
sapcli myobject write ZMYOBJECT zmyobject.clas
```

Write from stdin:

```bash
cat zmyobject.clas | sapcli myobject write ZMYOBJECT -
```

Write and activate:

```bash
sapcli myobject write ZMYOBJECT zmybdef.bdef --activate
```

Write multiple files (object name deduced from filename):

```bash
sapcli myobject write - zmybdef.bdef zmybdef2.bdef zmybdef3.bdef
```

## activate

Activates the given myobjects in the given order.

```bash
sapcli myobject activate [--ignore-errors] [--warning-errors] NAME NAME ...
```

* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

### Examples

Activate single object:

```bash
sapcli myobject activate ZMYOBJECT
```

Activate multiple objects:

```bash
sapcli myobject activate ZMYOBJECT ZMYOBJECT2 ZMYOBJECT3
```

## delete

Delete the give myobject

```bash
sapcli myobject delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given myobject

```bash
sapcli myobject whereused ZMYOBJECT
```

