# Function Module

- [Function Module](#function-module)
	- [create](#create)
	- [write](#write)
	- [chattr](#chattr)
	- [activate](#activate)
	- [read](#read)
	- [delete](#delete)
	- [whereused](#whereused)

## Group name resolution

Function modules always belong to a function group. Most commands require
the group name as the first argument. If you do not know the group name,
you can pass `-` instead and sapcli will resolve it automatically by
searching for the function module in the system.

```bash
# Explicit group name:
sapcli functionmodule read ZFG_PARENT Z_FUNCTION_MODULE

# Auto-resolve group name:
sapcli functionmodule read - Z_FUNCTION_MODULE
```

## create

Creates a function module in the given function group of the given name with
the given description.

```bash
sapcli functionmodule create ZFG_PARENT Z_FUNCTION_MODULE "Class description"
```

## write

Changes main source code of the given function module.

```
sapcli functionmodule write [GROUP_NAME|-] [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors] [--check|--no-check]
```

* _GROUP\_NAME_ either function group name or - to resolve it automatically via search; when OBJECT\_NAME is also -, the group is deduced from FILE\_PATH
* _OBJECT\_NAME_ either function module name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors
* _--check_ run the ADT `abapCheckRun` before the source is written and abort with readable findings on errors (off by default)
* _--no-check_ skip the ADT `abapCheckRun` even when `SAPCLI_CHECK_BEFORE_SAVE=true` enables it globally

Failed PUTs (with or without the flag) are always re-run through `abapCheckRun` so the user gets a readable diagnostic instead of the cryptic ADT save error. Set `SAPCLI_CHECK_BEFORE_SAVE=true` once to make every `write`/`checkin` invocation run the check up front - this is the agentic-workflow opt-in.

## chattr

Changes attributes of the given function module.

```bash
sapcli functionmodule chattr [ZFG_PARENT|-] Z_FUNCTION_MODULE [--processing_type normal|rfc] [--corrnr TRANSPORT]
```

* _GROUP\_NAME_ either function group name or - to resolve it automatically via search
* _--processing_type [normal|rfc]_ could be used to make RFC enabled
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed

## activate

Activates the given function module.

```bash
sapcli functionmodule activate [ZFG_PARENT|-] Z_FUNCTION_MODULE
```

* _GROUP\_NAME_ either function group name or - to resolve it automatically via search

## read

Download main source codes of the given function module.

```bash
sapcli functionmodule read [ZFG_PARENT|-] Z_FUNCTION_MODULE
```

* _GROUP\_NAME_ either function group name or - to resolve it automatically via search

## delete

Delete function module

```bash
sapcli functionmodule delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given function module

```bash
sapcli functionmodule whereused Z_FUNCTION_MODULE
```
