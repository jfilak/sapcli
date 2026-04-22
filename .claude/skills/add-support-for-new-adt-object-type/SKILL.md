---
name: add-support-for-new-adt-object-type
description: Implement new ADT object type handler with full read/write support and command line interface.
argument-hint: [capture-adt-http-communication-file-name]
---

# How to add a new ADT object

The architecture is briefly explained at [doc/architecture.md](../../../doc/architecture.md).

## Prerequisite 1: captured ADT HTTP traffic

Either use ABAP Communication log of the ADT frontend (Eclipse) or
use [mitmproxy](https://mitmproxy.org/) to capture the ADT HTTP traffic of the object you want to add.

The GET request defines ADT object URL. The URL consists of:
- the prefix `/sap/bc/adt/`
- the object category & type (e.g. `oo/classes` for ABAP classes)
- the object name
- and perhaps more (unfortunately, we are not aware of ADT API documentation)

The GET object object also defines objects mime-type:
- Header: `Accept: application/vnd.sap.adt.oo.classes.v4+xml`

The response contains the XML representation of the object. The root node of the XML contains the namespace which is required for the class level object OBJTYPE.

```xml
<?xml version="1.0" encoding="utf-8"?>
<class:abapClass
    xmlns:class="http://www.sap.com/adt/oo/classes"
    xmlns:adtcore="http://www.sap.com/adt/core"
    class:final="true"
    adtcore:responsible="DEVELOPER"
    adtcore:name="ZCL_HELLO_WORLD"
    adtcore:type="CLAS/OC"
    adtcore:changedAt="2019-03-07T20:22:01Z"
    adtcore:version="active"
    adtcore:descriptionTextLimit="60" adtcore:language="EN">

...

<class:abapClass>
```

## Step 1: create a new class for the ADT object

Either create a new file or place into a file with objects of the same category
in the directory `sap/adt/`.

```
class MyObject(ADTObject):
    """This is a wrapper for the ADT object type MyObject."""

    OBJTYPE = ADTObjectType(
        <attribute adtcore:type -> CLAS/OC>,
        <URL object category/type -> oo/classes>,
        # Root element namespace -> http://www.sap.com/adt/oo/classes
        xmlns_adtcore_ancestor('classes', 'http://www.sap.com/adt/oo/classes'),
        <the content of the header Accept -> 'application/vnd.sap.adt.oo.classes.v4+xml'>,
        # If the object is composed of multiple parts: e.g. metadata and source code.
        # If the object is composed of single part, use None.
        <mime type to URL part mapping -> 'text/plain': 'source/main'>
        <root element of the XML response -> abapClass>,
        # If the object has a source code part, the write operation requires
        # to send the source code in a separate request. This attribute defines
        # the handler for writing the source code part.
        # If the object does not have a source code part, use None.
        editor_factory=ADTObjectSourceEditor
    )

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package
```

## Step 2: create fixtures for the new class

Export the new type MyObject in the file @sap/adt/__init__.py.

```python
from sap.adt.my_object import MyObject
```

## Step 3: create fixtures for the new class

In the directory `test/unit`, crate the file `fixtures_sap_adt_my_object.py`.

```python
# Expected Object Name in XML response and request, e.g. <adtcore:name>MY_OBJECT</adtcore:name>
MY_OBJECT_NAME='MY_OBJECT'

# Respose sent by ADT for GET request
MY_OBJECT_ADT_GET_RESPONSE_XML="""<?xml version="1.0" encoding="utf-8"?>
...
"""

# Expected request body for POST request to create the object. This is required
# to test if the object is correctly serialized to XML.
MY_OBJECT_ADT_POST_REQUEST_XML="""<?xml version="1.0" encoding="utf-8"?>
...
"""
```

## Step 4: create tests for the new class

In the directory `test/unit`, crate the file `test_sap_adt_my_object.py`.

Purpose of the test is to verify object deserialization from the XML response
and serialization to the XML request.

Sample test cases is located at [assets/new_object_mapper_tests.py](assets/new_object_mapper_tests.py).

## Step 5: add command line interface

In the directory `sap/cli`, create the file `my_object.py`.

If your object does not need anything fancy, you can just
use the template class CommandGroupObjectMaster @sap/cli/object.py
which defines read, write, delete, and activate operations for the object.

```python
"""Command line interface for MyObject ADT object."""

import sap.adt
import sap.cli.object


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.MyObject
       calls.
    """

    def __init__(self):
        super().__init__('dataelement')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        return sap.adt.MyObject(connection, name.upper(), package=args.package, metadata=metadata)
```

## Step 6: add test for command line interface

In the directory `test/unit`, create the file `test_sap_cli_my_object.py`.
Use the file [assets/new_command_tests.py](assets/new_command_tests.py) as a template for the tests.

The purpose of the tests is to verify that the command line interface correctly
translates the command line parameters to the calls of the methods of the class
MyObject and to verify that the de-serialized object is correctly printed to
the console.

## Step 7: hook the command line interface to the main CLI entry point

In the file `sap/cli/__init__.py`, import the command group class and add it to
the main CLI entry point.

```python
class CommandsCache:

    def commands()
        ...
        import sap.cli.my_object
        ...

        if CommandsCache.adt is None:
            CommandsCache.adt = [
                ...
                (adt_connection_from_args, sap.cli.my_object.CommandGroup()),
                ...
            ]
```

## Step 8: add documentation for the command line interface

In the directory `doc/cli`, create the file `my_object.md`. Use the file
[assets/new_command_documentation_template.md](assets/new_command_documentation_template.md)
as a template for the documentation.

The documentation must contain all commands and options returned by the new
command help. Run `sapcli my-object --help` to get the list of commands and
options.
