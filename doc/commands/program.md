# Programs

- [Programs](#programs)
	- [create](#create)
	- [write](#write)
	- [activate](#activate)
	- [read](#read)
	- [delete](#delete)
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

Failed PUTs (with or without the flag) are always re-run through `abapCheckRun` so the user gets a readable diagnostic instead of the cryptic ADT save error. Set `SAPCLI_CHECK_BEFORE_SAVE=true` once to make every `write`/`checkin` invocation run the check up front - this is the agentic-workflow opt-in.

## activate

Activate an executable program.

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

## delete

Delete program

```bash
sapcli program delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given program

```bash
sapcli program whereused ZHELLOWORLD
```

