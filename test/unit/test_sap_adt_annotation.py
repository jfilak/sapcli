#!/bin/python

import unittest

import sap.adt
from sap.adt.annotations import xml_attribute, xml_element


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

    def test_xml_attribute_decorator(self):
        victory = ElementClass(DummyClass('initial'))
        self.assertEquals(victory.dummy.value, 'initial')

        victory.dummy = DummyClass('updated')
        self.assertEquals(victory.dummy.value, 'updated')


if __name__ == '__main__':
    unittest.main()
