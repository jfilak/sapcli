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

        sap.cli.package.create(connection, SimpleNamespace(name='$TEST', description='description', super_package='$MASTER'))

        self.assertIn('<pak:superPackage adtcore:name="$MASTER"/>', connection.execs[0].body)

    def test_create_package_without_super(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        sap.cli.package.create(connection, SimpleNamespace(name='$TEST', description='description', super_package=None))

        self.assertIn('<pak:superPackage/>', connection.execs[0].body)
