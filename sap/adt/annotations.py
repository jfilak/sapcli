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
