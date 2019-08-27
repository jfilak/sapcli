# Datapreview

Wrappers for ADT SQL console.

## osql

Executes a oneliner OSQL statement in ABAP system and prints out the results.

**Example**:

```bash
sapcli datapreview osql "select mandt cccategory from t000"
```

the output for ABAP Trial would be:

```
MANDT | CCCATEGORY
000 | S
001 | C
```

**Parameters**:

```bash
sapcli datapreview osql STATEMENT [--output human|json] [--rows (100)] [--noaging] [--noheadings]
```

* _STATEMENT_ the executed ABAP OpenSQL statement

* _--output_ either human friendly or JSON output format; where the default is human

* _--rows_ "up to"; where the default is 100

* _--noaging_ turns of data aging

* _--noheadings_ removes column names from the human friendly output

