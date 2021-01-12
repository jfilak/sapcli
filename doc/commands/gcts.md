# git enabled Change Transport System (gCTS)

sapcli's implementation forces use of packages as git repositories.

1. [repolist](#repolist)
2. [clone](#clone)
3. [checkout](#checkout)
4. [log](#log)
5. [pull](#pull)
6. [delete](#delete)
7. [config](#config)

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
- `--starting-folder FOLDER`: The directory inside the repository where to store ABAP files.
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

## log

Print out repository history log

```bash
sapcli gcts log PACKAGE
```

## pull

Pulls the repository on the system

```bash
sapcli gcts pull PACKAGE
```

## delete

Removes the repository not the package

```bash
sapcli gcts delete PACKAGE
```

## config

Configure the given repository

```bash
sapcli gcts config [-l|--list] PACKAGE
```
