# Abapgit

## Link

Links existing package to remote repository in abapgit

```bash
sapcli abapgit link [--remote-user USER] [--remote-password PASSWORD] [--branch BRANCH] [--corrnr CORRNR] PACKAGE URL
```

If the parameter `--branch` is not present, the `refs/heads/master` value is used.

## Pull

Pulls content from remote repositopry to a package.

After the operation completes, repository status is reported. If status is Error or Aborted, errors and warning from repository are printed.

```bash
sapcli abapgit pull [--remote-user USER] [--remote-password PASSWORD] [--branch BRANCH] [--corrnr CORRNR] PACKAGE
```

If the parameter `--branch` is not present, the `refs/heads/master` value is used.
