# git enabled Change Transport System (gCTS)

sapcli's implementation forces use of packages as git repositories.

1. [repolist](#repolist)
2. [clone](#clone)
3. [checkout](#checkout)
4. [log](#log)
5. [pull](#pull)
6. [commit](#commit)
7. [delete](#delete)
8. [config](#config)
9. [user get-credentials](#user-get-credentials)
10. [user set-credentials](#user-set-credentials)
11. [user delete-credentials](#user-delete-credentials)
12. [repo set-url](#repo-set-url)
13. [repo property get](#repo-property-get)
14. [repo property set](#repo-property-set)

## repolist

Get list of ABAP packages versioned as gCTS repositories

```bash
sapcli gcts repolist
```

## clone

Creates and pulls a new repository. If the argument package is
not given, the name is taken from repository name.

```
sapcli gcts clone [--vsid VSID] [--starting-folder FOLDER] [--role ROLE] [--type TYPE] [--vcs-token TOKEN] URL [package]
```

**Parameters**:
- `--vsid VSID`: Virtual System ID of the repository; default is **6IT**
- `--starting-folder FOLDER`: The directory inside the repository where to store ABAP files; default is **src/**.
- `--role ROLE`: Either SOURCE (Development) or TARGET (Provided); default is **SOURCE**
- `--type TYPE`: Either GIT or GITHUB; default is **GITHUB**
- `--vcs-token TOKEN`: Authentication token
- `URL`: Repository HTTP URL
- `package`: gCTS repository name; if no provided, deduced from URL

## checkout

Checkout branch

```bash
sapcli gcts checkout PACKAGE BRANCH
```

**Parameters:**:
- `PACKAGE`: Repository name or URL

## log

Print out repository history log

```bash
sapcli gcts log PACKAGE
```

**Parameters:**:
- `PACKAGE`: Repository name or URL

## pull

Pulls the repository on the system

```bash
sapcli gcts pull PACKAGE
```

**Parameters:**:
- `PACKAGE`: Repository name or URL

## commit

Commits & pushes a transport to the correspoding repository

```bash
sapcli gcts commit PACKAGE CORRNR [-m|--message MESSAGE] [--description DESCRIPTION]
```

**Parameters:**:
- `PACKAGE`: Repository name or URL
- `CORRNR`: Transport number (e.g. from *sapcli cts list transport*)
- `--message MESSAGE`: Short commit messsage
- `--description DESCRIPTION`: Commit message body

## delete

Removes the repository not the package

```bash
sapcli gcts delete PACKAGE
```

**Parameters:**:
- `PACKAGE`: Repository name or URL

## config

Configure the given repository

```bash
sapcli gcts config [-l|--list] PACKAGE
```

**Parameters:**:
- `PACKAGE`: Repository name or URL
- `--list`: Lists all configuration options for the specified repository

## user get-credentials

Get credentials of the logged in user

```bash
sapcli gcts user get-credentials [-f|--format] {HUMAN|JSON}
```

**Parameters:**
- `--format`: The format of the command's output

## user set-credentials

Set credentials of the logged in user

```bash
sapcli gcts user set-credentials --api-url [URL] --token [TOKEN]
```

**Parameters:**:
- `--api-url [URL]`: API URL
- `--token [TOKEN]`: The secret token

## user delete-credentials

Delete credentials of the logged in user

```bash
sapcli gcts user delete-credentials --api-url [URL]
```

**Parameters:**
- `--api-url [URL]`: API URL to delete

## repo set-url

Change URL of the given repository identified by package name (sapcli tries to
push users to map packages to repositories).

```bash
sapcli gcts repo set-url PACKAGE URL
```

**Parameters:**:
- `PACKAGE`: The repository name
- `URL`: The new url

## repo property get

Get properties of the given repository.

```bash
sapcli gcts repo property get PACKAGE
```

**Parameters:**:
- `PACKAGE`: The repository name

## repo property set

Set the specified property of the given repository.

```bash
sapcli gcts repo property set PACKAGE PROPERTY_NAME VALUE
```

**Parameters:**:
- `PACKAGE`: The repository name
- `PROPERTY_NAME`: The name of the property that is to be changed
- `VALUE`: New value for the specified property


# Deprecated
- command [repo set-url](#repo-set-url) is replaced by [repo property set](#TODO) with property
  set to `url`
