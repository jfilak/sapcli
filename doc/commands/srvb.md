# Service Binding (SRVB)

CRUD commands for the ABAP RAP **Service Binding** object (`SRVB/SVB`).

The Service Binding has no `text/plain` source body. v1 supports CRUD plus
`publish`. The `write` command is intentionally not provided in v1 - the
binding's configuration lives in XML attributes/nodes which require a
JSON round-trip (planned for v2).

1. [create](#create)
2. [read](#read)
3. [activate](#activate)
4. [publish](#publish)
5. [delete](#delete)
6. [whereused](#whereused)

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

## publish

Publish the OData / INA / SQL service exposed by the binding to its local
service endpoint.

```bash
sapcli srvb publish BINDING_NAME [--service SERVICE_NAME] [--version SERVICE_VERSION]
```

If the binding contains exactly one service, omitting `--service` and
`--version` publishes that one. Otherwise, the two filters narrow which
`<srvb:content>` entry is selected.

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
