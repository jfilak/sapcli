# ABAP

1. [find](#find)
2. [run](#run)

## find

Find ABAP objects by name using ADT quick search. A trailing `*` wildcard is
appended automatically so that prefix matching works out of the box.

```bash
sapcli abap find [--max-results MAX_RESULTS] TERM
```

* _TERM_ search query string (e.g. `BAPIRET2_T`)
* _--max-results MAX\_RESULTS_ maximum number of results to return (default: `51`)

### Find objects matching a prefix

```bash
sapcli abap find BAPIRET2_T
```

Example output:

```
Object type | Name        | Description
------------|-------------|----------------------------
TTYP/DA     | BAPIRET2_T  | Return parameter table
TABL/DS     | BAPIRET2_T1 | Proxy Structure (generated)
```

### Limit the number of results

```bash
sapcli abap find --max-results 10 Z_MY_OBJECT
```

## run

Executes ABAP code from a file or stdin by creating a temporary class that implements
`if_oo_adt_classrun`, running it, and unconditionally deleting it afterwards.

Find more about the options you have when writing your ABAP snippet at:
[help.sap.com/adt-class-execution](https://help.sap.com/docs/btp/sap-business-technology-platform/adt-class-execution)

```bash
sapcli abap run [--prefix PREFIX] [--package PACKAGE] SOURCE
```

* _SOURCE_ path to a file containing ABAP statements, or `-` to read from _stdin_
* _--prefix PREFIX_ class name prefix (default: `zcl_sapcli_run`)
* _--package PACKAGE_ package for the temporary class (default: `$tmp`)

The temporary class name follows the pattern `<prefix>_<username>_<random>` and is
exactly 30 characters long.

### Run ABAP from a file

```bash
sapcli abap run my_script.abap
```

### Run ABAP from stdin

```bash
echo -n "out->write( 'Hello World!' )." | sapcli abap run -
```

### Use a custom prefix and package

```bash
sapcli abap run --prefix zcl_myrun --package '$mypackage' my_script.abap
```
