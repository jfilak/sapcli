# Activation

1. [inactiveobjects](#inactiveobjects)
2. [objects](#objects)

## inactiveobjects

Deals with Inactive Objects

1. [list](#list)
2. [activate](#activate)

### list

List of all inactive objects

```bash
sapcli activation inactiveobjects list
```

### activate

Activate every object currently in the user's inactive worklist in a
single ADT activation request. Submitting all related inactive objects
together lets the kernel resolve cross-references in one transaction,
which is what the per-object CLI activation cannot do.

```bash
sapcli activation inactiveobjects activate [--dry-run] [--ignore-errors] [--warning-errors]
```

* _--dry-run_, _-n_ list the objects that would be activated, then exit
* _--ignore-errors_ return success even if activation reports errors
* _--warning-errors_ treat activation warnings as errors

## objects

Activate a specific set of named objects.

1. [activate](#activate-1)

### activate

Bundle-activate the explicit list of objects passed via repeated
`--object KIND=NAME` flags. Same single-request semantics as
`inactiveobjects activate`, useful when you want to activate only a
subset of your worklist or when ABAP objects you have just edited are
not yet visible in the worklist.

```bash
sapcli activation objects activate --object KIND=NAME [--object KIND=NAME ...] [--list-kinds] [--dry-run] [--ignore-errors] [--warning-errors]
```

* _--object KIND=NAME_ add an object to the bundle (repeat for multiple)
* _--list-kinds_ print the supported KINDs and exit
* _--dry-run_, _-n_ list the objects that would be activated, then exit
* _--ignore-errors_ return success even if activation reports errors
* _--warning-errors_ treat activation warnings as errors

Supported KINDs: `program` (alias `prog`), `include` (`incl`), `class`
(`clas`), `interface` (`intf`), `function-group` (`fugr`),
`function-module` (`fm`), `function-include`, `data-element`
(`dtel`), `domain` (`doma`), `table` (`tabl`), `structure` (`stru`),
`behavior-definition` (`bdef`), `message-class` (`msag`),
`transaction` (`tran`).

Examples:

```bash
# class definition include + its implementation include
sapcli activation objects activate \
    --object include=YOUR_INCLUDE_01 \
    --object include=YOUR_INCLUDE_02

# class + the interface it implements
sapcli activation objects activate \
    --object class=YOUR_CLASS \
    --object interface=YOUR_INTERFACE
```
