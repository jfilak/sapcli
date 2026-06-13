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
