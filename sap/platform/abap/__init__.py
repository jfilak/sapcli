"""ABAP language utilities"""

from typing import List


# pylint: disable=too-few-public-methods
class Structure:
    """NamedTuple like class"""

    def __init__(self, **kwargs):
        setattr(self, '__dict__', kwargs)


InternalTable = List
# pylint: disable=invalid-name
StringTable = InternalTable[str]


class _Auxiliary:
    """Helper"""

    @staticmethod
    def internal_table_to_xml(abap_table, dest, prefix):
        """Serializes internal table"""

        for item in abap_table:
            if isinstance(item, Structure):
                dest.write(f'{prefix}<{item.__class__.__name__}>\n')
                _Auxiliary.struct_members_to_xml(item, dest, prefix + ' ')
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
                _Auxiliary.struct_members_to_xml(value, dest, prefix + ' ')
                dest.write(prefix)
            elif isinstance(value, InternalTable):
                item_prefix = prefix + ' '
                dest.write('\n')
                _Auxiliary.internal_table_to_xml(value, dest, item_prefix)
                dest.write(prefix)
            else:
                dest.write(f'{value}')

            dest.write(f'</{attr}>\n')


def to_xml(abap_struct_or_table, dest, top_element=None):
    """Converts the give parameter into XML"""

    if top_element is None:
        top_element = abap_struct_or_table.__class__.__name__

    dest.write(f'''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <{top_element}>\n''')

    if isinstance(abap_struct_or_table, Structure):
        _Auxiliary.struct_members_to_xml(abap_struct_or_table, dest, '   ')
    elif isinstance(abap_struct_or_table, InternalTable):
        _Auxiliary.internal_table_to_xml(abap_struct_or_table, dest, '   ')

    dest.write(f'''  </{top_element}>
 </asx:values>
</asx:abap>\n''')
