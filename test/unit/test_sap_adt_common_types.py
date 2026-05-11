#!/bin/python

import unittest

import sap.adt.common_types
from sap.adt import ADTObject, ADTObjectType
from sap.adt.objects import XMLNamespace
from sap.adt.annotations import XmlNodeProperty
from sap.adt.marshalling import Marshal

NAMED_ITEM_LIST_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<nameditem:namedItemList xmlns:nameditem="http://www.sap.com/adt/nameditem">
  <nameditem:totalItemCount>2</nameditem:totalItemCount>
  <nameditem:namedItem>
    <nameditem:name>I_PRODUCTTP_2</nameditem:name>
    <nameditem:description>Second interface</nameditem:description>
    <nameditem:data>some data</nameditem:data>
  </nameditem:namedItem>
  <nameditem:namedItem>
    <nameditem:name>I_PRODUCTTP_3</nameditem:name>
    <nameditem:description/>
    <nameditem:data/>
  </nameditem:namedItem>
</nameditem:namedItemList>'''

NAMED_ITEM_LIST_EMPTY_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<nameditem:namedItemList xmlns:nameditem="http://www.sap.com/adt/nameditem">
  <nameditem:totalItemCount>0</nameditem:totalItemCount>
</nameditem:namedItemList>'''


class TestNamedItemList(unittest.TestCase):

    def test_parse_named_item_list(self):
        result = sap.adt.common_types.NamedItemList.from_xml(NAMED_ITEM_LIST_XML)

        self.assertEqual(result.total_item_count, 2)
        self.assertEqual(len(result.items), 2)

        self.assertEqual(result.items[0].name, 'I_PRODUCTTP_2')
        self.assertEqual(result.items[0].description, 'Second interface')
        self.assertEqual(result.items[0].data, 'some data')

        self.assertEqual(result.items[1].name, 'I_PRODUCTTP_3')
        self.assertIsNone(result.items[1].description)
        self.assertIsNone(result.items[1].data)

    def test_parse_empty_named_item_list(self):
        result = sap.adt.common_types.NamedItemList.from_xml(NAMED_ITEM_LIST_EMPTY_XML)

        self.assertEqual(result.total_item_count, 0)
        self.assertEqual(len(result.items), 0)

    def test_named_item_list_iteration(self):
        result = sap.adt.common_types.NamedItemList.from_xml(NAMED_ITEM_LIST_XML)

        names = [item.name for item in result]
        self.assertEqual(names, ['I_PRODUCTTP_2', 'I_PRODUCTTP_3'])


class TestADTTemplateProperty(unittest.TestCase):

    def test_template_property_with_value(self):
        prop = sap.adt.common_types.ADTTemplateProperty('base_bdef', 'R_PRODUCTTP')
        self.assertEqual(prop.key, 'base_bdef')
        self.assertEqual(prop.value, 'R_PRODUCTTP')

    def test_template_property_without_value(self):
        prop = sap.adt.common_types.ADTTemplateProperty('interface_bdef')
        self.assertEqual(prop.key, 'interface_bdef')
        self.assertIsNone(prop.value)

    def test_template_property_set_value(self):
        prop = sap.adt.common_types.ADTTemplateProperty('base_bdef')
        prop.value = 'R_PRODUCTTP'
        self.assertEqual(prop.value, 'R_PRODUCTTP')


class TestADTTemplate(unittest.TestCase):

    def test_template_items(self):
        template = sap.adt.common_types.ADTTemplate([
            sap.adt.common_types.ADTTemplateProperty('base_bdef', 'R_PRODUCTTP'),
            sap.adt.common_types.ADTTemplateProperty('interface_bdef'),
        ])

        self.assertEqual(len(template.properties), 2)
        self.assertEqual(template.properties[0].key, 'base_bdef')
        self.assertEqual(template.properties[0].value, 'R_PRODUCTTP')
        self.assertEqual(template.properties[1].key, 'interface_bdef')
        self.assertIsNone(template.properties[1].value)

    def test_empty_template(self):
        template = sap.adt.common_types.ADTTemplate()
        self.assertEqual(len(template.properties), 0)


class DummyObjectWithTemplate(ADTObject):

    OBJTYPE = ADTObjectType(
        None,
        None,
        XMLNamespace('adtcore', 'http://www.sap.com/adt/core'),
        None,
        None,
        'objectTemplate'
    )

    template = XmlNodeProperty('adtcore:adtTemplate',
                               factory=sap.adt.common_types.ADTTemplate)

    def __init__(self):
        super().__init__(None, None)


TEMPLATE_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectTemplate xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:packageRef/>
<adtcore:adtTemplate>
<adtcore:adtProperty adtcore:key="base_bdef">R_PRODUCTTP</adtcore:adtProperty>
<adtcore:adtProperty adtcore:key="interface_bdef">I_PRODUCTTP</adtcore:adtProperty>
<adtcore:adtProperty adtcore:key="empty_prop"/>
</adtcore:adtTemplate>
</adtcore:objectTemplate>'''


class TestADTTemplateMarshalling(unittest.TestCase):

    def test_serialize_template_with_properties(self):
        obj = DummyObjectWithTemplate()
        obj.template = sap.adt.common_types.ADTTemplate([
            sap.adt.common_types.ADTTemplateProperty('base_bdef', 'R_PRODUCTTP'),
            sap.adt.common_types.ADTTemplateProperty('interface_bdef', 'I_PRODUCTTP'),
        ])

        act = Marshal().serialize(obj)

        self.assertEqual(act, '''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectTemplate xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:packageRef/>
<adtcore:adtTemplate>
<adtcore:adtProperty adtcore:key="base_bdef">R_PRODUCTTP</adtcore:adtProperty>
<adtcore:adtProperty adtcore:key="interface_bdef">I_PRODUCTTP</adtcore:adtProperty>
</adtcore:adtTemplate>
</adtcore:objectTemplate>''')

    def test_serialize_empty_template(self):
        obj = DummyObjectWithTemplate()
        obj.template = sap.adt.common_types.ADTTemplate()

        act = Marshal().serialize(obj)

        self.assertEqual(act, '''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectTemplate xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:packageRef/>
<adtcore:adtTemplate/>
</adtcore:objectTemplate>''')

    def test_deserialize_template_with_properties(self):
        obj = DummyObjectWithTemplate()

        Marshal.deserialize(TEMPLATE_XML, obj)

        self.assertIsNotNone(obj.template)
        self.assertEqual(len(obj.template.properties), 3)
        self.assertEqual(obj.template.properties[0].key, 'base_bdef')
        self.assertEqual(obj.template.properties[0].value, 'R_PRODUCTTP')
        self.assertEqual(obj.template.properties[1].key, 'interface_bdef')
        self.assertEqual(obj.template.properties[1].value, 'I_PRODUCTTP')
        self.assertEqual(obj.template.properties[2].key, 'empty_prop')
        self.assertEqual(obj.template.properties[2].value, '')

    def test_serialize_template_property_with_special_chars(self):
        obj = DummyObjectWithTemplate()
        obj.template = sap.adt.common_types.ADTTemplate([
            sap.adt.common_types.ADTTemplateProperty('key', 'value with <special> & "chars"'),
        ])

        act = Marshal().serialize(obj)

        self.assertIn('value with &lt;special&gt; &amp; "chars"', act)


if __name__ == '__main__':
    unittest.main()
