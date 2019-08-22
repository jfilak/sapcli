#!/bin/python

import unittest

import sap.adt
from sap.adt.annotations import xml_attribute, xml_element, XmlElementKind


class DummyClass:

    def __init__(self, value):
        self._value = value

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
        self.assertEquals(victory.value, 'initial')

        victory.value = 'updated'
        self.assertEquals(victory.value, 'updated')

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
        self.assertEquals(victory.dummy.value, 'initial')

        victory.dummy = DummyClass('updated')
        self.assertEquals(victory.dummy.value, 'updated')

    def test_xml_element_deserialize(self):
        deserialized = xml_element('deserialized')
        self.assertTrue(deserialized(None).deserialize)

        readonly = xml_element('readonly', deserialize=False)
        self.assertFalse(readonly(None).deserialize)

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


if __name__ == '__main__':
    unittest.main()
