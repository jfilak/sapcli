# Function Module

1. [create](#create)
2. [chattr](#chattr)
3. [write](#write)
4. [activate](#activate)
5. [read](#read)

## create

Creates a function module in the given function group of the given name with
the given description.

```bash
sapcli functionmodule create ZFG_PARENT Z_FUNCTION_MODULE "Class description"
```

## write

Changes main source code of the given function module.

```
sapcli functiongroup write [GROUP_NAME|-] [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors]
```

* _GROUP\_NAME_ either function group name or - when it should be deduced from FILE\_PATH
* _OBJECT\_NAME_ either founction module name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

## chattr

Changes attributes of the given function module.

```bash
sapcli functionmodule chattr "ZFG_PARENT" "Z_FUNCTION_MODULE [--type normal|rfc] [--corrnr TRANSPORT]
```

* _--type [normal|rfc]_ could be used to make RFC enabled
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed

### activate

Activates the given function module.

```bash
sapcli functionmodule activate ZFG_PARENT Z_FUNCTION_MODULE
```

### read

Download main source codes of the given function module

```bash
sapcli functionmodule read ZFG_PARENT Z_FUNCTION_MODULE
```
