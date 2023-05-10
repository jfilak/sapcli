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

        self.assertIsNotNone(enh_impl.common.usages)
        self.assertEqual(len(enh_impl.common.usages), 2)

        self.assertEqual(enh_impl.common.usages[0].program_id, 'R3TR')
        self.assertEqual(enh_impl.common.usages[0].object_reference.name, 'ZCL_SAPCLI_BADI_IMPL')

        self.assertEqual(enh_impl.common.usages[1].element_usage, 'EXTO')
        self.assertEqual(enh_impl.common.usages[1].object_reference.name, 'SAPCLI_ENH_SPOT')

        self.assertEqual(len(enh_impl.specific.badis.implementations), 1)
        first_badi = next(iter(enh_impl.specific.badis.implementations))
        self.assertEqual(first_badi.name, 'SAPCLI_BADI_IMPL')

        self.assertTrue(first_badi.is_active_implementation)

        self.assertTrue(first_badi.enhancement_spot.name, 'SAPCLI_ENH_SPOT')
        self.assertTrue(first_badi.badi_definition.name, 'SAPCLI_BADI_DEF')
        self.assertTrue(first_badi.implementing_class.name, 'ZCL_SAPCLI_BADI_IMPL')
