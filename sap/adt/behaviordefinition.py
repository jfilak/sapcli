"""Behavior Definition ADT functionality module"""

from typing import Optional

from sap.adt.annotations import xml_attribute, xml_element, XmlListNodeProperty
from sap.adt.objects import (
    xmlns_adtcore_ancestor,
    ADTObject,
    ADTObjectType,
    ADTObjectSourceEditor,
)

from sap.adt.common_types import (
    ADTTemplate,
    ADTTemplateProperty,
    AtomLink,
    NamedItemList,
)


class BehaviorDefinition(ADTObject):
    """CDS Behavior Definition (BDEF)"""

    OBJTYPE = ADTObjectType(
        'BDEF/BDO',
        'bo/behaviordefinitions',
        xmlns_adtcore_ancestor('blue', 'http://www.sap.com/wbobj/blue'),
        'application/vnd.sap.adt.blues.v1+xml',
        {'text/plain': 'source/main'},
        'blueSource',
        editor_factory=ADTObjectSourceEditor.plain_text
    )

    links = XmlListNodeProperty('atom:link', value=[], factory=AtomLink)

    def __init__(self, connection, name: str, package: Optional[str] = None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package
        self._template = None
        self._description_text_limit = None
        self._source_uri = None
        self._fix_point_arithmetic = None
        self._active_unicode_check = None

    @xml_attribute('adtcore:descriptionTextLimit')
    def description_text_limit(self):
        """Maximum length of the description"""
        return self._description_text_limit

    @description_text_limit.setter
    def description_text_limit(self, value):
        self._description_text_limit = value

    @xml_attribute('abapsource:sourceUri')
    def source_uri(self):
        """URI of the source code relative to the object"""
        return self._source_uri

    @source_uri.setter
    def source_uri(self, value):
        self._source_uri = value

    @xml_attribute('abapsource:fixPointArithmetic')
    def fix_point_arithmetic(self):
        """Fixed point arithmetic flag as returned by ADT - true or false"""
        return self._fix_point_arithmetic

    @fix_point_arithmetic.setter
    def fix_point_arithmetic(self, value):
        self._fix_point_arithmetic = value

    @xml_attribute('abapsource:activeUnicodeCheck')
    def active_unicode_check(self):
        """Unicode checks flag as returned by ADT - true or false"""
        return self._active_unicode_check

    @active_unicode_check.setter
    def active_unicode_check(self, value):
        self._active_unicode_check = value

    @xml_element('adtcore:adtTemplate', ignore_empty=True)
    def template(self):
        """ADT template for behavior extension creation"""
        return self._template

    @template.setter
    def template(self, value):
        self._template = value

    @xml_element('adtcore:packageRef')
    def reference(self):
        """The object's package reference redefined to follow adtcore:adtTemplate"""
        return self._metadata.package_reference

    @classmethod
    def extend(cls, connection, name: str, base_bdef: str,
               package: Optional[str] = None, description: Optional[str] = None,
               interface_bdef: Optional[str] = None) -> 'BehaviorDefinition':
        """Factory method to create a BehaviorDefinition that extends a base BDEF."""

        bdef = cls(connection, name, package=package)

        if description:
            bdef.description = description  # type: ignore[method-assign]

        bdef.template = ADTTemplate([  # type: ignore[method-assign]
            ADTTemplateProperty('base_bdef', base_bdef),
            ADTTemplateProperty('interface_bdef', interface_bdef),
        ])

        return bdef

    @staticmethod
    def list_interfaces(connection, bdef_name: str) -> 'NamedItemList':
        """List BO interfaces assigned to the given behavior definition"""

        resp = connection.execute(
            'GET',
            'bo/behaviordefinitions/interfaces',
            params={'name': bdef_name.upper()},
            accept=['application/vnd.sap.adt.nameditems.v1+xml', 'application/xml'],
        )

        return NamedItemList.from_xml(resp.text)
