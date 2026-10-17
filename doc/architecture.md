# ADT object

ADT backend returns ABAP object data in XML.
sapcli defines a rather complicated XML to Object mapper (it works like pydantic).
Since it is not clear if the ADT backend needs the XML nodes in a certain order,
the XML to object mapper tries to serialize objects with the same order as the ADT frontend (Eclipse).

As written above the XML to object mapper works like pydantic by Python type metadata.
To make sure the defined members are serialized exactly in the way as they are defined
in Python classes, the classes must inherit their metaclass from OrderedClassMembers.

Top ADT objects such as ABAP Class or ABAP Function Module should inherit from ADTObject.
Helper ADT objects (members of the top ADT objects can just specify their metaclass=OrderedClassMembers).

ADTObject children must define class level object OBJTYPE which must be compatible with ADTObjectType.

Top ADT objects must declare their metadata stored in the class ADTCoreData.

The corresponding Python code is stored in the directory sap/adt/

## ADT object anatomy

Objects metadata such as `Master Language` is accessible via the property
`ADTObject.coredata` which returns an instance of `ADTCoreData`.

The authoritative package information for the give object is accessible via the
property `ADTOjbect.coredata.package_reference` which returns an instance of
`ADTCoreData.Reference`.

The complete Object ADT path is available in the property `full_adt_uri`.

### Modify ADT objects

ABAP objects must be locked before they can be modified and the lock must be
release at the end otherwise other users cannot access the object.

ADTObject provides the function `open_editor` which returns an instance of
`ADTObjectEditor` which is a context manager that takes care of locking and
releasing the lock at the end.

For simple updates of ADT object data the following code is sufficient:

```python
adt_object.content_item = "foo"

with adt_object.open_editor() as editor:
    editor.push()
```

For writing source code such as ABAP class methods, the following code is sufficient:

```python
with adt_object.open_editor() as editor:
    editor.write("METHOD foo. ENDMETHOD.")
```

### Text elements

Text elements (the text pool) are not a part of the ADT object they belong to.
ADT exposes them as a sibling ADT object with its own URI, lock and activation
status - `/sap/bc/adt/textelements/classes/{name}` for ABAP Classes and
`/sap/bc/adt/textelements/programs/{name}` for ABAP Programs. The text symbols
are its source `source/symbols` of the MIME type
`application/vnd.sap.adt.textelements.symbols.v1`. Hence, they are not
modeled as a class include but as independent `ADTObject` children
`ClassTextElements` and `ProgramTextElements` of the common base `TextElements`
in the module `sap/adt/textelements.py`.

Programs have also the text element sources `source/selections` (selection
texts) and `source/headings` (list headings) which sapcli does not support yet.

The module also provides the type `TextSymbol` and the functions `parse_symbols()`
and `serialize_symbols()` converting between the ADT text symbols format
(`@MaxLength:<n>` line followed by `<ID>=<text>` line) and Python objects.

```python
import sap.adt.wb
from sap.adt.textelements import ClassTextElements, TextSymbol, parse_symbols, serialize_symbols

texts = ClassTextElements(connection, 'ZCL_HELLO_WORLD')

symbols = parse_symbols(texts.text)
symbols.append(TextSymbol(id='002', text='Second symbol', max_length=25))

# the editor locks the text elements object, not the class
with texts.open_editor(corrnr=corrnr) as editor:
    editor.write(serialize_symbols(symbols))

# written text symbols are inactive until activated
sap.adt.wb.activate(texts)
```

Activating `ClassTextElements` or `ProgramTextElements` activates only the text
elements. Activating the parent `Class` activates its inactive text elements
too, all or nothing. But activating the parent `Program` does not activate its
inactive text elements - pass them as a dependent to activate both, all or
nothing (the command `sapcli program activate` does it):

```python
program = sap.adt.Program(connection, 'ZHELLO_WORLD')
texts = ProgramTextElements(connection, 'ZHELLO_WORLD')

sap.adt.wb.activate(program, dependents=[texts])
```

Deleting the class or the program deletes its text elements.

The editor validates the written content with `parse_symbols()` and raises
`SAPCliError` before the content is sent if the content is malformed.
Writing replaces the whole text pool and the texts are read and written
in the logon language.

### Functions

ABAP function modules s are organized in function groups which are something
like directories of function modules.
