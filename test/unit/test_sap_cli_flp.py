'''FLP CLI tests.'''
#!/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import unittest
import sap.cli.flp
from unittest.mock import MagicMock, Mock, mock_open, patch
from fixtures_flp_builder import FLP_BUILDER_CONFIG


def get_sample_init_args():
    args = Mock()
    args.config = "config"
    return args


@patch('builtins.open', mock_open(read_data=FLP_BUILDER_CONFIG))
class TestFlpCommands(unittest.TestCase):
    '''Test FLP cli commands'''

    @patch('sap.flp.builder.Builder', autospec=True)
    def test_init_ok(self, builder_mock):
        connection = MagicMock()

        builder_mock.return_value.run.return_value = None

        sap.cli.flp.init(connection, get_sample_init_args())

        builder_mock.assert_called_with(connection, "config")
        builder_mock.return_value.run.assert_called()
