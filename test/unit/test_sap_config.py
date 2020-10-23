#!/usr/bin/env python3

import os
import unittest
from unittest.mock import patch

import sap.config


class TestConfigGet(unittest.TestCase):

    def test_return_default(self):
        default = 'foo'
        actual = sap.config.config_get('bar', default=default)

        self.assertEqual(actual, default)

    def test_return_http_timeout(self):
        timeout = sap.config.config_get('http_timeout')

        self.assertEqual(timeout, 900)

    def test_return_http_timeout_from_env(self):
        with patch('os.environ', {'SAPCLI_HTTP_TIMEOUT': '0.777'}):
            timeout = sap.config.config_get('http_timeout')

        self.assertEqual(timeout, 0.777)
