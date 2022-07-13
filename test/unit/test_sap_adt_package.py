#!/bin/python

import unittest
from types import SimpleNamespace

from sap import get_logger
import sap.errors
import sap.adt

from mock import ConnectionViaHTTP as Connection, Response

from fixtures_adt_package import GET_PACKAGE_ADT_XML
from fixtures_adt_repository import (PACKAGE_ROOT_NODESTRUCTURE_OK_RESPONSE,
                                     PACKAGE_ROOT_REQUEST_XML,
                                     PACKAGE_SOURCE_LIBRARY_NODESTRUCUTRE_OK_RESPONSE,
                                     PACKAGE_SOURCE_LIBRARY_REQUEST_XML,
                                     PACKAGE_EMPTY_NODESTRUCTURE_OK_RESPONSE,
                                     PACKAGE_ENVELOPE_NODESTRUCTURE_OK_RESPONSE,
                                     PACKAGE_WITHOUT_SUBPKG_NODESTRUCTURE_OK_RESPONSE)


FIXTURE_PACKAGE_XML="""<?xml version="1.0" encoding="UTF-8"?>
<pak:package xmlns:pak="http://www.sap.com/adt/packages" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DEVC/K" adtcore:description="description" adtcore:language="EN" adtcore:name="$TEST" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:responsible="FILAK" adtcore:version="active">
<adtcore:packageRef adtcore:name="$TEST"/>
<pak:attributes pak:packageType="development"/>
<pak:superPackage adtcore:name="$MASTER"/>
<pak:applicationComponent pak:name="PPM"/>
<pak:transport>
<pak:softwareComponent pak:name="LOCAL"/>
<pak:transportLayer pak:name="HOME"/>
</pak:transport>
<pak:translation/>
<pak:useAccesses/>
<pak:packageInterfaces/>
<pak:subPackages/>
</pak:package>"""

class TestADTPackage(unittest.TestCase):

    def test_init(self):
        conn = Connection(collections={'/sap/bc/adt/packages': ['application/vnd.sap.adt.packages.v1+xml']})

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', master_system='NPL', responsible='FILAK')
        package = sap.adt.Package(conn, '$TEST', metadata=metadata)
        package.description = 'description'
        package.set_package_type('development')
        package.set_software_component('LOCAL')
        package.set_transport_layer('HOME')
        package.set_app_component('PPM')
        package.super_package.name = '$MASTER'
        package.create()

        self.assertEqual(len(conn.execs), 1)

        self.assertEqual(conn.execs[0][0], 'POST')
        self.assertEqual(conn.execs[0][1], '/sap/bc/adt/packages')
        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.adt.packages.v1+xml; charset=utf-8'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3].decode('utf-8'), FIXTURE_PACKAGE_XML)

    def test_package_serialization_v2(self):
        conn = Connection()

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', master_system='NPL', responsible='FILAK')
        package = sap.adt.Package(conn, '$TEST', metadata=metadata)
        package.description = 'description'
        package.set_package_type('development')
        package.set_software_component('LOCAL')
        package.set_transport_layer('HOME')
        package.set_app_component('PPM')
        package.super_package.name = '$MASTER'
        package.create()

        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.adt.packages.v2+xml; charset=utf-8'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3].decode('utf-8'), FIXTURE_PACKAGE_XML)

    def test_adt_package_fetch(self):
        conn = Connection([Response(text=GET_PACKAGE_ADT_XML,
                                    status_code=200,
                                    headers={'Content-Type': 'application/vnd.sap.adt.packages.v1+xml; charset=utf-8'})])

        package = sap.adt.Package(conn, '$IAMTHEKING')
        package.fetch()

        self.assertEqual(len(conn.execs), 1)

        self.assertEqual(conn.mock_methods(), [('GET', '/sap/bc/adt/packages/%24iamtheking')])

        self.maxDiff = None
        self.assertEqual(package.description, 'This is a package')


class TestADTPackageWalk(unittest.TestCase):

    def test_with_empty_subpackage(self):
        connection = Connection([PACKAGE_ROOT_NODESTRUCTURE_OK_RESPONSE,
                                 PACKAGE_SOURCE_LIBRARY_NODESTRUCUTRE_OK_RESPONSE,
                                 PACKAGE_EMPTY_NODESTRUCTURE_OK_RESPONSE])

        walk_iter = sap.adt.package.walk(sap.adt.Package(connection, '$VICTORY'))

        root_path, subpackages, objects = next(walk_iter)

        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/repository/nodestructure')
        self.assertEqual(connection.execs[0].params['parent_name'], '$VICTORY')
        self.assertEqual(connection.execs[0].body, PACKAGE_ROOT_REQUEST_XML)

        self.assertEqual(connection.execs[1].adt_uri, '/sap/bc/adt/repository/nodestructure')
        self.assertEqual(connection.execs[1].params['parent_name'], '$VICTORY')
        self.assertEqual(connection.execs[1].body, PACKAGE_SOURCE_LIBRARY_REQUEST_XML)

        self.assertEqual(root_path, [])
        self.assertEqual(subpackages, ['$VICTORY_TESTS'])
        self.assertEqual(objects,
                        [SimpleNamespace(typ='CLAS/OC', name='ZCL_HELLO_WORLD', uri='/sap/bc/adt/oo/classes/zcl_hello_world'),
                         SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD', uri='/sap/bc/adt/oo/interfaces/zif_hello_world'),
                         SimpleNamespace(typ='PROG/P', name='Z_HELLO_WORLD', uri='/sap/bc/adt/programs/programs/z_hello_world')])

        root_path, subpackages, objects = next(walk_iter)

        self.assertEqual(connection.execs[2].adt_uri, '/sap/bc/adt/repository/nodestructure')
        self.assertEqual(connection.execs[2].params['parent_name'], '$VICTORY_TESTS')
        self.assertEqual(connection.execs[2].body, PACKAGE_ROOT_REQUEST_XML)

        self.assertEqual(len(connection.execs), 3)

        self.assertEqual(root_path, ['$VICTORY_TESTS'])
        self.assertEqual(subpackages, [])
        self.assertEqual(objects, [])

    def test_with_envelope_root(self):
        connection = Connection([PACKAGE_ENVELOPE_NODESTRUCTURE_OK_RESPONSE,
                                 PACKAGE_WITHOUT_SUBPKG_NODESTRUCTURE_OK_RESPONSE,
                                 PACKAGE_SOURCE_LIBRARY_NODESTRUCUTRE_OK_RESPONSE])

        walk_iter = sap.adt.package.walk(sap.adt.Package(connection, '$VICTORY'))

        root_path, subpackages, objects = next(walk_iter)

        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/repository/nodestructure')
        self.assertEqual(connection.execs[0].params['parent_name'], '$VICTORY')
        self.assertEqual(connection.execs[0].body, PACKAGE_ROOT_REQUEST_XML)

        self.assertEqual(root_path, [])
        self.assertEqual(subpackages, ['$VICTORY_TESTS'])
        self.assertEqual(objects, [])

        self.assertEqual(len(connection.execs), 1)

        root_path, subpackages, objects = next(walk_iter)

        self.assertEqual(connection.execs[1].adt_uri, '/sap/bc/adt/repository/nodestructure')
        self.assertEqual(connection.execs[1].params['parent_name'], '$VICTORY_TESTS')
        self.assertEqual(connection.execs[1].body, PACKAGE_ROOT_REQUEST_XML)

        self.assertEqual(connection.execs[2].adt_uri, '/sap/bc/adt/repository/nodestructure')
        self.assertEqual(connection.execs[2].params['parent_name'], '$VICTORY_TESTS')
        self.assertEqual(connection.execs[2].body, PACKAGE_SOURCE_LIBRARY_REQUEST_XML)

        self.assertEqual(len(connection.execs), 3)

        self.assertEqual(root_path, ['$VICTORY_TESTS'])
        self.assertEqual(subpackages, [])
        self.assertEqual(objects,
                        [SimpleNamespace(typ='CLAS/OC', name='ZCL_HELLO_WORLD', uri='/sap/bc/adt/oo/classes/zcl_hello_world'),
                         SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD', uri='/sap/bc/adt/oo/interfaces/zif_hello_world'),
                         SimpleNamespace(typ='PROG/P', name='Z_HELLO_WORLD', uri='/sap/bc/adt/programs/programs/z_hello_world')])


if __name__ == '__main__':
    unittest.main()
