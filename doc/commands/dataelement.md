# Data Element

- [Data Element](#data-element)
	- [define](#define)

## define

Define an ABAP DDIC Data Element.

```bash
sapcli dataelement define DATA_ELEMENT_NAME --type=domain|predefinedAbapType [--corrnr TRANSPORT] [--activate] [--no-error-existing] [--domain_name] [--data_type] [--data_type_length] [--data_type_decimals] [--label_short] [--label_medium] [--label_long] [--label_heading]
```

* _DATA\_ELEMENT\_NAME_ specifying the name of the data element
* _--type [domain|predefinedAbapType]_ type kind
* _--domain\_name_ domain name (e.g. BUKRS) [default = ''] - mandatory in case the _--type_=domain **(optional)**
* _--data\_type_ data type (e.g. CHAR) [default = ''] - mandatory in case the _--type_=predefinedAbapType **(optional)**
* _--data\_type\_length_ data type length (e.g. 5) [default = '0'] **(optional)**
* _--data\_type\_decimals_ data type decimals (e.g. 3) [default = '0'] **(optional)**
* _--label\_short_ short label [default = ''] **(optional)**
* _--label\_medium_ medium label [default = ''] **(optional)**
* _--label\_long_ long label [default = ''] **(optional)**
* _--label\_heading_ heading label [default = ''] **(optional)**
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number **(optional)**
* _--activate_ activate after finishing the data element modification **(optional)**
* _--no-error-existing_ do not fail if data element already exists **(optional)**
