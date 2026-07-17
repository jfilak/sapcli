"""Unit tests for sap.http.truststore_support"""

import sys
import unittest
from unittest.mock import MagicMock, patch

import sap.http.truststore_support
from sap.http.truststore_support import (
    enable_system_cert_store,
    TruststoreNotAvailableError,
)
from sap.errors import SAPCliError


class TestEnableSystemCertStore(unittest.TestCase):

    def setUp(self):
        # Reset the one-shot guard so each test starts uninjected.
        sap.http.truststore_support._INJECTED.clear()

    def tearDown(self):
        sap.http.truststore_support._INJECTED.clear()

    def test_injects_truststore_into_ssl(self):
        fake_truststore = MagicMock()

        with patch.dict(sys.modules, {'truststore': fake_truststore}):
            enable_system_cert_store()

        fake_truststore.inject_into_ssl.assert_called_once_with()

    def test_is_idempotent(self):
        fake_truststore = MagicMock()

        with patch.dict(sys.modules, {'truststore': fake_truststore}):
            enable_system_cert_store()
            enable_system_cert_store()

        fake_truststore.inject_into_ssl.assert_called_once_with()

    def test_raises_sapclierror_when_truststore_missing(self):
        # Setting the module to None makes "import truststore" raise ImportError.
        with patch.dict(sys.modules, {'truststore': None}):
            with self.assertRaises(TruststoreNotAvailableError) as caught:
                enable_system_cert_store()

        self.assertIsInstance(caught.exception, SAPCliError)
        self.assertIn('truststore', str(caught.exception))

    def test_not_marked_injected_when_truststore_missing(self):
        with patch.dict(sys.modules, {'truststore': None}):
            try:
                enable_system_cert_store()
            except TruststoreNotAvailableError:
                pass

        self.assertFalse(sap.http.truststore_support._INJECTED)


if __name__ == '__main__':
    unittest.main()
