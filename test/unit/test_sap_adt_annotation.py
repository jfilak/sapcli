#!/bin/python

import unittest

import sap.adt
from sap.adt.annotations import xml_attribute, xml_element, XmlElementKind, XmlNodeProperty, XmlElementProperty, \
                                XmlAttributeProperty, XmlNodeAttributeProperty, XmlContainer, XmlListNodeProperty


class DummyClass:

    def __init__(self, value):
        self._value = value

    def __eq__(self, other):
        return self._value == other._value

    @xml_attribute('myValue')
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class ElementClass:

    def __init__(self, dummy):
        self._dummy = dummy

    @xml_element('myElement')
    def dummy(self):
        return self._dummy

    @dummy.setter
    def dummy(self, value):
        self._dummy = value

    @xml_element('serializer', deserialize=False)
    def readonly(self):
        return self._dummy

    @xml_element('noempty', ignore_empty=True)
    def noempty(self):
        return self._dummy


DummyList = XmlContainer.define('dummyitem', DummyClass)
DummyListConfigured = XmlContainer.define('dummyitemconfigured', DummyClass, version='v2')


class TestADTAnnotation(unittest.TestCase):

    def test_xml_attribute(self):
        def fget(obj):
            return obj['bar']

        def fset(obj, value):
            obj['bar'] = value

        obj = {'bar': 'blah'}

        dec = xml_attribute('foo')
        getter = dec(fget)
        self.assertEqual(getter.__get__(obj), 'blah')

        setter = getter.setter(fset)
        setter.__set__(obj, 'grc')
        self.assertEqual(getter.__get__(obj), 'grc')

    def test_xml_attribute_decorator(self):
        victory = DummyClass('initial')
        self.assertEqual(victory.value, 'initial')

        victory.value = 'updated'
        self.assertEqual(victory.value, 'updated')

    def test_xml_attribute_version(self):
        deserialized = xml_attribute('versioned')
        self.assertIsNone(deserialized(None).version)

        readonly = xml_attribute('readonly', version='v2')
        self.assertEqual(readonly(None).version, 'v2')

    def test_xml_element(self):
        def fget(obj):
            return obj['bar']

        def fset(obj, value):
            obj['bar'] = value

        obj = {'bar': 'blah'}

        dec = xml_element('foo')
        getter = dec(fget)
        self.assertEqual(getter.__get__(obj), 'blah')

        setter = getter.setter(fset)
        setter.__set__(obj, 'grc')
        self.assertEqual(getter.__get__(obj), 'grc')

    def test_xml_element_decorator(self):
        victory = ElementClass(DummyClass('initial'))
        self.assertEqual(victory.dummy.value, 'initial')

        victory.dummy = DummyClass('updated')
        self.assertEqual(victory.dummy.value, 'updated')

    def test_xml_element_deserialize(self):
        deserialized = xml_element('deserialized')
        self.assertTrue(deserialized(None).deserialize)

        readonly = xml_element('readonly', deserialize=False)
        self.assertFalse(readonly(None).deserialize)

    def test_xml_element_version(self):
        deserialized = xml_element('versioned')
        self.assertIsNone(deserialized(None).version)

        readonly = xml_element('readonly', version='v2')
        self.assertEqual(readonly(None).version, 'v2')

    def test_xml_element_factory(self):
        wo_factory = xml_element('wo_factory')
        self.assertIsNone(wo_factory(None).factory)

        factory = xml_element('factory', factory=int)
        self.assertEqual(factory(None).factory, int)

        factory = xml_element('factory', factory=int)
        self.assertEqual(factory(None).setter(None).factory, int)

    def test_xml_element_kind(self):
        wo_kind = xml_element('wo_kind')
        self.assertEqual(wo_kind(None).kind, XmlElementKind.OBJECT)

        kind = xml_element('kind', kind=XmlElementKind.TEXT)
        self.assertEqual(kind(None).kind, XmlElementKind.TEXT)

        kind_setter = xml_element('factory', kind=XmlElementKind.TEXT)
        self.assertEqual(kind_setter(None).setter(None).kind, XmlElementKind.TEXT)

    def test_xml_node_property_init(self):
        template = XmlElementProperty('element', None)

        node = XmlNodeProperty('element')
        self.assertIsNone(node.default_value)
        self.assertEqual(node.name, template.name)
        self.assertEqual(node.kind, template.kind)
        self.assertEqual(node.factory, template.factory)
        self.assertEqual(node.deserialize, template.deserialize)
        self.assertEqual(node.version, template.version)
        self.assertEqual(node.ignore_empty, template.ignore_empty)

        node = XmlNodeProperty('element', value='value', deserialize=False, factory=str, kind=XmlElementKind.TEXT,
                               version='v2', ignore_empty=True)
        self.assertEqual(node.default_value, 'value')
        self.assertEqual(node.name, 'element')
        self.assertEqual(node.kind, XmlElementKind.TEXT)
        self.assertEqual(node.factory, str)
        self.assertFalse(node.deserialize)
        self.assertEqual(node.version, 'v2')
        self.assertTrue(node.ignore_empty)

    def test_xml_node_property_get_set(self):
        node = XmlNodeProperty('element', value='value')
        obj = node

        self.assertEqual(node.get(obj), 'value')
        node.set(obj, 'foo')
        self.assertEqual(node.get(obj), 'foo')
        self.assertEqual(node.default_value, 'value')

    def test_xml_node_attribute_property_init(self):
        template = XmlAttributeProperty('attribute', None)

        node = XmlNodeAttributeProperty('attribute')
        self.assertIsNone(node.default_value)
        self.assertEqual(node.name, template.name)
        self.assertEqual(node.deserialize, template.deserialize)
        self.assertEqual(node.version, template.version)

        node = XmlNodeAttributeProperty('attribute2', value='value', deserialize=False, version='v2')
        self.assertEqual(node.default_value, 'value')
        self.assertEqual(node.name, 'attribute2')
        self.assertFalse(node.deserialize)
        self.assertEqual(node.version, 'v2')

    def test_xml_node_attribute_property_get_set(self):
        node = XmlNodeAttributeProperty('attribute3', value='value2')
        obj = node

        self.assertEqual(node.get(obj), 'value2')
        node.set(obj, 'foo2')
        self.assertEqual(node.get(obj), 'foo2')
        self.assertEqual(node.default_value, 'value2')

    def test_xml_container_instance(self):
        the_list = DummyList()

        the_list.items = DummyClass(1)
        the_list.items = DummyClass(2)

        self.assertEqual(the_list.items, [DummyClass(1), DummyClass(2)])

        self.assertEqual(len(the_list), 2)
        self.assertEqual(the_list[0], DummyClass(1))
        self.assertEqual(the_list[1], DummyClass(2))

        copy = [item for item in the_list]
        self.assertEqual(copy, [DummyClass(1), DummyClass(2)])

    def test_xml_container_version(self):
        the_nover_list = DummyList()
        attr = getattr(the_nover_list.__class__, 'items')
        self.assertEqual(attr.version, None)

        the_configured_list = DummyListConfigured()
        attr = getattr(the_configured_list.__class__, 'items')
        self.assertEqual(attr.version, 'v2')

    def test_xml_list_node_property_init(self):
        template = XmlElementProperty('element', None)

        node = XmlListNodeProperty('element')
        self.assertIsNone(node.default_value)
        self.assertEqual(node.name, template.name)
        self.assertEqual(node.kind, template.kind)
        self.assertEqual(node.factory, template.factory)
        self.assertEqual(node.deserialize, template.deserialize)
        self.assertEqual(node.version, template.version)

        node = XmlListNodeProperty('element', value=['value'], deserialize=False, factory=str, kind=XmlElementKind.TEXT,
                                   version='v2')
        self.assertEqual(node.default_value, ['value'])
        self.assertEqual(node.name, 'element')
        self.assertEqual(node.kind, XmlElementKind.TEXT)
        self.assertEqual(node.factory, str)
        self.assertFalse(node.deserialize)
        self.assertEqual(node.version, 'v2')

    def test_xml_list_node_property_get_set(self):
        check_value = ['a', 'b']
        node = XmlListNodeProperty('element', value=check_value)
        obj = node

        self.assertEqual(node.__get__(obj), ['a', 'b'])
        node.__set__(obj, 'c')
        self.assertEqual(node.__get__(obj), ['a', 'b', 'c'])

        self.assertEqual(node.default_value, ['a', 'b'])
        self.assertEqual(check_value, ['a', 'b'])

    def test_xml_list_node_property_default_none(self):
        node = XmlListNodeProperty('element')
        obj = node

        self.assertEqual(node.__get__(obj), None)
        node.__set__(obj, 'c')
        self.assertEqual(node.__get__(obj), ['c'])

        self.assertEqual(node.default_value, None)

    def test_xml_list_node_property_default_no_list(self):
        with self.assertRaises(RuntimeError) as caught:
            node = XmlListNodeProperty('element', value=1)


if __name__ == '__main__':
    unittest.main()
