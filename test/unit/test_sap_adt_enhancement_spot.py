'''Enhancement Spot wrapper tests.'''
# !/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import unittest

import sap.adt

from mock import Connection, Response

from fixtures_adt import (
    LOCK_RESPONSE_OK,
    EMPTY_RESPONSE_OK,
)

from fixtures_sap_adt_enhancement_spot import (
    ENHANCEMENT_SPOT_NAME,
    FIXTURE_ADT_ENHANCEMENT_SPOT,
    FIXTURE_SAPCLI_ADT_ENHANCEMENT_SPOT,
    FIXTURE_ADT_ENHS_REPOSITORY_ROOT,
    FIXTURE_ADT_ENHS_REPOSITORY_BADI_DEFINITIONS,
    FIXTURE_ADT_ENHS_REPOSITORY_EHNO,
)


RESPONSE_ENHANCEMENT_SPOT_OK = Response(
    text=FIXTURE_ADT_ENHANCEMENT_SPOT,
    status_code=200,
    content_type='application/vnd.sap.adt.enh.enhs.v2+xml; charset=utf-8'
)


def repository_response(text):
    """Builds a response of the repository node structure request"""

    return Response(text=text, status_code=200, headers={})


class TestEnhancementSpotFetch(unittest.TestCase):
    '''Deserialization of the ADT XML'''

    def setUp(self):
        self.connection = Connection([RESPONSE_ENHANCEMENT_SPOT_OK])

        self.enhancement_spot = sap.adt.EnhancementSpot(self.connection, ENHANCEMENT_SPOT_NAME)
        self.enhancement_spot.fetch()

    def test_enhancement_spot_fetch_request(self):
        get_request = self.connection.execs[0]

        self.assertEqual(get_request.method, 'GET')
        self.assertEqual(get_request.adt_uri, '/sap/bc/adt/enhancements/enhsxsb/ssample_enhs')

    def test_enhancement_spot_fetch_coredata(self):
        self.assertEqual(self.enhancement_spot.name, 'SSAMPLE_ENHS')
        self.assertEqual(self.enhancement_spot.description, 'Lovely Enhancement spot')
        self.assertEqual(self.enhancement_spot.language, 'EN')
        self.assertEqual(self.enhancement_spot.master_language, 'EN')
        self.assertEqual(self.enhancement_spot.master_system, 'A4H')
        self.assertEqual(self.enhancement_spot.responsible, 'DEVELOPER')
        self.assertEqual(self.enhancement_spot.coredata.package_reference.name, 'MY_ES')

    def test_enhancement_spot_fetch_content_common(self):
        common = self.enhancement_spot.common

        self.assertEqual(common.tool_type, 'BADI_DEF')
        self.assertEqual(common.internal, 'false')
        self.assertEqual(common.internal_flag_editable, 'true')

    def test_enhancement_spot_fetch_usages(self):
        usages = self.enhancement_spot.common.usages

        self.assertIsNotNone(usages)
        self.assertEqual(len(usages), 1)

        self.assertEqual(usages[0].program_id, 'R3TR')
        self.assertEqual(usages[0].element_usage, 'USEO')
        self.assertEqual(usages[0].upgrade, 'false')
        self.assertEqual(usages[0].automatic_transport, 'false')

        self.assertEqual(usages[0].object_reference.uri, '/sap/bc/adt/oo/interfaces/if_example_badi')
        self.assertEqual(usages[0].object_reference.typ, 'INTF/OI')
        self.assertEqual(usages[0].object_reference.name, 'IF_SAMPLE_ENHS')

        self.assertEqual(usages[0].main_object_reference.uri, '/sap/bc/adt/oo/interfaces/if_example_badi')
        self.assertEqual(usages[0].main_object_reference.typ, 'INTF/OI')
        self.assertEqual(usages[0].main_object_reference.name, 'IF_SAMPLE_ENHS')

    def test_enhancement_spot_fetch_badi_definitions(self):
        definitions = self.enhancement_spot.specific.badis.definitions

        self.assertEqual(len(definitions), 1)

        first_badi = definitions[0]
        self.assertEqual(first_badi.name, 'SAMPLE_ENHS')
        self.assertEqual(first_badi.short_text, 'BAdI for awesome')
        self.assertEqual(first_badi.single_use, 'false')
        self.assertEqual(first_badi.use_fallback_class, 'false')
        self.assertEqual(first_badi.filter_limitation, 'false')
        self.assertEqual(first_badi.documentation_id, 'SAMPLE_ENHS')
        self.assertEqual(first_badi.context_mode, 'N')
        self.assertEqual(first_badi.amdp, 'false')
        self.assertEqual(first_badi.internal_use, 'true')
        self.assertEqual(first_badi.custom_logic_registered, 'false')

        self.assertEqual(first_badi.interface.uri, '/sap/bc/adt/oo/interfaces/if_example_badi')
        self.assertEqual(first_badi.interface.typ, 'INTF/OI')
        self.assertEqual(first_badi.interface.name, 'IF_SAMPLE_ENHS')


class TestEnhancementSpotSerialize(unittest.TestCase):
    '''Serialization to the ADT XML'''

    def test_enhancement_spot_write(self):
        connection = Connection([RESPONSE_ENHANCEMENT_SPOT_OK, LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        enhancement_spot = sap.adt.EnhancementSpot(connection, ENHANCEMENT_SPOT_NAME)
        enhancement_spot.fetch()

        enhancement_spot.common.internal = 'true'

        with enhancement_spot.open_editor() as editor:
            editor.push()

        put_request = connection.execs[2]

        self.assertEqual(put_request.method, 'PUT')
        self.assertEqual(put_request.adt_uri, '/sap/bc/adt/enhancements/enhsxsb/ssample_enhs')

        self.assertEqual(sorted(put_request.headers), ['Content-Type'])
        self.assertEqual(put_request.headers['Content-Type'],
                         'application/vnd.sap.adt.enh.enhs.v2+xml; charset=utf-8')

        self.assertEqual(put_request.params, {'lockHandle': 'win'})

        self.maxDiff = None
        self.assertEqual(put_request.body.decode('utf-8'), FIXTURE_SAPCLI_ADT_ENHANCEMENT_SPOT)


class TestEnhancementSpotGetImplementations(unittest.TestCase):
    '''Listing of Enhancement Implementations of the Enhancement Spot'''

    def test_get_implementations(self):
        connection = Connection([
            repository_response(FIXTURE_ADT_ENHS_REPOSITORY_ROOT),
            repository_response(FIXTURE_ADT_ENHS_REPOSITORY_EHNO),
        ])

        enhancement_spot = sap.adt.EnhancementSpot(connection, ENHANCEMENT_SPOT_NAME)
        implementations = enhancement_spot.get_implementations()

        self.assertEqual(implementations, ['MY_FABULOUS_ENHS_ONE', 'OPEN_SOURCE_IS_BEST'])

    def test_get_implementations_requests(self):
        connection = Connection([
            repository_response(FIXTURE_ADT_ENHS_REPOSITORY_ROOT),
            repository_response(FIXTURE_ADT_ENHS_REPOSITORY_EHNO),
        ])

        enhancement_spot = sap.adt.EnhancementSpot(connection, ENHANCEMENT_SPOT_NAME)
        enhancement_spot.get_implementations()

        self.assertEqual(connection.mock_methods(), [
            ('POST', '/sap/bc/adt/repository/nodestructure'),
            ('POST', '/sap/bc/adt/repository/nodestructure'),
        ])

        root_request = connection.execs[0]
        self.assertEqual(root_request.params['parent_name'], ENHANCEMENT_SPOT_NAME)
        self.assertEqual(root_request.params['parent_type'], 'ENHS/XSB')
        self.assertIn('<TV_NODEKEY>000000</TV_NODEKEY>', root_request.body)

        # 000004 is the NODE_ID of ENHO/XHB in the root node response
        self.assertIn('<TV_NODEKEY>000004</TV_NODEKEY>', connection.execs[1].body)

    def test_get_implementations_without_enhancement_implementations(self):
        connection = Connection([
            repository_response(FIXTURE_ADT_ENHS_REPOSITORY_BADI_DEFINITIONS),
        ])

        enhancement_spot = sap.adt.EnhancementSpot(connection, ENHANCEMENT_SPOT_NAME)
        implementations = enhancement_spot.get_implementations()

        self.assertEqual(implementations, [])
        self.assertEqual(len(connection.execs), 1)


if __name__ == '__main__':
    unittest.main()
