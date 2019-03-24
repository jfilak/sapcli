"""ABAP language utilities"""


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


class InternalTable(object, metaclass=InternalTableMeta):
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


class XMLSerializers:
    """Helper"""

    @staticmethod
    def internal_table_to_xml(abap_table, dest, prefix):
        """Serializes internal table"""

        for item in abap_table:
            if isinstance(item, Structure):
                dest.write(f'{prefix}<{item.__class__.__name__}>\n')
                XMLSerializers.struct_members_to_xml(item, dest, prefix + ' ')
                dest.write(f'{prefix}</{item.__class__.__name__}>\n')
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
    def abap_to_xml(abap, dest, prefix, top_element=None):
        """Turns an abap instance to an XML"""

        if top_element is None:
            top_element = abap.__class__.__name__

        dest.write(f'''{prefix}<{top_element}>\n''')

        if isinstance(abap, Structure):
            XMLSerializers.struct_members_to_xml(abap, dest, prefix + ' ')
        elif isinstance(abap, InternalTable):
            XMLSerializers.internal_table_to_xml(abap, dest, prefix + ' ')

        dest.write(f'''{prefix}</{top_element}>\n''')


def to_xml(abap_struct_or_table, dest, top_element=None):
    """Converts the give parameter into XML"""

    dest.write(f'''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>\n''')

    XMLSerializers.abap_to_xml(abap_struct_or_table, dest, '  ', top_element=top_element)

    dest.write(''' </asx:values>
</asx:abap>\n''')
