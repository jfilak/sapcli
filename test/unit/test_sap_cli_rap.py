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

parse_args = generate_parse_args(sap.cli.rap.CommandGroup())


class TestRapBindingPublish(PatcherTestCase, ConsoleOutputTestCase):
    '''Test rap binding Publish command'''

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None

        self.connection = Mock()

        self.patch_console(console=self.console)
        self.binding_patch = self.patch('sap.adt.businessservice.ServiceBinding')

        self.publish_status = sap.adt.businessservice.StatusMessage()

        self.binding_inst = self.binding_patch.return_value
        self.binding_inst.publish = Mock()
        self.binding_inst.publish.return_value = self.publish_status

        self.param_version = '1234'
        self.param_service = 'SRVD_NAME'
        self.param_binding_name = 'SRVB_NAME'

    def execute_publish_service_version(self):
        args = parse_args(
            'publish',
            self.param_binding_name,
            '--version',
            self.param_version
        )
        return args.execute(self.connection, args)

    def execute_publish_service_name(self):
        args = parse_args(
            'publish',
            self.param_binding_name,
            '--service',
            self.param_service
        )
        return args.execute(self.connection, args)

    def execute_publish(self):
        args = parse_args(
            'publish',
            self.param_binding_name,
        )
        return args.execute(self.connection, args)

    def test_publish_service_version_ok(self):
        self.publish_status.SEVERITY = "OK"
        self.publish_status.SHORT_TEXT = "Foo bar"

        self.execute_publish_service_version()

        self.binding_patch.assert_called_once_with(self.connection, self.param_binding_name)
        self.binding_inst.publish.assert_called_once_with(None, self.param_version)
        self.assertConsoleContents(console=self.console,
                                   stdout=f'''Foo bar\nService in binding {self.param_binding_name} published successfully.
''')

    def test_publish_service_name_ok(self):
        self.publish_status.SEVERITY = "OK"
        self.publish_status.SHORT_TEXT = "Foo bar"

        self.execute_publish_service_name()

        self.binding_patch.assert_called_once_with(self.connection, self.param_binding_name)
        self.binding_inst.publish.assert_called_once_with(self.param_service, None)
        self.assertConsoleContents(console=self.console,
                                   stdout=f'''Foo bar\nService in binding {self.param_binding_name} published successfully.
''')

    def test_publish_service_ok(self):
        self.publish_status.SEVERITY = "OK"
        self.publish_status.SHORT_TEXT = "Foo bar"
        self.publish_status.LONG_TEXT = "Long text"

        self.execute_publish()

        self.binding_patch.assert_called_once_with(self.connection, self.param_binding_name)
        self.binding_inst.publish.assert_called_once_with(None, None)
        self.assertConsoleContents(console=self.console,
                                   stdout=f'''Foo bar\nLong text\nService in binding {self.param_binding_name} published successfully.
''')

    def test_publish_service_error(self):
        self.publish_status.SEVERITY = "NOTOK"
        self.publish_status.SHORT_TEXT = "Foo bar"

        self.execute_publish_service_version()

        self.binding_patch.assert_called_once()
        self.binding_inst.publish.assert_called_once()
        self.assertConsoleContents(console=self.console, stdout='Foo bar\n',
                                   stderr=f'''Failed to publish {self.param_binding_name}
''')
