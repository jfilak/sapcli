#!/usr/bin/env python3

import unittest
from types import SimpleNamespace

import sap.adt

from mock import ConnectionViaHTTP as Connection

from fixtures_adt_repository import (PACKAGE_ROOT_NODESTRUCTURE_OK_RESPONSE,
                                     PACKAGE_ROOT_REQUEST_XML,
                                     PACKAGE_SOURCE_LIBRARY_NODESTRUCUTRE_OK_RESPONSE,
                                     PACKAGE_SOURCE_LIBRARY_REQUEST_XML)


class TestRepository(unittest.TestCase):

    def read_package_node(self, responses, nodekeys):
        connection = Connection(responses)

        mypkg = sap.adt.Package(connection, '$VICTORY')

        repository = sap.adt.Repository(connection)

        if nodekeys is None:
            node = repository.read_node(mypkg)
        else:
            node = repository.read_node(mypkg, nodekeys=nodekeys)

        self.assertEqual(connection.mock_methods(), [('POST', '/sap/bc/adt/repository/nodestructure')])

        self.assertEqual(connection.execs[0].headers,
            {'Accept': 'application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.RepositoryObjectTreeContent',
             'Content-Type': 'application/vnd.sap.as+xml; charset=UTF-8; dataname=null'})

        self.assertEqual(connection.execs[0].params,
            {'parent_name': '$VICTORY',
             'parent_tech_name': '$VICTORY',
             'parent_type': 'DEVC/K',
             'withShortDescriptions': 'false'})

        return (node, connection)

    def test_read_node(self):
        node, connection = self.read_package_node([PACKAGE_ROOT_NODESTRUCTURE_OK_RESPONSE], None)

        self.assertEqual(connection.execs[0].body, PACKAGE_ROOT_REQUEST_XML)

        self.assertEqual([vars(obj) for obj in node.objects],
                         [vars(SimpleNamespace(
                              DESCRIPTION='Package with Tests',
                              DESCRIPTION_TYPE='',
                              EXPANDABLE='X',
                              IS_ABSTRACT='',
                              IS_CONSTANT='',
                              IS_CONSTRUCTOR='',
                              IS_EVENT_HANDLER='',
                              IS_FINAL='',
                              IS_FOR_TESTING='',
                              IS_READ_ONLY='',
                              IS_REDEFINITION='',
                              IS_STATIC='',
                              NODE_ID='',
                              OBJECT_NAME='$VICTORY_TESTS',
                              OBJECT_TYPE='DEVC/K',
                              OBJECT_URI='/sap/bc/adt/packages/%24victory_tests',
                              OBJECT_VIT_URI='/sap/bc/adt/vit/wb/object_type/devck/object_name/%24VICTORY_TESTS',
                              PARENT_NAME='',
                              TECH_NAME='$VICTORY_TESTS',
                              VISIBILITY='0'
                              ))])

        self.assertEqual(node.categories,
                         [SimpleNamespace(CATEGORY='packages', CATEGORY_LABEL='Package'),
                          SimpleNamespace(CATEGORY='source_library', CATEGORY_LABEL='Source Code Library')])

        self.assertEqual(node.types,
                         [SimpleNamespace(OBJECT_TYPE='CLAS/OC', CATEGORY_TAG='source_library', OBJECT_TYPE_LABEL='Classes', NODE_ID='000005'),
                          SimpleNamespace(OBJECT_TYPE='DEVC/K', CATEGORY_TAG='packages', OBJECT_TYPE_LABEL='Subpackages', NODE_ID='000007'),
                          SimpleNamespace(OBJECT_TYPE='INTF/OI', CATEGORY_TAG='source_library', OBJECT_TYPE_LABEL='Interfaces', NODE_ID='000011'),
                          SimpleNamespace(OBJECT_TYPE='PROG/P', CATEGORY_TAG='source_library', OBJECT_TYPE_LABEL='Programs', NODE_ID='000002')])

    def test_read_node(self):
        node, connection = self.read_package_node([PACKAGE_SOURCE_LIBRARY_NODESTRUCUTRE_OK_RESPONSE], ('000005', '000011', '000002'))

        self.assertEqual(connection.execs[0].body, PACKAGE_SOURCE_LIBRARY_REQUEST_XML)

        self.assertEqual([vars(obj) for obj in node.objects],
                         [vars(SimpleNamespace(
                              OBJECT_TYPE='CLAS/OC',
                              OBJECT_NAME='ZCL_HELLO_WORLD',
                              TECH_NAME='==============================CP',
                              OBJECT_URI='/sap/bc/adt/oo/classes/zcl_hello_world',
                              OBJECT_VIT_URI='/sap/bc/adt/vit/wb/object_type/clasoc/object_name/ZCL_HELLO_WORLD',
                              EXPANDABLE='X',
                              IS_FINAL='',
                              IS_ABSTRACT='',
                              IS_FOR_TESTING='',
                              IS_EVENT_HANDLER='',
                              IS_CONSTRUCTOR='',
                              IS_REDEFINITION='',
                              IS_STATIC='',
                              IS_READ_ONLY='',
                              IS_CONSTANT='',
                              VISIBILITY='0',
                              NODE_ID='',
                              PARENT_NAME='',
                              DESCRIPTION='Test class',
                              DESCRIPTION_TYPE='OC',
                              )),
                          vars(SimpleNamespace(
                              OBJECT_TYPE='INTF/OI',
                              OBJECT_NAME='ZIF_HELLO_WORLD',
                              TECH_NAME='ZIF_HELLO_WORLD',
                              OBJECT_URI='/sap/bc/adt/oo/interfaces/zif_hello_world',
                              OBJECT_VIT_URI='/sap/bc/adt/vit/wb/object_type/intfoi/object_name/ZIF_HELLO_WORLD',
                              EXPANDABLE='',
                              IS_FINAL='',
                              IS_ABSTRACT='',
                              IS_FOR_TESTING='',
                              IS_EVENT_HANDLER='',
                              IS_CONSTRUCTOR='',
                              IS_REDEFINITION='',
                              IS_STATIC='',
                              IS_READ_ONLY='',
                              IS_CONSTANT='',
                              VISIBILITY='0',
                              NODE_ID='',
                              PARENT_NAME='',
                              DESCRIPTION='Test interface',
                              DESCRIPTION_TYPE='OI',
                              )),
                          vars(SimpleNamespace(
                              OBJECT_TYPE='PROG/P',
                              OBJECT_NAME='Z_HELLO_WORLD',
                              TECH_NAME='Z_HELLO_WORLD',
                              OBJECT_URI='/sap/bc/adt/programs/programs/z_hello_world',
                              OBJECT_VIT_URI='/sap/bc/adt/vit/wb/object_type/progp/object_name/Z_HELLO_WORLD',
                              EXPANDABLE='X',
                              IS_FINAL='',
                              IS_ABSTRACT='',
                              IS_FOR_TESTING='',
                              IS_EVENT_HANDLER='',
                              IS_CONSTRUCTOR='',
                              IS_REDEFINITION='',
                              IS_STATIC='',
                              IS_READ_ONLY='',
                              IS_CONSTANT='',
                              VISIBILITY='0',
                              NODE_ID='',
                              PARENT_NAME='',
                              DESCRIPTION='Test program',
                              DESCRIPTION_TYPE='P',
                              ))
                         ])


if __name__ == '__main__':
    unittest.main()
