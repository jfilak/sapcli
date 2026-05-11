#!/bin/python

import unittest

import sap.adt.common_types

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


if __name__ == '__main__':
    unittest.main()
