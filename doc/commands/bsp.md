# BSP Applications

1. [create](#create)

## create

Creates new BSP application `APP123` in package `SOME_PACKAGE` and uploads
packed javascript sources. Be aware of:
* package and transport have to exist.
* zipped application codebase have to be preprocessed (minified), e.g. by
  [`@sap/ux-ui5-tooling`](https://www.npmjs.com/package/@sap/ux-ui5-tooling)
* it is not possible to upload zipped codebase to existing appllication yet
  (application cannot exist).

```bash
sapcli bsp create \
    --app=/some/dire/app.zip \
    --package=SOME_PACKAGE \
    --bsp=APP123 \
    --corrnr=C50K000167 \
```

