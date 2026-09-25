# BAdI (Enhancement Spot/Implementation)

1. [list](#list)
1. [set-active](#set-active)


## list

List BAdI implementations of a particular Enhancement Implementation

```bash
sapcli badi [-i|--enhancement_implementation ENHO] [list [--noheadings] [--columns COLUMNS]]
```

* _--enhancement_implementation ENHO_ name of the ENHO object (Enhancement Implementation)
* _--noheadings_ do not print the table header
* _--columns COLUMNS_ comma separated list of visible columns; available columns:
  name, active, implementing_class.name, badi_definition.name, customizing_lock,
  default, example, short_text; the columns are always printed in this order

## set-active

Change the definition of ABAP DDIC transparent table.

```bash
saplci badi [-i|--enhancement_implementation ENHO] set-active [-b|--badi NAME] [-a|--activate] [true|false]
```

* _--enhancement_implementation_ ENHO name of the ENHO object (Enhancement Implementation)
* _--name BADI_ name of the BAdI implementation
* _--activate_ run activation of the enhancement implementation after the change
* _[true|false]_ is the set value
