#!/usr/bin/env python3
import unittest
from unittest.mock import patch, Mock

import sap.rfc.core
from sap.rfc.errors import RFCLoginError, RFCCommunicationError, SAPCliError


class TestTryPyRFCExceptionType(unittest.TestCase):

    @patch('sap.rfc.core.rfc_is_available', return_value=False)
    def test_pyrfc_is_not_available(self, _):
        typ = None
        with self.assertRaises(SAPCliError) as caught:
            typ = sap.rfc.core.try_pyrfc_exception_type()

        self.assertIsNone(typ)
        self.assertEqual(str(caught.exception), 'RFC functionality is not available(enabled)')

    def test_pyrfc_logon_error(self):
        class FakeLogonError(Exception):
            def __init__(self, msg):
                self.message = msg

        fake_saprfc_module = Mock()
        fake_saprfc_module._exception.LogonError = FakeLogonError
        fake_saprfc_module.Connection.side_effect = fake_saprfc_module._exception.LogonError('Bad login')

        patch('sap.rfc.core.SAPRFC_MODULE', new=fake_saprfc_module).start()

        with self.assertRaises(RFCLoginError) as cm:
            sap.rfc.core.connect(ashost='host', user='user')
            print('the exception is not raised')

        self.assertEqual(str(cm.exception), 'RFC Connection Error: [HOST:"host", USER:"user"]: Bad login')

    def test_pyrfc_communication_error(self):
        class FakeLogonError(Exception):
            pass

        class FakeCommunicationError(Exception):
            def __init__(self, msg):
                self.message = msg

        fake_saprfc_module = Mock()
        # if not defined python throws TypeError because Mock does not derive from Exception
        fake_saprfc_module._exception.LogonError = FakeLogonError

        fake_saprfc_module._exception.CommunicationError = FakeCommunicationError
        fake_saprfc_module.Connection.side_effect = fake_saprfc_module._exception.CommunicationError('ERROR Communication error')

        patch('sap.rfc.core.SAPRFC_MODULE', new=fake_saprfc_module).start()

        with self.assertRaises(RFCCommunicationError) as cm:
            sap.rfc.core.connect(ashost='host', user='user')

        self.assertEqual(str(cm.exception), 'RFC Connection Error: [HOST:"host", USER:"user"]: Communication error')

    def test_pyrfc_communication_error_multiline(self):
        """Test parsing of multi-line ERROR section from RFC exception"""
        class FakeLogonError(Exception):
            pass

        class FakeCommunicationError(Exception):
            def __init__(self, msg):
                self.message = msg

        fake_saprfc_module = Mock()
        fake_saprfc_module._exception.LogonError = FakeLogonError
        fake_saprfc_module._exception.CommunicationError = FakeCommunicationError

        # Simulate a real RFC communication error with multi-line ERROR section
        multiline_error = """LOCATION    CPIC (TCP/IP) on local host with Unicode
ERROR       partner
            'very.long.dns.name.for.testing
            .com:3301' not reached
TIME        Tue Jan 20 17:44:07 2026
RELEASE     753
COMPONENT   NI (network interface)"""

        fake_saprfc_module.Connection.side_effect = fake_saprfc_module._exception.CommunicationError(multiline_error)

        patch('sap.rfc.core.SAPRFC_MODULE', new=fake_saprfc_module).start()

        with self.assertRaises(RFCCommunicationError) as cm:
            sap.rfc.core.connect(ashost='host', user='user')

        self.assertEqual(
            str(cm.exception),
            "RFC Connection Error: [HOST:\"host\", USER:\"user\"]: partner 'very.long.dns.name.for.testing.com:3301' not reached"
        )
