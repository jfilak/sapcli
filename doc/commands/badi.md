# BAdI (Enhancement Spot/Implementation)

1. [list](#list)
1. [set-active](#set-active)


## list

List BAdI implementations of a particular Enhancement Implementation

```bash
sapcli badi [-i|--enhancement_implementation ENHO] [list]
```

* _--enhancement_implementation ENHO_ name of the ENHO object (Enhancement Implementation)

## set-active

Change the definition of ABAP DDIC transparent table.

```bash
saplci badi [-i|--enhancement_implementation ENHO] set-active [-b|--badi NAME] [-a|--activate] [true|false]
```

* _--enhancement_implementation_ ENHO name of the ENHO object (Enhancement Implementation)
* _--name BADI_ name of the BAdI implementation
* _--activate_ run activation of the enhancement implementation after the change
* _[true|false]_ is the set value
