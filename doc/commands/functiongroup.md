# Function Group

1. [create](#create)
2. [write](#write)
3. [activate](#activate)
4. [read](#read)

## create

Creates a function group of the given name with the given description in the
given package.

```bash
sapcli functiongroup create ZFG_PARENT "Class description" '$PACKAGE'
```

## write

Changes main source code of the given function group.

```
sapcli functiongroup write [FUNCTION_GROUP_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors]
```

* _FUNCITON\_GROUP\_NAME_ either function group name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if FUNCTION\_GROUP\_NAME is not -, a single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

## activate

Activates the given function group.

```bash
sapcli functiongroup activate ZFG_PARENT
```

### read group

Download main source codes of the given function group

```bash
sapcli functiongroup read ZFG_PARENT
```
