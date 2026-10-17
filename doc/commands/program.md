# Programs

- [Programs](#programs)
	- [create](#create)
	- [write](#write)
	- [activate](#activate)
	- [read](#read)
		- [Text elements](#text-elements)
	- [delete](#delete)
	- [execute](#execute)
	- [whereused](#whereused)

## create

Create executable program

```bash
sapcli program create "ZHELLOWORLD" "Just a description" '$TMP'
```

## write

Change code of an executable program without activation.

```
sapcli program write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors] [--check|--no-check]
```

* _OBJECT\_NAME_ either program name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors
* _--check_ run the ADT `abapCheckRun` before the source is written and abort with readable findings on errors (off by default)
* _--no-check_ skip the ADT `abapCheckRun` even when `SAPCLI_CHECK_BEFORE_SAVE=true` enables it globally

Failed writes (with or without the flag) are always re-run through `abapCheckRun` so the user gets a readable diagnostic instead of the cryptic ADT save error. Set `SAPCLI_CHECK_BEFORE_SAVE=true` once to make every `write`/`checkin` invocation run the check up front - this is the agentic-workflow opt-in.

Replaces text symbols (the program text pool) of the given program without
activation - see [Text elements](#text-elements) for the file format

```bash
sapcli program write ZHELLOWORLD --type textelements zhelloworld.textelements.txt
```

The options _--check_ and _--no-check_ have no effect for text elements because
`abapCheckRun` checks only ABAP source code.

## activate

Activate an executable program together with its inactive text elements.

```bash
sapcli program activate [--ignore-errors] [--warning-errors] NAME NAME ...
```

* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

## read

Download source codes

```bash
sapcli program read ZHELLOWORLD
```

Download text symbols (the program text pool) in the logon language

```bash
sapcli program read ZHELLOWORLD --type textelements
```

### Text elements

Text symbols are what ABAP code references as `TEXT-001` or `'literal'(001)`.
The command `write --type textelements` replaces the whole text pool of the
program, so symbols missing in the file are removed. Text symbols are
language dependent and sapcli reads and writes them in the logon language.
Selection texts and list headings are not supported yet.

The file is line based and every symbol is defined by two lines:
the line `@MaxLength:<n>` with the maximum length of the text,
followed by the line `<ID>=<text>`. Empty lines are ignored and the text
can contain the character `=`.

```
@MaxLength:40
001=Hello, world from the text elements!
```

The written text symbols are inactive until they are activated:

* `write --type textelements --activate` activates only the text elements and
  leaves inactive program source code untouched
* `sapcli program activate` and `write --activate` of the source code activate
  the program together with its inactive text elements; if the source code
  activation fails, the text elements remain inactive too

```bash
sapcli program read ZHELLOWORLD --type textelements > zhelloworld.textelements.txt
# edit the file
sapcli program write ZHELLOWORLD --type textelements zhelloworld.textelements.txt --activate
```

## delete

Delete program

```bash
sapcli program delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## execute

Runs the executable program and prints its raw list output including the page
header. Selection screen parameters get their default values.

```bash
sapcli program execute ZPROG_HELLO_WORLD
```

## whereused

Find objects that reference the given program

```bash
sapcli program whereused ZHELLOWORLD
```

