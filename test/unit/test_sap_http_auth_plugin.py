#!/usr/bin/env python3

import json
import subprocess
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from sap.errors import SAPCliError
from sap.http.auth_plugin import (
    AuthPluginError,
    AuthPluginRequest,
    AuthPluginResponse,
    ConnectionInfo,
    run_plugin,
)


def _connection():
    return ConnectionInfo(
        proto='https',
        ashost='abap.example.org',
        port='44300',
        client='100',
        type='adt',
        path='/sap/bc/adt/core/systeminformation',
    )


def _completed_process(stdout='', stderr='', returncode=0):
    return subprocess.CompletedProcess(
        args=['plugin'],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


class TestConnectionInfo(unittest.TestCase):

    def test_to_dict_emits_all_fields(self):
        ci = _connection()

        self.assertEqual(ci.to_dict(), {
            'proto': 'https',
            'ashost': 'abap.example.org',
            'port': '44300',
            'client': '100',
            'type': 'adt',
            'path': '/sap/bc/adt/core/systeminformation',
            'sysnr': None,
            'verify': True,
            'ssl_server_cert': None,
        })

    def test_verify_defaults_to_true(self):
        # Safe default. Forwarded explicitly by sapcli when the user has
        # ssl_verify: false, so plugins do not need to read SAP_SSL_VERIFY
        # from env.
        self.assertIs(_connection().verify, True)
        self.assertIsNone(_connection().ssl_server_cert)

    def test_sysnr_defaults_to_none(self):
        # sysnr is only meaningful for RFC-based plugins; HTTP plugins can
        # ignore it. Defaulting to None keeps construction noise-free for
        # the common HTTP case.
        ci = _connection()

        self.assertIsNone(ci.sysnr)

    def test_to_dict_includes_sysnr_when_set(self):
        ci = ConnectionInfo(
            proto='https',
            ashost='abap.example.org',
            port='44300',
            client='100',
            type='adt',
            path='/sap/bc/adt/core/systeminformation',
            sysnr='00',
        )

        self.assertEqual(ci.to_dict()['sysnr'], '00')


class TestAuthPluginRequest(unittest.TestCase):

    def test_to_dict_nests_connection_and_parameters(self):
        request = AuthPluginRequest(
            connection=ConnectionInfo(
                proto='https',
                ashost='abap.example.org',
                port='44300',
                client='100',
                type='adt',
                path='/sap/bc/adt/core/systeminformation',
                sysnr='00',
            ),
            parameters={'channel': 'msedge'},
        )

        self.assertEqual(request.to_dict(), {
            'connection': {
                'proto': 'https',
                'ashost': 'abap.example.org',
                'port': '44300',
                'client': '100',
                'type': 'adt',
                'path': '/sap/bc/adt/core/systeminformation',
                'sysnr': '00',
                'verify': True,
                'ssl_server_cert': None,
            },
            'parameters': {'channel': 'msedge'},
        })

    def test_to_json_round_trips_through_to_dict(self):
        request = AuthPluginRequest(
            connection=_connection(),
            parameters={'channel': 'msedge'},
        )

        self.assertEqual(json.loads(request.to_json()), request.to_dict())

    def test_to_dict_with_empty_parameters(self):
        request = AuthPluginRequest(connection=_connection(), parameters={})

        self.assertEqual(request.to_dict()['parameters'], {})


class TestAuthPluginResponseFromDict(unittest.TestCase):

    def test_minimal_required_fields(self):
        response = AuthPluginResponse.from_dict({
            'message': 'OK',
            'content': {'type': 'cookie', 'cookies': []},
        })

        self.assertEqual(response.message, 'OK')
        self.assertEqual(response.content, {'type': 'cookie', 'cookies': []})
        self.assertIsNone(response.expiration)

    def test_parses_iso_expiration_with_z_suffix(self):
        response = AuthPluginResponse.from_dict({
            'message': 'OK',
            'content': {'type': 'cookie', 'cookies': []},
            'expiration': '2024-12-31T23:59:59Z',
        })

        self.assertEqual(
            response.expiration,
            datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        )

    def test_parses_iso_expiration_with_offset(self):
        response = AuthPluginResponse.from_dict({
            'message': 'OK',
            'content': {'type': 'cookie', 'cookies': []},
            'expiration': '2024-12-31T23:59:59+00:00',
        })

        self.assertEqual(
            response.expiration,
            datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        )

    def test_null_expiration_yields_none(self):
        response = AuthPluginResponse.from_dict({
            'message': 'OK',
            'content': {'type': 'cookie', 'cookies': []},
            'expiration': None,
        })

        self.assertIsNone(response.expiration)

    def test_empty_string_expiration_yields_none(self):
        response = AuthPluginResponse.from_dict({
            'message': 'OK',
            'content': {'type': 'cookie', 'cookies': []},
            'expiration': '',
        })

        self.assertIsNone(response.expiration)

    def test_missing_message_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            AuthPluginResponse.from_dict({
                'content': {'type': 'cookie', 'cookies': []},
            })

        self.assertIn('message', str(ctx.exception))

    def test_missing_content_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            AuthPluginResponse.from_dict({'message': 'OK'})

        self.assertIn('content', str(ctx.exception))

    def test_non_mapping_input_raises_value_error(self):
        with self.assertRaises(ValueError):
            AuthPluginResponse.from_dict(['not', 'a', 'mapping'])

    def test_invalid_expiration_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            AuthPluginResponse.from_dict({
                'message': 'OK',
                'content': {'type': 'cookie', 'cookies': []},
                'expiration': 'not-a-date',
            })


class TestAuthPluginResponseFromJSON(unittest.TestCase):

    def test_parses_json_string(self):
        raw = json.dumps({
            'message': 'OK',
            'content': {'type': 'cookie', 'cookies': []},
        })

        response = AuthPluginResponse.from_json(raw)

        self.assertEqual(response.message, 'OK')

    def test_invalid_json_raises_value_error(self):
        with self.assertRaises(ValueError):
            AuthPluginResponse.from_json('this is not json')


class TestAuthPluginResponseSerialize(unittest.TestCase):

    def test_to_dict_no_expiration_omits_field(self):
        response = AuthPluginResponse(message='ok', content={'type': 'cookie'})

        self.assertEqual(response.to_dict(), {
            'message': 'ok',
            'content': {'type': 'cookie'},
        })

    def test_to_dict_with_expiration_emits_iso_utc(self):
        response = AuthPluginResponse(
            message='ok',
            content={'type': 'cookie'},
            expiration=datetime(2026, 5, 8, 12, 30, tzinfo=timezone.utc),
        )

        self.assertEqual(response.to_dict()['expiration'], '2026-05-08T12:30:00+00:00')

    def test_to_dict_normalizes_naive_datetime_to_utc(self):
        # Naive datetimes are interpreted as UTC. Better than crashing or
        # silently treating them as local time, which would round-trip
        # differently in different timezones.
        response = AuthPluginResponse(
            message='ok',
            content={'type': 'cookie'},
            expiration=datetime(2026, 5, 8, 12, 30),
        )

        self.assertTrue(response.to_dict()['expiration'].endswith('+00:00'))

    def test_to_json_round_trips_through_from_json(self):
        response = AuthPluginResponse(
            message='ok',
            content={'type': 'cookie', 'cookies': [{'name': 'X', 'value': 'y'}]},
            expiration=datetime(2026, 5, 8, 12, 30, tzinfo=timezone.utc),
        )

        restored = AuthPluginResponse.from_json(response.to_json())

        self.assertEqual(restored.message, response.message)
        self.assertEqual(restored.content, response.content)
        self.assertEqual(restored.expiration, response.expiration)

    def test_to_json_without_expiration_round_trips(self):
        response = AuthPluginResponse(message='ok', content={'type': 'cookie'})

        restored = AuthPluginResponse.from_json(response.to_json())

        self.assertEqual(restored, response)


class TestAuthPluginResponseIsExpired(unittest.TestCase):

    def test_no_expiration_means_never_expired(self):
        # Spec lets sapcli choose; we mirror Token.is_expired semantics so
        # plugins that omit expiration get cached indefinitely (which is
        # what most session-cookie plugins want - the server invalidates).
        response = AuthPluginResponse(message='ok', content={})

        self.assertFalse(response.is_expired())

    def test_future_expiration_not_expired(self):
        future = datetime.now(timezone.utc) + timedelta(hours=1)
        response = AuthPluginResponse(
            message='ok', content={}, expiration=future,
        )

        self.assertFalse(response.is_expired())

    def test_past_expiration_is_expired(self):
        past = datetime.now(timezone.utc) - timedelta(seconds=1)
        response = AuthPluginResponse(
            message='ok', content={}, expiration=past,
        )

        self.assertTrue(response.is_expired())

    def test_within_leeway_is_expired(self):
        # Refresh slightly early to avoid races where the token expires
        # mid-flight between our check and the server's validation.
        soon = datetime.now(timezone.utc) + timedelta(seconds=10)
        response = AuthPluginResponse(
            message='ok', content={}, expiration=soon,
        )

        self.assertTrue(response.is_expired(leeway_seconds=30))
        self.assertFalse(response.is_expired(leeway_seconds=5))


class TestAuthPluginError(unittest.TestCase):

    def test_inherits_from_sapclierror(self):
        # CLI entry point relies on SAPCliError to print a friendly message
        # instead of a stack trace - a non-SAPCliError would regress that.
        self.assertTrue(issubclass(AuthPluginError, SAPCliError))


class TestRunPluginSubprocessInvocation(unittest.TestCase):

    @patch('sap.http.auth_plugin.subprocess.run')
    def test_invokes_command_as_argv(self, mock_run):
        mock_run.return_value = _completed_process(
            stdout=json.dumps({
                'message': 'OK',
                'content': {'type': 'cookie', 'cookies': []},
            }),
        )

        run_plugin('my-plugin', {'channel': 'msedge'}, _connection())

        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ['my-plugin'])

    @patch('sap.http.auth_plugin.subprocess.run')
    def test_writes_request_json_to_stdin(self, mock_run):
        mock_run.return_value = _completed_process(
            stdout=json.dumps({
                'message': 'OK',
                'content': {'type': 'cookie', 'cookies': []},
            }),
        )

        run_plugin('my-plugin', {'channel': 'msedge'}, _connection())

        kwargs = mock_run.call_args.kwargs
        sent = json.loads(kwargs['input'])
        self.assertEqual(sent, {
            'connection': _connection().to_dict(),
            'parameters': {'channel': 'msedge'},
        })

    @patch('sap.http.auth_plugin.subprocess.run')
    def test_captures_output_as_text_utf8(self, mock_run):
        mock_run.return_value = _completed_process(
            stdout=json.dumps({
                'message': 'OK',
                'content': {'type': 'cookie', 'cookies': []},
            }),
        )

        run_plugin('my-plugin', {}, _connection())

        kwargs = mock_run.call_args.kwargs
        self.assertTrue(kwargs.get('capture_output'))
        # Pass encoding so binary output isn't returned and the stdout/stderr
        # payloads we surface in errors are real strings.
        self.assertEqual(kwargs.get('encoding'), 'utf-8')

    @patch('sap.http.auth_plugin.subprocess.run')
    def test_does_not_pass_check_kwarg(self, mock_run):
        # check=True would convert non-zero exit into CalledProcessError before
        # we get a chance to wrap it; we want to handle the exit code ourselves.
        mock_run.return_value = _completed_process(
            stdout=json.dumps({
                'message': 'OK',
                'content': {'type': 'cookie', 'cookies': []},
            }),
        )

        run_plugin('my-plugin', {}, _connection())

        kwargs = mock_run.call_args.kwargs
        self.assertFalse(kwargs.get('check', False))

    @patch('sap.http.auth_plugin.subprocess.run')
    def test_does_not_set_timeout(self, mock_run):
        # Auth plugins may legitimately wait for the user to log in via a
        # browser; a default timeout would kill them mid-login.
        mock_run.return_value = _completed_process(
            stdout=json.dumps({
                'message': 'OK',
                'content': {'type': 'cookie', 'cookies': []},
            }),
        )

        run_plugin('my-plugin', {}, _connection())

        kwargs = mock_run.call_args.kwargs
        self.assertIsNone(kwargs.get('timeout'))


class TestRunPluginSuccess(unittest.TestCase):

    @patch('sap.http.auth_plugin.subprocess.run')
    def test_returns_parsed_response(self, mock_run):
        mock_run.return_value = _completed_process(
            stdout=json.dumps({
                'message': 'Authentication successful',
                'content': {
                    'type': 'cookie',
                    'cookies': [{'name': 'SAP_SESSION', 'value': 'abc'}],
                },
                'expiration': '2025-01-01T00:00:00Z',
            }),
        )

        response = run_plugin('my-plugin', {}, _connection())

        self.assertEqual(response.message, 'Authentication successful')
        self.assertEqual(response.content['type'], 'cookie')
        self.assertEqual(
            response.expiration,
            datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        )

    @patch('sap.http.auth_plugin.subprocess.run')
    def test_accepts_none_parameters(self, mock_run):
        mock_run.return_value = _completed_process(
            stdout=json.dumps({
                'message': 'OK',
                'content': {'type': 'cookie', 'cookies': []},
            }),
        )

        run_plugin('my-plugin', None, _connection())

        sent = json.loads(mock_run.call_args.kwargs['input'])
        self.assertEqual(sent['parameters'], {})


class TestRunPluginFailures(unittest.TestCase):

    @patch('sap.http.auth_plugin.subprocess.run')
    def test_file_not_found_raises_auth_plugin_error(self, mock_run):
        mock_run.side_effect = FileNotFoundError(2, 'No such file', 'missing-plugin')

        with self.assertRaises(AuthPluginError) as ctx:
            run_plugin('missing-plugin', {}, _connection())

        self.assertIn('missing-plugin', str(ctx.exception))

    @patch('sap.http.auth_plugin.subprocess.run')
    def test_permission_error_raises_auth_plugin_error(self, mock_run):
        mock_run.side_effect = PermissionError(13, 'Permission denied', 'plugin')

        with self.assertRaises(AuthPluginError):
            run_plugin('plugin', {}, _connection())

    @patch('sap.http.auth_plugin.subprocess.run')
    def test_non_zero_exit_raises_with_stderr_in_message(self, mock_run):
        mock_run.return_value = _completed_process(
            stdout='partial output',
            stderr='browser launch failed',
            returncode=2,
        )

        with self.assertRaises(AuthPluginError) as ctx:
            run_plugin('my-plugin', {}, _connection())

        message = str(ctx.exception)
        self.assertIn('2', message)
        self.assertIn('browser launch failed', message)
        self.assertIn('partial output', message)

    @patch('sap.http.auth_plugin.subprocess.run')
    def test_invalid_json_raises_with_stdout_in_message(self, mock_run):
        mock_run.return_value = _completed_process(stdout='not json at all')

        with self.assertRaises(AuthPluginError) as ctx:
            run_plugin('my-plugin', {}, _connection())

        self.assertIn('not json at all', str(ctx.exception))

    @patch('sap.http.auth_plugin.subprocess.run')
    def test_missing_required_field_raises(self, mock_run):
        mock_run.return_value = _completed_process(
            stdout=json.dumps({'message': 'OK'}),  # missing 'content'
        )

        with self.assertRaises(AuthPluginError) as ctx:
            run_plugin('my-plugin', {}, _connection())

        self.assertIn('content', str(ctx.exception))

    @patch('sap.http.auth_plugin.subprocess.run')
    def test_response_is_array_not_object_raises(self, mock_run):
        mock_run.return_value = _completed_process(stdout=json.dumps(['oops']))

        with self.assertRaises(AuthPluginError):
            run_plugin('my-plugin', {}, _connection())


if __name__ == '__main__':
    unittest.main()
