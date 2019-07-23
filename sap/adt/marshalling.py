"""Convert Python Objects to ADT XML entities"""

from functools import partial

import xml.sax
from xml.sax.handler import ContentHandler

from sap import get_logger
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


def adt_object_to_element_name(adt_object):
    """Returns XML element name for the given adt_object"""

    objtype = adt_object.objtype
    return f'{objtype.xmlnamespace.name}:{objtype.xmlname}'


def factory_with_setter(factory, setter, obj):
    """Creates a new product, calls the setter and returns the product"""

    product = factory()
    setter(obj, product)
    return product


class ElementHandler:
    """XML element desirialization"""

    def __init__(self, my_xpath, elements, factory=None):
        self.my_xpath = my_xpath
        self.elements = elements
        self.factory = factory
        self.attributes = None
        self.obj = None

    def new(self):
        """Returns a new object"""

        self.obj = self.factory()
        self.attributes = ElementHandler.load_definitions(self, self.obj)

    def set(self, attr_name, value):
        """Sets object's property value"""

        get_logger().debug('Going to set XML attribute property: %s', attr_name)
        try:
            self.attributes[attr_name].__set__(self.obj, value)
            get_logger().debug('Set XML attribute property: %s', attr_name)
        except AttributeError as ex:
            get_logger().error('XML property %s: %s', attr_name, str(ex))
        except KeyError:
            get_logger().debug('Not an XML attribute property: %s', attr_name)

    def load_definitions(self, obj):
        """Examines annotations of the current object"""

        attributes = dict()
        for attr_name in obj.__class__.__ordered__:
            if attr_name.startswith('__'):
                continue

            attr = getattr(obj.__class__, attr_name)

            if isinstance(attr, XmlElementProperty):
                xml_path = f'{self.my_xpath}/{attr.name}'

                if not attr.deserialize:
                    get_logger().debug('Found readonly XML element property: %s -> %s', attr_name, xml_path)
                    continue

                get_logger().debug('Found XML element property: %s -> %s', attr_name, xml_path)

                factory = attr.factory

                if factory is None:
                    factory = partial(attr.__get__, obj)

                if attr.fset is not None:
                    factory = partial(factory_with_setter, factory, attr.__set__, obj)

                self.elements[xml_path] = ElementHandler(xml_path, self.elements, factory)
            elif isinstance(attr, XmlAttributeProperty):
                if not attr.deserialize:
                    get_logger().debug('Found readonly XML attribute property: %s -> %s', attr_name, attr.name)
                    continue

                get_logger().debug('Found XML attribute property: %s -> %s', attr_name, attr.name)
                attributes[attr.name] = attr

        return attributes


class ADTObjectSAXHandler(ContentHandler):
    """ADT Object XML parser"""

    def __init__(self, elements):
        super(ADTObjectSAXHandler, self).__init__()

        self.stack = list()
        self.current = ''
        self.elements = elements

    def startElement(self, name, attrs):
        self.stack.append(self.current)
        self.current = f'{self.current}/{name}'
        get_logger().debug('Encountered XML element: %s', self.current)

        try:
            handler = self.elements[self.current]
        except KeyError:
            return

        get_logger().debug('Deserializing element: %s', self.current)

        # this loads handlers for children elements!! /o\
        handler.new()

        for attr_name, value in attrs.items():
            get_logger().debug('Encountered XML attribute: %s', attr_name)
            try:
                handler.set(attr_name, value)
            except KeyError:
                pass

    def endElement(self, name):
        self.current = self.stack.pop()


class Marshal:
    """ADT object marshaling"""

    def serialize(self, adt_object):
        """Serialized ADT Object"""

        tree = self._object_to_tree(adt_object)
        return self._tree_to_xml(tree)

    @staticmethod
    def deserialize(xml_text, adt_object):
        """Loads XML and stores values in the given adt_object and
           for the convenience of use returns the given adt_object.
        """

        name = '/' + adt_object_to_element_name(adt_object)

        elements = dict()
        handler = ElementHandler(name, elements, lambda: adt_object)
        elements[name] = handler

        parser = ADTObjectSAXHandler(elements)
        xml.sax.parseString(xml_text, parser)

        return adt_object

    def _object_to_tree(self, adt_object):
        """Create a DOM like representation of the given ADT object"""

        objtype = adt_object.objtype
        name = adt_object_to_element_name(adt_object)

        root = Element(name)
        declared_ns = self._declare_xmlns(root, objtype.xmlnamespace)

        if objtype.code is not None:
            root.add_attribute('adtcore:type', objtype.code)

        self._build_tree(root, adt_object, declared_ns)
        return root

    # pylint: disable=no-self-use
    def _declare_xmlns(self, root, xmlns, declared_ns=None):
        """Adds the xmlns attribute if such a Namespace hasn't already been
           declared any parent nodes.

           Returns set of all declared Namespaces.
        """

        if declared_ns is None:
            declared = set()
        else:
            declared = set(declared_ns)

        if xmlns.name not in declared:
            root.add_attribute(f'xmlns:{xmlns.name}', xmlns.uri)
            declared.add(xmlns.name)

        for parent_ns in xmlns.parents:
            if parent_ns.name in declared:
                continue

            root.add_attribute(f'xmlns:{parent_ns.name}', parent_ns.uri)
            declared.add(parent_ns.name)

        return declared

    def _serialize_object_to_node(self, root, node_name, child, declared_ns):

        if not isinstance(child, list):
            # Put a solo object to a list to simplify
            # the algorithm below - this might be a bad idea.
            child = [child]

        for item in child:

            new_ns = None
            if hasattr(item, 'objtype'):
                if hasattr(item.objtype, 'xmlnamespace'):
                    new_ns = item.objtype.xmlnamespace

            if node_name is XmlElementProperty.NAME_FROM_OBJECT:
                child_name = adt_object_to_element_name(item)
                child_elem = root.add_child(child_name)
            else:
                child_elem = root.add_child(node_name)

            if new_ns is None:
                child_ns = declared_ns
            else:
                child_ns = self._declare_xmlns(child_elem, new_ns, declared_ns)

            self._build_tree(child_elem, item, child_ns)

    def _build_tree(self, root, obj, declared_ns):
        """Convert ADT Object members to XML elements"""

        if obj is None:
            return

        for attr_name in obj.__class__.__ordered__:
            if attr_name.startswith('_'):
                continue

            attr = getattr(obj.__class__, attr_name)

            if isinstance(attr, XmlElementProperty):
                child = getattr(obj, attr_name)
                self._serialize_object_to_node(root, attr.name, child, declared_ns)
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

        xml_str = f'<{tree.name}'

        attributes = ' '.join(f'{key}="{value}"' for key, value in tree.attributes.items())
        if attributes:
            xml_str += f' {attributes}'

        children = '\n'.join((self._element_to_xml(child) for child in tree.children))
        if children:
            xml_str += f'>\n{children}\n</{tree.name}>'
        else:
            xml_str += '/>'

        return xml_str
