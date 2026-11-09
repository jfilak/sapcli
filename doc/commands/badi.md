# BAdI (Enhancement Spot/Implementation)

1. [list](#list)
1. [set-active](#set-active)


## list

List BAdI implementations of a particular Enhancement Implementation

```bash
sapcli badi -i|--enhancement_implementation ENHO [list [--noheadings] [--columns COLUMNS]]
```

* _--enhancement_implementation ENHO_ name of the ENHO object (Enhancement Implementation)
* _--noheadings_ do not print the table header
* _--columns COLUMNS_ comma separated list of visible columns; available columns:
  name, active, implementing_class.name, badi_definition.name, customizing_lock,
  default, example, short_text; the columns are always printed in this order

## set-active

Change the Active flag of a BAdI implementation in a particular Enhancement Implementation

```bash
sapcli badi -i|--enhancement_implementation ENHO set-active -b|--badi NAME [--corrnr TRANSPORT] [-a|--activate] true|false
```

* _--enhancement_implementation ENHO_ name of the ENHO object (Enhancement Implementation)
* _--badi NAME_ name of the BAdI implementation
* _--corrnr TRANSPORT_ transport number
* _--activate_ run activation of the enhancement implementation after the change
* _true|false_ is the set value
