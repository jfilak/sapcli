# rap

## binding

1. [publish](#publish)

### publish

Publishes a desired oData service name or oData service version in the corresponding service binding

```bash
sapcli rap binding publish BINDING_NAME [--service SERVICE_NAME | --version SERVICE_VERSION]
```

If no SERVICE_NAME or SERVICE_VERSION is supplied and the binding contains only one service, that service will
be published by default.

