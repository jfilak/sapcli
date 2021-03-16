'''oData service CLI tests.'''

# !/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

from unittest.mock import Mock, patch

from mock import (
    ConsoleOutputTestCase,
    PatcherTestCase,
)

import sap.cli.businessservice

from infra import generate_parse_args

parse_args = generate_parse_args(sap.cli.businessservice.CommandGroup())


class TestbusinessservicePublish(PatcherTestCase, ConsoleOutputTestCase):
    '''Test businessservice Publish command'''

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

        self.param_service_name = '1234'
        self.param_binding_name = 'SRVB_NAME'

    def execute_publish_all_params(self):
        args = parse_args(
            'publish',
            self.param_binding_name,
            self.param_service_name
        )
        return args.execute(self.connection, args)

    def test_publish_service_ok(self):
        self.publish_status.SEVERITY="OK"
        self.publish_status.SHORT_TEXT="Foo bar"

        self.execute_publish_all_params()

        self.binding_patch.assert_called_once_with(self.connection, self.param_binding_name)
        self.binding_inst.publish.assert_called_once_with(self.param_service_name)
        self.assertConsoleContents(console=self.console, stdout=f'''Foo bar\nService version {self.param_service_name} in binding {self.param_binding_name} published successfully.
''')

    def test_publish_service_error(self):
        self.publish_status.SEVERITY="NOTOK"
        self.publish_status.SHORT_TEXT="Foo bar"

        self.execute_publish_all_params()

        self.binding_patch.assert_called_once()
        self.binding_inst.publish.assert_called_once()
        self.assertConsoleContents(console=self.console, stdout='Foo bar\n', stderr=f'''Failed to publish {self.param_binding_name}
''')
