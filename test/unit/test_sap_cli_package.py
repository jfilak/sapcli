#!/usr/bin/env python3

import unittest
from unittest.mock import patch
from types import SimpleNamespace

from sap.errors import SAPCliError
import sap.cli.package

from mock import Connection, Response
from fixtures_adt import EMPTY_RESPONSE_OK


class TestPackageCreate(unittest.TestCase):

    def test_create_package_with_super(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        sap.cli.package.create(connection, SimpleNamespace(name='$TEST', description='description',
                                                           super_package='$MASTER', software_component='LOCAL',
                                                           app_component=None, transport_layer=None))

        self.assertIn('<pak:superPackage adtcore:name="$MASTER"/>', connection.execs[0].body)

    def test_create_package_without_super(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        sap.cli.package.create(connection, SimpleNamespace(name='$TEST', description='description',
                                                           super_package=None, software_component='LOCAL',
                                                           app_component=None, transport_layer=None))

        self.assertIn('<pak:superPackage/>', connection.execs[0].body)

    def test_create_package_with_app_component(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        sap.cli.package.create(connection, SimpleNamespace(name='$TEST', description='description',
                                                           super_package=None, software_component='LOCAL',
                                                           app_component='LOD', transport_layer=None))

        self.assertIn('<pak:applicationComponent pak:name="LOD"/>', connection.execs[0].body)

    def test_create_package_with_sw_component(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        sap.cli.package.create(connection, SimpleNamespace(name='$TEST', description='description',
                                                           super_package=None, software_component='SAP',
                                                           app_component=None, transport_layer=None))

        self.assertIn('<pak:softwareComponent pak:name="SAP"/>', connection.execs[0].body)

    def test_create_package_with_transport_layer(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        sap.cli.package.create(connection, SimpleNamespace(name='$TEST', description='description',
                                                           super_package=None, software_component='LOCAL',
                                                           app_component=None, transport_layer='SAP'))

        self.assertIn('<pak:transportLayer pak:name="SAP"/>', connection.execs[0].body)
