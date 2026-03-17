# ABAP

1. [run](#run)

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
