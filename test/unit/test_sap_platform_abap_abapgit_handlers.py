#!/usr/bin/env python3

import unittest

import sap.platform.abap.abapgit.handlers
from sap.platform.abap.localrepository import HandlerRegistry, ObjectHandler


class TestHandlers(unittest.TestCase):

    def test_file_types(self):
        file_types = sorted(handler.FILE_TYPE for handler in sap.platform.abap.abapgit.handlers.HANDLERS)

        self.assertEqual(file_types, ['bdef', 'clas', 'dcls', 'ddls', 'ddlx', 'doma', 'dtel', 'fugr', 'intf', 'prog',
                                      'tabl', 'ttyp'])

    def test_all_are_abapgit_xml_handlers(self):
        self.assertEqual({handler.METADATA_EXT for handler in sap.platform.abap.abapgit.handlers.HANDLERS}, {'xml'})
        self.assertTrue(all(isinstance(handler, ObjectHandler) for handler in sap.platform.abap.abapgit.handlers.HANDLERS))

    def test_registry_can_be_built(self):
        registry = HandlerRegistry(sap.platform.abap.abapgit.handlers.HANDLERS)

        self.assertEqual(registry.for_metadata_file('clas', 'xml').ADT_TYPES, ('CLAS/OC',))

        tabl_handler = registry.for_metadata_file('tabl', 'xml')
        self.assertIsNotNone(tabl_handler)
        self.assertIs(registry.for_adt_type('TABL/DT'), tabl_handler)
        self.assertIs(registry.for_adt_type('TABL/DS'), tabl_handler)


if __name__ == '__main__':
    unittest.main()
