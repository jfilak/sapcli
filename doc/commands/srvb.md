# Service Binding (SRVB)

CRUD commands for the ABAP RAP **Service Binding** object (`SRVB/SVB`),
plus `publish`, `unpublish` and a `preview` sub-group for inspecting the
bound OData service at runtime.

The Service Binding has no `text/plain` source body, so a top-level
`write` command is not provided - the binding's configuration lives in
XML attributes/nodes which require a JSON round-trip (planned for a
future version).

1. [create](#create)
2. [read](#read)
3. [activate](#activate)
4. [publish](#publish)
5. [unpublish](#unpublish)
6. [delete](#delete)
7. [whereused](#whereused)
8. [preview](#preview)
   - [preview metadata](#preview-metadata)
   - [preview fetch](#preview-fetch)
   - [preview html](#preview-html)

## create

Creates a new (inactive) Service Binding wired to an existing Service
Definition. The server rejects an empty binding, so `--service-definition`
is required.

```bash
sapcli srvb create NAME DESCRIPTION PACKAGE \
                   --binding-type {ODATAV2_UI,ODATAV2_API,ODATAV4_UI,ODATAV4_API} \
                   --service-definition SERVICE_DEFINITION_NAME \
                   [--service-version SERVICE_VERSION] \
                   [--corrnr TRANSPORT]
```

- **--binding-type** - Service Binding type. Selects both contract
  (OData V2 / V4) and category (`UI` or `API`).
- **--service-definition** - name of the Service Definition (SRVD) that
  this binding exposes.
- **--service-version** - version of the wired Service Definition
  (default: `0001`).
- **--corrnr** - transport request number.

## read

Print a structural summary of the binding (name, description, package,
type, version, published flag, list of bound services).

```bash
sapcli srvb read NAME
```

## activate

Activates the given Service Bindings.

```bash
sapcli srvb activate NAME [NAME ...] [--ignore-errors] [--warning-errors]
```

- **--ignore-errors** - do not stop activation in case of errors.
- **--warning-errors** - treat activation warnings as errors.

## publish

Publish the OData / INA / SQL service exposed by the binding to its
local service endpoint.

```bash
sapcli srvb publish BINDING_NAME [--service SERVICE_NAME] [--version SERVICE_VERSION]
```

If the binding contains exactly one service, omitting `--service` and
`--version` publishes that one. Otherwise, the two filters narrow which
`<srvb:content>` entry is selected.

## unpublish

Unpublish the OData service exposed by the binding from its
local service endpoint.

```bash
sapcli srvb unpublish BINDING_NAME [--service SERVICE_NAME] [--version SERVICE_VERSION] \
                      [--activate] [--ignore-errors] [--warning-errors]
```

If the binding contains exactly one service, omitting `--service` and
`--version` unpublishes that one. Otherwise, the two filters narrow which
`<srvb:content>` entry is selected.

- **--service** - service name of the binding's service to unpublish.
- **--version** - version of the binding's service to unpublish.
- **-a**, **--activate** - activate the Service Binding after a
  successful unpublish.
- **--ignore-errors** - do not stop activation in case of errors (only
  takes effect together with `--activate`).
- **--warning-errors** - treat activation warnings as errors (only takes
  effect together with `--activate`).

## delete

Deletes the given Service Bindings.

```bash
sapcli srvb delete NAME [NAME ...] [--corrnr TRANSPORT]
```

- **--corrnr** - transport request number.

## whereused

Find objects that reference the given Service Binding.

```bash
sapcli srvb whereused NAME
```

## preview

Sub-group of utilities for previewing the OData service exposed by a
Service Binding without leaving the command line. Each command takes
the binding name and, when the binding contains more than one Service
Definition, requires `--service` to disambiguate.

### preview metadata

Download and print the OData `$metadata` document of the bound service.

```bash
sapcli srvb preview metadata BINDING_NAME [--service SERVICE_NAME]
```

- **--service** - name of the binding's service to preview. Required
  only when the binding contains more than one Service Definition.

### preview fetch

Fetch entries of an entity set from the bound OData service and print
the JSON response.

```bash
sapcli srvb preview fetch BINDING_NAME ENTITY_SET [--service SERVICE_NAME]
```

- **ENTITY_SET** - name of the OData entity set to read (e.g.
  `BookSet`).
- **--service** - name of the binding's service to preview. Required
  only when the binding contains more than one Service Definition.

### preview html

Download and print the Fiori launchpad preview HTML page for the given
entity set of one of the services bound by a Service Binding, or - with
`--open` - open that page in the default web browser instead.

The command targets the ADT `feap/.../flp.html` endpoint and is
currently implemented for **OData V4** bindings only; running it against
an OData V2 binding raises an error before any preview request is
issued.

```bash
sapcli srvb preview html BINDING_NAME ENTITY_SET [--service SERVICE_NAME] [--open]
```

- **ENTITY_SET** - name of the OData entity set to preview (e.g.
  `BookSet`).
- **--service** - name of the binding's service to preview. Required
  only when the binding contains more than one Service Definition.
- **--open** - open the preview page in the default web browser
  instead of downloading its HTML. Uses Python's OS-agnostic
  `webbrowser` module, so it works on Linux, macOS and Windows.
