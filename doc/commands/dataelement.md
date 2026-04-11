# Data Element

- [Data Element](#data-element)
	- [define](#define)
	- [read](#read)
	- [delete](#delete)
	- [whereused](#whereused)

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

## read

Read and display a Data Element and its properties.

```bash
sapcli dataelement read DATA_ELEMENT_NAME [--format=ABAP|HUMAN]
```

* _DATA\_ELEMENT\_NAME_ specifying the name of the data element
* _--format_ output format for the data element details **(optional, default: HUMAN)**
  - `HUMAN` - human-readable format with labeled fields. For domain-based data elements, domain details are automatically included inline.
  - `ABAP` - ABAP-compatible JSON format for programmatic processing

**Example (HUMAN format - default):**

```bash
sapcli dataelement read Z_MY_DATAELEMENT
```

**Output (predefined ABAP type):**

```text
Data Element: Z_MY_DATAELEMENT
Description: My custom data element
Package: ZTEST
Master Language: EN

Definition:
  Type
    Kind: predefinedAbapType
    Name: CHAR
    Length: 10
    Decimals: 0

  Labels:
    Short: Short Lbl
    Medium: Medium Label
    Long: Long Label Text
    Heading: Heading Label Text
```

**Output (domain-based type):**

```text
Data Element: Z_MY_DATAELEMENT
Description: My custom data element based on domain
Package: ZTEST
Master Language: EN

Definition:
  Type
    Kind: domain
    Name: ZMYDOMAIN
    Description: Custom Domain

    Type Information:
        Datatype: CHAR
        Length: 10
    Output Information:
        Length: 10
    Value Information:
        Fix Values:
            - A: Option A
            - B: Option B

  Labels:
    Short: Short Lbl
    Medium: Medium Label
    Long: Long Label Text
    Heading: Heading Label Text
```

**Example (ABAP format):**

```bash
sapcli dataelement read Z_MY_DATAELEMENT --format=ABAP
```

**Output (predefined ABAP type):**

```json
{
  "formatVersion": "1",
  "header": {
    "description": "My custom data element",
    "originalLanguage": "en"
  },
  "definition": {
    "typeKind": "predefinedAbapType",
    "dataType": "CHAR",
    "length": 10,
    "decimals": 0
  },
  "labels": {
    "short": "Short Lbl",
    "medium": "Medium Label",
    "long": "Long Label Text",
    "heading": "Heading Label Text"
  }
}
```

**Output (domain-based type):**

```json
{
  "formatVersion": "1",
  "header": {
    "description": "My custom data element based on domain",
    "originalLanguage": "en"
  },
  "definition": {
    "typeKind": "domain",
    "domainName": "ZMYDOMAIN"
  },
  "labels": {
    "short": "Short Lbl",
    "medium": "Medium Label",
    "long": "Long Label Text",
    "heading": "Heading Label Text"
  }
}
```

**Note:**
- For domain-based data elements in HUMAN format, domain details (type information, output characteristics, fixed values) are automatically displayed inline.
- ABAP format includes only the data element definition without embedded domain details.
- If a domain cannot be fetched (e.g., doesn't exist or network error), a warning is printed to stderr, and the command continues without domain details.

## delete

Delete data element

```bash
sapcli dataelement delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given data element

```bash
sapcli dataelement whereused DATA_ELEMENT_NAME
```
