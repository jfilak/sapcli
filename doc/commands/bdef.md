# BehaviorDefinition (BDEF)

1. [create](#create)
2. [extend](#extend)
3. [read](#read)
4. [write](#write)
5. [activate](#activate)
6. [delete](#delete)
7. [whereused](#whereused)
8. [listinterfaces](#listinterfaces)

## create

Creates a CDS behavior definition (BDEF) of the given name with the given
description in the given package.

```bash
sapcli bdef create ZMYBDEF "Behavior definition description" '$PACKAGE'
```

### Examples

Create a regular behavior definition:

```bash
sapcli bdef create ZMYBDEF "My behavior definition" MYPACKAGE
```

## extend

Creates a behavior extension for an existing behavior definition. A behavior
extension is a special kind of behavior definition that extends a base behavior
definition with new behavior implementations.

```bash
sapcli bdef extend NAME DESCRIPTION PACKAGE BASE_BDEF [--interface-bdef INTERFACE] [--corrnr TRANSPORT]
```

* _NAME_ name of the new behavior extension
* _DESCRIPTION_ description of the new behavior extension
* _PACKAGE_ package in which the extension should be created
* _BASE\_BDEF_ the behavior definition to extend
* _--interface-bdef INTERFACE_ BO interface to assign the extension to (validated against existing interfaces)
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed

When `--interface-bdef` is provided, the command validates that the interface
exists on the base behavior definition or any of its extensions before creating.

### Examples

Create a behavior extension without specifying an interface:

```bash
sapcli bdef extend R_PRODUCTTP_EXT "Product extension" MYPACKAGE R_PRODUCTTP
```

Create a behavior extension with a specific BO interface:

```bash
sapcli bdef extend R_PRODUCTTP_EXT "Product extension" MYPACKAGE R_PRODUCTTP --interface-bdef I_PRODUCTTP_2
```

## read

Download source code of the given behavior definition.

```bash
sapcli bdef read ZMYBDEF
```

## write

Change source code of a behavior definition without activation.

```
sapcli bdef write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors]
```

* _OBJECT\_NAME_ either behavior definition name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

### Examples

Write from a file:

```bash
sapcli bdef write ZMYBDEF zmybdef.bdef
```

Write from stdin:

```bash
cat zmybdef.bdef | sapcli bdef write ZMYBDEF -
```

Write and activate:

```bash
sapcli bdef write ZMYBDEF zmybdef.bdef --activate
```

Write multiple files (object name deduced from filename):

```bash
sapcli bdef write - zmybdef.bdef zmybdef2.bdef zmybdef3.bdef
```

## activate

Activates the given behavior definitions in the given order.

```bash
sapcli bdef activate [--ignore-errors] [--warning-errors] NAME NAME ...
```

* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

### Examples

Activate single object:

```bash
sapcli bdef activate ZMYBDEF
```

Activate multiple objects:

```bash
sapcli bdef activate ZMYBDEF ZMYBDEF2 ZMYBDEF3
```

## delete

Delete behavior definition

```bash
sapcli bdef delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given behavior definition

```bash
sapcli bdef whereused ZMYBDEF
```

## listinterfaces

List BO interfaces assigned to a behavior definition. This is useful for
discovering valid interface names when creating behavior extensions.

```bash
sapcli bdef listinterfaces BDEF_NAME
```

### Examples

List interfaces for a behavior definition:

```bash
sapcli bdef listinterfaces R_PRODUCTTP
```
