#!/usr/bin/env python3

import unittest
from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

from sap.version import get_version, build_user_agent


class TestGetVersion(unittest.TestCase):

    @patch('sap.version.version', return_value='1.2.3')
    def test_installed_package(self, fake_version):
        self.assertEqual(get_version(), '1.2.3')
        fake_version.assert_called_once_with('sapcli')

    @patch('sap.version.version', side_effect=PackageNotFoundError('sapcli'))
    def test_package_not_installed(self, _):
        self.assertEqual(get_version(), 'unknown')


class TestBuildUserAgent(unittest.TestCase):

    def setUp(self):
        build_user_agent.cache_clear()

    def tearDown(self):
        build_user_agent.cache_clear()

    @patch('sap.version.requests.utils.default_user_agent', return_value='python-requests/2.32.3')
    @patch('sap.version.platform.python_version', return_value='3.12.3')
    @patch('sap.version.platform.python_implementation', return_value='CPython')
    @patch('sap.version.platform.machine', return_value='x86_64')
    @patch('sap.version.platform.system', return_value='Linux')
    @patch('sap.version.get_version', return_value='1.2.3')
    def test_format(self, *_):
        self.assertEqual(build_user_agent(),
                         'sapcli/1.2.3 (Linux; x86_64; CPython 3.12.3) python-requests/2.32.3')

    @patch('sap.version.get_version', return_value='1.2.3')
    def test_value_is_cached(self, fake_get_version):
        first = build_user_agent()
        second = build_user_agent()

        self.assertEqual(first, second)
        fake_get_version.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
