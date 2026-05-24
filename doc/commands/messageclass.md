# Message Class

- [Message Class](#message-class)
	- [create](#create)
	- [read](#read)
	- [write](#write)
	- [activate](#activate)
	- [delete](#delete)
	- [whereused](#whereused)
	- [Message](#message)
		- [create](#create-1)
		- [read](#read-1)
		- [write](#write-1)
		- [delete](#delete-1)

## create

Creates a message class of the given name with the given description in the
given package.

```bash
sapcli messageclass create ZMC_HELLO_WORLD "Message class description" '$PACKAGE'
```

## read

Download the message class content.

```bash
sapcli messageclass read ZMC_HELLO_WORLD [--output JSON|HUMAN]
```

* _--output HUMAN_ prints the message class in a human-readable table format (default)
* _--output JSON_ prints the message class in JSON format

Example HUMAN output:

```
Description: Testing messages

No. | Text               | Selfexplanatory
----|--------------------|-----------------
000 | &                  | true
001 | Repository not found | true
```

## write

Not implemented yet.

```bash
sapcli messageclass write ZMC_HELLO_WORLD
```

## activate

Message classes do not require activation. The command prints an informational
message.

```bash
sapcli messageclass activate ZMC_HELLO_WORLD
```

## delete

Delete message class.

```bash
sapcli messageclass delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given message class.

```bash
sapcli messageclass whereused ZMC_HELLO_WORLD
```

## Message

### create

Creates a new message in the given message class.

```bash
sapcli messageclass message create NAME MSGNO MSGTEXT [--selfexplanatory true|false] [--corrnr TRANSPORT]
```

* _NAME_ message class name
* _MSGNO_ message number (3 digits)
* _MSGTEXT_ message text
* _--selfexplanatory_ whether the message is self-explanatory (default: false)
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed

### read

Read a single message from a message class.

```bash
sapcli messageclass message read NAME MSGNO
```

Example output:

```
Number: 001
Text  : Repository not found
S./Ex.: true
```

### write

Update a message in a message class.

```bash
sapcli messageclass message write NAME MSGNO MSGTEXT [--selfexplanatory true|false] [--corrnr TRANSPORT]
```

* _NAME_ message class name
* _MSGNO_ message number (3 digits)
* _MSGTEXT_ message text
* _--selfexplanatory_ whether the message is self-explanatory (default: false)
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed

### delete

Delete a message from a message class.

```bash
sapcli messageclass message delete NAME MSGNO [--corrnr TRANSPORT]
```
