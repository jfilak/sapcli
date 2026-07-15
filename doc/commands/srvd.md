# Service Definition (SRVD)

CRUD commands for the ABAP RAP **Service Definition** object (`SRVD/SRV`).
The source body is plain CDS service definition syntax
(`define service ... { expose ... }`).

1. [create](#create)
2. [read](#read)
3. [write](#write)
4. [activate](#activate)
5. [delete](#delete)
6. [whereused](#whereused)

## create

Creates a new (inactive) Service Definition in the given package.

```bash
sapcli srvd create NAME DESCRIPTION PACKAGE [--type {definition,extension}] [--corrnr TRANSPORT]
```

- **--type** - source type of the Service Definition (default: `definition`):
  - **definition** - a regular Service Definition
  - **extension** - a Service Definition extension

## read

Download the source of the given Service Definition.

```bash
sapcli srvd read NAME
```

## write

Upload source code into an existing Service Definition. The name argument
can be either an explicit object name, or `-` to deduce the name from the
file name (in which case multiple file paths are allowed).

```bash
sapcli srvd write NAME FILEPATH [-a] [--ignore-errors] [--warning-errors] [--check|--no-check] [--corrnr TRANSPORT]
sapcli srvd write -    FILEPATH [FILEPATH ...] [-a] [--ignore-errors] [--warning-errors] [--check|--no-check] [--corrnr TRANSPORT]
```

Pass `-` as the file name to read source from standard input.

- **-a, --activate** - activate after write.
- **--ignore-errors** - do not stop activation on errors.
- **--warning-errors** - treat activation warnings as errors.
- **--check / --no-check** - run abapCheckRun before write
  (overrides `SAPCLI_CHECK_BEFORE_SAVE`).

## activate

Activates the given Service Definitions in the listed order.

```bash
sapcli srvd activate NAME [NAME ...] [--ignore-errors] [--warning-errors]
```

- **--ignore-errors** - do not stop activation on errors.
- **--warning-errors** - treat activation warnings as errors.

## delete

Deletes the given Service Definitions.

```bash
sapcli srvd delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given Service Definition.

```bash
sapcli srvd whereused NAME
```
