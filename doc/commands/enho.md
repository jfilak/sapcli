# BAdI Enhancement Implementation (ENHO/XHB)

An Enhancement Implementation is the transportable container of BAdI
Implementations of one Enhancement Spot. Use the command [badi](badi.md) to
work with the BAdI Implementations of an Enhancement Implementation.

1. [create](#create)
2. [activate](#activate)
3. [delete](#delete)
4. [whereused](#whereused)

## create

Creates a BAdI Enhancement Implementation of the given name with the given
description in the given package for the given Enhancement Spot. The created
Enhancement Implementation contains no BAdI Implementation.

```bash
sapcli enho create NAME DESCRIPTION PACKAGE -s|--enhancement-spot ENHANCEMENT_SPOT [--corrnr TRANSPORT]
```

* _NAME_ name of the new Enhancement Implementation
* _DESCRIPTION_ description of the new Enhancement Implementation
* _PACKAGE_ package of the new Enhancement Implementation
* _--enhancement-spot ENHANCEMENT\_SPOT_ the Enhancement Spot whose BAdI Definitions will be implemented
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed

### Examples

```bash
sapcli enho create ZSAPCLI_ENH_IMPL "Sample implementations" '$PACKAGE' --enhancement-spot SSAMPLE_ENHS
```

## activate

Activates the given Enhancement Implementations in the given order.

```bash
sapcli enho activate [--ignore-errors] [--warning-errors] NAME NAME ...
```

* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

## delete

Deletes the given Enhancement Implementations

```bash
sapcli enho delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given Enhancement Implementation

```bash
sapcli enho whereused NAME
```
