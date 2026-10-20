# checkout

This set of commands is intended for reading and writing whole packages.
Fetches all source codes of the given class and stores them in local files.

File format and names should be compatible with [abapGit](https://github.com/larshp/abapGit).

```bash
sapcli checkout class zcl_hello_world
```

Fetches source codes of the given program and stores it a local file.

```bash
sapcli checkout program z_hello_world
```

Fetches source codes of the given interface and stores it a local file.

```bash
sapcli checkout interface zif_hello_world
```

Fetches objects of given function group and stores objects' source codes to a local files.

```bash
sapcli checkout function_group zhello_world
```

Fetches attributes of the given table type and stores them in a local file.

```bash
sapcli checkout tabletype zhello_world_tab
```

Fetches source code and attributes of the given CDS data definition and stores
them in local files.

```bash
sapcli checkout ddl zhello_world_cds
```

Fetches source code and attributes of the given CDS access control and stores
them in local files.

```bash
sapcli checkout dcl zhello_world_role
```

Fetches source code and attributes of the given CDS metadata extension and
stores them in local files.

```bash
sapcli checkout ddlx zhello_world_ext
```

Fetches source codes of classes, programs, interfaces, function groups,
table types, CDS data definitions, CDS access controls, and CDS metadata
extensions of the given package
and stores them in corresponding files in a local file system directory.

The new directory is populated with the file _.abapgit.xml_ which has the format
recognized by [abapGit](https://github.com/larshp/abapGit).

```bash
sapcli checkout package '$hello_world' [directory] [--recursive] [--starting-folder DIR]
```

* _directory_ the name of a new directory to checkout the given package into;
  if not provided, the package name is used instead

* _--starting-folder_ forces sapcli to create the corresponding object files in
  the given directory; by default, sapcli uses the directory `src`

* _--recursive_ forces sapcli to download also the sub-packages into sub-directories

## Text elements

Text symbols of classes and programs (`TEXT-001`) are stored as the entries
with ID `I` in the section `TPOOL` of the files _.clas.xml_ and _.prog.xml_
the same way as abapGit does. They are read in the logon language.

```xml
   <TPOOL>
    <item>
     <ID>I</ID>
     <KEY>001</KEY>
     <ENTRY>Hello, world!</ENTRY>
     <LENGTH>20</LENGTH>
    </item>
   </TPOOL>
```

The command `sapcli checkin package` writes the text symbols in the logon
language and activates them together with the class or the program. Other text
pool entries such as selection texts (ID `S`) and list headings (IDs `H` and
`T`) are not supported yet - checkin skips them with a warning. Program titles
(ID `R`) are used as program descriptions as before. Includes do not have own
text elements, so checkin skips their text symbols with a warning too.


## Table types

Table types are stored in the files _.ttyp.xml_ with the sections `DD40V`
(header) and `DD42V` (primary key components) the same way as abapGit does.
Only table types of DDIC types (structures, tables, data elements, table types)
and of predefined ABAP types are supported - range table types and table types
of references are not.

The command `sapcli checkin package` creates table types before classes,
interfaces, and programs to allow them to use the table types. Secondary keys
(`DD43V`) are not supported yet - both checkin and checkout skip them with
a warning.

Checkout does not write the fields `TYPELEN` and `ROWTYPEPOS` because ADT does
not provide them. Checkin does not need them.


## Data definitions

CDS data definitions (DDL sources) are stored in the files _.ddls.asddls_
(source code) and _.ddls.xml_ (attributes in the section `DDLS`) the same way
as abapGit does.

The command `sapcli checkin package` creates data definitions together with
table types before classes, interfaces, and programs to allow them to use the
data definitions. Checkin accepts but does not need the files _.ddls.baseinfo_
because ADT computes the list of used objects from the source code.

Checkout does not write the files _.ddls.baseinfo_ and the field
`SOURCE_ORIGIN`. ADT does not provide the abapGit codes of `SOURCE_TYPE`, so
checkout derives them from the definition statement - `V` (view), `W` (view
entity), `P` (projection view), `F` (table function), and `A` (abstract entity).
Checkout leaves out `SOURCE_TYPE` of other data definitions with a warning.


## Access controls

CDS access controls (DCL sources) are stored in the files _.dcls.asdcls_
(source code) and _.dcls.xml_ (attributes in the section `DCLS`) the same way
as abapGit does.

The command `sapcli checkin package` creates access controls after all other
objects to allow them to use the data definitions the same way as abapGit
deserializes them in the late step.


## Metadata extensions

CDS metadata extensions are stored in the files _.ddlx.asddlxs_ (source code)
and _.ddlx.xml_ (attributes in the section `DDLX`) the same way as abapGit
does. Unlike the other objects, the section `DDLX` holds the original language
as an ISO code (e.g. `EN`).

The command `sapcli checkin package` creates metadata extensions after data
definitions to allow them to annotate the data definitions. Old abapGit
versions stored the source code in the file _.ddlx.xml_ - checkin does not
support such files and reports the missing file _.ddlx.asddlxs_ instead.
