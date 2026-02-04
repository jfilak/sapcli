# Change Transport System (CTS)

1. [list](#list)
2. [create](#create)
3. [release](#release)
5. [reassign](#reassign)
4. [delete](#delete)

## list

Get list of CTS requests

```bash
sapcli cts list {transport,task} [--recursive|--recursive|...] [--owner login]
```

## create

Create a CTS request - either Transport or Transport Task

```bash
sapcli cts create [transport,task] [--description DESCRIPTION] [--target TARGET] [--transport-type TYPE]
```

The parameter *--transport-type* specifies the type of transport to create and is only applicable when creating a transport (not a task). The default value is *workbench*.

Available transport types:
- *workbench* (K) - Workbench request
- *customizing* (W) - Customizing request
- *transport-of-copies* (T) - Transport of Copies
- *development-correction* (S) - Development/Correction
- *repair* (R) - Repair

## release

Release CTS request - either Transport or Transport Task

```bash
sapcli cts release [transport,task] [--recursive] $number
```

When applied to a transport, the parameter *--recursive* causes that
unreleased tasks of the given transport are released first.

## reassign

Change owner of a CTS request - either Transport or Transport Task

```bash
sapcli cts reassign [transport,task] [--recursive] NUMBER OWNER
```

When applied to a transport, the parameter *--recursive* causes that
unreleased tasks of the given transport are reassigned too.

## delete

Delete a CTS request - either Transport or Transport Task

```bash
sapcli cts delete [transport,task] [--recursive] NUMBER
```

When applied to a transport, the parameter *--recursive* causes that
unreleased tasks of the given transport are deleted too.
