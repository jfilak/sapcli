'''Enhancement Implementation wraper tests.'''
# !/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import unittest
import unittest.mock as mock

import sap.errors
import sap.adt

from mock import Connection, Response, Request

from fixtures_adt_enhancement_implementation import (
    ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4,
)


RESPONSE_ENHANCEMENT_IMPLEMENTATION_OK = Response(
    text=ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4,
    status_code=200,
    content_type='application/vnd.sap.adt.enh.enhoxhb.v4+xml; charset=utf-8'
)


class TestEnhancementImplemenetation(unittest.TestCase):
    '''Enhancement Implementation'''

    def test_enhancement_implementation_fetch(self):
        connection = Connection([RESPONSE_ENHANCEMENT_IMPLEMENTATION_OK])

        enh_impl_name = 'SAPCLI_ENH_IMPL'

        enh_impl = sap.adt.EnhancementImplementation(connection, enh_impl_name)
        enh_impl.fetch()

        self.assertEqual(enh_impl.common.tool_type, 'BADI_IMPL')
        self.assertEqual(enh_impl.common.adjustment_status, 'adjusted')
        self.assertEqual(enh_impl.common.upgrade_flag, 'false')
        self.assertEqual(enh_impl.common.switch_supported, 'true')

        self.assertIsNotNone(enh_impl.common.usages)
        self.assertEqual(len(enh_impl.common.usages), 2)

        self.assertEqual(enh_impl.common.usages[0].program_id, 'R3TR')
        self.assertEqual(enh_impl.common.usages[0].element_usage, 'USEO')
        self.assertEqual(enh_impl.common.usages[0].upgrade, 'false')
        self.assertEqual(enh_impl.common.usages[0].automatic_transport, 'false')

        self.assertEqual(enh_impl.common.usages[0].object_reference.uri, '/sap/bc/adt/oo/classes/zcl_sapcli_badi_impl')
        self.assertEqual(enh_impl.common.usages[0].object_reference.typ, 'CLAS/OC')
        self.assertEqual(enh_impl.common.usages[0].object_reference.name, 'ZCL_SAPCLI_BADI_IMPL')

        self.assertEqual(enh_impl.common.usages[0].main_object_reference.uri, '/sap/bc/adt/oo/classes/zcl_sapcli_badi_impl')
        self.assertEqual(enh_impl.common.usages[0].main_object_reference.typ, 'CLAS/OC')
        self.assertEqual(enh_impl.common.usages[0].main_object_reference.name, 'ZCL_SAPCLI_BADI_IMPL')

        self.assertEqual(enh_impl.common.usages[1].program_id, 'R3TR')
        self.assertEqual(enh_impl.common.usages[1].element_usage, 'EXTO')
        self.assertEqual(enh_impl.common.usages[1].object_reference.name, 'SAPCLI_ENH_SPOT')
        self.assertEqual(enh_impl.common.usages[1].upgrade, 'false')
        self.assertEqual(enh_impl.common.usages[1].automatic_transport, 'false')

        self.assertEqual(enh_impl.common.usages[1].object_reference.uri, '/sap/bc/adt/enhancements/enhsxsb/sapcli_enh_spot')
        self.assertEqual(enh_impl.common.usages[1].object_reference.typ, 'ENHS/XSB')
        self.assertEqual(enh_impl.common.usages[1].object_reference.name, 'SAPCLI_ENH_SPOT')

        self.assertEqual(enh_impl.common.usages[1].main_object_reference.uri, '/sap/bc/adt/enhancements/enhsxsb/sapcli_enh_spot')
        self.assertEqual(enh_impl.common.usages[1].main_object_reference.typ, 'ENHS/XSB')
        self.assertEqual(enh_impl.common.usages[1].main_object_reference.name, 'SAPCLI_ENH_SPOT')


        self.assertEqual(len(enh_impl.specific.badis.implementations), 1)
        first_badi = next(iter(enh_impl.specific.badis.implementations))
        self.assertEqual(first_badi.name, 'SAPCLI_BADI_IMPL')
        self.assertEqual(first_badi.short_text, 'SAPCLI badi')
        self.assertEqual(first_badi.example, 'false')
        self.assertEqual(first_badi.default, 'false')
        self.assertEqual(first_badi.active, 'true')
        self.assertEqual(first_badi.customizing_lock, '')
        self.assertEqual(first_badi.runtime_behavior_shorttext, 'The implementation will be called')

        self.assertTrue(first_badi.is_active_implementation)

        self.assertTrue(first_badi.enhancement_spot.uri, '/sap/bc/adt/enhancements/enhsxsb/sapcli_enh_spot')
        self.assertTrue(first_badi.enhancement_spot.typ, 'ENHS/XSB')
        self.assertTrue(first_badi.enhancement_spot.name, 'SAPCLI_ENH_SPOT')

        self.assertTrue(first_badi.badi_definition.uri, '/sap/bc/adt/enhancements/enhsxsb/sapcli_enh_spot#type=enhs%2fxb;name=sapcli_badi_def')
        self.assertTrue(first_badi.badi_definition.typ, 'ENHS/XSB')
        self.assertTrue(first_badi.badi_definition.name, 'SAPCLI_BADI_DEF')

        self.assertTrue(first_badi.implementing_class.uri, '/sap/bc/adt/oo/classes/zcl_sapcli_badi_impl')
        self.assertTrue(first_badi.implementing_class.typ, 'CLAS/OC')
        self.assertTrue(first_badi.implementing_class.name, 'ZCL_SAPCLI_BADI_IMPL')

        first_badi_item = enh_impl.specific.badis.implementations[first_badi.name]
        self.assertEqual(first_badi, first_badi_item)

class BadiImplementationContainer(unittest.TestCase):

    def test_getitem_unknow_key(self):
        container = sap.adt.enhancement_implementation.BadiImplementationContainer()

        with self.assertRaises(KeyError) as caught:
            self.assertFalse(container['FOO'])

        self.assertEqual(str(caught.exception), "'FOO'")

class TestBadiImplementation(unittest.TestCase):

    def setUp(self):
        self.badi_impl = sap.adt.enhancement_implementation.BadiImplementation()

    def test_badi_implementation_default_error(self):
        self.assertIsNone(self.badi_impl.active)

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            self.assertFalse(self.badi_impl.is_active_implementation)

        self.assertEqual(str(caught.exception), 'BadiImplementation() holds invalid active: ""')

    def test_badi_implementation_bogus_error(self):
        self.assertIsNone(self.badi_impl.active)
        self.badi_impl.name = 'MyBAdI'
        self.badi_impl.active = 'foobar'

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            self.assertFalse(self.badi_impl.is_active_implementation)

        self.assertEqual(str(caught.exception), 'BadiImplementation(MyBAdI) holds invalid active: "foobar"')

    def test_badi_implementation_default_to_inactive(self):
        self.assertIsNone(self.badi_impl.active)

        self.badi_impl.is_active_implementation = False
        self.assertFalse(self.badi_impl.is_active_implementation)
        self.assertEqual(self.badi_impl.active, 'false')

    def test_badi_implementation_default_to_active(self):
        self.assertIsNone(self.badi_impl.active)

        self.badi_impl.is_active_implementation = True
        self.assertTrue(self.badi_impl.is_active_implementation)
        self.assertEqual(self.badi_impl.active, 'true')

    def test_badi_implementation_inactive_to_active(self):
        self.badi_impl.active = 'false'
        self.assertFalse(self.badi_impl.is_active_implementation)

        self.badi_impl.is_active_implementation = True
        self.assertTrue(self.badi_impl.is_active_implementation)
        self.assertEqual(self.badi_impl.active, 'true')

    def test_badi_implementation_active_to_inactive(self):
        self.badi_impl.active = 'true'
        self.assertTrue(self.badi_impl.is_active_implementation)

        self.badi_impl.is_active_implementation = False
        self.assertFalse(self.badi_impl.is_active_implementation)
        self.assertEqual(self.badi_impl.active, 'false')

    def test_badi_implementation_inactive_to_inactive(self):
        self.badi_impl.active = 'false'
        self.assertFalse(self.badi_impl.is_active_implementation)

        self.badi_impl.is_active_implementation = False
        self.assertFalse(self.badi_impl.is_active_implementation)
        self.assertEqual(self.badi_impl.active, 'false')

    def test_badi_implementation_active_to_active(self):
        self.badi_impl.active = 'true'
        self.assertTrue(self.badi_impl.is_active_implementation)

        self.badi_impl.is_active_implementation = True
        self.assertTrue(self.badi_impl.is_active_implementation)
        self.assertEqual(self.badi_impl.active, 'true')
