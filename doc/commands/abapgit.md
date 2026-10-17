# Abapgit

## Link

Links existing package to remote repository in abapgit

```bash
sapcli abapgit link [--api {steampunk,rfc-via-classrun}] [--remote-user USER] [--remote-password PASSWORD] [--branch BRANCH] [--corrnr CORRNR]
                    [--folder-logic {PREFIX,FULL}] [--starting-folder FOLDER] [--ignore-subpackages] [--main-lang-only]
                    PACKAGE URL
```

The parameter `--api` selects the abapGit API:

- `steampunk` (default) - the ADT abapGit API of SAP's abapGit fork for SAP BTP ABAP Environment
- `rfc-via-classrun` - the function module `ZABAPGIT_API_RFC_LINK` of
  [abapgit-api-rfc](https://github.com/jfilak/abapgit-api-rfc). The function
  module is not called over RFC but from a temporary class executed via ADT
  (the same way as `sapcli abap run`), so no RFC libraries are needed. Mind
  that the values of the parameters, including `--remote-password`, are
  part of the source code of the temporary class.

If the parameter `--api` is not present, the value of the environment variable
`SAPCLI_ABAPGIT_API` is used and if that is not set either, `steampunk` is used.

If the parameter `--branch` is not present, the `refs/heads/master` value is used
for `steampunk` and the default branch of the remote repository for `rfc-via-classrun`.

The parameter `--corrnr` is supported only by `steampunk`. The parameters
`--folder-logic` (default `PREFIX`), `--starting-folder` (default `/src/`),
`--ignore-subpackages` and `--main-lang-only` are supported only by `rfc-via-classrun`.

## Pull

Pulls content from remote repositopry to a package.

After the operation completes, repository status is reported. If status is Error or Aborted, errors and warning from repository are printed.

```bash
sapcli abapgit pull [--remote-user USER] [--remote-password PASSWORD] [--branch BRANCH] [--corrnr CORRNR] PACKAGE
```

If the parameter `--branch` is not present, the `refs/heads/master` value is used.
