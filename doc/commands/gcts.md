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

```bash
sapcli gcts clone URL [package]
```

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

## log

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
