# sapcli supported commands

1. [Programs](#programs)
   1. [create](#create)
   2. [write](#write)
   3. [activate](#activate)
   4. [read](#read)
2. [Includes](#includes)
   1. [create](#include-create)
   2. [write](#include-write)
   3. [activate](#include-activate)
   4. [read](#include-read)
3. [Functions](#functions)
   1. [create group](#function-group-create)
   2. [create module](#function-module-create)
   3. [change module attributes](#function-module-chattr)
   4. [write group](#function-group-write)
   5. [write module](#function-module-write)
   6. [activate group](#function-group-activate)
   7. [activate module](#function-module-activate)
   8. [read group](#function-group-read)
   9. [read module](#function-module-read)
4. [Classes](#classes)
   1. [create](#create-1)
   2. [write](#write-1)
   3. [activate](#activate-1)
   4. [read](#read-1)
   4. [attributes](#attributes)
5. [Interfaces](#interfaces)
   1. [create](#create-2)
   2. [write](#write-2)
   3. [activate](#activate-2)
   4. [read](#read-2)
6. [DataDefinition (CDS)](#datadefinition-cds)
   1. [read](#read-3)
   2. [activate](#activate-3)
7. [Packages](#packages)
   1. [create](#create-3)
   2. [list](#list)
8. [ABAP Unit](#abap-unit)
   1. [run](#run)
9. [Change Transport System](#change-transport-system-cts)
   1. [list](#list-1)
   2. [release](#release)
10. [Source Code Library](#source-code-library)
   1. [checkout](#checkout)

## Programs

### create

Create executable program

```bash
sapcli program create "ZHELLOWORLD" "Just a description" "$TMP"
```

### write

Change code of an executable program without activation.

```
sapcli program write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate]
```

* _OBJECT\_NAME_ either program name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation

### activate

Activate an executable program.

```bash
sapcli program activate "ZHELLOWORLD"
```

### read

Download source codes

```bash
sapcli program read ZHELLOWORLD
```

## Includes

### include create

Create executable program

```bash
sapcli include create "ZHELLOWORLD_INC" "Just a description" "$TMP"
```

### include write

Change code of an executable program without activation.

```
sapcli include write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate]
```

* _OBJECT\_NAME_ either include name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation

### include activate

Activate an executable program.

```bash
sapcli include activate "ZHELLOWORLD_INC" [--master ZHELLOWORLD]
```

* _--master PROGRAM_ sets the master program for include activation

### include read

Download source codes

```bash
sapcli include read ZHELLOWORLD_INC
```

## Functions

### create group

Creates a function group of the given name with the given description in the
given package.

```bash
sapcli functiongroup create ZFG_PARENT "Class description" '$PACKAGE'
```

### create module

Creates a function module in the given function group of the given name with
the given description.

```bash
sapcli functionmodule create ZFG_PARENT Z_FUNCTION_MODULE "Class description"
```

### write group

Changes main source code of the given function group.

```
sapcli functiongroup write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate]
```

* _OBJECT\_NAME_ either function group name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation

### write module

Changes main source code of the given function module.

```
sapcli functiongroup write [GROUP_NAME|-] [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate]
```

* _GROUP\_NAME_ either function group name or - when it should be deduced from FILE\_PATH
* _OBJECT\_NAME_ either founction module name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation

### change attributes module

Changes attributes of the given function module.

```bash
sapcli functionmodule chattr "ZFG_PARENT" "Z_FUNCTION_MODULE [--type basic|rfc] [--corrnr TRANSPORT]
```

* _--type [basic|rfc]_ could be used to make RFC enabled
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed

### activate group

Activates the given function group.

```bash
sapcli functiongroup activate ZFG_PARENT
```

### activate module

Activates the given function module.

```bash
sapcli functionmodule activate ZFG_PARENT Z_FUNCTION_MODULE
```

### read group

Download main source codes of the given function group

```bash
sapcli functiongroup read ZFG_PARENT
```

### read module

Download main source codes of the given function module

```bash
sapcli functionmodule read ZFG_PARENT Z_FUNCTION_MODULE
```


## Classes

### create

Creates a public final global class of the given name with the given
description in the given package.

```bash
sapcli class create ZCL_HELLOWORLD "Class description" '$PACKAGE'
```

### write

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

### activate

Activates the given class.

```bash
sapcli class activate ZCL_HELLOWORLD
```

### read

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

### attributes

Prints out some attributes of the given class

```bash
sapcli class attributes ZCL_HELLOWORLD
```

Supported attributes:
* Name
* Description
* Responsible
* Package

## Interfaces

### create

Creates a public interface of the given name with the given
description in the given package.

```bash
sapcli interface create ZIF_GREETER "Interface description" '$PACKAGE'
```

### write

Changes source code of the given interfaces without activation

```
sapcli interface write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate]
```

* _OBJECT\_NAME_ either interface name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation

### activate

Activates the given interface

```bash
sapcli interface activate ZIF_GREETER
```

### read

Download main source codes of the given public interface

```bash
sapcli interface read ZIF_GREETER
```

## DataDefinition (CDS)

### activate

Activates the given CDS views in the given order

```bash
sapcli ddl activate ZCDS1 ZCDS2 ZCDS3 ...
```

### read

Download main source codes of the given public CDS view

```bash
sapcli ddl read ZCDS1
```

## Packages

### create

Creates non-transportable packages

```bash
sapcli package create \$tests "with description"
```

### list

List sub-packages and object of the given package

```bash
sapcli package list \$tests [--recursive]
```

If the parameter `--recursive` is present, the command prints out contents of
sub-packages too.

## ABAP Unit

Find more detailed description at [aunit.md](aunit.md)

### run

Runs ABAP unit tests of the give object

```bash
sapcli aunit run {package,class,program} NAME [--output {raw,human,junit4}]
```

## Change Transport System (CTS)

### list

Get list of CTS requests

```bash
sapcli cts list {transport,task} [--recusive|--recusive|...] [--owner login]
```

### release

Release CTS request - either Transport or Transport Task

```bash
sapcli cts release [transport,task] $number
```

## Source Code Library

This set of commands is intended for reading and writing whole packages.

File format and names should be compatible with [abapGit](https://github.com/larshp/abapGit).

### checkout

Fetches all source codes of the given class and stores them in local files.

```bash
sapcli checkout class zcl_hello_world
```

Fetches source codes of the given program and stores it a local file.

```bash
sapcli checkout program z_hello_world
```

Fetches source codes of the given interface and stores it a local file.

```bash
sapcli checkout interface zif_hello_world
```

Fetches source codes of classes, programs and interfaces of the given package
and stores them in corresponding files in a local file system directory.

The new directory is populated with the file _.abapgit.xml_ which has the format
recognized by [abapGit](https://github.com/larshp/abapGit).

```bash
sapcli checkout package '$hello_world' [directory] [--recursive] [--starting-folder DIR]
```

* _directory_ the name of a new directory to checkout the given package into;
  if not provided, the package name is used instead

* _--starting-folder_ forces sapcli to create the corresponding object files in
  the given directory; by default, sapcli uses the directory `src`

* _--recursive_ forces sapcli to download also the sub-packages into sub-directories
