#!/usr/bin/env python3

import types
import unittest
from unittest.mock import call, patch, Mock, PropertyMock, MagicMock, mock_open
from io import StringIO

import sap.adt.wb
import sap.cli.activation
import sap.errors

from mock import Connection, Response, GroupArgumentParser, patch_get_print_console_with_buffer

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

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(conn, args)

        self.assertEqual("", fake_console.caperr)
        self.assertEqual(fake_console.capout,
                         """CL_PARENT_CLASS (CLAS/OC)
 + CL_PARENT_CLASS===RUN (CLAS/OC/M)
CL_ANOTHER_CLASS (CLAS/OC)
FAKE (SAPCLI/PYTEST)
""")


class TestInactiveobjectsActivate(unittest.TestCase):

    @patch('sap.cli.activation.mass_activate')
    @patch('sap.cli.activation.fetch_inactive_objects')
    def test_no_inactive_objects(self, fake_fetch, fake_mass):
        conn = Mock()

        fake_fetch.return_value = sap.adt.wb.IOCList()

        args = INACTIVEOBJECTS_PARSER.parse('activate')

        with patch_get_print_console_with_buffer() as fake_console:
            rc = args.execute(conn, args)

        self.assertEqual(rc, 0)
        fake_mass.assert_not_called()
        self.assertIn('No inactive objects.', fake_console.capout)

    @patch('sap.cli.activation.mass_activate')
    @patch('sap.cli.activation.fetch_inactive_objects')
    def test_two_entries_are_sent_in_one_request(self, fake_fetch, fake_mass):
        conn = Mock()

        builder = IOCObjectListBuilder()
        builder.add_class('CL_FIRST')
        builder.add_class('CL_SECOND')
        fake_fetch.return_value = builder.objects

        results = Mock()
        results.has_errors = False
        results.has_warnings = False
        results.messages = []
        fake_mass.return_value = (results, Mock())

        args = INACTIVEOBJECTS_PARSER.parse('activate')

        with patch_get_print_console_with_buffer() as fake_console:
            rc = args.execute(conn, args)

        self.assertEqual(rc, 0)
        self.assertEqual(fake_mass.call_count, 1)
        sent_refs = fake_mass.call_args.args[1]
        self.assertEqual(len(sent_refs.references), 2)
        self.assertIn('Activating 2 object(s):', fake_console.capout)
        self.assertIn('Activation finished.', fake_console.capout)

    @patch('sap.cli.activation.mass_activate')
    @patch('sap.cli.activation.fetch_inactive_objects')
    def test_deleted_entries_are_skipped(self, fake_fetch, fake_mass):
        conn = Mock()

        builder = IOCObjectListBuilder()
        builder.add_class('CL_KEEP')
        deleted = builder.add_class('CL_DELETED')
        deleted.object.deleted = 'true'
        fake_fetch.return_value = builder.objects

        results = Mock()
        results.has_errors = False
        results.has_warnings = False
        results.messages = []
        fake_mass.return_value = (results, Mock())

        args = INACTIVEOBJECTS_PARSER.parse('activate')

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(conn, args)

        sent_refs = fake_mass.call_args.args[1]
        self.assertEqual(len(sent_refs.references), 1)
        self.assertEqual(sent_refs.references[0].name, 'CL_KEEP')

        # The printed listing must reflect the filtered set that is actually
        # sent to mass_activate; the deleted entry must not appear.
        self.assertIn('Activating 1 object(s):', fake_console.capout)
        self.assertIn('CL_KEEP', fake_console.capout)
        self.assertNotIn('CL_DELETED', fake_console.capout)

    @patch('sap.cli.activation.mass_activate')
    @patch('sap.cli.activation.fetch_inactive_objects')
    def test_dry_run_does_not_call_mass_activate(self, fake_fetch, fake_mass):
        conn = Mock()

        builder = IOCObjectListBuilder()
        builder.add_class('CL_FOO')
        fake_fetch.return_value = builder.objects

        args = INACTIVEOBJECTS_PARSER.parse('activate', '--dry-run')

        with patch_get_print_console_with_buffer() as fake_console:
            rc = args.execute(conn, args)

        self.assertEqual(rc, 0)
        fake_mass.assert_not_called()
        self.assertIn('Dry run', fake_console.capout)

    @patch('sap.cli.activation.mass_activate')
    @patch('sap.cli.activation.fetch_inactive_objects')
    def test_errors_return_one(self, fake_fetch, fake_mass):
        conn = Mock()

        builder = IOCObjectListBuilder()
        builder.add_class('CL_FOO')
        fake_fetch.return_value = builder.objects

        message = Mock()
        message.typ = 'E'
        message.obj_descr = 'CL_FOO'
        message.short_text = 'syntax error'
        message.is_warning = False
        message.is_error = True

        results = Mock()
        results.has_errors = True
        results.has_warnings = False
        results.messages = [message]
        fake_mass.return_value = (results, Mock())

        args = INACTIVEOBJECTS_PARSER.parse('activate')

        with patch_get_print_console_with_buffer():
            rc = args.execute(conn, args)

        self.assertEqual(rc, 1)

    @patch('sap.cli.activation.mass_activate')
    @patch('sap.cli.activation.fetch_inactive_objects')
    def test_ignore_errors_returns_zero(self, fake_fetch, fake_mass):
        conn = Mock()

        builder = IOCObjectListBuilder()
        builder.add_class('CL_FOO')
        fake_fetch.return_value = builder.objects

        message = Mock()
        message.typ = 'E'
        message.obj_descr = 'CL_FOO'
        message.short_text = 'syntax error'
        message.is_warning = False
        message.is_error = True

        results = Mock()
        results.has_errors = True
        results.has_warnings = False
        results.messages = [message]
        fake_mass.return_value = (results, Mock())

        args = INACTIVEOBJECTS_PARSER.parse('activate', '--ignore-errors')

        with patch_get_print_console_with_buffer():
            rc = args.execute(conn, args)

        self.assertEqual(rc, 0)


OBJECTS_PARSER = GroupArgumentParser(sap.cli.activation.ObjectsGroup)


class TestObjectsActivate(unittest.TestCase):

    def test_list_kinds_short_circuits(self):
        conn = Mock()

        args = OBJECTS_PARSER.parse('activate', '--list-kinds')

        with patch_get_print_console_with_buffer() as fake_console:
            rc = args.execute(conn, args)

        self.assertEqual(rc, 0)
        self.assertIn('Supported KINDs:', fake_console.capout)
        self.assertIn('program', fake_console.capout)

    def test_missing_object_without_list_kinds_raises(self):
        conn = Mock()

        args = OBJECTS_PARSER.parse('activate')

        with patch_get_print_console_with_buffer():
            with self.assertRaises(sap.errors.SAPCliError):
                args.execute(conn, args)

    @patch('sap.cli.activation.mass_activate')
    def test_two_objects_sent_in_one_request(self, fake_mass):
        conn = Connection()

        results = Mock()
        results.has_errors = False
        results.has_warnings = False
        results.messages = []
        fake_mass.return_value = (results, Mock())

        args = OBJECTS_PARSER.parse(
            'activate',
            '--object', 'program=ZMYREP',
            '--object', 'include=ZMYREP_C01'
        )

        with patch_get_print_console_with_buffer() as fake_console:
            rc = args.execute(conn, args)

        self.assertEqual(rc, 0)
        self.assertEqual(fake_mass.call_count, 1)
        sent_refs = fake_mass.call_args.args[1]
        self.assertEqual(len(sent_refs.references), 2)
        self.assertIn('Activating 2 object(s):', fake_console.capout)

    def test_unknown_kind_raises_sapclierror(self):
        conn = Mock()

        args = OBJECTS_PARSER.parse('activate', '--object', 'foobar=ZX')

        with patch_get_print_console_with_buffer():
            with self.assertRaises(sap.errors.SAPCliError):
                args.execute(conn, args)

    def test_malformed_spec_raises_sapclierror(self):
        conn = Mock()

        args = OBJECTS_PARSER.parse('activate', '--object', 'no-equals-sign')

        with patch_get_print_console_with_buffer():
            with self.assertRaises(sap.errors.SAPCliError):
                args.execute(conn, args)

    @patch('sap.cli.activation.mass_activate')
    def test_dry_run_does_not_call_mass_activate(self, fake_mass):
        conn = Connection()

        args = OBJECTS_PARSER.parse(
            'activate', '--dry-run', '--object', 'program=ZMYREP'
        )

        with patch_get_print_console_with_buffer() as fake_console:
            rc = args.execute(conn, args)

        self.assertEqual(rc, 0)
        fake_mass.assert_not_called()
        self.assertIn('Dry run', fake_console.capout)

    def test_alias_resolves_to_same_class(self):
        # The CLI accepts both canonical and ABAP aliases. Going through
        # the CLI ensures the resolution is wired up via the shared
        # human_names_factory rather than a CLI-local table.
        conn = Connection()

        results = Mock()
        results.has_errors = False
        results.has_warnings = False
        results.messages = []

        with patch('sap.cli.activation.mass_activate') as fake_mass:
            fake_mass.return_value = (results, Mock())

            args = OBJECTS_PARSER.parse(
                'activate',
                '--object', 'prog=ZMYREP',
                '--object', 'clas=CL_FOO',
                '--object', 'incl=ZMYREP_C01',
            )

            with patch_get_print_console_with_buffer():
                args.execute(conn, args)

            sent_refs = fake_mass.call_args.args[1]

        names = [ref.name for ref in sent_refs.references]
        self.assertEqual(names, ['ZMYREP', 'CL_FOO', 'ZMYREP_C01'])


if __name__ == '__main__':
    unittest.main()
