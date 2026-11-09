#!/usr/bin/env python3

import unittest

import sap.cli.enho

from mock import (
    ConsoleOutputTestCase,
    Connection,
    Request,
    Response,
)

from infra import generate_parse_args
from fixtures_adt_wb import RESPONSE_ACTIVATION_OK
from fixtures_adt_enhancement_implementation import (
    ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4,
    SAPCLI_XML_ENHANCEMENT_IMPLEMENTATION_CREATE,
)


parse_args = generate_parse_args(sap.cli.enho.CommandGroup())


class TestEnhancementImplementationCommands(unittest.TestCase):

    def test_read_not_supported(self):
        with self.assertRaises(SystemExit):
            parse_args('read', 'SAPCLI_ENH_IMPL')

    def test_write_not_supported(self):
        with self.assertRaises(SystemExit):
            parse_args('write', 'SAPCLI_ENH_IMPL', '-')

    def test_create_without_enhancement_spot(self):
        with self.assertRaises(SystemExit):
            parse_args('create', 'SAPCLI_ENH_IMPL', 'SAPCLI enhancement implementation', '$TMP')


class TestEnhancementImplementationCreate(ConsoleOutputTestCase):

    def test_create(self):
        connection = Connection(user='DEVELOPER')

        args = parse_args('create', 'sapcli_enh_impl', 'SAPCLI enhancement implementation', '$tmp',
                          '--enhancement-spot', 'sapcli_enh_spot', '--corrnr', '420')
        args.execute(connection, args)

        expected_request = Request(
            adt_uri='/sap/bc/adt/enhancements/enhoxhb',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.enh.enhoxhb.v4+xml; charset=utf-8'},
            body=bytes(SAPCLI_XML_ENHANCEMENT_IMPLEMENTATION_CREATE, 'utf-8'),
            params={'corrNr': '420'}
        )

        self.maxDiff = None
        expected_request.assertEqual(connection.execs[0], self)

    def test_create_short_option(self):
        connection = Connection(user='DEVELOPER')

        args = parse_args('create', 'SAPCLI_ENH_IMPL', 'SAPCLI enhancement implementation', '$TMP',
                          '-s', 'SAPCLI_ENH_SPOT')
        args.execute(connection, args)

        self.assertIn('adtcore:name="SAPCLI_ENH_SPOT"', connection.execs[0].body.decode('utf-8'))


class TestEnhancementImplementationActivate(ConsoleOutputTestCase):

    def test_activate(self):
        connection = Connection([
            RESPONSE_ACTIVATION_OK,
            Response(text=ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4, status_code=200,
                     content_type='application/vnd.sap.adt.enh.enhoxhb.v4+xml; charset=utf-8')
        ])

        args = parse_args('activate', 'sapcli_enh_impl')
        args.console_factory = lambda: self.console
        args.execute(connection, args)

        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/activation')
        self.assertIn('adtcore:uri="/sap/bc/adt/enhancements/enhoxhb/sapcli_enh_impl"',
                      connection.execs[0].body)


if __name__ == '__main__':
    unittest.main()
