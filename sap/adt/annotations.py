"""Python decorators for conversions of Python objects to ADT XML fragments"""

from enum import Enum


class XmlElementKind(Enum):
    """XML element kinds"""

    OBJECT = 1
    TEXT = 2


# pylint: disable=too-few-public-methods
class XmlAttributeProperty(property):
    """XML Annotation"""

    def __init__(self, name, fget, fset=None, deserialize=True):
        super(XmlAttributeProperty, self).__init__(fget, fset)

        self.name = name
        self.deserialize = deserialize

    def setter(self, fset):
        return type(self)(self.name, self.fget, fset, deserialize=self.deserialize)


# pylint: disable=too-few-public-methods
class XmlElementProperty(property):
    """XML Annotation"""

    NAME_FROM_OBJECT = None

    def __init__(self, name, fget, fset=None, deserialize=True, factory=None, kind=XmlElementKind.OBJECT):
        super(XmlElementProperty, self).__init__(fget, fset)

        self.name = name
        self.deserialize = deserialize
        self.factory = factory
        self.kind = kind

    def setter(self, fset):
        return type(self)(self.name, self.fget, fset, deserialize=self.deserialize, factory=self.factory,
                          kind=self.kind)


class XmlPropertyImpl:
    """XML Property implementation which enriches the given object with a new
       attribute whose name is built from the corresponding XML name.
    """

    def __init__(self, name, default_value=None):

        self.attr = f'_{name}'.replace(':', '_')
        self.default_value = default_value

    def get(self, obj):
        """Getter"""

        try:
            return getattr(obj, self.attr)
        except AttributeError:
            return self.default_value

    def set(self, obj, value):
        """Setter"""

        obj.__dict__[self.attr] = value


class XmlNodeProperty(XmlElementProperty, XmlPropertyImpl):
    """A descriptor class to avoid the need to define 2 useless functions
       get/set when absolutely not necessary.
    """

    def __init__(self, name, value=None, deserialize=True, factory=None, kind=XmlElementKind.OBJECT):
        super(XmlNodeProperty, self).__init__(name, self.get, fset=self.set, deserialize=deserialize, factory=factory,
                                              kind=kind)
        XmlPropertyImpl.__init__(self, name, default_value=value)

    def setter(self, fset):
        """Turned off setter decorator which is not necessary and confusing"""

        # TODO: reorder inheritance - this is stupid!
        raise NotImplementedError()


class XmlNodeAttributeProperty(XmlAttributeProperty, XmlPropertyImpl):
    """A descriptor class to avoid the need to define 2 useless functions
       get/set when absolutely not necessary.
    """

    def __init__(self, name, value=None, deserialize=True):
        super(XmlNodeAttributeProperty, self).__init__(name, self.get, fset=self.set, deserialize=deserialize)
        XmlPropertyImpl.__init__(self, name, default_value=value)

    def setter(self, fset):
        """Turned off setter decorator which is not necessary and confusing"""

        # TODO: reorder inheritance - this is stupid!
        raise NotImplementedError()


def xml_text_node_property(name, value=None, deserialize=True):
    """A factory method returning a descriptor property XML Element holding
       the value in a text node.
    """

    return XmlNodeProperty(name, value=value, deserialize=deserialize, factory=None, kind=XmlElementKind.TEXT)


def xml_attribute(name, deserialize=True):
    """Mark the given property as a XML element attribute of the given name"""

    def decorator(meth):
        """Creates a property object"""

        return XmlAttributeProperty(name, meth, deserialize=deserialize)

    return decorator


def xml_element(name, deserialize=True, factory=None, kind=XmlElementKind.OBJECT):
    """Mark the given property as a XML element of the given name"""

    def decorator(meth):
        """Creates a property object"""

        return XmlElementProperty(name, meth, deserialize=deserialize, factory=factory, kind=kind)

    return decorator
