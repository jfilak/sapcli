'''oData service CLI tests.'''

# !/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

from unittest.mock import Mock, patch

from mock import (
    ConsoleOutputTestCase,
    PatcherTestCase
)

import sap.cli.rap

from infra import generate_parse_args

from mock import Connection, Response, Request
from fixtures_adt_wb import RESPONSE_ACTIVATION_OK
from fixtures_adt_businessservice import SERVICE_DEFINITION_ADT_XML

parse_args = generate_parse_args(sap.cli.rap.CommandGroup())

# Single source of truth for the deprecation warning text - kept in sync with
# `sap/cli/rap.py::_deprecation_warning`.
DEPRECATION_PUBLISH = (
    'WARNING: `sapcli rap binding publish` is deprecated; use `sapcli srvb '
    'publish`. This alias will be removed in the next minor release.\n'
)

DEPRECATION_DEFINITION_ACTIVATE = (
    'WARNING: `sapcli rap definition activate` is deprecated; use `sapcli '
    'srvd activate`. This alias will be removed in the next minor release.\n'
)


class TestRapBindingPublish(ConsoleOutputTestCase, PatcherTestCase):
    '''Test rap binding Publish command'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None

        self.connection = Mock()

        self.param_version = '1234'
        self.param_service = 'SRVD_NAME'
        self.param_binding_name = 'SRVB_NAME'

        self.patch_console(console=self.console)
        # `rap binding publish` now delegates to `sap.cli.srvb.publish_binding`
        # which constructs the binding via `sap.adt.ServiceBinding(...)`. Patch
        # the module attribute the new code path actually resolves at runtime.
        self.binding_patch = self.patch('sap.adt.ServiceBinding')

        self.service = Mock()
        self.service.definition = Mock()
        self.service.definition.name = self.param_service
        self.service.name = self.param_binding_name
        self.service.version = self.param_version

        self.publish_status = sap.adt.businessservice.StatusMessage()

        self.binding_inst = self.binding_patch.return_value
        self.binding_inst.find_service = Mock()
        self.binding_inst.find_service.return_value = self.service
        self.binding_inst.publish = Mock()
        self.binding_inst.publish.return_value = self.publish_status
        self.binding_inst.services = [self.service]

    def execute_publish_service_version(self):
        args = parse_args(
            'binding',
            'publish',
            self.param_binding_name,
            '--version',
            self.param_version
        )
        return args.execute(self.connection, args)

    def execute_publish_service_name(self):
        args = parse_args(
            'binding',
            'publish',
            self.param_binding_name,
            '--service',
            self.param_service
        )
        return args.execute(self.connection, args)

    def execute_publish_service_name_version(self):
        args = parse_args(
            'binding',
            'publish',
            self.param_binding_name,
            '--service',
            self.param_service,
            '--version',
            self.param_version
        )
        return args.execute(self.connection, args)

    def execute_publish(self):
        args = parse_args(
            'binding',
            'publish',
            self.param_binding_name,
        )
        return args.execute(self.connection, args)

    def test_publish_service_version_ok(self):
        self.publish_status.SEVERITY = "OK"
        self.publish_status.SHORT_TEXT = "Foo bar"

        self.execute_publish_service_version()

        self.binding_patch.assert_called_once_with(self.connection, self.param_binding_name)
        self.binding_inst.publish.assert_called_once_with(self.service)
        self.assertConsoleContents(console=self.console,
                                   stdout=f'''Publishing:
* {self.param_service} {self.param_binding_name} {self.param_version}
Foo bar
''',
                                   stderr=DEPRECATION_PUBLISH)

    def test_publish_service_name_ok(self):
        self.publish_status.SEVERITY = "OK"
        self.publish_status.SHORT_TEXT = "Foo bar"

        self.execute_publish_service_name()

        self.binding_patch.assert_called_once_with(self.connection, self.param_binding_name)

        self.binding_inst.find_service.assert_called_once_with(self.param_service, None)
        self.binding_inst.publish.assert_called_once_with(self.service)
        self.assertConsoleContents(console=self.console,
                                   stdout=f'''Publishing:
* {self.param_service} {self.param_binding_name} {self.param_version}
Foo bar
''',
                                   stderr=DEPRECATION_PUBLISH)

    def test_publish_service_ok(self):
        self.publish_status.SEVERITY = "OK"
        self.publish_status.SHORT_TEXT = "Foo bar"
        self.publish_status.LONG_TEXT = "Long text"

        self.execute_publish()

        self.binding_patch.assert_called_once_with(self.connection, self.param_binding_name)
        self.binding_inst.publish.assert_called_once_with(self.service)
        self.assertConsoleContents(console=self.console,
                                   stdout=f'''Publishing:
* {self.param_service} {self.param_binding_name} {self.param_version}
Foo bar
Long text
''',
                                   stderr=DEPRECATION_PUBLISH)

    def test_publish_service_error(self):
        self.publish_status.SEVERITY = "NOTOK"
        self.publish_status.SHORT_TEXT = "Foo bar"

        exitcode = self.execute_publish_service_version()

        self.binding_patch.assert_called_once()
        self.binding_inst.publish.assert_called_once()
        self.assertConsoleContents(console=self.console,
                                   stdout=f'''Publishing:
* {self.param_service} {self.param_binding_name} {self.param_version}
Foo bar
''',
                                   stderr=DEPRECATION_PUBLISH + f'''Failed to publish Service {self.param_service} in Binding {self.param_binding_name}
''')
        self.assertEqual(exitcode, 1)

    def test_publish_service_no_services(self):
        self.binding_inst.services = []

        exitcode = self.execute_publish_service_version()

        self.binding_patch.assert_called_once()
        self.binding_inst.find_service.assert_not_called()
        self.binding_inst.publish.assert_not_called()

        self.assertConsoleContents(console=self.console,
                                   stderr=DEPRECATION_PUBLISH + f'''Business Service Biding {self.param_binding_name} does not contain any services
''')
        self.assertEqual(exitcode, 1)

    def test_publish_service_too_many_services(self):
        self.binding_inst.services = [Mock(), Mock()]

        exitcode = self.execute_publish()

        self.binding_patch.assert_called_once()

        self.binding_inst.find_service.assert_not_called()
        self.binding_inst.publish.assert_not_called()

        self.assertConsoleContents(console=self.console,
                                   stderr=DEPRECATION_PUBLISH + f'''Cannot publish Business Service Biding {self.param_binding_name} without
Service Definition filters because the business binding contains more than one
Service Definition
''')
        self.assertEqual(exitcode, 1)

    def test_publish_service_not_found_service_name_version(self):
        self.binding_inst.find_service.return_value = None

        exitcode = self.execute_publish_service_name_version()

        self.binding_inst.publish.assert_not_called()

        self.assertConsoleContents(console=self.console,
                                   stderr=DEPRECATION_PUBLISH + f'''Business Service Binding {self.param_binding_name} has no Service Definition
with supplied name "{self.param_service}" and version "{self.param_version}"
''')
        self.assertEqual(exitcode, 1)

    def test_publish_service_not_found_service_version(self):
        self.binding_inst.find_service.return_value = None

        exitcode = self.execute_publish_service_version()

        self.binding_inst.publish.assert_not_called()

        self.assertConsoleContents(console=self.console,
                                   stderr=DEPRECATION_PUBLISH + f'''Business Service Binding {self.param_binding_name} has no Service Definition
with supplied name "" and version "{self.param_version}"
''')
        self.assertEqual(exitcode, 1)

    def test_publish_service_not_found_service_name(self):
        self.binding_inst.find_service.return_value = None

        exitcode = self.execute_publish_service_name()

        self.binding_inst.publish.assert_not_called()

        self.assertConsoleContents(console=self.console,
                                   stderr=DEPRECATION_PUBLISH + f'''Business Service Binding {self.param_binding_name} has no Service Definition
with supplied name "{self.param_service}" and version ""
''')
        self.assertEqual(exitcode, 1)

    def test_rap_binding_publish_emits_deprecation_warning(self):
        # explicit contract: a single deprecation warning lands on stderr
        # the moment the alias is invoked.
        self.publish_status.SEVERITY = 'OK'
        self.publish_status.SHORT_TEXT = 'OK'

        self.execute_publish_service_version()

        self.assertIn(DEPRECATION_PUBLISH.strip(), self.console.caperr)
        # Sanity: warning appears exactly once.
        self.assertEqual(self.console.caperr.count('deprecated'), 1)


class TestRapDefinition(ConsoleOutputTestCase, PatcherTestCase):
    '''Test rap definition command group'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None

        self.patch_console(console=self.console)

        self.connection = Connection([
            RESPONSE_ACTIVATION_OK,
            Response(text=SERVICE_DEFINITION_ADT_XML, status_code=200, headers={})
        ])
        self.param_definition_name = 'EXAMPLE_CONFIG_SRV'

    def execute_definition_activate(self):
        args = parse_args(
            'definition',
            'activate',
            self.param_definition_name
        )
        return args.execute(self.connection, args)

    def test_activate(self):
        self.execute_definition_activate()

        self.assertConsoleContents(console=self.console,
                                   stdout=f'''Activating:
* EXAMPLE_CONFIG_SRV
Activation has finished
Warnings: 0
Errors: 0
''',
                                   stderr=DEPRECATION_DEFINITION_ACTIVATE)

        self.connection.execs[0].assertEqual(
            Request.post_xml(
                uri='/sap/bc/adt/activation',
                accept='application/xml',
                params={'method':'activate', 'preauditRequested':'true'},
                body='''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/ddic/srvd/sources/example_config_srv" adtcore:name="EXAMPLE_CONFIG_SRV"/>
</adtcore:objectReferences>'''
            ),
            self
        )

    def test_rap_definition_activate_emits_deprecation_warning(self):
        self.execute_definition_activate()

        self.assertIn(DEPRECATION_DEFINITION_ACTIVATE.strip(), self.console.caperr)
        # Sanity: warning appears exactly once.
        self.assertEqual(self.console.caperr.count('deprecated'), 1)
