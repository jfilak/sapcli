# rap

## binding

1. [publish](#publish)

### publish

Publishes a desired oData service name or oData service version in the corresponding service binding

```bash
sapcli rap binding publish BINDING_NAME [--service SERVICE_NAME] [--version SERVICE_VERSION]
```

**Parameters**:
- `BINDING_NAME`: A business service binding whose service definition will be published
- `--service SERVICE_NAME`: Name of the service to publish
- `--version SERVICE_VERSION`: Version of the service to publish

If no SERVICE\_NAME nor SERVICE\_VERSION is supplied and the binding contains only
one service, that service will be published by default. Otherwise, the command
will exit with non-0 code and action will be performed.

If SERVICE\_NAME or SERVICE\_VERSION or both values are supplied, a first service
matching the give parameters will be published. If there is no such a service,
the operation will be aborted and sapcli will exit with non-0 code.
