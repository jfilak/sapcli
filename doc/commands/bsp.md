# BSP Applications

1. [upload](#upload)
2. [stat](#stat)
3. [delete](#delete)

## upload

Uploads the packed javascript sources for the BSP application `APP123` in package `SOME_PACKAGE`.
Be aware of:

* package and transport have to exist.
* zipped application codebase have to be preprocessed (minified), e.g. by
  [`@sap/ux-ui5-tooling`](https://www.npmjs.com/package/@sap/ux-ui5-tooling)
* if the application does not exist yet, it will be created automatically

```bash
sapcli bsp upload \
    --app=/some/dire/app.zip \
    --package=SOME_PACKAGE \
    --bsp=APP123 \
    --corrnr=C50K000167 \
```

## stat

Prints basic set of BSP application attributes. Returned exit could be interpreted as:

* `0` - application found
* `10` - application not found

```bash
sapcli bsp stat --bsp=APP123
```

which results in output similar to:

```
Name                   :APP123
Package                :SOME_PACKAGE
Description            :Application Description
```

## delete

Deletes a BSP application

```bash
sapcli bsp delete --bsp=APP123 --corrnr=C50K000167
```
