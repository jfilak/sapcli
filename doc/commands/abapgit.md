# abapGit

Commands for linking ABAP packages to git repositories, pulling their content,
listing linked repositories, and committing changes.

1. [abapGit APIs](#abapgit-apis)
2. [link](#link)
3. [pull](#pull)
4. [list](#list)
5. [commit](#commit)

## abapGit APIs

All commands accept the parameter `--api` which selects the abapGit API
sapcli talks to. If the parameter `--api` is not present, the value of the
environment variable `SAPCLI_ABAPGIT_API` is used and if that is not set
either, `steampunk` is used.

| Command  | `steampunk` | `rfc-via-classrun` |
|----------|-------------|--------------------|
| `link`   | yes         | yes                |
| `pull`   | yes         | yes                |
| `list`   | no          | yes                |
| `commit` | no          | yes                |

### steampunk

The ADT abapGit REST API (`/sap/bc/adt/abapgit/repos`) of SAP's abapGit fork
for SAP BTP ABAP Environment. The API must be available on the target ABAP
system.

### rfc-via-classrun

**Requirements**: the target ABAP system must have the following installed:

1. [abapGit developer version](https://docs.abapgit.org/user-guide/getting-started/install.html#install-developer-version) -
   the standalone report `ZABAPGIT` is not enough
2. [abapgit-api-rfc](https://github.com/abapGit/abapgit-api-rfc) - provides
   the function modules `ZABAPGIT_API_RFC_*` which sapcli calls

Without them, the commands fail. sapcli does not install them.

The commands `list` and `commit` call the function modules
`ZABAPGIT_API_RFC_LIST` and `ZABAPGIT_API_RFC_COMMITPUSH` with the table type
`ZABAPGIT_API_RFC_REPO_T`. These are not part of the abapgit-api-rfc main
branch yet - they are proposed in
[abapgit-api-rfc#14](https://github.com/abapGit/abapgit-api-rfc/pull/14).

The function modules are not called over RFC but from a temporary class
executed via ADT (the same way as [`sapcli abap run`](abap.md#run)), so
sapcli does not need PyRFC or any other RFC library and the user needs
authorizations to create, activate, execute, and delete a class in the
package `$TMP`. Mind that the values of the parameters, including
`--remote-password`, are part of the source code of the temporary class.

## link

Links an existing ABAP package to a remote git repository.

```bash
sapcli abapgit link [--api {steampunk,rfc-via-classrun}] [--branch BRANCH] \
                    [--remote-user USER] [--remote-password PASSWORD] [--corrnr CORRNR] \
                    [--folder-logic {PREFIX,FULL}] [--starting-folder FOLDER] \
                    [--ignore-subpackages] [--main-lang-only] \
                    PACKAGE URL
```

**Parameters**:
- `PACKAGE`: ABAP package to link; the name is converted to upper case
- `URL`: Remote git repository URL
- `--api {steampunk,rfc-via-classrun}`: abapGit API - see [abapGit APIs](#abapgit-apis)
- `--branch BRANCH`: Git branch to link; default is **refs/heads/master** for
  `steampunk` and the default branch of the remote repository for `rfc-via-classrun`
- `--remote-user USER`: User name for the remote git repository
- `--remote-password PASSWORD`: Password for the remote git repository
- `--corrnr CORRNR`: Transport request number; `steampunk` only
- `--folder-logic {PREFIX,FULL}`: abapGit folder logic; default is **PREFIX**; `rfc-via-classrun` only
- `--starting-folder FOLDER`: Repository folder with sources; default is **/src/**; `rfc-via-classrun` only
- `--ignore-subpackages`: Ignore subpackages; `rfc-via-classrun` only
- `--main-lang-only`: Serialize main language only; `rfc-via-classrun` only

The command fails if a parameter is not supported by the selected API.

With `steampunk`, sapcli prints `Repository was linked.` on success.

With `rfc-via-classrun`, the messages of the function module are printed and
the command fails if there is an error message.

**Example**:

```bash
sapcli abapgit link --branch refs/heads/main --corrnr NPLK900123 zhello_world https://github.com/example/zhello_world.git
sapcli abapgit link --api rfc-via-classrun --folder-logic FULL zhello_world https://github.com/example/zhello_world.git
```

## pull

Pulls content from the remote git repository to an ABAP package which has
already been linked (see [link](#link)).

```bash
sapcli abapgit pull [--api {steampunk,rfc-via-classrun}] [--branch BRANCH] \
                    [--remote-user USER] [--remote-password PASSWORD] [--corrnr CORRNR] \
                    PACKAGE
```

**Parameters**:
- `PACKAGE`: Linked ABAP package; the name is converted to upper case
- `--api {steampunk,rfc-via-classrun}`: abapGit API - see [abapGit APIs](#abapgit-apis)
- `--branch BRANCH`: Git branch to pull; by default, the branch configured for
  the linked repository is used; `steampunk` only
- `--remote-user USER`: User name for the remote git repository
- `--remote-password PASSWORD`: Password for the remote git repository
- `--corrnr CORRNR`: Transport request number

With `steampunk`, the pull runs in the background on the ABAP system. sapcli
triggers it, checks the repository status every second and prints a progress
indicator while the pull is running. When the pull finishes, sapcli prints the
repository status text. If the status is Error or Aborted, the status text and
all non-success messages from the repository log are printed to the standard
error output in the form:

```
MSG_TYPE: OBJECT_TYPE OBJECT_NAME:  MESSAGE_TEXT
```

With `rfc-via-classrun`, the messages of the function module are printed and
the command fails if there is an error message. The branch linked to the package
is pulled, hence the parameter `--branch` is not supported. Locally modified
objects and objects from unexpected packages are overwritten.

**Example**:

```bash
sapcli abapgit pull --corrnr NPLK900123 zhello_world
sapcli abapgit pull --api rfc-via-classrun --corrnr NPLK900123 zhello_world
```

## list

Lists git repositories linked to ABAP packages.

```bash
sapcli abapgit list [--api {steampunk,rfc-via-classrun}]
```

**Parameters**:
- `--api {steampunk,rfc-via-classrun}`: abapGit API - see [abapGit APIs](#abapgit-apis)

The command is implemented only for `rfc-via-classrun` and fails with the message
`not implemented` for `steampunk`.

The repositories are printed as a table with the columns Key, Package, Name, URL,
Branch and Deserialized At (UTC).

```
Key          | Package       | Name | URL                                       | Branch          | Deserialized At
--------------------------------------------------------------------------------------------------------------------
000000000008 | $SAPCLI_AGRFC | CLAS | https://github.com/abapGit-tests/CLAS.git | refs/heads/main | 2026-10-17 20:09:31
```

## commit

Commits all changes of a package and pushes them to the linked remote repository.

```bash
sapcli abapgit commit [--api {steampunk,rfc-via-classrun}] [--remote-user USER] [--remote-password PASSWORD] \
                      -m MESSAGE [--description DESCRIPTION] \
                      [--committer-name NAME] [--committer-email EMAIL] \
                      [--author-name NAME] [--author-email EMAIL] \
                      PACKAGE
```

**Parameters**:
- `PACKAGE`: Linked ABAP package; the name is converted to upper case
- `--api {steampunk,rfc-via-classrun}`: abapGit API - see [abapGit APIs](#abapgit-apis)
- `--remote-user USER`: User name for the remote git repository
- `--remote-password PASSWORD`: Password for the remote git repository
- `-m MESSAGE, --message MESSAGE`: Commit summary; mandatory
- `--description DESCRIPTION`: Commit body which may span several lines
- `--committer-name NAME`, `--committer-email EMAIL`: Committer
- `--author-name NAME`, `--author-email EMAIL`: Author

The command is implemented only for `rfc-via-classrun` and fails with the message
`not implemented` for `steampunk`.

If the committer is not given, abapGit settings of the repository, abapGit
default settings, the user master record and finally the SAP user name are used.

The messages of the function module, including the list of committed objects,
are printed and the command fails if there is an error message.

**Example**:

```bash
sapcli abapgit commit --api rfc-via-classrun -m "Fix greeting" zhello_world
```
