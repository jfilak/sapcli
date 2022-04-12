#!/usr/bin/env python3

import unittest
from unittest.mock import patch, Mock, call

from argparse import ArgumentParser

import sap.cli.datapreview

from mock import ConnectionViaHTTP as Connection, Response
from fixtures_adt_datapreview import ADT_XML_FREESTYLE_TABLE_T000_ONE_ROW


parser = ArgumentParser()
sap.cli.datapreview.CommandGroup().install_parser(parser)


def parse_args(*argv):
    global parser
    return parser.parse_args(argv)


class TestDataPreviewOSQL(unittest.TestCase):

    def test_print_human(self):
        connection = Connection([Response(text=ADT_XML_FREESTYLE_TABLE_T000_ONE_ROW,
                                          status_code=200,
                                          content_type='application/vnd.sap.adt.datapreview.table.v1+xml; charset=utf-8')])

        args = parse_args('osql', 'select * from t000', '--rows', '1')
        with patch('sap.cli.datapreview.printout', Mock()) as fake_printout:
            args.execute(connection, args)

        self.assertEqual(fake_printout.call_args_list, [call('MANDT'), call('000')])

    def test_print_human_without_headings(self):
        connection = Connection([Response(text=ADT_XML_FREESTYLE_TABLE_T000_ONE_ROW,
                                          status_code=200,
                                          content_type='application/vnd.sap.adt.datapreview.table.v1+xml; charset=utf-8')])

        args = parse_args('osql', 'select * from t000', '-n', '--rows', '1')
        with patch('sap.cli.datapreview.printout', Mock()) as fake_printout:
            args.execute(connection, args)

        self.assertEqual(fake_printout.call_args_list, [call('000')])

    def test_print_json(self):
        connection = Connection([Response(text=ADT_XML_FREESTYLE_TABLE_T000_ONE_ROW,
                                          status_code=200,
                                          content_type='application/vnd.sap.adt.datapreview.table.v1+xml; charset=utf-8')])

        args = parse_args('osql', 'select * from t000', '-o', 'json', '--rows', '1')
        with patch('sap.cli.datapreview.printout', Mock()) as fake_printout:
            args.execute(connection, args)

        self.assertEqual(fake_printout.call_args_list, [call('''[
  {
    "MANDT": "000"
  }
]''')])
