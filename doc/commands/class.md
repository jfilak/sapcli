# Class

1. [create](#create-1)
2. [write](#write-1)
3. [activate](#activate-1)
4. [read](#read-1)
4. [attributes](#attributes)

## create

Creates a public final global class of the given name with the given
description in the given package.

```bash
sapcli class create ZCL_HELLOWORLD "Class description" '$PACKAGE'
```

## write

Changes main source code of the given class without activation

```
sapcli class write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate]

```

* _OBJECT\_NAME_ either class name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation

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

```bash
sapcli class activate ZCL_HELLOWORLD
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
