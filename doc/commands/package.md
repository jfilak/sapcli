# Package

1. [create](#create)
2. [list](#list)
3. [check](#check)
4. [stat](#stat)

## create

Creates non-transportable packages

```bash
sapcli package create [--super-package SUPER_PKG] [--app-component APP_COMP] [--software-component SW_COMP] [--transport-layer TR_LAYER] [--no-error-existing] NAME DESCRIPTION
```

**Parameters**:
- `--super-package SUPER_PKG`: Name of the parent package. **(optional)**
- `--app-component APP_COMP`: Name of assigned Application Component. **(optional)**
- `--software-component SW_COMP`: Name of assigned Software Component. **(optional)**
- `--transport-layer TR_LAYER`: Name of assigned Transport Layer. **(optional)**
- `--no-error-existing`: Do not exit with non-0 exit code if the package already exists. **(optional)**
- `NAME`: Name of the newly created package. Do not forget to escape $ in shell to avoid ENV variable evaluation.
- `DESCRIPTION`: Description of the newly created package. Do not forget to use " if you need more words.

## list

List sub-packages and objects of the given package

```bash
sapcli package list \$tests [-r|--recursive] [-l|--long]
```

**Parameters**:
- `-r, --recursive`: List contents of sub-packages recursively. **(optional)**
- `-l, --long`: Print details (type, name, description) for sub-packages and objects in column-aligned format. **(optional)**

**Examples**:

Basic listing:
```bash
sapcli package list \$tests
```

Output:
```
$TESTS_SUB
ZIF_HELLO_WORLD
ZCL_HELLO_WORLD
Z_HELLO_WORLD
```

Long format with details:
```bash
sapcli package list \$tests --long
```

Output:
```
DEVC/K   $TESTS_SUB       Test Subpackage
INTF/OI  ZIF_HELLO_WORLD  Test interface
CLAS/OC  ZCL_HELLO_WORLD  Test class
PROG/P   Z_HELLO_WORLD    Test program
```

## check

Run all available standard ADT checks for all objects of the give package.

```bash
sapcli package check \$productive_code
```

## stat

Prints basic set of package attributes. Returned exit could be interpreted as:
* `0` - package found
* `10` - package not found

```bash
sapcli package stat \$productive_code
```

which results in output similar to:
```
Name                   :PROD_BSP_APS
Active                 :active
Application Component  :APP-COMP-XY
Software Component     :SW-COMP-XY
Transport Layer        :
Package Type           :development
```
