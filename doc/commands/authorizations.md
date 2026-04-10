# Authorization Objects

- [Authorization Field](#authorization-field)
    - [read](#read)
    - [whereused](#whereused)
    - [activate](#activate)

## Authorization Field

Authorization fields are ABAP dictionary objects used in authorization checks to control access to business data and transactions.

### read

Read and display an Authorization Field and its properties.

```bash
sapcli authorizationfield read AUTHORIZATION_FIELD_NAME [--format=HUMAN|ABAP]
```

* _AUTHORIZATION\_FIELD\_NAME_ specifying the name of the authorization field (e.g., BEGRU, ACTVT)
* _--format_ output format for the authorization field details **(optional, default: HUMAN)**
  - `HUMAN` - human-readable format with labeled fields
  - `ABAP` - ABAP-compatible format (not yet implemented)

**Example:**

```bash
sapcli authorizationfield read BEGRU
```

**Output:**

```text
Authorization Field: BEGRU
Description: Authorization Group
Package: S_BUPA_GENERAL
Responsible: KNOETIG
Master Language: DE

Content:
  Field Name: BEGRU
  Roll Name: BEGRU
  Check Table: 
  Exit FB: 
  Domain Name: BEGRU
  Output Length: 000004
  Conversion Exit: 
  Search: false
  Object Exit: false
  Org Level Info: Field is not defined as Organizational level.
  Collective Search Help: false
  Collective Search Help Name: 
  Collective Search Help Description: 
```

### whereused

Find objects that reference the given authorization field.

```bash
sapcli authorizationfield whereused AUTHORIZATION_FIELD_NAME
```

* _AUTHORIZATION\_FIELD\_NAME_ specifying the name of the authorization field

**Example:**

```bash
sapcli authorizationfield whereused BEGRU
```

### activate

Activate the given authorization field.

```bash
sapcli authorizationfield activate AUTHORIZATION_FIELD_NAME [AUTHORIZATION_FIELD_NAME ...] [--ignore-errors] [--warning-errors]
```

* _AUTHORIZATION\_FIELD\_NAME_ one or more authorization field names to activate
* _--ignore-errors_ do not stop activation in case of errors **(optional)**
* _--warning-errors_ treat activation warnings as errors **(optional)**

**Example:**

```bash
sapcli authorizationfield activate BEGRU ACTVT
```

**Note:** Create, write, and delete operations are disabled because these operations have not been tested.
