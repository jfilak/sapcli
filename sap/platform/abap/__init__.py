# pylint: skip-file
"""ABAP language utilities"""

import xml.sax
from xml.sax.handler import ContentHandler

from sap import get_logger


def mod_log():
    """ADT Module logger"""

    return get_logger()


# pylint: disable=too-few-public-methods
class Structure:
    """Abstract base class for defining ABAP like structures. Use this class as
       a parent for your structures like the following:

           class MY_STRUCT(Structure):
               KEY: str
               VALUE: str

       Instance can be created without parameters or with random subset of
       defined members where the not given ones will hold None.
    """

    def __init__(self, **kwargs):

        for attr, value in kwargs.items():
            # pylint: disable=no-member
            if attr not in self.__class__.__annotations__:
                raise TypeError(f'{self.__class__.__name__} does not define member {attr}')

            self.__dict__[attr] = value

        # pylint: disable=no-member
        for attr in self.__class__.__annotations__:
            if attr not in kwargs:
                self.__dict__[attr] = None

    def __repr__(self):
        return ';'.join(f'{attr}={"" if self.__dict__[attr] is None else self.__dict__[attr]}'
                        # pylint: disable=no-member
                        for attr in self.__class__.__annotations__)

    def __eq__(self, other):
        if other is None:
            return False

        if other.__class__ != self.__class__:
            return False

        if id(other) == id(self):
            return True

        # pylint: disable=no-member
        return all((self.__dict__[attr] == other.__dict__[attr] for attr in self.__class__.__annotations__))


class InternalTableMeta(type):
    """Metaclass for InternalTable which is needed to __getitem__ on class level"""

    def define(cls, name, rowtype):
        """Defines a new internal table type of the given name and the give row
           type.

           Allows you to define new internal table types of the given name
           without the need to create a dummy thing envelope class:

           MY_STRUCT_TT = InternalTable.define('MY_STRUCT_TT', MY_STRUCT)
        """

        return type(name, (cls,), dict(_rowtype=rowtype))

    def __getitem__(cls, rowtype):
        """Defines a new internal table type of the given row type with
           a generated name.

           Particularly useful when you want to save some typing to define
           a new internal table type:

           class MY_STRUCT_TT(InternalTable[MY_STRUCT): pass
        """

        # pylint: disable=no-value-for-parameter
        return cls.define(f'InternalTable_{rowtype.__class__.__name__}', rowtype)


class InternalTable(metaclass=InternalTableMeta):
    """Represents an ABAP internal table with empty key. You can define an inernal
       as a dummy thin envelope class:

           class MY_STRUCT_TT(InternalTable[MY_STRUCT): pass

       or create a type variable:

           MY_STRUCT_TT = InternalTable.define('MY_STRUCT_TT', MY_STRUCT)
    """

    def __init__(self, *args):
        """The instance of InternalTable can created:
             - without parameters
             - with a single parameter of a list of the row type
             - with a single parameter of this internal table
             - with 1-n parameters of the row type
        """

        # pylint: disable=no-member
        self._type = self._rowtype
        self._rows = list()

        if len(args) == 1:
            arg = args[0]

            if isinstance(arg, list):
                for row in arg:
                    self._append_row(row)
            elif isinstance(arg, InternalTable):
                # pylint: disable=protected-access
                if arg._type != self._type:
                    # pylint: disable=protected-access
                    raise TypeError(f'cannot copy InternalTable of type {arg._type.__name__}')

                self._rows = arg._rows.copy()
            else:
                self._append_row(arg)

        elif len(args) > 1:
            for row in args:
                self._append_row(row)

    def __repr__(self):
        return f'[[{self._rows}]]'

    def __iter__(self):
        return self._rows.__iter__()

    def __getitem__(self, index):
        return self._rows.__getitem__(index)

    def __len__(self):
        return self._rows.__len__()

    def _append_row(self, row):
        if not isinstance(row, self._type):
            srctyp = row.__class__.__name__
            tgttyp = self._type.__name__
            raise TypeError(f'type of appended value {srctyp} does not match table type {tgttyp}')

        self._rows.append(row)

    def append(self, *args, **kwargs):
        """Adds new row to the internal table. The method can be called with

           - 1 parameter of the row type
           - Keyword parameters which will be used to create an new instance of the row type
        """

        if args and kwargs:
            raise TypeError('cannot mix positional and keyword parameters')

        if not args and not kwargs:
            raise TypeError('no parameters given')

        if args:
            if len(args) != 1:
                raise TypeError(f'append accepts only one positional argument but {len(args)} were given')

            self._append_row(args[0])
        else:
            factory = self._type
            self._rows.append(factory(**kwargs))


# pylint: disable=invalid-name
StringTable = InternalTable.define('StringTable', str)


def row_type_name_getter(row):
    """Returns type name of the row"""

    return row.__class__.__name__


class XMLSerializers:
    """Helper"""

    @staticmethod
    def internal_table_to_xml(abap_table, dest, prefix, row_name_getter=None):
        """Serializes internal table"""

        if row_name_getter is None:
            row_name_getter = row_type_name_getter

        for item in abap_table:
            if isinstance(item, Structure):
                element = row_name_getter(item)
                dest.write(f'{prefix}<{element}>\n')
                XMLSerializers.struct_members_to_xml(item, dest, prefix + ' ')
                dest.write(f'{prefix}</{element}>\n')
            else:
                dest.write(f'{prefix}<item>{item}</item>\n')

    @staticmethod
    def struct_members_to_xml(abap_struct, dest, prefix):
        """Serializes structure members"""

        for attr, value in abap_struct.__dict__.items():
            if attr.startswith('_'):
                continue

            dest.write(f'{prefix}<{attr}>')

            if isinstance(value, Structure):
                dest.write('\n')
                XMLSerializers.struct_members_to_xml(value, dest, prefix + ' ')
                dest.write(prefix)
            elif isinstance(value, InternalTable):
                item_prefix = prefix + ' '
                dest.write('\n')
                XMLSerializers.internal_table_to_xml(value, dest, item_prefix)
                dest.write(prefix)
            else:
                dest.write(f'{value}')

            dest.write(f'</{attr}>\n')

    @staticmethod
    def abap_to_xml(abap, dest, prefix, top_element=None, row_name_getter=None):
        """Turns an abap instance to an XML"""

        if top_element is None:
            top_element = abap.__class__.__name__

        dest.write(f'''{prefix}<{top_element}>\n''')

        if isinstance(abap, Structure):
            XMLSerializers.struct_members_to_xml(abap, dest, prefix + ' ')
        elif isinstance(abap, InternalTable):
            XMLSerializers.internal_table_to_xml(abap, dest, prefix + ' ', row_name_getter=row_name_getter)

        dest.write(f'''{prefix}</{top_element}>\n''')


def to_xml(abap_struct_or_table, dest, top_element=None):
    """Converts the give parameter into XML"""

    dest.write(f'''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>\n''')

    XMLSerializers.abap_to_xml(abap_struct_or_table, dest, '  ', top_element=top_element)

    dest.write(''' </asx:values>
</asx:abap>\n''')


class ABAPBaseWriter:
    """An adapter for structures and tables"""

    def __init__(self, parent, obj, name):
        self.parent = parent
        self.obj = obj
        self.name = name

    def do_start(self, name, attrs):
        """Handle opening tag in an ancestor class.
           Should return a writer adapter - either self or a new child adapter.
        """

        return self

    def start(self, name, attrs):
        """Handle opening tag - (overwrite do_start)"""

        return self.do_start(name, attrs)

    def get_type(self):
        """Returns type of the adapted object"""

        raise NotImplementedError()

    def get_member_type(self, name):
        """Returns type of the member of the given name"""

        typ = self.get_type()
        try:
            return self.get_type().__annotations__[name]
        except KeyError:
            raise RuntimeError(f'{typ.__name__} does not have the member {name}')

    def do_end(self, name, contents):
        """Handle closing tag in an ancestor class.
           Should return a writer adapter - either self or a new child adapter.
        """

        raise NotImplementedError()

    def set_child(self, name, child_obj):
        """Sets the member of the given name in the adapted object"""

        raise NotImplementedError()

    def end(self, name, contents):
        """Handle closing tag - (overwrite do_end)"""

        if name == self.name:
            if self.parent is not None:
                mod_log().debug('Setting: %s.%s = %s', self.parent.obj, name, self.obj)
                self.parent.set_child(name, self.obj)

            return self.parent

        return self.do_end(name, contents)


class ABAPStructureWriter(ABAPBaseWriter):

    def get_type(self):
        return type(self.obj)

    def set_child(self, name, child_obj):
        setattr(self.obj, name, child_obj)

    def do_end(self, name, contents):
        self.set_child(name, contents)

        return self


class ABAPTableWriter(ABAPBaseWriter):

    def __init__(self, *args, **kwargs):
        super(ABAPTableWriter, self).__init__(*args, **kwargs)

        typ = self.get_type()
        self.plain_list = not issubclass(typ, (Structure, InternalTable))

    def get_type(self):
        return type(self.obj._type)

    def get_member_type(self, name):
        if not self.plain_list:
            raise RuntimeError('Must be called from object writer')

        return self.get_type()

    def do_start(self, name, attrs):
        if name == 'item':
            if not self.plain_list:
                raise RuntimeError('Structure called "item" is not allowed')

            return self

        # Return a new adapter for item type of the table
        row = self.obj._type()
        return ABAPStructureWriter(self, row, name)

    def set_child(self, name, child_obj):
        mod_log().debug('Appending: %s', child_obj)
        self.obj.append(child_obj)

    def do_end(self, name, contents):
        if name != 'item':
            # Closing tag of the item type must be
            # handled in the corresponding adapter.
            raise RuntimeError('No members allowed')

        if not self.plain_list:
            raise RuntimeError('Structure called "item" is not allowed')

        row = self.obj._type(contents)
        self.set_child(name, row)

        return self


class ABAPContentHandler(ContentHandler):
    """A helper class for parsing ABAP types serialized into XML"""

    def __init__(self, master_obj, root_elem=None):
        self.root_elem = master_obj.__class__.__name__ if root_elem is None else root_elem

        typ = type(master_obj)

        if issubclass(typ, Structure):
            self.current = ABAPStructureWriter(None, master_obj, self.root_elem)
        elif issubclass(typ, InternalTable):
            self.current = ABAPTableWriter(None, master_obj, self.root_elem)
        else:
            raise RuntimeError('Master object must be structure or internal table')

        self.contents = None

    def startElement(self, name, attrs):
        mod_log().debug('<%s>', name)

        if name in ['asx:abap', 'asx:values', self.root_elem]:
            return

        typ = self.current.get_member_type(name)

        if issubclass(typ, Structure):
            self.current = ABAPStructureWriter(self.current, typ(), name)
        elif issubclass(typ, InternalTable):
            self.current = ABAPTableWriter(self.current, typ(), name)
        else:
            self.current = self.current.start(name, attrs)
            self.contents = ''

    def characters(self, content):
        if self.contents is None:
            return

        self.contents += content
        mod_log().debug('<>%s</>', self.contents)

    def endElement(self, name):
        mod_log().debug('</%s>', name)

        if name in ['asx:abap', 'asx:values']:
            return

        self.current = self.current.end(name, self.contents)
        self.contents = None


def from_xml(abap_struct_or_table, xml_contents, root_elem=None):
    """"Reads the given xml_contents and stores the values in the give abap_struct_or_table"""

    parser = ABAPContentHandler(abap_struct_or_table, root_elem=root_elem)
    xml.sax.parseString(xml_contents, parser)

    return abap_struct_or_table
