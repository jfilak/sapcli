#!/bin/python

import unittest

from sap import get_logger
from sap.adt import ADTObject, ADTObjectType, ADTCoreData, OrderedClassMembers
from sap.adt.objects import XMLNamespace
from sap.adt.annotations import xml_element, xml_attribute, XmlElementProperty, XmlElementKind, XmlNodeProperty, \
                                XmlNodeAttributeProperty, XmlContainer, XmlListNodeProperty
from sap.adt.marshalling import Marshal, Element, adt_object_to_element_name, ElementHandler


class Dummy(ADTObject):

    OBJTYPE = ADTObjectType(
        'CODE',
        'prefix/dummy',
        XMLNamespace('dummyxmlns', 'http://www.sap.com/adt/xmlns/dummy'),
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

    @xml_attribute('attr_third', deserialize=False)
    def third(self):
        return '3333'

    @xml_element('first_elem')
    def value(self):
        return self._nested

    @xml_element('readonly_elem', deserialize=False)
    def readonly(self):
        return Dummy.Nested()


class DummyWithSetters(ADTObject):

    OBJTYPE = ADTObjectType(
        'CODE',
        'prefix/dummy',
        XMLNamespace('dummyxmlns', 'http://www.sap.com/adt/xmlns/dummy'),
        'application/vnd.sap.adt.test.elements.v2+xml',
        {'text/plain': 'source/main'},
        'dummyelem'
    )

    class Nested(metaclass=OrderedClassMembers):

        class SuperNested(metaclass=OrderedClassMembers):

            def __init__(self):
                self._yetanother = None

            @xml_attribute('sup_nst_fst')
            def yetanother(self):
                return self._yetanother

            @yetanother.setter
            def yetanother(self, value):
                self._yetanother = value

        def __init__(self):
            self._child = DummyWithSetters.Nested.SuperNested()
            self._first = None
            self._second = None

        @xml_attribute('nst_fst')
        def first(self):
            return self._first

        @first.setter
        def first(self, value):
            self._first = value

        @xml_attribute('nst_scn')
        def second(self):
            return self._second

        @second.setter
        def second(self, value):
            self._second = value

        @xml_element('child_nst')
        def supernested(self):
            return self._child


    def __init__(self):
        super(DummyWithSetters, self).__init__(
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

        self._nested = DummyWithSetters.Nested()
        self._first = None
        self._second = None

    @xml_attribute('attr_first')
    def first(self):
        return self._first

    @first.setter
    def first(self, value):
        self._first = value

    @xml_attribute('attr_second')
    def second(self):
        return self._second

    @second.setter
    def second(self, value):
        self._second = value

    @xml_attribute('attr_third', deserialize=False)
    def third(self):
        return 'EEE'

    @xml_element('first_elem')
    def value(self):
        return self._nested

    @xml_element('readonly_elem', deserialize=False)
    def readonly(self):
        # If there is a bug in deserialization, the return None will reveal
        # that Marshal tried to modify read-only property
        return None



class DummyChild(metaclass=OrderedClassMembers):

    instances = None

    def __init__(self):
        if DummyChild.instances is None:
            DummyChild.instances = list()
        DummyChild.instances.append(self)

        get_logger().debug('New instance')
        self._attribute = None

    @xml_attribute('attribute')
    def attribute(self):
        return self._attribute

    @attribute.setter
    def attribute(self, value):
        self._attribute = value


class DummyWithChildFactory(ADTObject):

    OBJTYPE = ADTObjectType(
        'CODE',
        'prefix/dummy',
        XMLNamespace('dummyxmlns', 'http://www.sap.com/adt/xmlns/dummy'),
        'application/vnd.sap.adt.test.elements.v2+xml',
        {'text/plain': 'source/main'},
        'dummyelem'
    )

    def __init__(self):
        self._child = None
        self._child_setter = None

    @xml_element('child', factory=DummyChild)
    def child(self):
        return self._child

    @xml_element('child_setter', factory=DummyChild)
    def child_setter(self):
        get_logger().debug('Get instance')
        return self._child_setter

    @child_setter.setter
    def child_setter(self, value):
        get_logger().debug('Set instance')
        self._child_setter = value


class DummyADTCore(ADTObject):

    OBJTYPE = ADTObjectType(
        None,
        None,
        XMLNamespace('adtcore', 'http://www.sap.com/adt/core'),
        None,
        None,
        'root'
    )

    def __init__(self):
        super(DummyADTCore, self).__init__(None, None)


class DummyContainerItem(metaclass=OrderedClassMembers):

    def __init__(self, no=None):
        self._no = no

    @xml_attribute('number')
    def attribute(self):
        return self._no

    @attribute.setter
    def attribute(self, value):
        self._no = int(value)

    def __eq__(self, other):
        return self._no == other._no

    def __repr__(self):
        return f'DummyContainerItem({self._no})'


class DummyContainer(ADTObject):

    OBJTYPE = ADTObjectType(
        None,
        None,
        XMLNamespace('adtcore', 'http://www.sap.com/adt/core'),
        None,
        None,
        'container'
    )

    def __init__(self):
        super(DummyContainer, self).__init__(None, None)

    @xml_element('item')
    def items(self):
        return [DummyContainerItem('1'), DummyContainerItem('2'), DummyContainerItem('3')]


class DummyOjbectWithContainer(ADTObject):

    OBJTYPE = ADTObjectType(
        None,
        None,
        XMLNamespace('adtcore', 'http://www.sap.com/adt/core'),
        None,
        None,
        'container'
    )

    ContainerClass = XmlContainer.define('item', DummyContainerItem)

    def __init__(self):
        super(DummyOjbectWithContainer, self).__init__(None, None)

        self._items = DummyOjbectWithContainer.ContainerClass()

    @xml_element('items')
    def items(self):
        return self._items


class ChildrenADTObject(metaclass=OrderedClassMembers):

    def __init__(self):
        self.objtype = ADTObjectType(None, None,
                                     XMLNamespace('mock', 'https://example.org/mock',
                                                  parents=[XMLNamespace('foo', 'bar')]),
                                     'application/xml',
                                     None,
                                     'child')

    @xml_attribute('value')
    def value(self):
        return "stub"


class ParentADTObject(metaclass=OrderedClassMembers):

    def __init__(self):
        self.objtype = ADTObjectType(None, None,
                                     XMLNamespace('mock', 'https://example.org/mock'),
                                     'application/xml',
                                     None,
                                     'parent')

    @xml_element(XmlElementProperty.NAME_FROM_OBJECT)
    def children(self):
        return ChildrenADTObject()


class TextElementADTObject(metaclass=OrderedClassMembers):

    def __init__(self):
        self.objtype = ADTObjectType(None, None,
                                     XMLNamespace('mock', 'https://example.org/mock'),
                                     'application/xml',
                                     None,
                                     'have_child_with_text')
        self._text = 'content'

    @xml_element('mock:holdstext', kind=XmlElementKind.TEXT)
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value


class XmlNodePropertyADTObject(metaclass=OrderedClassMembers):

    def __init__(self):
        self.objtype = ADTObjectType(None, None,
                                     XMLNamespace('mock', 'https://example.org/mock'),
                                     'application/xml',
                                     None,
                                     'xmlnodeparent')

    child = XmlNodeProperty('mock:child', factory=DummyChild)


class XmlNodeAttributePropertyADTObject(metaclass=OrderedClassMembers):

    def __init__(self):
        self.objtype = ADTObjectType(None, None,
                                     XMLNamespace('mock', 'https://example.org/mock'),
                                     'application/xml',
                                     None,
                                     'xmlnode')

    attribute = XmlNodeAttributeProperty('mock:attribute')


class DummyWithTheTextList(metaclass=OrderedClassMembers):

    def __init__(self):
        self.objtype = ADTObjectType(None, None,
                                     XMLNamespace('mock', 'https://example.org/mock'),
                                     'application/xml',
                                     None,
                                     'withlist')

    the_text_list = XmlListNodeProperty('mock:item', kind=XmlElementKind.TEXT)


class DummyADTObjectWithVersions(ADTObject):

    OBJTYPE = ADTObjectType(
        None,
        None,
        XMLNamespace('mock', 'https://github.com/jfilak/sapcli/mock'),
        None,
        None,
        'versioned'
    )

    elemverfst = XmlNodeProperty('mock:elemverfst', kind=XmlElementKind.TEXT, version='V1')
    elemverboth = XmlNodeProperty('mock:elemverboth', kind=XmlElementKind.TEXT, version=['V1', 'V2'])

    attrverfst = XmlNodeAttributeProperty('mock:attrverfst', version='V1')
    attrverboth = XmlNodeAttributeProperty('mock:attrverboth', version=['V1', 'V2'])

    def __init__(self):
        super(DummyADTObjectWithVersions, self).__init__(None, None)

        self._elemverall = 'Init-elem-all'
        self.elemverfst = 'Init-elem-fst'
        self.elemverboth = 'Init-elem-both'

        self._attrverall = 'Init-attr-all'
        self.attrverfst = 'Init-attr-fst'
        self.attrverboth = 'Init-attr-both'

    @xml_element('mock:elemverall', kind=XmlElementKind.TEXT)
    def elemverall(self):
        return self._elemverall

    @elemverall.setter
    def elemverall(self, value):
        self._elemverall = value

    @xml_attribute('mock:attrverall')
    def attrverall(self):
        return self._attrverall

    @attrverall.setter
    def attrverall(self, value):
        self._attrverall = value


class TestADTAnnotation(unittest.TestCase):


    def test_tree_generation(self):
        obj = Dummy()
        marshal = Marshal()
        xmltree = marshal._object_to_tree(obj)

        self.assertEqual(xmltree.name, 'dummyxmlns:dummyelem')
        self.assertEqual(xmltree.attributes['attr_first'], '11111')
        self.assertEqual(xmltree.attributes['attr_second'], '22222')
        self.assertEqual(xmltree.attributes['attr_third'], '3333')

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

    def test_element_handler(self):
        adt_object = DummyWithSetters()
        name = '/' + adt_object_to_element_name(adt_object)
        self.assertEqual('/dummyxmlns:dummyelem', name)

        elements = dict()
        handler = ElementHandler(name, elements, lambda: adt_object)
        elements[name] = handler
        handler.new()

        self.assertIn(f'{name}/first_elem', elements)

        handler.set('attr_first', '1st')
        self.assertEqual(adt_object.first, '1st')

        handler.set('attr_second', '2nd')
        self.assertEqual(adt_object.second, '2nd')

        child_handler = elements[f'{name}/first_elem']
        child_handler.new()

        self.assertIn(f'{name}/first_elem/child_nst', elements)

        child_handler.set('nst_fst', '1.')
        self.assertEqual(adt_object.value.first, '1.')

        child_handler.set('nst_scn', '2.')
        self.assertEqual(adt_object.value.second, '2.')

        grand_child_handler = elements[f'{name}/first_elem/child_nst']
        grand_child_handler.new()

        grand_child_handler.set('sup_nst_fst', 'X')
        self.assertEqual(adt_object.value.supernested.yetanother, 'X')


    def test_deserialization(self):
        obj = Dummy()
        marshal = Marshal()
        xml_data = marshal.serialize(obj)

        clone = DummyWithSetters()
        ret = Marshal.deserialize(xml_data, clone)
        self.assertEqual(clone, ret)

        self.assertEqual(obj.first, clone.first)
        self.assertEqual(obj.second, clone.second)
        self.assertEqual('EEE', clone.third)
        self.assertEqual(obj.value.first, clone.value.first)
        self.assertEqual(obj.value.second, clone.value.second)
        self.assertEqual(obj.value.supernested.yetanother, clone.value.supernested.yetanother)

    def test_deserialize_with_factory(self):
        dummy = DummyWithChildFactory()

        Marshal.deserialize("""<?xml version="1.0" encoding="UTF-8"?>
<dummyxmlns:dummyelem>
  <child attribute="implicit"/>
  <child_setter attribute="setter"/>
</dummyxmlns:dummyelem>
""", dummy)

        self.assertEqual(DummyChild.instances[0].attribute, 'implicit')
        self.assertEqual(dummy.child_setter.attribute, 'setter')

    def test_serialize_adtcore_and_no_code(self):
        obj = DummyADTCore()
        act = Marshal().serialize(obj)

        self.assertEqual(act, '''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:root xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:packageRef/>
</adtcore:root>''')

    def test_serialize_list(self):
        container = DummyContainer()

        act = Marshal().serialize(container)

        self.assertEqual(act, '''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:container xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:packageRef/>
<item number="1"/>
<item number="2"/>
<item number="3"/>
</adtcore:container>''')

    def test_serialize_with_elem_from_object(self):
        parent = ParentADTObject()

        act = Marshal().serialize(parent)

        self.assertEqual(act, '''<?xml version="1.0" encoding="UTF-8"?>
<mock:parent xmlns:mock="https://example.org/mock">
<mock:child xmlns:foo="bar" value="stub"/>
</mock:parent>''')

    def test_serialize_with_elem_text(self):
        parent = TextElementADTObject()

        act = Marshal().serialize(parent)

        self.assertEqual(act, '''<?xml version="1.0" encoding="UTF-8"?>
<mock:have_child_with_text xmlns:mock="https://example.org/mock">
<mock:holdstext>content</mock:holdstext>
</mock:have_child_with_text>''')

    def test_deserialize_with_elem_text(self):
        parent = TextElementADTObject()

        Marshal.deserialize('''<?xml version="1.0" encoding="UTF-8"?>
<mock:have_child_with_text xmlns:mock="https://example.org/mock">
<mock:holdstext>message</mock:holdstext>
</mock:have_child_with_text>''', parent)

        self.assertEqual(parent.text, 'message')

    def test_deserialize_with_elem_text_empty(self):
        parent = TextElementADTObject()

        Marshal.deserialize('''<?xml version="1.0" encoding="UTF-8"?>
<mock:have_child_with_text xmlns:mock="https://example.org/mock">
<mock:holdstext></mock:holdstext>
</mock:have_child_with_text>''', parent)

        self.assertEqual(parent.text, '')

    def test_serialize_with_node_object_none(self):
        parent = XmlNodePropertyADTObject()
        self.assertIsNone(parent.child)

        act = Marshal().serialize(parent)

        self.assertEqual(act, '''<?xml version="1.0" encoding="UTF-8"?>
<mock:xmlnodeparent xmlns:mock="https://example.org/mock">
<mock:child/>
</mock:xmlnodeparent>''')

    def test_serialize_with_node_attribute_value_none(self):
        parent = XmlNodeAttributePropertyADTObject()
        self.assertIsNone(parent.attribute)

        act = Marshal().serialize(parent)

        self.assertEqual(act, '''<?xml version="1.0" encoding="UTF-8"?>
<mock:xmlnode xmlns:mock="https://example.org/mock"/>''')

    def test_serialize_with_node_object(self):
        parent = XmlNodePropertyADTObject()
        parent.child = DummyChild()
        self.assertIsNotNone(parent.child)

        # TODO: why it does not mind invalid attr name
        parent.child.attribute = 'foo'
        self.assertEqual(parent.child.attribute, 'foo')

        act = Marshal().serialize(parent)

        self.assertEqual(act, '''<?xml version="1.0" encoding="UTF-8"?>
<mock:xmlnodeparent xmlns:mock="https://example.org/mock">
<mock:child attribute="foo"/>
</mock:xmlnodeparent>''')

    def test_serialize_with_node_attribute_value(self):
        parent = XmlNodeAttributePropertyADTObject()
        parent.attribute = 'foo'
        self.assertIsNotNone(parent.attribute)

        # TODO: why it does not mind invalid attr name
        parent.attribute = 'foo'
        self.assertEqual(parent.attribute, 'foo')

        act = Marshal().serialize(parent)

        self.assertEqual(act, '''<?xml version="1.0" encoding="UTF-8"?>
<mock:xmlnode xmlns:mock="https://example.org/mock" mock:attribute="foo"/>''')

    def test_deserialize_with_node_object_missing(self):
        parent = XmlNodePropertyADTObject()

        Marshal.deserialize('''<?xml version="1.0" encoding="UTF-8"?>
<mock:xmlnodeparent xmlns:mock="https://example.org/mock"/>''', parent)

        self.assertIsNone(parent.child)

    def test_deserialize_with_node_attribute_missing(self):
        parent = XmlNodeAttributePropertyADTObject()

        Marshal.deserialize('''<?xml version="1.0" encoding="UTF-8"?>
<mock:xmlnode xmlns:mock="https://example.org/mock"/>''', parent)

        self.assertIsNone(parent.attribute)

    def test_deserialize_with_node_object_none(self):
        parent = XmlNodePropertyADTObject()

        Marshal.deserialize('''<?xml version="1.0" encoding="UTF-8"?>
<mock:xmlnodeparent xmlns:mock="https://example.org/mock">
<mock:child/>
</mock:xmlnodeparent>''', parent)

        self.assertIsNotNone(parent.child)

    def test_deserialize_with_node_object(self):
        parent = XmlNodePropertyADTObject()
        Marshal.deserialize('''<?xml version="1.0" encoding="UTF-8"?>
<mock:xmlnodeparent xmlns:mock="https://example.org/mock">
<mock:child attribute="deserialize"/>
</mock:xmlnodeparent>''', parent)

        self.assertIsNotNone(parent.child)
        self.assertEqual(parent.child.attribute, 'deserialize')

    def test_deserialize_with_node_attribute_value(self):
        parent = XmlNodeAttributePropertyADTObject()
        Marshal.deserialize('''<?xml version="1.0" encoding="UTF-8"?>
<mock:xmlnode xmlns:mock="https://example.org/mock" mock:attribute="deserialize"/>''', parent)

        self.assertEqual(parent.attribute, 'deserialize')

    def test_serialize_xml_container(self):
        container = DummyOjbectWithContainer()

        container.items.append(DummyContainerItem(1))
        container.items.append(DummyContainerItem(2))
        container.items.append(DummyContainerItem(3))

        act = Marshal().serialize(container)

        self.assertEqual(act, '''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:container xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:packageRef/>
<items>
<item number="1"/>
<item number="2"/>
<item number="3"/>
</items>
</adtcore:container>''')

    def test_deserialize_xml_container(self):
        container = DummyOjbectWithContainer()

        act = Marshal.deserialize('''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:container xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:packageRef/>
<items>
<item number="1"/>
<item number="2"/>
<item number="3"/>
</items>
</adtcore:container>''', container)

        self.assertEqual(container.items[0], DummyContainerItem(1))
        self.assertEqual(container.items[1], DummyContainerItem(2))
        self.assertEqual(container.items[2], DummyContainerItem(3))

    def test_serialize_xml_text_list(self):
        container = DummyWithTheTextList()

        container.the_text_list = '1'
        container.the_text_list = '2'
        container.the_text_list = '3'

        act = Marshal().serialize(container)

        self.assertEqual(act, '''<?xml version="1.0" encoding="UTF-8"?>
<mock:withlist xmlns:mock="https://example.org/mock">
<mock:item>1</mock:item>
<mock:item>2</mock:item>
<mock:item>3</mock:item>
</mock:withlist>''')

    def test_deserialize_xml_text_list(self):
        container = DummyWithTheTextList()

        act = Marshal.deserialize('''<?xml version="1.0" encoding="UTF-8"?>
<mock:withlist xmlns:mock="https://example.org/mock">
<mock:item>1</mock:item>
<mock:item>2</mock:item>
<mock:item>3</mock:item>
</mock:withlist>''', container)

        self.assertEqual(container.the_text_list, ['1', '2', '3'])

    def test_serialize_versioned_none(self):
        obj = DummyADTObjectWithVersions()
        marshal = Marshal()

        with self.assertRaises(RuntimeError) as caught:
            xml = marshal.serialize(obj)

        self.assertEqual(str(caught.exception), 'The XML item mock:elemverfst specifies but its parent class does not')

    def test_serialize_versioned_ver1(self):
        obj = DummyADTObjectWithVersions()
        marshal = Marshal(object_schema_version='V1')
        xml = marshal.serialize(obj)

        self.maxDiff = None

        self.assertEqual(xml, '''<?xml version="1.0" encoding="UTF-8"?>
<mock:versioned xmlns:mock="https://github.com/jfilak/sapcli/mock" mock:attrverfst="Init-attr-fst" mock:attrverboth="Init-attr-both" mock:attrverall="Init-attr-all">
<adtcore:packageRef/>
<mock:elemverfst>Init-elem-fst</mock:elemverfst>
<mock:elemverboth>Init-elem-both</mock:elemverboth>
<mock:elemverall>Init-elem-all</mock:elemverall>
</mock:versioned>''')

    def test_serialize_versioned_ver2(self):
        obj = DummyADTObjectWithVersions()
        marshal = Marshal(object_schema_version='V2')
        xml = marshal.serialize(obj)

        self.maxDiff = None

        self.assertEqual(xml, '''<?xml version="1.0" encoding="UTF-8"?>
<mock:versioned xmlns:mock="https://github.com/jfilak/sapcli/mock" mock:attrverboth="Init-attr-both" mock:attrverall="Init-attr-all">
<adtcore:packageRef/>
<mock:elemverboth>Init-elem-both</mock:elemverboth>
<mock:elemverall>Init-elem-all</mock:elemverall>
</mock:versioned>''')

    def test_serialize_versioned_ver3(self):
        obj = DummyADTObjectWithVersions()
        marshal = Marshal(object_schema_version='V3')
        xml = marshal.serialize(obj)

        self.maxDiff = None

        self.assertEqual(xml, '''<?xml version="1.0" encoding="UTF-8"?>
<mock:versioned xmlns:mock="https://github.com/jfilak/sapcli/mock" mock:attrverall="Init-attr-all">
<adtcore:packageRef/>
<mock:elemverall>Init-elem-all</mock:elemverall>
</mock:versioned>''')

    def test_deserialize_versioned(self):
        obj = DummyADTObjectWithVersions()
        marshal = Marshal()
        marshal.deserialize('''<?xml version="1.0" encoding="UTF-8"?>
<mock:versioned xmlns:mock="https://github.com/jfilak/sapcli/mock" mock:attrverfst="de-attr-fst" mock:attrverboth="de-attr-both" mock:attrverall="de-attr-all">
<adtcore:packageRef/>
<mock:elemverfst>de-elem-fst</mock:elemverfst>
<mock:elemverboth>de-elem-both</mock:elemverboth>
<mock:elemverall>de-elem-all</mock:elemverall>
</mock:versioned>''', obj)

        self.assertEqual(obj.attrverfst, 'de-attr-fst')
        self.assertEqual(obj.attrverboth, 'de-attr-both')
        self.assertEqual(obj.attrverall, 'de-attr-all')

        self.assertEqual(obj.elemverfst, 'de-elem-fst')
        self.assertEqual(obj.elemverboth, 'de-elem-both')
        self.assertEqual(obj.elemverall, 'de-elem-all')


if __name__ == '__main__':
    unittest.main()
