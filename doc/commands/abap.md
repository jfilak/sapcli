# ABAP

1. [find](#find)
2. [run](#run)
3. [systeminfo](#systeminfo)
4. [feeds](#feeds)
5. [shortdumps](#shortdumps)

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
sapcli abap run [--prefix PREFIX] [--package PACKAGE] [-D NAME=VALUE] SOURCE
```

* _SOURCE_ path to a file containing ABAP statements, or `-` to read from _stdin_
* _--prefix PREFIX_ class name prefix (default: `zcl_sapcli_run`)
* _--package PACKAGE_ package for the temporary class (default: `$tmp`)
* _-D NAME=VALUE, --define NAME=VALUE_ replace `{{NAME}}` tokens in the source
  with `VALUE` (repeatable; case sensitive; the last definition of the same
  name wins)

The temporary class name follows the pattern `<prefix>_<username>_<random>` and is
exactly 30 characters long.

Before the source is written, the ADT `abapCheckRun` reporter is run on the
generated class so that obvious syntax errors are reported to the user with a
human-readable location instead of the cryptic ADT save error. The check can
be disabled globally via the environment variable
`SAPCLI_CHECK_BEFORE_SAVE=false`. There is no per-invocation flag here on
purpose - `abap run` is internal orchestration; if the check itself misfires
the global env-var is the right knob.

### Preprocessor

The source is treated as a template: every `{{NAME}}` token is replaced with
the value given via `--define NAME=VALUE` before the code is sent to the
system. Whitespace inside the braces is allowed (`{{ NAME }}`), the token must
not span lines, and names follow the C identifier grammar
(`[A-Za-z_][A-Za-z0-9_]*`, ASCII only). The value may contain `=` - only the
first `=` separates the name from the value. Values are inserted literally;
they are not re-scanned for tokens. Substitution happens everywhere in the
source, including character literals and comments.

The preprocessor fails with an error instead of sending questionable code to
the system when the source contains:

* a token without a matching `--define` (a forgotten substitution),
* anything but a plain name between `{{` and `}}` - the content is reserved
  for future template features (e.g. Jinja2 style filters),
* the Jinja2 delimiters `{%` or `{#` anywhere in the code - reserved for
  future template statements and comments.

Because the reservation errors are based on the raw text, ABAP code with a
literal `{{`, `{%` or `{#` inside a character literal or a comment is
rejected too; there is no escape syntax yet.

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

### Substitute values in the source

```bash
echo -n "out->write( '{{GREETING}}, {{WHO}}!' )." | sapcli abap run --define GREETING=Hello --define WHO=World -
```

## systeminfo

Prints system information (system ID, client, user, database, operating system,
application server, ...) gathered from ADT.

```bash
sapcli abap systeminfo [--key KEY]
```

* _--key KEY_ print only the value of the given entry instead of the whole list

### Print all system information

```bash
sapcli abap systeminfo
```

### Print a single value

```bash
sapcli abap systeminfo --key OSName
```

## feeds

Work with the ADT feeds (ATOM feeds published by the system, e.g. runtime
dumps or the system log).

### list

Lists the feeds available on the system.

```bash
sapcli abap feeds list
```

Example output:

```
Title               | Id
--------------------|---------------------------
ABAP Runtime Errors | /sap/bc/adt/runtime/dumps
System Log          | /sap/bc/adt/runtime/syslog
```

### read

Reads a single feed identified by its URL (the `Id` value shown by
`feeds list`) and prints its entries as a table.

```bash
sapcli abap feeds read FEED_URL
```

* _FEED\_URL_ the ADT feed URL (e.g. `/sap/bc/adt/runtime/syslog`)

```bash
sapcli abap feeds read /sap/bc/adt/runtime/syslog
```

As a convenience, reading the runtime dumps feed
(`/sap/bc/adt/runtime/dumps`) is redirected to
[`shortdumps list`](#shortdumps) so that the richer dump columns (author,
timestamp) are shown.

## shortdumps

Work with ABAP runtime short dumps.

### list

Lists the runtime short dumps available on the system.

```bash
sapcli abap shortdumps list
```

Example output:

```
Author    | Title                                  | Updated              | Id
----------|----------------------------------------|----------------------|-------
DEVELOPER | CX_SY_ZERODIVIDE Division by zero      | 2024-01-15T10:30:00Z | ABC123
TESTER    | CX_SY_ITAB_LINE_NOT_FOUND              | 2024-01-16T11:00:00Z | DEF456
```

### show

Prints a single short dump, formatted by the system, identified by its ID (the
`Id` value shown by `shortdumps list`).

```bash
sapcli abap shortdumps show DUMP_ID
```

* _DUMP\_ID_ the short dump ID (e.g. `ABC123`)

```bash
sapcli abap shortdumps show ABC123
```
