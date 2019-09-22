# Package

1. [create](#create)
2. [list](#list)
3. [check](#check)

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
