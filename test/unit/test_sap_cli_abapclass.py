#!/bin/python

from argparse import ArgumentParser
import unittest

import sap.cli.abapclass

from mock import Connection
from fixtures_adt import EMPTY_RESPONSE_OK


FIXTURE_ELEMENTARY_CLASS_XML="""<?xml version="1.0" encoding="UTF-8"?>
<class:abapClass xmlns:class="http://www.sap.com/adt/oo/classes" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="CLAS/OC" adtcore:description="Class Description" adtcore:language="EN" adtcore:name="ZCL_HELLO_WORLD" adtcore:masterLanguage="EN" adtcore:responsible="ANZEIGER" class:final="true" class:visibility="public">
<adtcore:packageRef adtcore:name="$THE_PACKAGE"/>
<class:include adtcore:name="CLAS/OC" adtcore:type="CLAS/OC" class:includeType="testclasses"/>
<class:superClassRef/>
</class:abapClass>"""


def parse_args(argv):
    parser = ArgumentParser()
    sap.cli.abapclass.CommandGroup().install_parser(parser)
    return parser.parse_args(argv)


class TestCommandGroup(unittest.TestCase):

    def test_constructor(self):
        sap.cli.abapclass.CommandGroup()


class TestClassCreate(unittest.TestCase):

    def test_class_create_defaults(self):
        connection = Connection([EMPTY_RESPONSE_OK])
        args = parse_args(['create', 'ZCL_HELLO_WORLD', 'Class Description', '$THE_PACKAGE'])
        args.execute(connection, args)

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs], [('POST', '/sap/bc/adt/oo/classes')])

        create_request = connection.execs[0]
        self.assertEqual(create_request.body, FIXTURE_ELEMENTARY_CLASS_XML)

        self.assertIsNone(create_request.params)

        self.assertEqual(sorted(create_request.headers.keys()), ['Content-Type'])
        self.assertEqual(create_request.headers['Content-Type'], 'application/vnd.sap.adt.oo.classes.v2+xml')


if __name__ == '__main__':
    unittest.main()
