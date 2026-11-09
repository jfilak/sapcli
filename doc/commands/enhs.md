# Enhancement Spot (ENHS/XSB)

1. [list-implementations](#list-implementations)
2. [list-badi-definitions](#list-badi-definitions)

## list-implementations

List Enhancement Implementations of the given Enhancement Spot.

```bash
sapcli enhs list-implementations ENHANCEMENT_SPOT
```

* _ENHANCEMENT\_SPOT_ name of the ENHS object (Enhancement Spot)

The command prints out the name of each Enhancement Implementation
belonging to the given Enhancement Spot - one name per line.

### Examples

```bash
sapcli enhs list-implementations SSAMPLE_ENHS
```

```
MY_FABULOUS_ENHS_ONE
OPEN_SOURCE_IS_BEST
```

Use the command [badi](badi.md) to work with the BAdI implementations
of the listed Enhancement Implementations.

## list-badi-definitions

List BAdI Definitions of the given Enhancement Spot.

```bash
sapcli enhs list-badi-definitions ENHANCEMENT_SPOT [--noheadings] [--columns COLUMNS]
```

* _ENHANCEMENT\_SPOT_ name of the ENHS object (Enhancement Spot)
* _--noheadings_ do not print the table header
* _--columns COLUMNS_ comma separated list of visible columns; available columns:
  name, interface.name, single_use, use_fallback_class, short_text;
  the columns are always printed in this order

The column Interface holds the name of the ABAP interface that classes
implementing the BAdI must implement.

### Examples

```bash
sapcli enhs list-badi-definitions SSAMPLE_ENHS
```

```
Name        | Interface      | Single Use | Fallback Class | Short Text
-----------------------------------------------------------------------------
SAMPLE_ENHS | IF_SAMPLE_ENHS | false      | false          | BAdI for awesome
```

Use the command [enho](enho.md) to create an Enhancement Implementation of
the Enhancement Spot and the command [badi](badi.md) to create BAdI
Implementations in it.
