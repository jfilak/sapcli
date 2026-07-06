#!/usr/bin/env python3

import unittest
import warnings
from unittest.mock import patch, call

from sap.errors import SAPCliError
from sap.platform.abap.run import (
    generate_class_name,
    build_class_code,
    execute_abap,
    preprocess,
    DEFAULT_PREFIX,
    DEFAULT_PACKAGE,
)

from mock import Connection, Response
from fixtures_adt import EMPTY_RESPONSE_OK, LOCK_RESPONSE_OK
from fixtures_adt_clas import GET_CLASS_ADT_XML
from fixtures_adt_checks import (
    ADT_XML_RUN_OBJECT_CHECK_RESPONSE_CLEAN,
    ADT_XML_RUN_OBJECT_CHECK_RESPONSE_ERRORS,
)


def _make_check_response(text=ADT_XML_RUN_OBJECT_CHECK_RESPONSE_CLEAN):
    return Response(
        text=text,
        status_code=200,
        headers={'Content-Type': 'application/vnd.sap.adt.checkmessages+xml; charset=utf-8'},
    )


FIXED_CLASS_NAME = 'zcl_sapcli_run_anzeiger_abcde'
FIXED_CLASS_NAME_UPPER = FIXED_CLASS_NAME.upper()


class TestGenerateClassName(unittest.TestCase):

    def test_length_is_30(self):
        name = generate_class_name(DEFAULT_PREFIX, 'developer')
        self.assertEqual(len(name), 30)

    def test_starts_with_prefix(self):
        name = generate_class_name(DEFAULT_PREFIX, 'developer')
        self.assertTrue(name.startswith(DEFAULT_PREFIX + '_'))

    def test_contains_username(self):
        name = generate_class_name(DEFAULT_PREFIX, 'DEVELOPER')
        parts = name.split('_', name.count('_') - 1)
        self.assertIn('developer', name)

    def test_username_lowercased(self):
        name_upper = generate_class_name(DEFAULT_PREFIX, 'UPPER')
        name_lower = generate_class_name(DEFAULT_PREFIX, 'upper')
        # Both should contain 'upper' (lowercase)
        self.assertIn('_upper_', name_upper)
        self.assertIn('_upper_', name_lower)

    def test_prefix_lowercased(self):
        name = generate_class_name('ZCL_SAPCLI_RUN', 'user')
        self.assertEqual(name, name.lower())

    def test_too_long_raises_sap_cli_error(self):
        # prefix + _ + username alone would exceed 28 chars
        with self.assertRaises(SAPCliError):
            generate_class_name('zcl_sapcli_run_very_long_px', 'longusernamex')

    def test_custom_prefix(self):
        name = generate_class_name('zcl_myprefix', 'user')
        self.assertEqual(len(name), 30)
        self.assertTrue(name.startswith('zcl_myprefix_user_'))


class TestBuildClassCode(unittest.TestCase):

    def test_contains_class_name(self):
        code = build_class_code(FIXED_CLASS_NAME, 'WRITE "hello".')
        self.assertIn(FIXED_CLASS_NAME_UPPER, code)

    def test_contains_user_code(self):
        user_code = 'WRITE "hello".'
        code = build_class_code(FIXED_CLASS_NAME, user_code)
        self.assertIn(user_code, code)

    def test_implements_interface(self):
        code = build_class_code(FIXED_CLASS_NAME, '')
        self.assertIn('INTERFACES if_oo_adt_classrun.', code)

    def test_main_method_present(self):
        code = build_class_code(FIXED_CLASS_NAME, '')
        self.assertIn('METHOD if_oo_adt_classrun~main.', code)

    def test_user_code_indented(self):
        user_code = 'WRITE "hello".'
        code = build_class_code(FIXED_CLASS_NAME, user_code)
        self.assertIn('        ' + user_code, code)

    def test_multiline_user_code_indented(self):
        user_code = 'line one.\nline two.'
        code = build_class_code(FIXED_CLASS_NAME, user_code)
        self.assertIn('        line one.\n        line two.', code)

    def test_abap_doc_comment_present(self):
        code = build_class_code(FIXED_CLASS_NAME, '')
        self.assertIn('"! This is a temporary class created by sapcli for execution', code)


def _make_activate_response():
    return Response(
        text=GET_CLASS_ADT_XML.replace('ZCL_HELLO_WORLD', FIXED_CLASS_NAME_UPPER),
        status_code=200,
        headers={'Content-Type': 'application/vnd.sap.adt.oo.classes.v4+xml'}
    )


class TestExecuteAbap(unittest.TestCase):

    def _make_connection(self, execution_output='hello from abap'):
        return Connection([
            EMPTY_RESPONSE_OK,           # create
            _make_check_response(),      # check_before_save
            LOCK_RESPONSE_OK,            # lock (open_editor)
            EMPTY_RESPONSE_OK,           # write source
            EMPTY_RESPONSE_OK,           # unlock
            EMPTY_RESPONSE_OK,           # activate (POST)
            _make_activate_response(),   # fetch after activate (GET)
            Response(text=execution_output, status_code=200,
                     headers={'Content-Type': 'text/plain'}),  # execute
            EMPTY_RESPONSE_OK,           # delete
        ])

    def test_returns_execution_output(self):
        connection = self._make_connection('ABAP output')

        with patch('sap.platform.abap.run.generate_class_name', return_value=FIXED_CLASS_NAME):
            result = execute_abap(connection, 'WRITE "hello".')

        self.assertEqual(result, 'ABAP output')

    def test_creates_class_in_default_package(self):
        connection = self._make_connection()

        with patch('sap.platform.abap.run.generate_class_name', return_value=FIXED_CLASS_NAME):
            execute_abap(connection, 'WRITE "hello".')

        create_request = connection.execs[0]
        self.assertEqual(create_request.method, 'POST')
        self.assertIn('/sap/bc/adt/oo/classes', create_request.adt_uri)
        self.assertIn(DEFAULT_PACKAGE.upper(), create_request.body.decode('utf-8'))

    def test_creates_class_with_description(self):
        connection = self._make_connection()

        with patch('sap.platform.abap.run.generate_class_name', return_value=FIXED_CLASS_NAME):
            execute_abap(connection, 'WRITE "hello".')

        create_request = connection.execs[0]
        self.assertIn('Temporary class created by sapcli', create_request.body.decode('utf-8'))

    def test_deletes_class_after_execution(self):
        connection = self._make_connection()

        with patch('sap.platform.abap.run.generate_class_name', return_value=FIXED_CLASS_NAME):
            execute_abap(connection, 'WRITE "hello".')

        delete_request = connection.execs[-1]
        self.assertEqual(delete_request.method, 'POST')
        self.assertIn('deletion/delete', delete_request.adt_uri)

    def test_deletes_class_on_exception(self):
        connection = Connection([
            EMPTY_RESPONSE_OK,           # create
            _make_check_response(),      # check_before_save
            LOCK_RESPONSE_OK,            # lock
            EMPTY_RESPONSE_OK,           # write source
            EMPTY_RESPONSE_OK,           # unlock
            EMPTY_RESPONSE_OK,           # activate
            _make_activate_response(),   # fetch
            Response(status_code=500, headers={}, text='Error'),  # execute fails
            EMPTY_RESPONSE_OK,           # delete must still happen
        ])

        with patch('sap.platform.abap.run.generate_class_name', return_value=FIXED_CLASS_NAME):
            with self.assertRaises(Exception):
                execute_abap(connection, 'WRITE "hello".')

        delete_request = connection.execs[-1]
        self.assertEqual(delete_request.method, 'POST')
        self.assertIn('deletion/delete', delete_request.adt_uri)

    def test_uses_custom_prefix(self):
        connection = self._make_connection()

        custom_prefix = 'zcl_myrun'
        with patch('sap.platform.abap.run.generate_class_name',
                   return_value=FIXED_CLASS_NAME) as mock_gen:
            execute_abap(connection, 'WRITE.', prefix=custom_prefix)

        mock_gen.assert_called_once_with(custom_prefix, connection.user)

    def test_uses_custom_package(self):
        connection = self._make_connection()

        custom_package = '$mypackage'
        with patch('sap.platform.abap.run.generate_class_name', return_value=FIXED_CLASS_NAME):
            execute_abap(connection, 'WRITE.', package=custom_package)

        create_request = connection.execs[0]
        self.assertIn(custom_package.upper(), create_request.body.decode('utf-8'))

    def test_passes_username_to_generate_class_name(self):
        connection = self._make_connection()

        with patch('sap.platform.abap.run.generate_class_name',
                   return_value=FIXED_CLASS_NAME) as mock_gen:
            execute_abap(connection, 'WRITE.')

        mock_gen.assert_called_once_with(DEFAULT_PREFIX, connection.user)

    def test_check_failure_skips_write_and_activate_but_still_deletes(self):
        from sap.adt.checks import ObjectCheckFindings

        connection = Connection([
            EMPTY_RESPONSE_OK,                                                  # create
            _make_check_response(ADT_XML_RUN_OBJECT_CHECK_RESPONSE_ERRORS),     # checkrun finds errors
            EMPTY_RESPONSE_OK,                                                  # delete (finally block)
        ])

        with patch('sap.platform.abap.run.generate_class_name', return_value=FIXED_CLASS_NAME):
            with self.assertRaises(ObjectCheckFindings):
                execute_abap(connection, 'WRITE.')

        methods = connection.mock_methods()
        # Three calls only: create, checkrun POST, delete.
        self.assertEqual(len(methods), 3)
        self.assertEqual(methods[1], ('POST', '/sap/bc/adt/checkruns'))
        # No PUT to source/main, no activation request.
        self.assertFalse(any(m == 'PUT' and uri.endswith('/source/main') for m, uri in methods))
        self.assertFalse(any('activation' in uri for _, uri in methods))
        # Delete still happens.
        self.assertIn('deletion/delete', connection.execs[-1].adt_uri)

    def test_delete_failure_emits_warning_instead_of_exception(self):
        connection = Connection([
            EMPTY_RESPONSE_OK,           # create
            _make_check_response(),      # check_before_save
            LOCK_RESPONSE_OK,            # lock
            EMPTY_RESPONSE_OK,           # write source
            EMPTY_RESPONSE_OK,           # unlock
            EMPTY_RESPONSE_OK,           # activate (POST)
            _make_activate_response(),   # fetch after activate (GET)
            Response(text='output', status_code=200,
                     headers={'Content-Type': 'text/plain'}),  # execute
            Response(text='Not found', status_code=404, headers={}),  # delete fails
        ])

        with patch('sap.platform.abap.run.generate_class_name', return_value=FIXED_CLASS_NAME):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                result = execute_abap(connection, 'WRITE "hello".')

        self.assertEqual(result, 'output')
        self.assertEqual(len(caught), 1)
        self.assertIn(FIXED_CLASS_NAME, str(caught[0].message))

    def test_delete_failure_after_create_failure_emits_warning(self):
        connection = Connection([
            Response(text='Create failed', status_code=500, headers={}),  # create fails
            Response(text='Not found', status_code=404, headers={}),      # delete fails too
        ])

        with patch('sap.platform.abap.run.generate_class_name', return_value=FIXED_CLASS_NAME):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                with self.assertRaises(Exception):
                    execute_abap(connection, 'WRITE "hello".')

        self.assertEqual(len(caught), 1)
        self.assertIn(FIXED_CLASS_NAME, str(caught[0].message))

    def test_check_disabled_via_env_skips_check_post(self):
        connection = Connection([
            EMPTY_RESPONSE_OK,           # create
            LOCK_RESPONSE_OK,            # lock (open_editor)
            EMPTY_RESPONSE_OK,           # write source
            EMPTY_RESPONSE_OK,           # unlock
            EMPTY_RESPONSE_OK,           # activate (POST)
            _make_activate_response(),   # fetch after activate (GET)
            Response(text='out', status_code=200,
                     headers={'Content-Type': 'text/plain'}),
            EMPTY_RESPONSE_OK,           # delete
        ])

        with patch('os.environ', {'SAPCLI_CHECK_BEFORE_SAVE': 'false'}):
            with patch('sap.platform.abap.run.generate_class_name', return_value=FIXED_CLASS_NAME):
                execute_abap(connection, 'WRITE "hi".')

        methods = connection.mock_methods()
        self.assertFalse(any(uri.startswith('/sap/bc/adt/checkruns') for _, uri in methods))

    def test_new_session_called_before_execute(self):
        """A new HTTP session must be started between activate and execute
        to avoid the transient ADT error:
        'Class does not implement if_oo_adt_classrun~main method!'"""
        connection = self._make_connection('hello')

        call_order = []
        real_new_session = connection.new_session

        def track_new_session():
            call_order.append(len(connection.execs))
            real_new_session()

        with patch.object(connection, 'new_session', side_effect=track_new_session) as mock_new_session:
            with patch('sap.platform.abap.run.generate_class_name', return_value=FIXED_CLASS_NAME):
                execute_abap(connection, 'WRITE "hello".')

        mock_new_session.assert_called_once_with()

        # The mock sequence in _make_connection is:
        # 0 create, 1 check, 2 lock, 3 write, 4 unlock,
        # 5 activate POST, 6 activate fetch GET, 7 execute, 8 delete
        # new_session() must be called after the activation fetch (index 6 done)
        # and before the execute request (index 7).
        self.assertEqual(call_order, [7])

    def test_new_session_not_called_when_check_fails(self):
        """When the pre-save check finds errors, execution is skipped and
        there is no reason to reset the session."""
        from sap.adt.checks import ObjectCheckFindings

        connection = Connection([
            EMPTY_RESPONSE_OK,                                                  # create
            _make_check_response(ADT_XML_RUN_OBJECT_CHECK_RESPONSE_ERRORS),     # checkrun
            EMPTY_RESPONSE_OK,                                                  # delete
        ])

        with patch.object(connection, 'new_session') as mock_new_session:
            with patch('sap.platform.abap.run.generate_class_name', return_value=FIXED_CLASS_NAME):
                with self.assertRaises(ObjectCheckFindings):
                    execute_abap(connection, 'WRITE.')

        mock_new_session.assert_not_called()


class TestPreprocess(unittest.TestCase):

    def test_replaces_single_token(self):
        result = preprocess('WRITE {{VALUE}}.', {'VALUE': '42'})
        self.assertEqual(result, 'WRITE 42.')

    def test_replaces_multiple_occurrences_of_same_token(self):
        result = preprocess('{{X}} + {{X}}', {'X': '1'})
        self.assertEqual(result, '1 + 1')

    def test_replaces_multiple_distinct_tokens(self):
        result = preprocess('{{A}} {{B}}', {'A': 'foo', 'B': 'bar'})
        self.assertEqual(result, 'foo bar')

    def test_allows_whitespace_inside_braces(self):
        result = preprocess('{{ NAME }}', {'NAME': 'x'})
        self.assertEqual(result, 'x')

    def test_code_without_tokens_unchanged(self):
        code = 'WRITE / lv_text.'
        self.assertEqual(preprocess(code, {'UNUSED': '1'}), code)

    def test_no_definitions_and_no_tokens_returns_same(self):
        code = 'WRITE / lv_text.'
        self.assertEqual(preprocess(code, {}), code)

    def test_single_braces_are_not_tokens(self):
        code = "out->write( |Hello { lv_name }| )."
        self.assertEqual(preprocess(code, {'lv_name': 'x'}), code)

    def test_empty_value_replacement(self):
        result = preprocess('x{{E}}y', {'E': ''})
        self.assertEqual(result, 'xy')

    def test_value_is_not_interpreted_as_regex(self):
        result = preprocess('CALL {{FN}}.', {'FN': "method( '\\1' )"})
        self.assertEqual(result, "CALL method( '\\1' ).")

    def test_undefined_token_raises(self):
        with self.assertRaises(SAPCliError) as caught:
            preprocess('WRITE {{MISSING}}.', {})

        self.assertIn('MISSING', str(caught.exception))

    def test_undefined_token_error_lists_missing_only(self):
        with self.assertRaises(SAPCliError) as caught:
            preprocess('{{KNOWN}} {{UNKNOWN}}', {'KNOWN': '1'})

        self.assertIn('UNKNOWN', str(caught.exception))

    def test_unsupported_expression_bash_default_raises(self):
        with self.assertRaises(SAPCliError) as caught:
            preprocess("WRITE {{NAME:-'x'}}.", {'NAME': '1'})

        self.assertIn("{{NAME:-'x'}}", str(caught.exception))

    def test_unsupported_expression_filter_raises(self):
        with self.assertRaises(SAPCliError) as caught:
            preprocess("WRITE {{name | default('')}}.", {'name': '1'})

        self.assertIn('Unsupported preprocessor expression', str(caught.exception))

    def test_unsupported_expression_function_raises(self):
        with self.assertRaises(SAPCliError) as caught:
            preprocess('WRITE {{file(name)}}.', {'name': '1'})

        self.assertIn('Unsupported preprocessor expression', str(caught.exception))

    def test_unsupported_expression_empty_raises(self):
        with self.assertRaises(SAPCliError) as caught:
            preprocess('WRITE {{}}.', {})

        self.assertIn('Unsupported preprocessor expression', str(caught.exception))

    def test_unsupported_expression_digits_only_raises(self):
        with self.assertRaises(SAPCliError) as caught:
            preprocess('WRITE {{123}}.', {'123': '1'})

        self.assertIn('Unsupported preprocessor expression', str(caught.exception))

    def test_name_starting_with_underscore_is_valid(self):
        result = preprocess('WRITE {{_NAME}}.', {'_NAME': '1'})
        self.assertEqual(result, 'WRITE 1.')

    def test_token_must_not_span_lines(self):
        code = 'WRITE {{A\nB}} {{C}}.'
        result = preprocess(code, {'C': '1'})
        self.assertEqual(result, 'WRITE {{A\nB}} 1.')

    def test_statement_delimiter_is_reserved(self):
        with self.assertRaises(SAPCliError) as caught:
            preprocess('{% if x %}WRITE.{% endif %}', {})

        self.assertIn('{%', str(caught.exception))

    def test_comment_delimiter_is_reserved(self):
        with self.assertRaises(SAPCliError) as caught:
            preprocess('{# note #}WRITE.', {})

        self.assertIn('{#', str(caught.exception))

    def test_unpaired_statement_delimiter_is_reserved(self):
        with self.assertRaises(SAPCliError) as caught:
            preprocess("WRITE '{%'.", {})

        self.assertIn('{%', str(caught.exception))

    def test_reserved_delimiter_error_lists_all_found(self):
        with self.assertRaises(SAPCliError) as caught:
            preprocess('{# doc #}\n{% if x %}WRITE.{% endif %}', {})

        self.assertIn('{%', str(caught.exception))
        self.assertIn('{#', str(caught.exception))

    def test_reserved_delimiter_detected_even_with_valid_tokens(self):
        with self.assertRaises(SAPCliError) as caught:
            preprocess('{{A}} {% set x = 1 %}', {'A': '1'})

        self.assertIn('{%', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
