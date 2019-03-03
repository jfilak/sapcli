# sapcli supported commands

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

### unit tests

Execute unit tets

```bash
sapcli aunit run program ZHELLOWORLD [--output {raw,human}]
```

## Classes

### create

Creates a public final global class of the given name with the given
description in the given package.

```bash
sapcli class create ZCL_HELLOWORLD "Class description" '$PACKAGE'
```

### read

Download source codes

```bash
sapcli program class ZCL_HELLOWORLD
```

### unit tests

Execute unit tets

```bash
sapcli aunit run class ZCL_HELLOWORLD [--output {raw,human}]
```

## Packages

### create

Creates non-transportable packages

```bash
sapcli package create \$tests "with description"
```

### unit tests

Execute unit tests

```bash
sapcli aunit run package \$tests [--output {raw,human}]
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
