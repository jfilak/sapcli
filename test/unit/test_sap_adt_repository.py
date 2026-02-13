#!/usr/bin/env python3

import unittest
from types import SimpleNamespace

import sap.adt

from mock import Connection, PatcherTestCase
from fixtures_adt_repository import (PACKAGE_ROOT_NODESTRUCTURE_OK_RESPONSE,
                                     PACKAGE_ROOT_REQUEST_XML,
                                     PACKAGE_SOURCE_LIBRARY_NODESTRUCUTRE_OK_RESPONSE,
                                     PACKAGE_SOURCE_LIBRARY_REQUEST_XML)


class TestRepository(unittest.TestCase, PatcherTestCase):

    @staticmethod
    def get_ordered_set(items):
        return dict.fromkeys(items)  # as of Python 3.7, dict keeps insertion order

    def setUp(self) -> None:
        super().setUp()
        self.patch('sap.adt.repository.set', new=lambda items: self.get_ordered_set(items))

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

    def test_read_node_not_unique_nodekeys(self):
        node, connection = self.read_package_node([PACKAGE_SOURCE_LIBRARY_NODESTRUCUTRE_OK_RESPONSE],
                                                  ('000005', '000011', '000002', '000005'))

        self.assertEqual(connection.execs[0].body, PACKAGE_SOURCE_LIBRARY_REQUEST_XML)

    def test_walk_step(self):
        subpackages = [SimpleNamespace(OBJECT_NAME='SUBPACKAGE1'), SimpleNamespace(OBJECT_NAME='SUBPACKAGE2')]
        types = [SimpleNamespace(NODE_ID='000005', OBJECT_TYPE='CLAS/OC'),
                 SimpleNamespace(NODE_ID='000011', OBJECT_TYPE='DEVC/K')]
        first_call = SimpleNamespace(objects=subpackages, types=types)

        objects = [SimpleNamespace(OBJECT_NAME='OBJECT1', OBJECT_TYPE='PROG', OBJECT_URI='URI', DESCRIPTION='Desc 1'),
                   SimpleNamespace(OBJECT_NAME='OBJECT2', OBJECT_TYPE='FUGR/F', OBJECT_URI='URI', DESCRIPTION='Desc 2')]
        second_call = SimpleNamespace(objects=objects)

        self.patch('sap.adt.repository.Repository.read_node', side_effect=[first_call, second_call])

        repository = sap.adt.Repository(None)
        actual_subpackages, actual_objects = repository.walk_step('PACKAGE')

        self.assertEqual(actual_subpackages, [subpackage.OBJECT_NAME for subpackage in subpackages])
        self.assertEqual(actual_objects,
                         [SimpleNamespace(typ=obj.OBJECT_TYPE, name=obj.OBJECT_NAME, uri=obj.OBJECT_URI, description=obj.DESCRIPTION) for obj in objects])

    def test_walk_step_empty_nodekeys(self):
        subpackages = [SimpleNamespace(OBJECT_NAME='SUBPACKAGE1'), SimpleNamespace(OBJECT_NAME='SUBPACKAGE2')]
        types = [SimpleNamespace(NODE_ID='000005', OBJECT_TYPE='DEVC/K')]
        first_call = SimpleNamespace(objects=subpackages, types=types)
        self.patch('sap.adt.repository.Repository.read_node', side_effect=[first_call])

        repository = sap.adt.Repository(None)
        actual_subpackages, actual_objects = repository.walk_step('PACKAGE')

        self.assertEqual(actual_subpackages, [subpackage.OBJECT_NAME for subpackage in subpackages])
        self.assertEqual(actual_objects, [])

    def test_walk_step_with_description(self):
        subpackages = [SimpleNamespace(OBJECT_NAME='SUBPACKAGE1', OBJECT_TYPE='DEVC/K', OBJECT_URI='URI1', DESCRIPTION='Subpkg 1'),
                       SimpleNamespace(OBJECT_NAME='SUBPACKAGE2', OBJECT_TYPE='DEVC/K', OBJECT_URI='URI2', DESCRIPTION='Subpkg 2')]
        types = [SimpleNamespace(NODE_ID='000005', OBJECT_TYPE='CLAS/OC'),
                 SimpleNamespace(NODE_ID='000011', OBJECT_TYPE='DEVC/K')]
        first_call = SimpleNamespace(objects=subpackages, types=types)

        objects = [SimpleNamespace(OBJECT_NAME='OBJECT1', OBJECT_TYPE='PROG', OBJECT_URI='URI', DESCRIPTION='Desc 1')]
        second_call = SimpleNamespace(objects=objects)

        self.patch('sap.adt.repository.Repository.read_node', side_effect=[first_call, second_call])

        repository = sap.adt.Repository(None)
        actual_subpackages, actual_objects = repository.walk_step('PACKAGE', withdescr=True)

        self.assertEqual(actual_subpackages,
                         [SimpleNamespace(typ=subpkg.OBJECT_TYPE, name=subpkg.OBJECT_NAME, uri=subpkg.OBJECT_URI, description=subpkg.DESCRIPTION)
                          for subpkg in subpackages])
        self.assertEqual(actual_objects,
                         [SimpleNamespace(typ=obj.OBJECT_TYPE, name=obj.OBJECT_NAME, uri=obj.OBJECT_URI, description=obj.DESCRIPTION)
                          for obj in objects])


if __name__ == '__main__':
    unittest.main()
