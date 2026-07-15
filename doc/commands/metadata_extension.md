# MetadataExtension (DDLX/EX)

CDS Metadata Extension operations.

1. [create](#create)
2. [read](#read)
3. [write](#write)
4. [activate](#activate)
5. [delete](#delete)
6. [whereused](#whereused)
7. [edit](#edit)

## create

Creates a CDS Metadata Extension of the given name with the given description
in the given package.

```bash
sapcli ddlx create Z_MD_EXT "Metadata Extension description" '$PACKAGE' [--corrnr TRANSPORT]
```

## read

Download source code of the given CDS Metadata Extension.

```bash
sapcli ddlx read Z_MD_EXT
```

## write

Change the source code of the given CDS Metadata Extension.

```bash
sapcli ddlx write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors] [--check] [--no-check]
```

* _OBJECT\_NAME_ either the Metadata Extension name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, a single file path or - for reading _stdin_; otherwise a space separated list of file paths
* _--corrnr TRANSPORT_ specifies the CTS Transport Request Number if needed
* _--activate_ activate after the write operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors
* _--check_ run abapCheckRun before writing source code (overrides SAPCLI\_CHECK\_BEFORE\_SAVE)
* _--no-check_ skip abapCheckRun before writing source code (overrides SAPCLI\_CHECK\_BEFORE\_SAVE)

### Examples

Write from a file:

```bash
sapcli ddlx write Z_MD_EXT z_md_ext.ddlxs
```

Write from stdin:

```bash
cat z_md_ext.ddlxs | sapcli ddlx write Z_MD_EXT -
```

Write and activate:

```bash
sapcli ddlx write Z_MD_EXT z_md_ext.ddlxs --activate
```

Write multiple files (object name deduced from filename):

```bash
sapcli ddlx write - z_md_ext.ddlxs z_md_ext2.ddlxs z_md_ext3.ddlxs
```

## activate

Activates the given CDS Metadata Extensions in the given order.

```bash
sapcli ddlx activate [--ignore-errors] [--warning-errors] NAME [NAME ...]
```

* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

### Examples

Activate a single object:

```bash
sapcli ddlx activate Z_MD_EXT
```

Activate multiple objects:

```bash
sapcli ddlx activate Z_MD_EXT Z_MD_EXT2 Z_MD_EXT3
```

## delete

Delete the given CDS Metadata Extension.

```bash
sapcli ddlx delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given CDS Metadata Extension.

```bash
sapcli ddlx whereused Z_MD_EXT
```

## edit

Fetch the source code of the given CDS Metadata Extension, open it in the
user's editor, and write it back if it was modified.

```bash
sapcli ddlx edit Z_MD_EXT [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors] [--check] [--no-check]
```

* _--corrnr TRANSPORT_ specifies the CTS Transport Request Number if needed
* _--activate_ activate after the edit operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors
* _--check_ run abapCheckRun before writing source code (overrides SAPCLI\_CHECK\_BEFORE\_SAVE)
* _--no-check_ skip abapCheckRun before writing source code (overrides SAPCLI\_CHECK\_BEFORE\_SAVE)
