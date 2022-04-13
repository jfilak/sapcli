#!/usr/bin/env python3
import unittest
from unittest.mock import patch

import sap.rfc.core


class TestTryPyRFCExceptionType:

    @patch('sap.rfc.core.rfc_is_available', return_value=False)
    def test_pyrfc_is_not_available(self):
        with self.assertRaises('sap.errors.SAPCliError') as caught:
            typ = sap.rfc.core.try_pyrfc_exception_type()

        self.assertIsNone(typ)
        self.assertEqual(str(caught.exception), 'RFC functionality is not available(enabled)')
