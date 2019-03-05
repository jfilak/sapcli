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
3. [Packages](#packages)
   1. [create](#create-2)
4. [ABAP Unit](#abap-unit)
   1. [run](#run)
5. [Change Transport System](#change-transport-system-cts)
   1. [list](#list)
   2. [release](#release)

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

## Packages

### create

Creates non-transportable packages

```bash
sapcli package create \$tests "with description"
```

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
