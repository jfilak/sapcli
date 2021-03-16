'''oData service CLI tests.'''

# !/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

from unittest.mock import Mock, patch

from mock import (
    ConsoleOutputTestCase,
    PatcherTestCase,
)

import sap.cli.odataservice

from infra import generate_parse_args

parse_args = generate_parse_args(sap.cli.odataservice.CommandGroup())


class TestOdataservicePublish(PatcherTestCase, ConsoleOutputTestCase):
    '''Test Odataservice Publish command'''

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None

        self.connection = Mock()

        self.patch_console(console=self.console)
        self.binding_patch = self.patch('sap.adt.odataservice.ServiceBinding')

        self.binding_inst = self.binding_patch.return_value
        self.binding_inst.publish = Mock()
        self.binding_inst.get_binding_type = Mock(return_value='bindingtype')

        self.param_service_version = '1234'
        self.param_binding_name = 'SRVB_NAME'

    def execute_publish_all_params(self):
        args = parse_args(
            'publish',
            self.param_binding_name,
            '--service_version', self.param_service_version
        )
        return args.execute(self.connection, args)

    def test_publish_service_ok(self):
        self.binding_inst.publish.return_value.status_code = 200
        self.execute_publish_all_params()

        self.binding_patch.assert_called_once_with(self.connection, self.param_service_version, self.param_binding_name)
        self.binding_inst.publish.assert_called_once()
        self.assertConsoleContents(console=self.console, stdout=f'''Service version {self.param_service_version} in binding {self.param_binding_name} published successfully.
''')

    def test_publish_service_error(self):
        self.binding_inst.publish.return_value.status_code = 500
        self.execute_publish_all_params()

        self.binding_patch.assert_called_once()
        self.binding_inst.publish.assert_called_once()
        self.assertConsoleContents(console=self.console, stderr=f'''Failed to publish {self.param_binding_name} {self.binding_inst.publish()}
''')
