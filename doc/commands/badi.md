# BAdI (Enhancement Spot/Implementation)

1. [list](#list)
1. [create](#create)
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

## create

Create a new active BAdI implementation in a particular Enhancement Implementation

```bash
sapcli badi -i|--enhancement_implementation ENHO create -b|--badi NAME -d|--badi-definition BADI_DEFINITION -c|--implementing-class CLASS [--corrnr TRANSPORT] [-a|--activate]
```

* _--enhancement_implementation ENHO_ name of the ENHO object (Enhancement Implementation)
* _--badi NAME_ name of the new BAdI implementation
* _--badi-definition BADI\_DEFINITION_ the implemented BAdI definition which must belong
  to the Enhancement Spot of the Enhancement Implementation
* _--implementing-class CLASS_ an existing ABAP class implementing the interface of the BAdI definition
* _--corrnr TRANSPORT_ transport number
* _--activate_ run activation of the enhancement implementation after the change

### Examples

The complete workflow of implementing a BAdI:

```bash
# find out the interface of the BAdI definition
sapcli enhs list-badi-definitions ZSAMPLE_ENHS

# create and activate the class implementing the interface ZIF_SAMPLE_BADI
sapcli class create ZCL_SAMPLE_BADI_IMPL "Sample BAdI implementation" '$PACKAGE'
sapcli class write ZCL_SAMPLE_BADI_IMPL zcl_sample_badi_impl.clas.abap --activate

# create the enhancement implementation and the BAdI implementation
sapcli enho create ZSAMPLE_ENHO "Sample implementations" '$PACKAGE' --enhancement-spot ZSAMPLE_ENHS
sapcli badi -i ZSAMPLE_ENHO create -b ZSAMPLE_BADI_IMPL -d ZSAMPLE_BADI -c ZCL_SAMPLE_BADI_IMPL --activate
```

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
