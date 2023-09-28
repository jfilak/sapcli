# Function Group

- [Function Group](#function-group)
	- [create](#create)
	- [write](#write)
	- [activate](#activate)
	- [read group](#read-group)
	- [Function Group Include](#function-group-include)
		- [create](#create-1)
		- [write](#write-1)
		- [activate](#activate-1)
		- [read group](#read-group-1)

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

## read group

Download main source codes of the given function group

```bash
sapcli functiongroup read ZFG_PARENT
```

## Function Group Include

### create

Creates a function group of the given name with the given description in the
given package.

```bash
sapcli functiongroup include create ZFG_PARENT ZFGI_HELLO_WORLD "Function Group Include description"
```

### write

Changes main source code of the given function group.

```
sapcli functiongroup include write [FUNCTION_GROUP_NAME] [FUNCTION_GROUP_INCLUDE_NAME] [FILE_PATH|-] [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors]
```

* _FUNCITON\_GROUP\_NAME_ function group name
* _FUNCITON\_GROUP\_INCLUDE\_NAME_ function group include name
* _FILE\_PATH_ a single file path or - for reading _stdin_
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

### activate

Activates the given function group.

```bash
sapcli functiongroup include activate ZFG_PARENT ZFGI_HELLO_WORLD
```

### read group

Download main source codes of the given function group

```bash
sapcli functiongroup include read ZFG_PARENT ZFGI_HELLO_WORLD
```
