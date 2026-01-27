#!/usr/bin/env python3

import json
import unittest

from sap.errors import SAPCliError
from sap.rest.gcts.log_messages import (
    _is_empty_line,
    GCTSApplicationInfo,
    TransportToolsApplicationInfo,
    ClientApplicationInfo,
    ProcessMessage,
    ActionMessage,
)

from test.unit.fixtures_sap_rest_gcts_log_messages import (
    GCTS_LOG_MESSAGES_DATA,
    GCTS_LOG_MESSAGES_JSON_EXP,
    GCTS_LOG_MESSAGES_PROCESS_CCC_DATA,
    GCTS_LOG_MESSAGES_PROCESS_CCC_JSON_EXP,
)


class TestIsEmptyLine(unittest.TestCase):

    def test_none_is_empty(self):
        self.assertTrue(_is_empty_line(None))

    def test_empty_string_is_empty(self):
        self.assertTrue(_is_empty_line(''))

    def test_whitespace_only_is_empty(self):
        self.assertTrue(_is_empty_line('   '))
        self.assertTrue(_is_empty_line('\t'))
        self.assertTrue(_is_empty_line('\n'))
        self.assertTrue(_is_empty_line('  \t\n  '))

    def test_non_empty_string(self):
        self.assertFalse(_is_empty_line('hello'))
        self.assertFalse(_is_empty_line('  hello  '))

    def test_non_string_non_none_is_not_empty(self):
        self.assertFalse(_is_empty_line(42))
        self.assertFalse(_is_empty_line([]))
        self.assertFalse(_is_empty_line({}))


class TestGCTSApplicationInfo(unittest.TestCase):

    def test_init_stores_message(self):
        info = GCTSApplicationInfo('Test message')
        self.assertEqual(info.message, 'Test message')

    def test_init_converts_to_string(self):
        info = GCTSApplicationInfo(12345)
        self.assertEqual(info.message, '12345')

    def test_application_property(self):
        info = GCTSApplicationInfo('Test message')
        self.assertEqual(info.application, 'gCTS')

    def test_json_object_returns_message(self):
        info = GCTSApplicationInfo('Test message')
        self.assertEqual(info.json_object, 'Test message')

    def test_formatted_str_no_indent(self):
        info = GCTSApplicationInfo('Test message')
        self.assertEqual(info.formatted_str(), 'Test message')

    def test_formatted_str_with_indent(self):
        info = GCTSApplicationInfo('Test message')
        self.assertEqual(info.formatted_str(indent=4), '    Test message')

    def test_str_returns_json_dumps(self):
        info = GCTSApplicationInfo('Test message')
        self.assertEqual(str(info), '"Test message"')


class TestTransportToolsApplicationInfo(unittest.TestCase):

    def test_init_parses_stdout(self):
        raw = json.dumps({
            'stdout': [
                {'line': 'Line 1'},
                {'line': 'Line 2'}
            ]
        })
        info = TransportToolsApplicationInfo(raw)
        self.assertEqual(info.json_object['stdout'], ['Line 1', 'Line 2'])

    def test_init_empty_stdout(self):
        raw = json.dumps({'stdout': []})
        info = TransportToolsApplicationInfo(raw)
        self.assertEqual(info.json_object['stdout'], [])

    def test_init_missing_line_key(self):
        raw = json.dumps({
            'stdout': [
                {'other': 'value'},
                {'line': 'Line 2'}
            ]
        })
        info = TransportToolsApplicationInfo(raw)
        self.assertEqual(info.json_object['stdout'], ['', 'Line 2'])

    def test_application_property(self):
        raw = json.dumps({'stdout': []})
        info = TransportToolsApplicationInfo(raw)
        self.assertEqual(info.application, 'Transport Tools')

    def test_formatted_str_no_indent(self):
        raw = json.dumps({
            'stdout': [
                {'line': 'Line 1'},
                {'line': 'Line 2'}
            ]
        })
        info = TransportToolsApplicationInfo(raw)
        self.assertEqual(info.formatted_str(), 'Line 1\nLine 2')

    def test_formatted_str_with_indent(self):
        raw = json.dumps({
            'stdout': [
                {'line': 'Line 1'},
                {'line': 'Line 2'}
            ]
        })
        info = TransportToolsApplicationInfo(raw)
        self.assertEqual(info.formatted_str(indent=2), '  Line 1\n  Line 2')

    def test_formatted_str_filters_empty_lines(self):
        raw = json.dumps({
            'stdout': [
                {'line': 'Line 1'},
                {'line': ''},
                {'line': '   '},
                {'line': 'Line 2'}
            ]
        })
        info = TransportToolsApplicationInfo(raw)
        self.assertEqual(info.formatted_str(), 'Line 1\nLine 2')

    def test_str_returns_json_dumps(self):
        raw = json.dumps({'stdout': [{'line': 'test'}]})
        info = TransportToolsApplicationInfo(raw)
        expected = json.dumps({'stdout': ['test']}, indent=2)
        self.assertEqual(str(info), expected)


class TestClientApplicationInfo(unittest.TestCase):

    def test_init_parses_parameters_section(self):
        raw = json.dumps([
            {
                'type': 'Parameters',
                'protocol': [json.dumps({'param1': 'value1'})]
            }
        ])
        info = ClientApplicationInfo(raw)
        self.assertEqual(info.json_object[0]['protocol'], {'param1': 'value1'})

    def test_init_parses_client_log_section(self):
        raw = json.dumps([
            {
                'type': 'Client Log',
                'protocol': ['log line 1', 'log line 2']
            }
        ])
        info = ClientApplicationInfo(raw)
        self.assertEqual(info.json_object[0]['protocol'], ['log line 1', 'log line 2'])

    def test_init_parses_client_response_section(self):
        response_protocol = {'log': [{'message': 'test', 'type': 'INFO'}]}
        raw = json.dumps([
            {
                'type': 'Client Response',
                'protocol': [json.dumps(response_protocol)]
            }
        ])
        info = ClientApplicationInfo(raw)
        self.assertEqual(info.json_object[0]['protocol'], response_protocol)
        self.assertEqual(info.client_response, response_protocol)

    def test_init_parses_client_stack_log_section(self):
        stack_log = [{'code': '001', 'type': 'ERROR', 'message': 'error msg'}]
        raw = json.dumps([
            {
                'type': 'Client Stack Log',
                'protocol': [json.dumps(stack_log)]
            }
        ])
        info = ClientApplicationInfo(raw)
        self.assertEqual(info.json_object[0]['protocol'], stack_log)

    def test_application_property(self):
        raw = json.dumps([
            {
                'type': 'Client Log',
                'protocol': []
            }
        ])
        info = ClientApplicationInfo(raw)
        self.assertEqual(info.application, 'Client')

    def test_formatted_str_extracts_client_response_log(self):
        response_protocol = {
            'log': [
                {'message': 'First message', 'type': 'INFO'},
                {'message': 'Second message', 'type': 'ERROR'}
            ]
        }
        raw = json.dumps([
            {
                'type': 'Client Response',
                'protocol': [json.dumps(response_protocol)]
            }
        ])
        info = ClientApplicationInfo(raw)
        expected = 'INFO: First message\nERROR: Second message'
        self.assertEqual(info.formatted_str(), expected)

    def test_formatted_str_with_indent(self):
        response_protocol = {
            'log': [
                {'message': 'First message', 'type': 'INFO'}
            ]
        }
        raw = json.dumps([
            {
                'type': 'Client Response',
                'protocol': [json.dumps(response_protocol)]
            }
        ])
        info = ClientApplicationInfo(raw)
        self.assertEqual(info.formatted_str(indent=3), '   INFO: First message')

    def test_formatted_str_skips_empty_messages(self):
        response_protocol = {
            'log': [
                {'message': 'First message', 'type': 'INFO'},
                {'message': '', 'type': 'WARN'},
                {'message': '   ', 'type': 'DEBUG'},
                {'type': 'ERROR'},
                {'message': 'Last message', 'type': 'INFO'}
            ]
        }
        raw = json.dumps([
            {
                'type': 'Client Response',
                'protocol': [json.dumps(response_protocol)]
            }
        ])
        info = ClientApplicationInfo(raw)
        expected = 'INFO: First message\nINFO: Last message'
        self.assertEqual(info.formatted_str(), expected)

    def test_formatted_str_no_log_key_in_client_response(self):
        """Test formatted_str when client_response has no 'log' key"""
        response_protocol = {'status': 'ok'}
        raw = json.dumps([
            {
                'type': 'Client Response',
                'protocol': [json.dumps(response_protocol)]
            }
        ])
        info = ClientApplicationInfo(raw)
        # With no 'log' key, the method should handle it gracefully
        # and return an empty string (empty buffer minus trailing newline)
        self.assertEqual(info.formatted_str(), '')

    def test_formatted_str_empty_log_in_client_response(self):
        """Test formatted_str when client_response has empty 'log' list"""
        response_protocol = {'log': []}
        raw = json.dumps([
            {
                'type': 'Client Response',
                'protocol': [json.dumps(response_protocol)]
            }
        ])
        info = ClientApplicationInfo(raw)
        self.assertEqual(info.formatted_str(), '')

    def test_formatted_str_uses_default_type_when_missing(self):
        response_protocol = {
            'log': [
                {'message': 'No type message'}
            ]
        }
        raw = json.dumps([
            {
                'type': 'Client Response',
                'protocol': [json.dumps(response_protocol)]
            }
        ])
        info = ClientApplicationInfo(raw)
        self.assertEqual(info.formatted_str(), '?????: No type message')


class TestProcessMessage(unittest.TestCase):

    def test_appl_info_returns_gcts_application_info(self):
        raw_message = {
            'application': 'gCTS',
            'applInfo': 'gCTS message'
        }
        pm = ProcessMessage(raw_message)
        appl_info = pm.appl_info
        self.assertIsInstance(appl_info, GCTSApplicationInfo)
        self.assertEqual(appl_info.message, 'gCTS message')

    def test_appl_info_returns_transport_tools_application_info(self):
        raw_message = {
            'application': 'Transport Tools',
            'applInfo': json.dumps({'stdout': [{'line': 'test'}]})
        }
        pm = ProcessMessage(raw_message)
        appl_info = pm.appl_info
        self.assertIsInstance(appl_info, TransportToolsApplicationInfo)
        self.assertEqual(appl_info.json_object['stdout'], ['test'])

    def test_appl_info_returns_client_application_info(self):
        raw_message = {
            'application': 'Client',
            'applInfo': json.dumps([
                {
                    'type': 'Client Log',
                    'protocol': ['test log']
                }
            ])
        }
        pm = ProcessMessage(raw_message)
        appl_info = pm.appl_info
        self.assertIsInstance(appl_info, ClientApplicationInfo)

    def test_appl_info_is_cached(self):
        raw_message = {
            'application': 'gCTS',
            'applInfo': 'gCTS message'
        }
        pm = ProcessMessage(raw_message)
        first_call = pm.appl_info
        second_call = pm.appl_info
        self.assertIs(first_call, second_call)

    def test_appl_info_raises_on_unknown_application(self):
        raw_message = {
            'application': 'Unknown App',
            'applInfo': 'some info'
        }
        pm = ProcessMessage(raw_message)
        with self.assertRaises(SAPCliError) as cm:
            _ = pm.appl_info
        self.assertEqual(str(cm.exception), 'Unknown application type in process message: Unknown App')


class TestClientApplicationInfoErrors(unittest.TestCase):

    def test_raises_on_non_list_format(self):
        raw = json.dumps({'not': 'a list'})
        with self.assertRaises(SAPCliError) as cm:
            ClientApplicationInfo(raw)
        self.assertEqual(str(cm.exception), 'Invalid Client application info format')

    def test_raises_on_invalid_parameters_protocol_not_list(self):
        raw = json.dumps([
            {
                'type': 'Parameters',
                'protocol': 'not a list'
            }
        ])
        with self.assertRaises(SAPCliError) as cm:
            ClientApplicationInfo(raw)
        self.assertEqual(str(cm.exception), 'Invalid Client Parameters section format')

    def test_raises_on_invalid_parameters_protocol_wrong_length(self):
        raw = json.dumps([
            {
                'type': 'Parameters',
                'protocol': [json.dumps({'a': 1}), json.dumps({'b': 2})]
            }
        ])
        with self.assertRaises(SAPCliError) as cm:
            ClientApplicationInfo(raw)
        self.assertEqual(str(cm.exception), 'Invalid Client Parameters section format')

    def test_raises_on_invalid_parameters_protocol_empty(self):
        raw = json.dumps([
            {
                'type': 'Parameters',
                'protocol': []
            }
        ])
        with self.assertRaises(SAPCliError) as cm:
            ClientApplicationInfo(raw)
        self.assertEqual(str(cm.exception), 'Invalid Client Parameters section format')

    def test_raises_on_invalid_client_log_protocol_not_list(self):
        raw = json.dumps([
            {
                'type': 'Client Log',
                'protocol': 'not a list'
            }
        ])
        with self.assertRaises(SAPCliError) as cm:
            ClientApplicationInfo(raw)
        self.assertEqual(str(cm.exception), 'Invalid Client Log section format')

    def test_raises_on_invalid_client_response_protocol_not_list(self):
        raw = json.dumps([
            {
                'type': 'Client Response',
                'protocol': 'not a list'
            }
        ])
        with self.assertRaises(SAPCliError) as cm:
            ClientApplicationInfo(raw)
        self.assertEqual(str(cm.exception), 'Invalid Client Response section format')

    def test_raises_on_invalid_client_response_protocol_wrong_length(self):
        raw = json.dumps([
            {
                'type': 'Client Response',
                'protocol': [json.dumps({'log': []}), json.dumps({'log': []})]
            }
        ])
        with self.assertRaises(SAPCliError) as cm:
            ClientApplicationInfo(raw)
        self.assertEqual(str(cm.exception), 'Invalid Client Response section format')

    def test_raises_on_invalid_client_stack_log_protocol_not_list(self):
        raw = json.dumps([
            {
                'type': 'Client Stack Log',
                'protocol': 'not a list'
            }
        ])
        with self.assertRaises(SAPCliError) as cm:
            ClientApplicationInfo(raw)
        self.assertEqual(str(cm.exception), 'Invalid Client Response section format')

    def test_raises_on_invalid_client_stack_log_protocol_wrong_length(self):
        raw = json.dumps([
            {
                'type': 'Client Stack Log',
                'protocol': []
            }
        ])
        with self.assertRaises(SAPCliError) as cm:
            ClientApplicationInfo(raw)
        self.assertEqual(str(cm.exception), 'Invalid Client Response section format')

    def test_raises_on_unknown_section_type(self):
        raw = json.dumps([
            {
                'type': 'Unknown Section',
                'protocol': []
            }
        ])
        with self.assertRaises(SAPCliError) as cm:
            ClientApplicationInfo(raw)
        self.assertEqual(str(cm.exception), 'Unknown Client application info section type: Unknown Section')


class TestTransportToolsApplicationInfoErrors(unittest.TestCase):

    def test_raises_on_invalid_stdout_not_list(self):
        raw = json.dumps({'stdout': 'not a list'})
        with self.assertRaises(SAPCliError) as cm:
            TransportToolsApplicationInfo(raw)
        self.assertEqual(str(cm.exception), 'Invalid Transport Tools application info format')

    def test_raises_on_invalid_json(self):
        with self.assertRaises(json.JSONDecodeError):
            TransportToolsApplicationInfo('not valid json')


class TestClientApplicationInfoJsonErrors(unittest.TestCase):

    def test_raises_on_invalid_json(self):
        with self.assertRaises(json.JSONDecodeError):
            ClientApplicationInfo('not valid json')


class TestActionMessage(unittest.TestCase):

    def test_raises_on_processId_key_already_exists(self):
        raw_message = {
            'time': '2024-01-01T12:00:00',
            'caller': 'user',
            'processName': 'Clone',
            'status': 'success',
            'process': '12345',
            'processId': 'should-not-exist'
        }
        with self.assertRaises(SAPCliError) as cm:
            ActionMessage(raw_message)
        self.assertEqual(str(cm.exception), "Invalid action message format: 'processId' key already exists")

    def test_embedded_process(self):
        am = ActionMessage(GCTS_LOG_MESSAGES_DATA[0], raw_process_messages=GCTS_LOG_MESSAGES_PROCESS_CCC_DATA)

        exp_json = dict(GCTS_LOG_MESSAGES_JSON_EXP[0])
        exp_json['process'] = GCTS_LOG_MESSAGES_PROCESS_CCC_JSON_EXP

        self.assertEqual(am.json_object, exp_json)


if __name__ == '__main__':
    unittest.main()
