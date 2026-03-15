# DataDefinition (CDS)

1. [read](#read)
2. [activate](#activate)
3. [delete](#delete)
4. [whereused](#whereused)

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
