'''Enhancement Spot CLI tests.'''
# !/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import unittest

import sap.cli.enhs

from mock import (
    BufferConsole,
    Connection,
    Response,
)

from infra import generate_parse_args

from fixtures_sap_adt_enhancement_spot import (
    ENHANCEMENT_SPOT_NAME,
    FIXTURE_ADT_ENHS_REPOSITORY_ROOT,
    FIXTURE_ADT_ENHS_REPOSITORY_BADI_DEFINITIONS,
    FIXTURE_ADT_ENHS_REPOSITORY_EHNO,
)


parse_args = generate_parse_args(sap.cli.enhs.CommandGroup())


def repository_response(text):
    """Builds a response of the repository node structure request"""

    return Response(text=text, status_code=200, headers={})


class TestEnhancementSpotListImplementations(unittest.TestCase):

    def list_implementations_cmd(self, *args, **kwargs):
        return parse_args('list-implementations', *args, **kwargs)

    def execute(self, connection, *args):
        console = BufferConsole()
        the_cmd = self.list_implementations_cmd(*args)
        the_cmd.console_factory = lambda: console
        the_cmd.execute(connection, the_cmd)

        return console

    def test_list_implementations(self):
        connection = Connection([
            repository_response(FIXTURE_ADT_ENHS_REPOSITORY_ROOT),
            repository_response(FIXTURE_ADT_ENHS_REPOSITORY_EHNO),
        ])

        console = self.execute(connection, ENHANCEMENT_SPOT_NAME)

        self.assertEqual(console.capout, 'MY_FABULOUS_ENHS_ONE\nOPEN_SOURCE_IS_BEST\n')
        self.assertEqual(console.caperr, '')

    def test_list_implementations_requests(self):
        connection = Connection([
            repository_response(FIXTURE_ADT_ENHS_REPOSITORY_ROOT),
            repository_response(FIXTURE_ADT_ENHS_REPOSITORY_EHNO),
        ])

        self.execute(connection, ENHANCEMENT_SPOT_NAME)

        self.assertEqual(connection.mock_methods(), [
            ('POST', '/sap/bc/adt/repository/nodestructure'),
            ('POST', '/sap/bc/adt/repository/nodestructure'),
        ])

        self.assertEqual(connection.execs[0].params['parent_name'], ENHANCEMENT_SPOT_NAME)
        self.assertEqual(connection.execs[0].params['parent_type'], 'ENHS/XSB')

    def test_list_implementations_none(self):
        connection = Connection([
            repository_response(FIXTURE_ADT_ENHS_REPOSITORY_BADI_DEFINITIONS),
        ])

        console = self.execute(connection, ENHANCEMENT_SPOT_NAME)

        self.assertEqual(console.capout, '')
        self.assertEqual(console.caperr, '')


if __name__ == '__main__':
    unittest.main()
