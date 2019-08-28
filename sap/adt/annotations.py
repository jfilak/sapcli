"""Python decorators for conversions of Python objects to ADT XML fragments"""

from enum import Enum
import collections


class OrderedClassMembers(type):
    """MetaClass to preserve get order of member declarations
       to serialize the XML elements in the expected order.
    """

    @classmethod
    # pylint: disable=unused-argument
    def __prepare__(mcs, name, bases):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, classdict):
        members = []

        if bases:
            parent = bases[-1]
            if hasattr(parent, '__ordered__'):
                members.extend(parent.__ordered__)

        members.extend([key for key in classdict.keys()
                        if key not in ('__module__', '__qualname__')])

        classdict['__ordered__'] = members

        return type.__new__(mcs, name, bases, classdict)


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


class XmlListNodeProperty(XmlElementProperty):
    """Many repetitions of the same tag"""

    def __init__(self, name, value=None, deserialize=True, factory=None, kind=XmlElementKind.OBJECT):
        super(XmlListNodeProperty, self).__init__(name, self.get, fset=self.append, deserialize=deserialize,
                                                  factory=factory, kind=kind)

        if value is not None and not isinstance(value, list):
            raise RuntimeError()

        self.attr = f'_{name}'.replace(':', '_')
        self.default_value = value

    def _get_list(self, obj):
        items = obj.__dict__.get(self.attr, None)
        if items is None:
            if self.default_value is not None:
                items = list(self.default_value)
                obj.__dict__[self.attr] = items

        return items

    def get(self, obj):
        """Getter"""

        try:
            return getattr(obj, self.attr)
        except AttributeError:
            return self._get_list(obj)

    def append(self, obj, value):
        """Setter"""

        items = self._get_list(obj)
        if items is None:
            items = list()
            obj.__dict__[self.attr] = items

        items.append(value)


class XmlContainerMeta(OrderedClassMembers):
    """A MetaClass adding the class-method 'define' which returns
       a class representing ADT XML container - i.e a wrapping node
       with many children of the same tag.
    """

    def define(cls, item_element_name, item_factory):
        """Defines a new class with the property items which will be
           annotated as XmlElement.

           The annotated property is named 'items' and can be publicly used.
        """

        items_property = XmlListNodeProperty(item_element_name, deserialize=True, factory=item_factory,
                                             value=list(), kind=XmlElementKind.OBJECT)

        return type(f'XMLContainer_{item_factory.__name__}', (cls,), dict(items=items_property))


class XmlContainer(metaclass=XmlContainerMeta):
    """A template class with the property items which is annotated as XmlElement."""

    def append(self, value):
        """Appends the give value to the XML container"""

        # pylint: disable=no-member
        self.items.append(value)

    def __iter__(self):
        # pylint: disable=no-member
        return self.items.__iter__()

    def __getitem__(self, index):
        # pylint: disable=no-member
        return self.items.__getitem__(index)

    def __len__(self):
        # pylint: disable=no-member
        return self.items.__len__()


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
