"""Convert Python Objects to ADT XML entities"""

from sap.adt.annotations import XmlAttributeProperty, XmlElementProperty


class Element:
    """XML element representation"""

    def __init__(self, name):
        self._name = name
        self._children = []
        self._attributes = {}

    @property
    def name(self):
        """Element name"""

        return self._name

    @property
    def children(self):
        """Child elements"""

        return self._children

    @property
    def attributes(self):
        """Element attributes"""

        return self._attributes

    def add_child(self, name):
        """Adds a new child element and return it"""

        child = Element(name)
        self._children.append(child)
        return child

    def add_attribute(self, name, value):
        """Adds a new attribute or change the value"""

        self._attributes[name] = value


class Marshal:
    """ADT object marshaling"""

    def serialize(self, adt_object):
        """Serialized ADT Object"""

        tree = self._object_to_tree(adt_object)
        return self._tree_to_xml(tree)

    def _object_to_tree(self, adt_object):
        """Create a DOM like representation of the given ADT object"""

        objtype = adt_object.objtype
        name = f'{objtype.xmlnamespace[0]}:{objtype.xmlname}'

        root = Element(name)
        root.add_attribute(f'xmlns:{objtype.xmlnamespace[0]}', objtype.xmlnamespace[1])
        root.add_attribute(f'xmlns:adtcore', 'http://www.sap.com/adt/core')
        root.add_attribute('adtcore:version', 'active')
        root.add_attribute('adtcore:type', objtype.code)

        self._build_tree(root, adt_object)
        return root

    def _build_tree(self, root, obj):
        """Convert ADT Object members to XML elements"""

        if obj is None:
            return

        for attr_name in dir(obj.__class__):
            if attr_name.startswith('_'):
                continue

            attr = getattr(obj.__class__, attr_name)

            if isinstance(attr, XmlElementProperty):
                element = root.add_child(attr.name)
                self._build_tree(element, getattr(obj, attr_name))
            elif isinstance(attr, XmlAttributeProperty):
                value = getattr(obj, attr_name)
                if value is not None:
                    root.add_attribute(attr.name, value)

    def _tree_to_xml(self, tree):
        """Turn the given abstract XML tree to XML string"""

        body = '<?xml version="1.0" encoding="UTF-8"?>\n'

        return body + self._element_to_xml(tree)

    def _element_to_xml(self, tree):
        """ """

        xml = f'<{tree.name}'

        attributes = ' '.join(f'{key}="{value}"' for key, value in tree.attributes.items())
        if attributes:
            xml += f' {attributes}'

        children = '\n'.join((self._element_to_xml(child) for child in tree.children))
        if children:
            xml += f'>\n{children}\n</{tree.name}>'
        else:
            xml += '/>'

        return xml
