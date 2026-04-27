# Transaction

1. [create](#create)
2. [read](#read)
3. [write](#write)
4. [activate](#activate)
5. [delete](#delete)
6. [whereused](#whereused)

## create

Creates a transaction of the given name, description, and package. The
transaction type must be specified with `-t` and determines which additional
flags are required.

```
sapcli transaction create NAME DESCRIPTION PACKAGE -t TYPE [--corrnr TRANSPORT] [--abap-language-version VERSION] [--update-mode MODE]
```

* _NAME_ the transaction code
* _DESCRIPTION_ short description text
* _PACKAGE_ the target ABAP package
* _-t, --type TYPE_ transaction type: `report`, `parameter`, `dialog`, `oo`, `variant`
* _--corrnr TRANSPORT_ CTS Transport Request Number
* _--abap-language-version VERSION_ ABAP language version (default: `Standard ABAP`)
* _--update-mode MODE_ update mode: `notSet`, `asynchronous`, `synchronous`, `local` (default: `notSet`)

### Report Transaction

Creates a report transaction that calls a selection screen of a report.

```bash
sapcli transaction create ZTRAN "My report tran" '$PACKAGE' -t report \
  --report-name ZREPORT --report-dynnr 1000 --report-variant-name MYVAR
```

* _--report-name NAME_ report program name
* _--report-dynnr DYNNR_ selection screen number
* _--report-variant-name NAME_ variant name (optional)

### Parameter Transaction

Creates a parameter transaction that specializes a dialog or report transaction
by presetting initial screen values.

```bash
sapcli transaction create ZTRAN "My param tran" '$PACKAGE' -t parameter \
  --parent-transaction SE38
```

* _--parent-transaction NAME_ core transaction code

### Dialog Transaction

Creates a dialog transaction that calls a dynpro of a program.

```bash
sapcli transaction create ZTRAN "My dialog tran" '$PACKAGE' -t dialog \
  --program-name SAPMZMY --program-dynnr 0100
```

* _--program-name NAME_ program name
* _--program-dynnr DYNNR_ dynpro number

### OO Transaction

Creates an OO transaction that calls a class method.

```bash
sapcli transaction create ZTRAN "My OO tran" '$PACKAGE' -t oo \
  --class-name ZCL_MY_CLASS --method-name MY_METHOD
```

```bash
sapcli transaction create ZTRAN "Local OO tran" '$PACKAGE' -t oo \
  --class-name LCL_LOCAL --method-name RUN \
  --class-program-name ZPROGRAM --local-in-program --oo-transaction-model
```

* _--class-name NAME_ ABAP class name
* _--method-name NAME_ method name
* _--class-program-name NAME_ program name (optional, for local classes)
* _--local-in-program_ flag indicating the class is local in the program (optional)
* _--oo-transaction-model_ flag enabling the OO transaction model (optional)

### Variant Transaction

Creates a variant transaction that customizes a dialog or report transaction
by adapting menus and screens at runtime.

```bash
sapcli transaction create ZTRAN "My variant tran" '$PACKAGE' -t variant \
  --parent-transaction SE38 --cross-client --transaction-variant-name MYVARIANT
```

* _--parent-transaction NAME_ core transaction code
* _--cross-client_ flag indicating a cross-client variant (optional)
* _--transaction-variant-name NAME_ transaction variant name (optional)

## read

Prints the JSON source content of the given transaction to stdout.

```bash
sapcli transaction read ZTRAN
```

## write

Changes the source content of the given transaction.

```
sapcli transaction write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors] [--check|--no-check]
```

* _OBJECT\_NAME_ either transaction name or `-` when it should be deduced from the source file name
* _FILE\_PATH_ if OBJECT\_NAME is not `-`, single file path or `-` for reading stdin; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ CTS Transport Request Number
* _--activate_ activate after finishing the write operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors
* _--check_ run the ADT `abapCheckRun` before writing source code
* _--no-check_ skip the ADT `abapCheckRun`

## activate

Activates the given transaction(s).

```
sapcli transaction activate [--ignore-errors] [--warning-errors] NAME [NAME ...]
```

* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

## delete

Deletes the given transaction(s).

```
sapcli transaction delete [--corrnr TRANSPORT] NAME [NAME ...]
```

* _--corrnr TRANSPORT_ CTS Transport Request Number

## whereused

Finds objects that reference the given transaction.

```bash
sapcli transaction whereused ZTRAN
```
