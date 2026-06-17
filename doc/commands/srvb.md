# Service Binding (SRVB)

CRUD commands for the ABAP RAP **Service Binding** object (`SRVB/SVB`).

The Service Binding has no `text/plain` source body. v1 supports CRUD
operations only; the `write` command is intentionally not provided in v1
because the binding's configuration lives in XML attributes/nodes which
require a JSON round-trip (planned for v2).

1. [create](#create)
2. [read](#read)
3. [activate](#activate)
4. [delete](#delete)
5. [whereused](#whereused)

## create

Creates a new (inactive) Service Binding wired to an existing Service
Definition. The server rejects an empty binding, so `--service` is required.

```bash
sapcli srvb create NAME DESCRIPTION PACKAGE \
                   --type {ODATA,INA,SQL} \
                   --version {V2,V4,1} \
                   --service SERVICE_DEFINITION_NAME \
                   [--service-version SERVICE_VERSION] \
                   [--corrnr TRANSPORT]
```

- **--type** - binding contract type. `ODATA`, `INA`, or `SQL`.
- **--version** - binding contract version. `V2` or `V4` for OData, `1` for INA/SQL.
- **--service** - name of the Service Definition (SRVD) that this binding exposes.
- **--service-version** - version of the wired Service Definition (default `0001`).
- **--corrnr** - transport request number.

## read

Print a structural summary of the binding (name, description, package, type,
version, published flag, list of bound services).

```bash
sapcli srvb read NAME
```

## activate

Activates the given Service Bindings.

```bash
sapcli srvb activate NAME [NAME ...] [--ignore-errors] [--warning-errors]
```

## delete

Deletes the given Service Bindings.

```bash
sapcli srvb delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given Service Binding.

```bash
sapcli srvb whereused NAME
```
