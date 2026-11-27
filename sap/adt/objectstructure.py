"""ADT Object Structure

Read-only model of the structure of an ABAP object returned by the ADT resource
<object URI>/objectstructure: the object, its components (methods, attributes,
local classes, ...), their components and their positions in the sources of
the object.

    clas = sap.adt.Class(connection, 'ZCL_FOO')
    root = sap.adt.objectstructure.get_object_structure(clas)

    for element in root.children:
        print(element.adt_type, element.name, element.implementation_block)

The positions are sap.adt.uri.StatementPosition, for example:

    StatementPosition('zcl_foo', 'source/main', 46, 2, 49, 11, 'CLAS/OC')

Only classes and interfaces have positions. Programs and function groups have
the object structure too, but their links refer to the definitions by type and
name (e.g. #type=PROG%2FPD;name=FOO), so their positions are None and the raw
links are in the member links. Function modules, CDS views (DDLS) and behavior
definitions (BDEF) have no object structure (HTTP 404).
"""

from typing import Optional
from urllib.parse import urljoin

from sap.adt.annotations import OrderedClassMembers, XmlNodeAttributeProperty, XmlListNodeProperty
from sap.adt.common_types import AtomLink
from sap.adt.marshalling import Marshal
from sap.adt.objects import ADTObjectType, XMLNamespace
from sap.adt.uri import StatementPosition, parse_statement_uri


XMLNS_ABAPSOURCE = XMLNamespace('abapsource', 'http://www.sap.com/adt/abapsource')

OBJECT_STRUCTURE_MIME_TYPE = 'application/vnd.sap.adt.objectstructure.v2+xml'

REL_DEFINITION_IDENTIFIER = 'http://www.sap.com/adt/relations/source/definitionIdentifier'
REL_DEFINITION_BLOCK = 'http://www.sap.com/adt/relations/source/definitionBlock'
REL_IMPLEMENTATION_IDENTIFIER = 'http://www.sap.com/adt/relations/source/implementationIdentifier'
REL_IMPLEMENTATION_BLOCK = 'http://www.sap.com/adt/relations/source/implementationBlock'


# XmlNodeAttributeProperty turns off the decorator setter on purpose by raising
# NotImplementedError and this class keeps it turned off
# pylint: disable=abstract-method
class _XmlFlagAttributeProperty(XmlNodeAttributeProperty):
    """Read-only XML attribute that ADT sends only as "true" or leaves out:
       the value is True if the attribute is "true", otherwise False.
    """

    def __init__(self, name):
        super().__init__(name, value=False)

    def set(self, obj, value):
        super().set(obj, value == 'true')


def _has_source_range(href):
    """Returns True if the fragment of the href is a source range
       (#start=L,C;end=L,C). Classes and interfaces send source ranges.
       Programs and function groups send object references
       (#type=PROG%2FPD;name=FOO) and the links of some elements have no
       fragment at all (e.g. text elements).
    """

    fragment = href.partition('#')[2]
    return 'start' in [token.partition('=')[0] for token in fragment.split(';')]


def _new_element():
    """Returns a new child element - the class ObjectStructureElement
       is not defined yet when its property children is defined.
    """

    return ObjectStructureElement()


class ObjectStructureElement(metaclass=OrderedClassMembers):
    """An element of the object structure: the object itself (the root),
       a component of the object or a component of a local class or interface.

       The attributes are None (texts) or False (flags) if ADT does not send them.
    """

    objtype = ADTObjectType(None, None, XMLNS_ABAPSOURCE, OBJECT_STRUCTURE_MIME_TYPE, None,
                            'objectStructureElement')

    xml_base = XmlNodeAttributeProperty('xml:base')
    adt_type = XmlNodeAttributeProperty('adtcore:type')
    name = XmlNodeAttributeProperty('adtcore:name')
    visibility = XmlNodeAttributeProperty('visibility')
    level = XmlNodeAttributeProperty('level')
    clif_name = XmlNodeAttributeProperty('clif_name')
    description = XmlNodeAttributeProperty('description')
    # e.g. Screen, GUI Status or GUI Titles of programs and function groups
    type_description = XmlNodeAttributeProperty('typeDescription')
    # the include of a local class of a program
    include = XmlNodeAttributeProperty('include')

    abstract = _XmlFlagAttributeProperty('abstract')
    final = _XmlFlagAttributeProperty('final')
    constant = _XmlFlagAttributeProperty('constant')
    read_only = _XmlFlagAttributeProperty('readOnly')
    constructor = _XmlFlagAttributeProperty('constructor')
    redefinition = _XmlFlagAttributeProperty('redefinition')
    event_handler_method = _XmlFlagAttributeProperty('eventhandlermethod')
    test_class = _XmlFlagAttributeProperty('testclass')
    test_method = _XmlFlagAttributeProperty('testmethod')
    is_external_ref = _XmlFlagAttributeProperty('isExternalRef')

    links = XmlListNodeProperty('atom:link', value=[], factory=AtomLink)
    children = XmlListNodeProperty('abapsource:objectStructureElement', value=[], factory=_new_element)

    def __init__(self):
        # The XML base of the element: its xml:base resolved against the base
        # of its parent. The hrefs of the links are relative to it.
        # Set by parse_object_structure.
        self.base_uri = None

    def _position(self, rel) -> Optional[StatementPosition]:
        """Returns the position the link of the given relation points to or None
           if the element has no such link or the link does not point to a source
           range (e.g. the link of text elements).
        """

        href = next((link.href for link in self.links if link.rel == rel), None)
        if href is None or not _has_source_range(href):
            return None

        return parse_statement_uri(urljoin(self.base_uri or '', href))

    @property
    def definition_identifier(self) -> Optional[StatementPosition]:
        """Position of the name in the definition"""

        return self._position(REL_DEFINITION_IDENTIFIER)

    @property
    def definition_block(self) -> Optional[StatementPosition]:
        """Position of the whole definition"""

        return self._position(REL_DEFINITION_BLOCK)

    @property
    def implementation_identifier(self) -> Optional[StatementPosition]:
        """Position of the name in the implementation"""

        return self._position(REL_IMPLEMENTATION_IDENTIFIER)

    @property
    def implementation_block(self) -> Optional[StatementPosition]:
        """Position of the whole implementation"""

        return self._position(REL_IMPLEMENTATION_BLOCK)


def _apply_xml_base(element, parent_base_uri):
    """Sets base_uri of the element and its children as XML Base defines it:
       xml:base is relative to the base of the parent and elements without
       xml:base have the base of the parent. ADT sends xml:base only in the root.
    """

    element.base_uri = urljoin(parent_base_uri, element.xml_base or '')

    for child in element.children:
        _apply_xml_base(child, element.base_uri)


def parse_object_structure(xml_text: str) -> ObjectStructureElement:
    """Returns the root element of the given object structure XML"""

    root = Marshal.deserialize(xml_text, ObjectStructureElement())
    _apply_xml_base(root, '')

    return root


def get_object_structure(adt_object, version=None) -> ObjectStructureElement:
    """Fetches the object structure of the given ADT object and returns
       its root element.

       Parameters:
        adt_object: an ADT object with the members connection and uri, e.g. sap.adt.Class
        version: None to get the same version as the source code without
                 the version parameter (the inactive version if there is one),
                 or 'active' or 'inactive'
    """

    params = None
    if version is not None:
        params = {'version': version}

    resp = adt_object.connection.execute('GET', f'{adt_object.uri}/objectstructure', params=params,
                                         accept=OBJECT_STRUCTURE_MIME_TYPE)

    return parse_object_structure(resp.text)
