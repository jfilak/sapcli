#!/bin/python

import unittest

from sap.adt import ADTObject, ADTObjectType, ADTCoreData, OrderedClassMembers
from sap.adt.annotations import xml_element, xml_attribute
from sap.adt.marshalling import Marshal, Element


class Dummy(ADTObject):

    OBJTYPE = ADTObjectType(
        'CODE',
        'prefix/dummy',
        ('dummyxmlns', 'http://www.sap.com/adt/xmlns/dummy'),
        'application/vnd.sap.adt.test.elements.v2+xml',
        {'text/plain': 'source/main'},
        'dummyelem'
    )

    class Nested(metaclass=OrderedClassMembers):

        class SuperNested(metaclass=OrderedClassMembers):

            @xml_attribute('sup_nst_fst')
            def yetanother(self):
                return 'yetanother'

        @xml_attribute('nst_fst')
        def first(self):
            return 'nst_fst_val'

        @xml_attribute('nst_scn')
        def second(self):
            return 'nst_scn_val'

        @xml_element('child_nst')
        def supernested(self):
            return Dummy.Nested.SuperNested()

    def __init__(self):
        super(Dummy, self).__init__(
            None, 'dmtname',
            metadata=ADTCoreData(
                package='testpkg',
                description='Description',
                language='CZ',
                master_language='EN',
                master_system='NPL',
                responsible='FILAK'
            )
        )

        self._nested = Dummy.Nested()

    @xml_attribute('attr_first')
    def first(self):
        return '11111'

    @xml_attribute('attr_second')
    def second(self):
        return '22222'

    @xml_element('first_elem')
    def value(self):
        return self._nested


class TestADTAnnotation(unittest.TestCase):

    def test_tree_generation(self):
        obj = Dummy()
        marshal = Marshal()
        xmltree = marshal._object_to_tree(obj)

        self.assertEqual(xmltree.name, 'dummyxmlns:dummyelem')
        self.assertEqual(xmltree.attributes['attr_first'], '11111')
        self.assertEqual(xmltree.attributes['attr_second'], '22222')

        self.assertEqual(xmltree.children[0].name, 'adtcore:packageRef')

        self.assertEqual(xmltree.children[1].name, 'first_elem')
        self.assertEqual(xmltree.children[1].attributes['nst_fst'], 'nst_fst_val')
        self.assertEqual(xmltree.children[1].attributes['nst_scn'], 'nst_scn_val')

        self.assertEqual(xmltree.children[1].children[0].name, 'child_nst')
        self.assertEqual(xmltree.children[1].children[0].attributes['sup_nst_fst'], 'yetanother')

    def test_xml_formatting(self):
        marshal = Marshal()
        elem = Element('root')
        elem.add_attribute('one', '1')
        elem.add_attribute('two', '2')
        child = elem.add_child('child')
        xml = marshal._tree_to_xml(elem)
        self.assertEqual(xml, '<?xml version="1.0" encoding="UTF-8"?>\n<root one="1" two="2">\n<child/>\n</root>')


if __name__ == '__main__':
    unittest.main()
