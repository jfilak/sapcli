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

Fetches source codes of classes, programs, interfaces, function groups, and
table types of the given package
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
