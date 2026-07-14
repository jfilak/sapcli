#!/usr/bin/env python3
'''CLI tests for sapcli srvb (Service Binding).'''

# pylint: disable=missing-function-docstring

import unittest
from unittest.mock import patch, Mock

import sap.adt.businessservice
import sap.cli.srvb
import sap.errors

from infra import generate_parse_args
from mock import (
    Connection,
    Response,
    ConsoleOutputTestCase,
    PatcherTestCase,
    patch_get_print_console_with_buffer,
)
from fixtures_adt_businessservice import (
    SERVICE_BINDING_NAME,
    SERVICE_BINDING_PACKAGE,
    SERVICE_BINDING_ADT_GET_V4_XML,
    SERVICE_BINDING_ADT_GET_V4_UITEST_XML,
    SERVICE_BINDING_PUBLISH_OK_XML,
    SERVICE_BINDING_UITEST_NAME,
    SERVICE_GROUP_ODATAV4_GET_XML,
    SERVICE_GROUP_ODATAV4_UITEST_GET_XML,
    SERVICE_GROUP_ODATAV2_GET_XML,
    SERVICE_GROUP_UITEST_ENCODEDPATHPARAMS,
    SERVICE_GROUP_UITEST_ENTITY_SET,
)


parse_args = generate_parse_args(sap.cli.srvb.CommandGroup())


class TestCommandGroup(unittest.TestCase):

    def test_cli_srvb_commands_constructor(self):
        sap.cli.srvb.CommandGroup()

    def test_cli_srvb_has_no_write_command(self):
        # SRVB v1 does not support source-text write because the binding has
        # no text/plain source body. Make this contract explicit.
        with self.assertRaises(SystemExit):
            parse_args('write', SERVICE_BINDING_NAME, '/dev/null')


class TestSRVBCreate(unittest.TestCase):

    @patch('sap.adt.ServiceBinding')
    def test_cli_srvb_create_with_odata_v4(self, fake_srvb):
        fake_conn = Mock()
        fake_conn.user = 'TESTER'
        fake_srvb.return_value = Mock()

        args = parse_args('create', SERVICE_BINDING_NAME,
                          'Test binding', SERVICE_BINDING_PACKAGE,
                          '--binding-type', 'ODATAV4_UI',
                          '--service-definition', 'ZSAPCLI_TEST_SRVD')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        self.assertEqual(fake_srvb.call_count, 1)
        kwargs = fake_srvb.call_args.kwargs
        self.assertEqual(kwargs['package'], SERVICE_BINDING_PACKAGE)
        self.assertEqual(kwargs['typ'], 'ODATA')
        self.assertEqual(kwargs['version'], 'V4')
        self.assertEqual(kwargs['category'], '0')

        fake_srvb.return_value.add_service.assert_called_once_with(SERVICE_BINDING_NAME, 'ZSAPCLI_TEST_SRVD', '0001')
        fake_srvb.return_value.create.assert_called_once_with(corrnr=None)

    @patch('sap.adt.ServiceBinding')
    def test_cli_srvb_create_with_odata_v2(self, fake_srvb):
        fake_conn = Mock()
        fake_conn.user = 'TESTER'
        fake_srvb.return_value = Mock()

        args = parse_args('create', SERVICE_BINDING_NAME,
                          'Test binding', SERVICE_BINDING_PACKAGE,
                          '--binding-type', 'ODATAV2_API',
                          '--service-definition', 'ZSAPCLI_TEST_SRVD')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        kwargs = fake_srvb.call_args.kwargs
        self.assertEqual(kwargs['version'], 'V2')
        self.assertEqual(kwargs['category'], '1')

    @patch('sap.adt.ServiceBinding')
    def test_cli_srvb_create_with_explicit_service_version(self, fake_srvb):
        fake_conn = Mock()
        fake_conn.user = 'TESTER'
        fake_srvb.return_value = Mock()

        args = parse_args('create', SERVICE_BINDING_NAME,
                          'Test binding', SERVICE_BINDING_PACKAGE,
                          '--binding-type', 'ODATAV4_API',
                          '--service-definition', 'ZSAPCLI_TEST_SRVD',
                          '--service-version', '0002')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        fake_srvb.return_value.add_service.call_args.assert_called_once_with(SERVICE_BINDING_NAME, 'ZSAPCLI_TEST_SRVD', '0002')


class TestSRVBRead(unittest.TestCase):

    def test_cli_srvb_read_prints_summary(self):
        conn = Connection([
            Response(text=SERVICE_BINDING_ADT_GET_V4_XML, status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.adt.businessservices.servicebinding.v2+xml; charset=utf-8'}),
            Response(text=SERVICE_GROUP_ODATAV4_GET_XML, status_code=200,
                    headers={'Content-Type':
                             'application/vnd.sap.adt.businessservices.odatav4.v2+xml; charset=utf-8'}),
        ])

        args = parse_args('read', SERVICE_BINDING_NAME)
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(conn, args)

        out = fake_console.capout
        self.assertEqual(out, '''Name        : ZSAPCLI_TEST_BND
Description : Test service binding
Package     : $TMP
Type        : ODATA
Version     : V4
Published   : false
Services:
  ZSAPCLI_TEST_BND (version 0001, NOT_RELEASED)
    URL: /sap/opu/odata4/sap/zscli_svcdemo_c/srvd/sap/zscli_svcdemo_c/0001/
    Entity Sets and Associations:
      Demo
      FourthDemo
''')


class TestSRVBActivate(unittest.TestCase):

    @patch('sap.adt.wb.try_activate')
    @patch('sap.adt.ServiceBinding')
    def test_cli_srvb_activate_defaults(self, fake_srvb, fake_activate):
        instances = []

        def add_instance(conn, name, package=None, metadata=None):
            srvb = Mock()
            srvb.name = name
            srvb.active = 'active'
            instances.append(srvb)
            return srvb

        fake_srvb.side_effect = add_instance
        fake_activate.return_value = (sap.adt.wb.CheckResults(), None)
        fake_conn = Mock()

        args = parse_args('activate', SERVICE_BINDING_NAME.lower())
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        fake_srvb.assert_called_once_with(fake_conn, SERVICE_BINDING_NAME, package=None, metadata=None)
        fake_activate.assert_called_once_with(instances[0])


class TestSRVBDelete(unittest.TestCase):

    @patch('sap.adt.ServiceBinding')
    def test_cli_srvb_delete_defaults(self, fake_srvb):
        srvb = Mock()
        fake_srvb.return_value = srvb
        fake_conn = Mock()

        args = parse_args('delete', SERVICE_BINDING_NAME)
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        fake_srvb.assert_called_once_with(fake_conn, SERVICE_BINDING_NAME, package=None, metadata=None)
        srvb.delete.assert_called_once_with(corrnr=None)


class TestSRVBWhereUsed(unittest.TestCase):

    @patch('sap.adt.whereused.where_used')
    @patch('sap.adt.ServiceBinding')
    def test_cli_srvb_whereused_defaults(self, fake_srvb, fake_where_used):
        fake_conn = Mock()
        srvb = Mock()
        srvb.full_adt_uri = '/sap/bc/adt/businessservices/bindings/zsapcli_test_bnd'
        fake_srvb.return_value = srvb

        result = Mock()
        result.referenced_objects = []
        fake_where_used.return_value = result

        args = parse_args('whereused', SERVICE_BINDING_NAME)
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        fake_where_used.assert_called_once_with(
            fake_conn, '/sap/bc/adt/businessservices/bindings/zsapcli_test_bnd')


class TestSRVBPublish(ConsoleOutputTestCase, PatcherTestCase):
    '''Test sapcli srvb publish'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        PatcherTestCase.unpatch_all(self)

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        self.connection = Mock()
        self.param_version = '0001'
        self.param_service = 'ZSAPCLI_TEST_SRV'
        self.param_binding_name = SERVICE_BINDING_NAME

        self.patch_console(console=self.console)
        self.binding_patch = self.patch('sap.adt.ServiceBinding')

        self.service = Mock()
        self.service.definition = Mock()
        self.service.definition.name = self.param_service
        self.service.name = SERVICE_BINDING_NAME
        self.service.version = self.param_version

        self.publish_status = sap.adt.businessservice.StatusMessage()

        self.binding_inst = self.binding_patch.return_value
        self.binding_inst.find_service = Mock(return_value=self.service)
        self.binding_inst.publish = Mock(return_value=self.publish_status)
        self.binding_inst.services = [self.service]

    def execute_publish(self, *extra):
        args = parse_args('publish', self.param_binding_name, *extra)
        return args.execute(self.connection, args)

    def test_publish_single_service_default_ok(self):
        self.publish_status.SEVERITY = 'OK'
        self.publish_status.SHORT_TEXT = 'Service published successfully'

        self.execute_publish()

        self.binding_inst.fetch.assert_called_once_with()
        self.binding_inst.publish.assert_called_once_with(self.service)
        self.assertConsoleContents(
            console=self.console,
            stdout=(f'Publishing:\n'
                    f'* {self.param_service} {SERVICE_BINDING_NAME} {self.param_version}\n'
                    f'Service published successfully\n'))

    def test_publish_with_service_filter(self):
        self.publish_status.SEVERITY = 'OK'
        self.publish_status.SHORT_TEXT = 'OK'

        self.execute_publish('--service', self.param_service)

        self.binding_inst.find_service.assert_called_once_with(self.param_service, None)
        self.binding_inst.publish.assert_called_once_with(self.service)

    def test_publish_with_service_and_version(self):
        self.publish_status.SEVERITY = 'OK'
        self.publish_status.SHORT_TEXT = 'OK'

        self.execute_publish('--service', self.param_service, '--version', self.param_version)

        self.binding_inst.find_service.assert_called_once_with(self.param_service, self.param_version)
        self.binding_inst.publish.assert_called_once_with(self.service)

    def test_publish_no_services_errors(self):
        self.binding_inst.services = []

        exitcode = self.execute_publish()

        self.binding_inst.publish.assert_not_called()
        self.assertEqual(exitcode, 1)
        self.assertIn('does not contain any services', self.console.caperr)

    def test_publish_too_many_services_without_filter_errors(self):
        self.binding_inst.services = [Mock(), Mock()]

        exitcode = self.execute_publish()

        self.binding_inst.publish.assert_not_called()
        self.assertEqual(exitcode, 1)
        self.assertIn('without', self.console.caperr)

    def test_publish_service_not_found_errors(self):
        self.binding_inst.find_service.return_value = None

        exitcode = self.execute_publish('--service', self.param_service, '--version', self.param_version)

        self.binding_inst.publish.assert_not_called()
        self.assertEqual(exitcode, 1)
        self.assertIn('has no Service Definition', self.console.caperr)

    def test_publish_severity_not_ok_returns_1(self):
        self.publish_status.SEVERITY = 'ERROR'
        self.publish_status.SHORT_TEXT = 'Local Publish failed'

        exitcode = self.execute_publish()

        self.assertEqual(exitcode, 1)
        self.assertIn('Failed to publish', self.console.caperr)

    def test_publish_url_uses_lowercase_name(self):
        # The CLI delegates to ServiceBinding.publish() which builds the URL
        # via self.objtype.basepath + .lower(name); we just assert the
        # ServiceBinding constructor was called with the user-provided name
        # (uppercased per CLI convention) so the URL builder gets the right
        # input.
        self.publish_status.SEVERITY = 'OK'
        self.publish_status.SHORT_TEXT = 'OK'

        self.execute_publish()

        # First positional arg = connection, second = binding name (uppercased
        # by the CLI adapter).
        positional = self.binding_patch.call_args.args
        self.assertEqual(positional[0], self.connection)
        self.assertEqual(positional[1], self.param_binding_name)


class TestSRVBUnpublish(ConsoleOutputTestCase, PatcherTestCase):
    '''Test sapcli srvb unpublish'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        PatcherTestCase.unpatch_all(self)

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        self.connection = Mock()
        self.param_version = '0001'
        self.param_service = 'ZSAPCLI_TEST_SRV'
        self.param_binding_name = SERVICE_BINDING_NAME

        self.patch_console(console=self.console)
        self.binding_patch = self.patch('sap.adt.ServiceBinding')
        self.try_activate = self.patch('sap.adt.wb.try_activate')
        self.try_activate.return_value = (sap.adt.wb.CheckResults(), None)

        self.service = Mock()
        self.service.definition = Mock()
        self.service.definition.name = self.param_service
        self.service.name = SERVICE_BINDING_NAME
        self.service.version = self.param_version

        self.unpublish_status = sap.adt.businessservice.StatusMessage()

        self.binding_inst = self.binding_patch.return_value
        self.binding_inst.name = self.param_binding_name
        self.binding_inst.active = 'active'
        self.binding_inst.find_service = Mock(return_value=self.service)
        self.binding_inst.unpublish = Mock(return_value=self.unpublish_status)
        self.binding_inst.services = [self.service]

    def execute_unpublish(self, *extra):
        args = parse_args('unpublish', self.param_binding_name, *extra)
        return args.execute(self.connection, args)

    def test_unpublish_single_service_default_ok(self):
        self.unpublish_status.SEVERITY = 'OK'
        self.unpublish_status.SHORT_TEXT = 'Service unpublished successfully'

        self.execute_unpublish()

        self.binding_inst.fetch.assert_called_once_with()
        self.binding_inst.unpublish.assert_called_once_with(self.service)
        self.try_activate.assert_not_called()
        self.assertConsoleContents(
            console=self.console,
            stdout=(f'Unpublishing:\n'
                    f'* {self.param_service} {SERVICE_BINDING_NAME} {self.param_version}\n'
                    f'Service unpublished successfully\n'))

    def test_unpublish_with_service_filter(self):
        self.unpublish_status.SEVERITY = 'OK'
        self.unpublish_status.SHORT_TEXT = 'OK'

        self.execute_unpublish('--service', self.param_service)

        self.binding_inst.find_service.assert_called_once_with(self.param_service, None)
        self.binding_inst.unpublish.assert_called_once_with(self.service)

    def test_unpublish_with_service_and_version(self):
        self.unpublish_status.SEVERITY = 'OK'
        self.unpublish_status.SHORT_TEXT = 'OK'

        self.execute_unpublish('--service', self.param_service, '--version', self.param_version)

        self.binding_inst.find_service.assert_called_once_with(self.param_service, self.param_version)
        self.binding_inst.unpublish.assert_called_once_with(self.service)

    def test_unpublish_no_services_errors(self):
        self.binding_inst.services = []

        exitcode = self.execute_unpublish()

        self.binding_inst.unpublish.assert_not_called()
        self.assertEqual(exitcode, 1)
        self.assertIn('does not contain any services', self.console.caperr)

    def test_unpublish_too_many_services_without_filter_errors(self):
        self.binding_inst.services = [Mock(), Mock()]

        exitcode = self.execute_unpublish()

        self.binding_inst.unpublish.assert_not_called()
        self.assertEqual(exitcode, 1)
        self.assertIn('without', self.console.caperr)

    def test_unpublish_service_not_found_errors(self):
        self.binding_inst.find_service.return_value = None

        exitcode = self.execute_unpublish('--service', self.param_service, '--version', self.param_version)

        self.binding_inst.unpublish.assert_not_called()
        self.assertEqual(exitcode, 1)
        self.assertIn('has no Service Definition', self.console.caperr)

    def test_unpublish_severity_not_ok_returns_1(self):
        self.unpublish_status.SEVERITY = 'ERROR'
        self.unpublish_status.SHORT_TEXT = 'Local Unpublish failed'

        exitcode = self.execute_unpublish('--activate')

        self.assertEqual(exitcode, 1)
        self.assertIn('Failed to unpublish', self.console.caperr)
        # A failed unpublish must never trigger activation.
        self.try_activate.assert_not_called()

    def test_unpublish_with_activate_long_flag_runs_activation(self):
        self.unpublish_status.SEVERITY = 'OK'
        self.unpublish_status.SHORT_TEXT = 'OK'

        exitcode = self.execute_unpublish('--activate')

        self.binding_inst.unpublish.assert_called_once_with(self.service)
        self.try_activate.assert_called_once_with(self.binding_inst)
        self.assertEqual(exitcode, 0)
        self.assertIn('Activation has finished', self.console.capout)

    def test_unpublish_with_activate_short_flag_runs_activation(self):
        self.unpublish_status.SEVERITY = 'OK'
        self.unpublish_status.SHORT_TEXT = 'OK'

        exitcode = self.execute_unpublish('-a')

        self.try_activate.assert_called_once_with(self.binding_inst)
        self.assertEqual(exitcode, 0)

    def test_unpublish_activate_failure_returns_1(self):
        self.unpublish_status.SEVERITY = 'OK'
        self.unpublish_status.SHORT_TEXT = 'OK'
        # A binding that stays inactive after activation is reported as a
        # failure by activate_object_list.
        self.binding_inst.active = 'inactive'

        exitcode = self.execute_unpublish('--activate')

        self.try_activate.assert_called_once_with(self.binding_inst)
        self.assertEqual(exitcode, 1)
        self.assertIn('Inactive objects:', self.console.capout)

    def test_unpublish_activate_forwards_error_flags_to_worker(self):
        self.unpublish_status.SEVERITY = 'OK'
        self.unpublish_status.SHORT_TEXT = 'OK'

        with patch('sap.cli.object.activate_object_list', return_value=0) as fake_activate_list:
            exitcode = self.execute_unpublish('--activate', '--ignore-errors', '--warning-errors')

        self.assertEqual(exitcode, 0)
        fake_activate_list.assert_called_once()
        worker, object_list, count, _console = fake_activate_list.call_args.args
        self.assertTrue(worker.continue_on_errors)
        self.assertTrue(worker.warnings_as_errors)
        self.assertEqual(object_list, [(self.binding_inst.name, self.binding_inst)])
        self.assertEqual(count, 1)


class TestSRVBUnpublishHttp(unittest.TestCase):
    '''Ensures sapcli srvb unpublish issues the expected HTTP calls end-to-end.'''

    def test_unpublish_v4_with_activate_sends_all_requests(self):
        binding_lower = SERVICE_BINDING_NAME.lower()

        conn = Connection([
            # GET the binding (binding.fetch())
            Response(text=SERVICE_BINDING_ADT_GET_V4_XML, status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.adt.businessservices.servicebinding.v2+xml; charset=utf-8'}),
            # POST unpublishjobs
            Response(text=SERVICE_BINDING_PUBLISH_OK_XML, status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.as+xml; charset=utf-8; '
                              'dataname=com.sap.adt.StatusMessage'}),
            # POST activation
            Response(text='', status_code=200, headers={'Content-Type': 'text/plain'}),
            # GET re-fetch performed by try_activate
            Response(text=SERVICE_BINDING_ADT_GET_V4_XML, status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.adt.businessservices.servicebinding.v2+xml; charset=utf-8'}),
        ])

        args = parse_args('unpublish', SERVICE_BINDING_NAME, '--activate')
        with patch_get_print_console_with_buffer():
            exitcode = args.execute(conn, args)

        self.assertEqual(exitcode, 0)
        self.assertEqual(conn.mock_methods(), [
            ('GET', f'/sap/bc/adt/businessservices/bindings/{binding_lower}'),
            ('POST', '/sap/bc/adt/businessservices/odatav4/unpublishjobs'),
            ('POST', '/sap/bc/adt/activation'),
            ('GET', f'/sap/bc/adt/businessservices/bindings/{binding_lower}'),
        ])

    def test_unpublish_v4_without_activate_skips_activation(self):
        binding_lower = SERVICE_BINDING_NAME.lower()

        conn = Connection([
            Response(text=SERVICE_BINDING_ADT_GET_V4_XML, status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.adt.businessservices.servicebinding.v2+xml; charset=utf-8'}),
            Response(text=SERVICE_BINDING_PUBLISH_OK_XML, status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.as+xml; charset=utf-8; '
                              'dataname=com.sap.adt.StatusMessage'}),
        ])

        args = parse_args('unpublish', SERVICE_BINDING_NAME)
        with patch_get_print_console_with_buffer():
            exitcode = args.execute(conn, args)

        self.assertEqual(exitcode, 0)
        self.assertEqual(conn.mock_methods(), [
            ('GET', f'/sap/bc/adt/businessservices/bindings/{binding_lower}'),
            ('POST', '/sap/bc/adt/businessservices/odatav4/unpublishjobs'),
        ])


class TestSRVBPreviewHtml(unittest.TestCase):
    '''sapcli srvb preview html'''

    def test_preview_html_v4_sends_expected_request(self):
        binding_lower = SERVICE_BINDING_UITEST_NAME.lower()
        html_body = '<html><body>preview</body></html>'

        conn = Connection([
            Response(text=SERVICE_BINDING_ADT_GET_V4_UITEST_XML, status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.adt.businessservices.servicebinding.v2+xml; charset=utf-8'}),
            Response(text=SERVICE_GROUP_ODATAV4_UITEST_GET_XML, status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.adt.businessservices.odatav4.v2+xml; charset=utf-8'}),
            Response(text=html_body, status_code=200,
                     headers={'Content-Type': 'text/html; charset=utf-8'}),
        ])

        args = parse_args('preview', 'html',
                          SERVICE_BINDING_UITEST_NAME,
                          SERVICE_GROUP_UITEST_ENTITY_SET)
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(conn, args)

        self.assertEqual(len(conn.execs), 3)

        binding_fetch = conn.execs[0]
        self.assertEqual(binding_fetch.method, 'GET')
        self.assertEqual(
            binding_fetch.adt_uri,
            f'/sap/bc/adt/businessservices/bindings/{binding_lower}',
        )

        service_group_get = conn.execs[1]
        self.assertEqual(service_group_get.method, 'GET')
        self.assertEqual(
            service_group_get.adt_uri,
            f'/sap/bc/adt/businessservices/odatav4/{SERVICE_BINDING_UITEST_NAME}',
        )

        preview_request = conn.execs[2]
        self.assertEqual(preview_request.method, 'GET')
        self.assertEqual(
            preview_request.adt_uri,
            f'/sap/bc/adt/businessservices/odatav4/feap/'
            f'{SERVICE_GROUP_UITEST_ENCODEDPATHPARAMS}/flp.html',
        )
        self.assertEqual(preview_request.params, {
            'sap-ui-xx-viewCache': 'false',
            'sap-ui-language': 'EN',
            'sap-client': 'mockclient',
        })

        self.assertEqual(fake_console.capout, html_body + '\n')

    def test_preview_html_v2_raises(self):
        # For OData V2 bindings the encoded-path preview endpoint is not yet
        # implemented; the CLI must surface a friendly SAPCliError instead of
        # silently issuing a broken request.
        conn = Connection([
            Response(text=SERVICE_BINDING_ADT_GET_V4_UITEST_XML.replace(
                'srvb:version="V4"', 'srvb:version="V2"'),
                     status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.adt.businessservices.servicebinding.v2+xml; charset=utf-8'}),
            Response(text=SERVICE_GROUP_ODATAV2_GET_XML, status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.adt.businessservices.odatav2.v3+xml; charset=utf-8'}),
        ])

        args = parse_args('preview', 'html',
                          SERVICE_BINDING_UITEST_NAME,
                          SERVICE_GROUP_UITEST_ENTITY_SET)
        with patch_get_print_console_with_buffer():
            with self.assertRaises(sap.errors.SAPCliError) as ctx:
                args.execute(conn, args)

        self.assertIn('V4', str(ctx.exception))

        # No HTTP request beyond fetching the binding and its service group
        # should have been issued.
        self.assertEqual(len(conn.execs), 2)

    def test_preview_html_open_launches_browser(self):
        conn = Connection([
            Response(text=SERVICE_BINDING_ADT_GET_V4_UITEST_XML, status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.adt.businessservices.servicebinding.v2+xml; charset=utf-8'}),
            Response(text=SERVICE_GROUP_ODATAV4_UITEST_GET_XML, status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.adt.businessservices.odatav4.v2+xml; charset=utf-8'}),
        ])

        args = parse_args('preview', 'html',
                          SERVICE_BINDING_UITEST_NAME,
                          SERVICE_GROUP_UITEST_ENTITY_SET,
                          '--open')

        with patch('sap.cli.srvb.webbrowser.open') as fake_open:
            with patch_get_print_console_with_buffer() as fake_console:
                args.execute(conn, args)

        # With --open only the binding + service group are fetched; the
        # HTML page itself is opened in the browser, not retrieved via HTTP.
        self.assertEqual(len(conn.execs), 2)

        expected_url = (
            f'https://mockhost:443/sap/bc/adt/businessservices/odatav4/feap/'
            f'{SERVICE_GROUP_UITEST_ENCODEDPATHPARAMS}/flp.html'
            f'?sap-ui-xx-viewCache=false&sap-ui-language=EN&sap-client=mockclient'
            f'#app-preview'
        )
        fake_open.assert_called_once_with(expected_url)

        # Nothing is printed to stdout when --open is used.
        self.assertEqual(fake_console.capout, '')

    def test_preview_html_open_v2_raises_before_launching_browser(self):
        conn = Connection([
            Response(text=SERVICE_BINDING_ADT_GET_V4_UITEST_XML.replace(
                'srvb:version="V4"', 'srvb:version="V2"'),
                     status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.adt.businessservices.servicebinding.v2+xml; charset=utf-8'}),
            Response(text=SERVICE_GROUP_ODATAV2_GET_XML, status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.adt.businessservices.odatav2.v3+xml; charset=utf-8'}),
        ])

        args = parse_args('preview', 'html',
                          SERVICE_BINDING_UITEST_NAME,
                          SERVICE_GROUP_UITEST_ENTITY_SET,
                          '--open')

        with patch('sap.cli.srvb.webbrowser.open') as fake_open:
            with patch_get_print_console_with_buffer():
                with self.assertRaises(sap.errors.SAPCliError):
                    args.execute(conn, args)

        fake_open.assert_not_called()


if __name__ == '__main__':
    unittest.main()
