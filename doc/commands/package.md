# Package

1. [create](#create)
2. [list](#list)

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
