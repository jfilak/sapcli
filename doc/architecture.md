# ADT object

ADT backend returns ABAP object data in XML.
sapcli defines a rather complicated XML to Object mapper (it works like pydantic).
Since it is not clear if the ADT backend needs the xml nodes in a certain order,
the XML to object mapper tries to serialize objects with the same order as the ADT frontend (Eclipse).

As written above the XML to objec mapper works like pydantic by Python type metadata.
To make sure the defined members are serialized exactly in the way as they are defined
in Python classes, the classes must inherit their metaclass from OrderedClassMembers.

Top ADT objects such as ABAP Class or ABAP Function Module should inherit from ADTObject.
Helper ADT objects (members of the top adt objects can just specify their metaclass=OrderedClassMembers).

ADTObject childern must define class level object OBJTYPE which must be compatible with ADTObjectType.

Top ADT objects must declare their metadata stored in the class ADTCoreData.

The corresponding Python code is stored in the directory sap/adt/

# Functions

ABAP function modules s are organized in function groups which are something
like directories of function modules.
