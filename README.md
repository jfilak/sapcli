# SAP CLI

Command line interface to SAP products

## Philosophy

Let's automate!

This tool provides command line interface for ADT which should help you to
build your CI tools.

## Features

### Programs

#### create

Create executable program

```bash
sapcli program create "ZHELLOWORLD" "Just a description" "$TMP"
```

#### write

Change code of an executable program without activation.

```bash
sapcli program write "ZHELLOWORLD" zhelloworld.abap
```

#### activate

Activate an executable program.

```bash
sapcli program activate "ZHELLOWORLD"
```

#### read

Download source codes

```bash
sapcli program read ZHELLOWORLD
```

#### unit tests

Execute unit tets

```bash
sapcli aunit run program ZHELLOWORLD
```

### Classes

#### read

Download source codes

```bash
sapcli program class ZCL_HELLOWORLD
```

#### unit tests

Execute unit tets

```bash
sapcli aunit run class ZCL_HELLOWORLD
```

### Packages

#### create

Creates non-transportable packages

```bash
sapcli package create \$tests "with description"
```

#### unit tests

Execute unit tests

```bash
sapcli aunit run package \$tests
```
