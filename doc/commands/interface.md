# Interfaces

1. [create](#create)
2. [write](#write)
3. [activate](#activate)
4. [read](#read)

## create

Creates a public interface of the given name with the given
description in the given package.

```bash
sapcli interface create ZIF_GREETER "Interface description" '$PACKAGE'
```

## write

Changes source code of the given interfaces without activation

```bash
sapcli interface write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors]
```

* _OBJECT\_NAME_ either interface name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

## activate

Activates the given interface

```bash
sapcli interface activate [--ignore-errors] [--warning-errors] NAME NAME ...
```

* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

## read

Download main source codes of the given public interface

```bash
sapcli interface read ZIF_GREETER
```
