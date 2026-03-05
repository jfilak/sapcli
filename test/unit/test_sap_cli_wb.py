#!/usr/bin/env python3

import unittest
from unittest.mock import patch, Mock

import sap.adt.wb
import sap.cli.wb
import sap.errors

from mock import patch_get_print_console_with_buffer, BufferConsole

from fixtures_adt_wb import MessageBuilder


class TestObjectActivationWorker(unittest.TestCase):

    def setUp(self):
        self.worker = sap.cli.wb.ObjectActivationWorker()
        self.activated_object = Mock(active='inactive') # by default, simulate inactive object
        self.message_builder = MessageBuilder()
        self.stats = sap.cli.wb.ObjectActivationStats()

    def test_properties(self):
        self.assertFalse(self.worker.continue_on_errors)
        self.assertFalse(self.worker.warnings_as_errors)

        self.worker.continue_on_errors = True
        self.assertTrue(self.worker.continue_on_errors)

        self.worker.warnings_as_errors = True
        self.assertTrue(self.worker.warnings_as_errors)

    def test_begin(self):
        cases = [(None, 'Activating:\n'),
                 (1, 'Activating:\n'),
                 (2, 'Activating 2 objects:\n')]

        for no, case in enumerate(cases):
            with patch_get_print_console_with_buffer() as fake_console:
                self.worker.begin(case[0])

            self.assertEqual(fake_console.caperr, '', f'Case {no}')
            self.assertEqual(fake_console.capout, case[1], f'Case {no}')

    def test_start_object(self):
        cases = [('CL_NONE', 1, None, '* CL_NONE\n'),
                 ('CL_ONE', 1, 1, '* CL_ONE\n'),
                 ('CL_TWO', 1, 2, '* CL_TWO (1/2)\n')]

        for no, case in enumerate(cases):
            with patch_get_print_console_with_buffer() as fake_console:
                self.worker.start_object(case[0], case[1], case[2])

            self.assertEqual(fake_console.caperr, '', f'Case {no}')
            self.assertEqual(fake_console.capout, case[3], f'Case {no}')

    def test_handle_message(self):
        message, lines = self.message_builder.build_warning()

        with patch_get_print_console_with_buffer() as fake_console:
            self.worker.handle_message(message)

        self.assertEqual(fake_console.caperr, '')
        self.assertEqual(fake_console.capout, lines)

    def assert_ok_stats(self, stats):
        self.assertEqual(stats.warnings, 0)
        self.assertEqual(stats.errors, 0)
        self.assertEqual(stats.active_objects, [self.activated_object])
        self.assertEqual(stats.inactive_objects, [])

    def test_handle_results_without_messages(self):
        self.activated_object.active = "active" # simulate activated object

        with patch_get_print_console_with_buffer() as fake_console:
            self.worker.handle_results('CL_NO_MESSAGES',
                                       self.activated_object,
                                       self.message_builder.build_results_without_messages(),
                                       self.stats)

        self.assertEqual(fake_console.caperr, '')
        self.assertEqual(fake_console.capout, '')

        self.assert_ok_stats(self.stats)

    def assert_error_stats(self, stats):
        self.assertEqual(stats.warnings, 0)
        self.assertEqual(stats.errors, 1)
        self.assertEqual(stats.active_objects, [])
        self.assertEqual(stats.inactive_objects, [self.activated_object])

    def assert_error_message_output(self, fake_console):
        self.assertEqual(fake_console.caperr, '')
        self.assertEqual(fake_console.capout, self.message_builder.error_message[1])

    def test_handle_results_with_errors_no_continue(self):
        with self.assertRaises(sap.cli.wb.StopObjectActivation) as caught, \
             patch_get_print_console_with_buffer() as fake_console:
            self.worker.handle_results('CL_NO_MESSAGES',
                                       self.activated_object,
                                       self.message_builder.build_results_with_errors(),
                                       self.stats)

        self.assert_error_message_output(fake_console)
        self.assert_error_stats(caught.exception.stats)

    def test_handle_results_with_errors_continue(self):
        self.worker.continue_on_errors = True

        with patch_get_print_console_with_buffer() as fake_console:
            stats = self.worker.handle_results('CL_NO_MESSAGES',
                                       self.activated_object,
                                       self.message_builder.build_results_with_errors(),
                                       self.stats)

        self.assert_error_message_output(fake_console)
        self.assert_error_stats(self.stats)

    def assert_warning_stats(self, stats):
        self.assertEqual(stats.warnings, 1)
        self.assertEqual(stats.active_objects, [self.activated_object])
        self.assertEqual(stats.inactive_objects, [])

    def assert_warning_message_output(self, fake_console):
        self.assertEqual(fake_console.caperr, '')
        self.assertEqual(fake_console.capout, self.message_builder.warning_message[1])

    def test_handle_results_with_warnings_and_stop(self):
        self.worker.warnings_as_errors = True
        self.activated_object.active = "active" # simulate activated object

        with self.assertRaises(sap.cli.wb.StopObjectActivation) as caught, \
             patch_get_print_console_with_buffer() as fake_console:
            self.worker.handle_results('CL_NO_MESSAGES',
                                       self.activated_object,
                                       self.message_builder.build_results_with_warnings(),
                                       self.stats)

        self.assert_warning_message_output(fake_console)
        self.assert_warning_stats(caught.exception.stats)
        self.assertEqual(caught.exception.stats.errors, 1)

    def test_handle_results_with_warnings(self):
        self.activated_object.active = "active" # simulate activated object

        with patch_get_print_console_with_buffer() as fake_console:
            stats = self.worker.handle_results('CL_NO_MESSAGES',
                                       self.activated_object,
                                       self.message_builder.build_results_with_warnings(),
                                       self.stats)

        self.assert_warning_message_output(fake_console)
        self.assert_warning_stats(self.stats)
        self.assertEqual(self.stats.errors, 0)

    def test_handle_results_with_warnings_as_error_and_ignore(self):
        self.worker.continue_on_errors = True
        self.worker.warnings_as_errors = True
        self.activated_object.active = "active" # simulate activated object

        with patch_get_print_console_with_buffer() as fake_console:
            stats = self.worker.handle_results('CL_NO_MESSAGES',
                                       self.activated_object,
                                       self.message_builder.build_results_with_warnings(),
                                       self.stats)

        self.assert_warning_message_output(fake_console)
        self.assert_warning_stats(self.stats)
        self.assertEqual(self.stats.errors, 1)

    def test_activate_sequentially(self):
        self.activated_object.active = "active" # simulate activated object

        with patch('sap.adt.wb.try_activate') as fake_try_activate, \
             patch_get_print_console_with_buffer() as fake_console:

            fake_try_activate.return_value = (self.message_builder.build_results_without_messages(), None)
            items = (itm for itm in [('mock_obj_name', self.activated_object)])
            stats = self.worker.activate_sequentially(items, count=2)

        self.assertEqual(fake_console.caperr, '')
        self.assertEqual(fake_console.capout, '''Activating 2 objects:
* mock_obj_name (1/2)
''')

        self.assert_ok_stats(stats)


class TestActivate(unittest.TestCase):

    def setUp(self):
        self.connection = Mock()
        self.console = BufferConsole()
        self.inactive_objects = Mock()

    @patch('sap.adt.wb.try_mass_activate')
    def test_no_messages(self, fake_mass_activate):
        fake_mass_activate.return_value = None

        sap.cli.wb.activate(self.connection, self.inactive_objects, self.console)

        fake_mass_activate.assert_called_once_with(self.connection, self.inactive_objects)
        self.assertEqual(self.console.capout, '')

    @patch('sap.adt.wb.try_mass_activate')
    def test_info_messages(self, fake_mass_activate):
        msg = Mock()
        msg.is_error = False
        msg.obj_descr = 'CL_TEST'
        msg.typ = 'I'
        msg.short_text = 'Info message'

        fake_mass_activate.return_value = [msg]

        sap.cli.wb.activate(self.connection, self.inactive_objects, self.console)

        self.assertEqual(self.console.capout, '* CL_TEST ::\n| I: Info message\n')

    @patch('sap.adt.wb.try_mass_activate')
    def test_error_messages(self, fake_mass_activate):
        msg = Mock()
        msg.is_error = True
        msg.obj_descr = 'CL_BROKEN'
        msg.typ = 'E'
        msg.short_text = 'Syntax error'

        fake_mass_activate.return_value = [msg]

        with self.assertRaises(sap.errors.SAPCliError) as cm:
            sap.cli.wb.activate(self.connection, self.inactive_objects, self.console)

        self.assertEqual(str(cm.exception), 'Aborting because of activation errors')
        self.assertEqual(self.console.capout, '* CL_BROKEN ::\n| E: Syntax error\n')

    @patch('sap.adt.wb.try_mass_activate')
    def test_mixed_messages(self, fake_mass_activate):
        info_msg = Mock()
        info_msg.is_error = False
        info_msg.obj_descr = 'CL_OK'
        info_msg.typ = 'I'
        info_msg.short_text = 'All good'

        err_msg = Mock()
        err_msg.is_error = True
        err_msg.obj_descr = 'CL_BAD'
        err_msg.typ = 'E'
        err_msg.short_text = 'Not good'

        fake_mass_activate.return_value = [info_msg, err_msg]

        with self.assertRaises(sap.errors.SAPCliError):
            sap.cli.wb.activate(self.connection, self.inactive_objects, self.console)

        self.assertIn('* CL_OK ::', self.console.capout)
        self.assertIn('* CL_BAD ::', self.console.capout)


if __name__ == '__main__':
    unittest.main()
