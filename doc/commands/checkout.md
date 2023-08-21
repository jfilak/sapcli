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

Fetches source codes of classes, programs and interfaces of the given package
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

