# sapcli supported commands

1. [Programs](#programs)
   1. [create](#create)
   2. [write](#write)
   3. [activate](#activate)
   4. [read](#read)
2. [Classes](#classes)
   1. [create](#create-1)
   2. [write](#write-1)
   3. [activate](#activate-1)
   4. [read](#read-1)
2. [Interfaces](#interfaces)
   1. [create](#create-2)
   2. [write](#write-2)
   3. [activate](#activate-2)
   4. [read](#read-2)
3. [Packages](#packages)
   1. [create](#create-3)
   2. [list](#list)
4. [ABAP Unit](#abap-unit)
   1. [run](#run)
5. [Change Transport System](#change-transport-system-cts)
   1. [list](#list-1)
   2. [release](#release)
5. [Source Code Library](#source-code-library)
   1. [checkout](#checkout)

## Programs

### create

Create executable program

```bash
sapcli program create "ZHELLOWORLD" "Just a description" "$TMP"
```

### write

Change code of an executable program without activation.

```bash
sapcli program write "ZHELLOWORLD" zhelloworld.abap
```

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

## Classes

### create

Creates a public final global class of the given name with the given
description in the given package.

```bash
sapcli class create ZCL_HELLOWORLD "Class description" '$PACKAGE'
```

### write

Changes main source code of the given class without activation

```bash
sapcli class write "ZCL_HELLOWORLD" zcl_helloworld.abap
```

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

## Interfaces

### create

Creates a public interface of the given name with the given
description in the given package.

```bash
sapcli interface create ZIF_GREETER "Interface description" '$PACKAGE'
```

### write

Changes source code of the given interfaces without activation

```bash
sapcli interface write "ZIF_GREETER" zif_greeter.abap
```

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
