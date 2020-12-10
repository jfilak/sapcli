# Package

1. [create](#create)
2. [list](#list)
3. [check](#check)
4. [stat](#stat)

## create

Creates non-transportable packages

```bash
sapcli package create \$tests "with description"
```

## list

List sub-packages and object of the given package

```bash
sapcli package list \$tests [--recursive]
```

If the parameter `--recursive` is present, the command prints out contents of
sub-packages too.

## check

Run all available standard ADT checks for all objects of the give package.

```bash
sapcli package check \$productive_code
```

## stat

Prints basic set of package attributes. Returned exit could be interpreted as:
* `0` - package found
* `1` - package not found

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
