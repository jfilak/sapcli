# Table Type (TTYP/DA)

1. [define](#define)
2. [create](#create)
3. [activate](#activate)
4. [delete](#delete)
5. [whereused](#whereused)

## define

Creates a Table Type of the given name with the given description in the given
package and defines it as a table of the given DDIC structure.

```bash
sapcli tabletype define NAME DESCRIPTION PACKAGE -r ROW_TYPE [--access-type {standard,sorted,hashed,index,notSpecified}]
                        [--key-definition {standard,rowType,keyComponents,empty,notSpecified}]
                        [--key-kind {unique,nonUnique,notSpecified}] [--key-component KEY_COMPONENT ...]
                        [--activate] [--no-error-existing] [--corrnr TRANSPORT]
```

* _-r ROW\_TYPE_, _--row-type ROW\_TYPE_ the DDIC structure the table rows are made of
* _--access-type_ table access type; default: _standard_
* _--key-definition_ primary key definition; default: _standard_
* _--key-kind_ primary key kind; default: _nonUnique_ or _notSpecified_ for the key definitions _empty_ and _notSpecified_
* _--key-component KEY\_COMPONENT_ a primary key component (structure field); repeat the parameter for more
  components; allowed and required only for the key definition _keyComponents_
* _--activate_ activate the table type after the definition
* _--no-error-existing_ do not fail if the table type already exists and redefine it
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed

### Examples

Standard table with the standard key:

```bash
sapcli tabletype define ZTT_MESSAGES "Messages" '$PACKAGE' --row-type BAPIRET2 --activate
```

Sorted table with a unique key:

```bash
sapcli tabletype define ZTT_MESSAGES_SORTED "Sorted messages" '$PACKAGE' --row-type BAPIRET2 \
    --access-type sorted --key-definition keyComponents --key-kind unique \
    --key-component TYPE --key-component ID --key-component NUMBER --activate
```

## create

Creates a Table Type of the given name with the given description in the given
package. The definition is left as ADT sets it up.

```bash
sapcli tabletype create ZTT_MESSAGES "Messages" '$PACKAGE' [--corrnr TRANSPORT]
```

## activate

Activates the given table types in the given order.

```bash
sapcli tabletype activate [--ignore-errors] [--warning-errors] NAME NAME ...
```

* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

## delete

Delete the given table types

```bash
sapcli tabletype delete NAME [NAME ...] [--corrnr TRANSPORT]
```

## whereused

Find objects that reference the given table type

```bash
sapcli tabletype whereused ZTT_MESSAGES
```
