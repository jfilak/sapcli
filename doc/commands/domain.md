# Domain

ABAP Domains define elementary data types and their technical characteristics (data type, length, value range). Domains can be referenced by data elements.

- [create](#create) ⚠️ *Disabled - Not Supported*
- [read](#read)
- [write](#write) ⚠️ *Disabled - Not Supported*
- [activate](#activate)
- [delete](#delete) ⚠️ *Disabled - Not Supported*
- [whereused](#whereused)

## create

⚠️ **This command is currently disabled.**

Creating domains is not supported because this operation is dangerous and has not been tested.

```bash
sapcli domain create DOMAIN_NAME DESCRIPTION PACKAGE
```

**Note:** Attempting to use this command will result in an error: "Create Domain is not supported."

## read

Read and display a Domain and its properties.

```bash
sapcli domain read DOMAIN_NAME [--format=ABAP|HUMAN]
```

* _DOMAIN\_NAME_ specifying the name of the domain (e.g., BEGRM, CHAR20)
* _--format_ output format for the domain details **(optional, default: ABAP)**
  - `ABAP` - ABAP-compatible JSON format for programmatic processing
  - `HUMAN` - human-readable format with labeled fields

**Example (ABAP format - default):**

```bash
sapcli domain read BEGRM
```

**Output:**

```json
{
  "formatVersion": "1",
  "header": {
    "description": "Authorization group in the material master",
    "originalLanguage": "en"
  },
  "format": {
    "dataType": "CHAR",
    "length": 4
  },
  "outputCharacteristics": {
    "length": 4
  },
  "fixedValues": [
    {
      "fixedValue": "H",
      "description": "History"
    },
    {
      "fixedValue": "X",
      "description": "Xml"
    }
  ]
}
```

**Example (HUMAN format):**

```bash
sapcli domain read BEGRM --format=HUMAN
```

**Output:**

```text
Domain: BEGRM
Description: Authorization group in the material master
Package: MGA
Master Language: EN

Content:
    Type Information:
        Datatype: CHAR
        Length: 4
    Output Information:
        Length: 4
    Value Information:
        Table Reference: TMBG
        Fix Values:
            - H: History
            - X: Xml
```

## write

⚠️ **This command is currently disabled.**

Writing to domains is not supported because this operation is dangerous and has not been tested.

```bash
sapcli domain write DOMAIN_NAME SOURCE [SOURCE ...]
```

**Note:** Attempting to use this command will result in an error: "Write Domain is not supported."

## activate

Activate the given domain.

```bash
sapcli domain activate DOMAIN_NAME [DOMAIN_NAME ...] [--ignore-errors] [--warning-errors]
```

* _DOMAIN\_NAME_ one or more domain names to activate
* _--ignore-errors_ do not stop activation in case of errors **(optional)**
* _--warning-errors_ treat activation warnings as errors **(optional)**

**Example:**

```bash
sapcli domain activate BEGRM CHAR20
```

## delete

⚠️ **This command is currently disabled.**

Deleting domains is not supported because this operation is dangerous and has not been tested.

```bash
sapcli domain delete DOMAIN_NAME [DOMAIN_NAME ...]
```

**Note:** Attempting to use this command will result in an error: "Delete Domain is not supported."

## whereused

Find objects that reference the given domain.

```bash
sapcli domain whereused DOMAIN_NAME
```

* _DOMAIN\_NAME_ specifying the name of the domain

**Example:**

```bash
sapcli domain whereused BEGRM
```
