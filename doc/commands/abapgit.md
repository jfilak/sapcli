# Abapgit

## abapGit APIs

The commands `link`, `pull` and `list` accept the parameter `--api` which selects the abapGit API:

- `steampunk` (default) - the ADT abapGit API of SAP's abapGit fork for SAP BTP ABAP Environment
- `rfc-via-classrun` - the function modules `ZABAPGIT_API_RFC_*` of
  [abapgit-api-rfc](https://github.com/jfilak/abapgit-api-rfc). The function
  modules are not called over RFC but from a temporary class executed via ADT
  (the same way as `sapcli abap run`), so no RFC libraries are needed. Mind
  that the values of the parameters, including `--remote-password`, are
  part of the source code of the temporary class.

If the parameter `--api` is not present, the value of the environment variable
`SAPCLI_ABAPGIT_API` is used and if that is not set either, `steampunk` is used.

## Link

Links existing package to remote repository in abapgit

```bash
sapcli abapgit link [--api {steampunk,rfc-via-classrun}] [--remote-user USER] [--remote-password PASSWORD] [--branch BRANCH] [--corrnr CORRNR]
                    [--folder-logic {PREFIX,FULL}] [--starting-folder FOLDER] [--ignore-subpackages] [--main-lang-only]
                    PACKAGE URL
```

The parameter `--api` selects the abapGit API - see [abapGit APIs](#abapgit-apis).

If the parameter `--branch` is not present, the `refs/heads/master` value is used
for `steampunk` and the default branch of the remote repository for `rfc-via-classrun`.

The parameter `--corrnr` is supported only by `steampunk`. The parameters
`--folder-logic` (default `PREFIX`), `--starting-folder` (default `/src/`),
`--ignore-subpackages` and `--main-lang-only` are supported only by `rfc-via-classrun`.

## Pull

Pulls content from remote repositopry to a package.

```bash
sapcli abapgit pull [--api {steampunk,rfc-via-classrun}] [--remote-user USER] [--remote-password PASSWORD] [--branch BRANCH] [--corrnr CORRNR] PACKAGE
```

The parameter `--api` selects the abapGit API - see [abapGit APIs](#abapgit-apis).

With `steampunk`, after the operation completes, repository status is reported.
If status is Error or Aborted, errors and warning from repository are printed.
If the parameter `--branch` is not present, the `refs/heads/master` value is used.

With `rfc-via-classrun`, the messages of the function module are printed and
the command fails if there is an error message. The branch linked to the package
is pulled, hence the parameter `--branch` is not supported. Locally modified
objects and objects from unexpected packages are overwritten.

## List

Lists git repositories linked to ABAP packages.

```bash
sapcli abapgit list [--api {steampunk,rfc-via-classrun}]
```

The parameter `--api` selects the abapGit API - see [abapGit APIs](#abapgit-apis).
The command is implemented only for `rfc-via-classrun` and fails with the message
`not implemented` for `steampunk`.

The repositories are printed as a table with the columns Key, Package, Name, URL,
Branch and Deserialized At (UTC).

```
Key          | Package       | Name | URL                                       | Branch          | Deserialized At
--------------------------------------------------------------------------------------------------------------------
000000000008 | $SAPCLI_AGRFC | CLAS | https://github.com/abapGit-tests/CLAS.git | refs/heads/main | 2026-10-17 20:09:31
```
