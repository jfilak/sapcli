"""Python decorators for conversions of Python objects to ADT XML fragments"""


# pylint: disable=too-few-public-methods
class XmlAttributeProperty(property):
    """XML Annotation"""

    def __init__(self, name, fget, fset=None):
        super(XmlAttributeProperty, self).__init__(fget, fset)

        self.name = name

    def setter(self, fset):
        return type(self)(self.name, self.fget, fset)


# pylint: disable=too-few-public-methods
class XmlElementProperty(property):
    """XML Annotation"""

    def __init__(self, name, fget, fset=None, deserialize=True):
        super(XmlElementProperty, self).__init__(fget, fset)

        self.name = name
        self.deserialize = deserialize

    def setter(self, fset):
        return type(self)(self.name, self.fget, fset, deserialize=self.deserialize)


def xml_attribute(name):
    """Mark the given property as a XML element attribute of the given name"""

    def decorator(meth):
        """Creates a property object"""

        return XmlAttributeProperty(name, meth)

    return decorator


def xml_element(name, deserialize=True):
    """Mark the given property as a XML element of the given name"""

    def decorator(meth):
        """Creates a property object"""

        return XmlElementProperty(name, meth, deserialize=deserialize)

    return decorator
