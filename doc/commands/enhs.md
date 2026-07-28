# Enhancement Spot (ENHS/XSB)

1. [list-implementations](#list-implementations)

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
