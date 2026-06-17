# rap (deprecated)

The `rap` command group is **deprecated**. Both subcommands listed here
emit a stderr deprecation warning when invoked and delegate to the new
top-level `srvd` / `srvb` groups. They will be removed in the next
minor release.

| Old (deprecated)                | New equivalent              |
| ------------------------------- | --------------------------- |
| `sapcli rap definition activate` | `sapcli srvd activate`      |
| `sapcli rap binding publish`     | `sapcli srvb publish`       |

For full CRUD on Service Definitions and Service Bindings, see:

- [`doc/commands/srvd.md`](srvd.md)
- [`doc/commands/srvb.md`](srvb.md)

## definition activate (deprecated)

Activates the given Business Service Definition. Same semantics as
`sapcli srvd activate`; this alias only writes a deprecation warning
to stderr and forwards.

```bash
sapcli rap definition activate NAME [NAME [NAME ...]]
```

## binding publish (deprecated)

Publishes a desired oData service name or oData service version in the
corresponding service binding. Same semantics as `sapcli srvb publish`;
this alias only writes a deprecation warning to stderr and forwards.

```bash
sapcli rap binding publish BINDING_NAME [--service SERVICE_NAME] [--version SERVICE_VERSION]
```
