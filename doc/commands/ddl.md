# DataDefinition (CDS)

1. [read](#read)
2. [activate](#activate)
3. [delete](#delete)
4. [whereused](#whereused)
5. [apistate list](#apistate-list)
6. [apistate set](#apistate-set)

## activate

Activates the given CDS views in the given order

```bash
sapcli ddl activate ZCDS1 ZCDS2 ZCDS3 ...
```

## read

Download main source codes of the given public CDS view

```bash
sapcli ddl read ZCDS1
```

## delete

Delete CDS view

```bash
sapcli ddl delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given CDS view

```bash
sapcli ddl whereused ZCDS1
```

## apistate list

List API release states for the given CDS view. Displays the release state,
description, and authorization default value for each contract level (C0-C4).

```bash
sapcli ddl apistate list ZCDS1
```

Sample output:

```
Extended (Contract C0): not set
Use System-Internally (Contract C1):
  Release State: Released
  Local Comment: 
  Use in Cloud Development: No
  Use in Key User Apps: Yes
  Authorization Default Value: disabled
Use as Remote API (Contract C2): not set
Contract C3: not set
Contract C4: not set
```

## apistate set

Set API release state for a specific contract level. The command validates the
change with the server before applying it. If validation returns warnings, the
user is prompted for confirmation unless `--force` is specified.

```bash
sapcli ddl apistate set CONTRACT NAME [--state STATE] [--comment COMMENT] [--cloud-dev YES|NO] [--key-user-apps YES|NO] [--corrnr TRANSPORT] [--force]
```

- **CONTRACT** - contract level: c0, c1, c2, c3, c4
- **NAME** - CDS view name
- **--state** - release state value (e.g. RELEASED, DEPRECATED, NOT_RELEASED)
- **--comment** - free-text comment
- **--cloud-dev** - use in Cloud Development: Yes or No
- **--key-user-apps** - use in Key User Apps: Yes or No
- **--corrnr** - transport request number
- **--force** - skip confirmation on validation warnings
