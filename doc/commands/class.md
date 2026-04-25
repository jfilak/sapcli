# Class

1. [create](#create-1)
2. [write](#write-1)
3. [activate](#activate-1)
4. [read](#read-1)
5. [delete](#delete)
6. [whereused](#whereused)
7. [attributes](#attributes)
8. [execute](#execute)

## create

Creates a public final global class of the given name with the given
description in the given package.

```bash
sapcli class create ZCL_HELLOWORLD "Class description" '$PACKAGE'
```

## write

Changes main source code of the given class without activation

```
sapcli class write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors] [--check|--no-check]
```

* _OBJECT\_NAME_ either class name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors
* _--check_ run the ADT `abapCheckRun` before the source is written and abort with readable findings on errors (off by default)
* _--no-check_ skip the ADT `abapCheckRun` even when `SAPCLI_CHECK_BEFORE_SAVE=true` enables it globally

Failed PUTs (with or without the flag) are always re-run through `abapCheckRun` so the user gets a readable diagnostic instead of the cryptic ADT save error. Set `SAPCLI_CHECK_BEFORE_SAVE=true` once to make every `write`/`checkin` invocation run the check up front - this is the agentic-workflow opt-in.

Changes definitions source code of the given class without activation

```bash
sapcli class write "ZCL_HELLOWORLD" --type definitions zcl_helloworld.definitions.abap
```

Changes implementations source code of the given class without activation

```bash
sapcli class write "ZCL_HELLOWORLD" --type implementations zcl_helloworld.implementations.abap
```

Changes test classes source code of the given class without activation

```bash
sapcli class write "ZCL_HELLOWORLD" --type testclassess zcl_helloworld.testclasses.abap
```

## activate

Activates the given class.

```
sapcli class activate [--ignore-errors] [--warning-errors] NAME NAME ...
```

## read

Download main source codes of the given public class

```bash
sapcli class read ZCL_HELLOWORLD
```

Downloads definitions source codes of the given public class

```bash
sapcli class read ZCL_HELLOWORLD --type definitions
```

Downloads implementations source codes of the given public class

```bash
sapcli class read ZCL_HELLOWORLD --type implementations
```

Downloads test classes source codes of the given public class

```bash
sapcli class read ZCL_HELLOWORLD --type testclasses
```

## delete

Delete class

```bash
sapcli class delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given class

```bash
sapcli class whereused ZCL_HELLOWORLD
```

## attributes

Prints out some attributes of the given class

```bash
sapcli class attributes ZCL_HELLOWORLD
```

Supported attributes:
* Name
* Description
* Responsible
* Package

## execute

Executes the class if it implements the `if_oo_adt_classrun~main` method and prints the raw output

```bash
sapcli class execute ZCL_HELLOWORLD
```