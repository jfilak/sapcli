#!/usr/bin/env python3

import unittest
from unittest.mock import call, patch, Mock, PropertyMock, MagicMock, mock_open
from io import StringIO

import sap.adt.wb
import sap.cli.activation

from mock import GroupArgumentParser, patch_get_print_console_with_buffer

from fixtures_adt_wb import RESPONSE_INACTIVE_OBJECTS_V1


INACTIVEOBJECTS_PARSER = GroupArgumentParser(sap.cli.activation.InactiveObjectsGroup)


class IOCObjectListBuilder:

    def __init__(self):
        self.objects = sap.adt.wb.IOCList()

    def create_basic_object(self):
        ioc_object = sap.adt.wb.IOCEntry()
        ioc_object.object = sap.adt.wb.IOCEntryData()
        ioc_object.object.user = 'FILAK'
        ioc_object.object.linked = ''
        ioc_object.object.deleted = ''

        return ioc_object

    def populate_class_reference(self, reference, name):
        reference.name = f'{name.upper()}'
        reference.uri = f'/sap/bc/adt/classes/{name.lower()}'
        reference.parent_uri = None
        reference.typ = 'CLAS/OC'
        reference.description = f'Class {name}'

    def populate_class_method_reference(self, reference, name, ioc_class):
        reference.name = f'{ioc_class.object.name}==={name.upper()}'
        reference.uri = f'{ioc_class.object.uri};method={name.lower()}'
        reference.parent_uri = ioc_class.object.uri
        reference.typ = f'{ioc_class.object.typ}/M'
        reference.description = f'Method {name} of {ioc_class.object.name}'

    def add_class(self, name):
        ioc_class = self.create_basic_object()
        self.populate_class_reference(ioc_class.object.reference, name)

        self.objects.entries.append(ioc_class)

        return ioc_class

    def add_class_method(self, ioc_class, name):
        ioc_class_method = self.create_basic_object()
        self.populate_class_method_reference(ioc_class_method.object.reference, name, ioc_class)

        self.objects.entries.append(ioc_class_method)

        return ioc_class_method


class TestInactiveobjectsList(unittest.TestCase):

    @patch('sap.cli.activation.fetch_inactive_objects')
    def test_inactiveobjects_list(self, fake_fetch):
        conn = Mock()

        ioc_list_builder = IOCObjectListBuilder()
        ioc_class = ioc_list_builder.add_class('CL_PARENT_CLASS')
        ioc_class_method = ioc_list_builder.add_class_method(ioc_class, 'RUN')
        ioc_list_builder.add_class('CL_ANOTHER_CLASS')

        child_of_child = sap.adt.wb.IOCEntry()
        child_of_child.object = sap.adt.wb.IOCEntryData()
        child_of_child.object.reference.name = 'FAKE'
        child_of_child.object.reference.typ = 'SAPCLI/PYTEST'
        child_of_child.object.reference.parent_uri = ioc_class_method.object.uri

        ioc_list_builder.objects.entries.append(child_of_child)

        # BEGIN: malicious re-add already added objects
        # needed to test all statements of the function inactiveobjects_list
        ioc_list_builder.objects.entries.append(ioc_class)
        ioc_list_builder.objects.entries.append(ioc_class_method)
        # END

        fake_fetch.return_value = ioc_list_builder.objects

        args = INACTIVEOBJECTS_PARSER.parse('list')

        std_output = StringIO()
        err_output = StringIO()

        with patch_get_print_console_with_buffer() as fake_get_console:
            args.execute(conn, args)

        self.assertEqual("", fake_get_console.return_value.err_output.getvalue())
        self.assertEqual(fake_get_console.return_value.std_output.getvalue(),
                         """CL_PARENT_CLASS (CLAS/OC)
 + CL_PARENT_CLASS===RUN (CLAS/OC/M)
CL_ANOTHER_CLASS (CLAS/OC)
FAKE (SAPCLI/PYTEST)
""")


if __name__ == '__main__':
    unittest.main()
