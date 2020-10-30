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
sapcli cts create [transport,task] [--description DESCRIPTION] [--target TARGET]
```

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
