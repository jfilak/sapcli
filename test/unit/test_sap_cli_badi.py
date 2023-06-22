#!/usr/bin/env python3

from io import StringIO
import unittest
import json
from unittest.mock import MagicMock, patch, Mock, PropertyMock, mock_open, call

import sap.cli.badi
import sap.cli.core
from sap.rest.errors import HTTPRequestError

from mock import (
    Connection,
    Request,
    Response,
    ConsoleOutputTestCase,
    PatcherTestCase,
)

from fixtures_adt import (
    EMPTY_RESPONSE_OK,
    LOCK_RESPONSE_OK,
)

from fixtures_adt_enhancement_implementation import (
    ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4,
)

from infra import generate_parse_args


parse_args = generate_parse_args(sap.cli.badi.CommandGroup())

OK_ENHO_RESPONSE = Response(
    status_code=200,
    text=ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4,
    content_type='application/vnd.sap.adt.enh.enhoxhb.v4+xml'
)

class TestBadiEnhImplList(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)

    def default_action(self, *args, **kwargs):
        return parse_args(*args, **kwargs)

    def list(self, enhimpl, *args, **kwargs):
        return parse_args('-i', enhimpl, 'list', *args, **kwargs)

    def set_active(self, enhimpl, badi, active, *args, **kwargs):
        value = 'true' if active else 'false'
        return parse_args('-i', enhimpl, 'set-active', '-b', badi, value, *args, **kwargs)

    def test_list_all_badis(self):
        conn = Connection([OK_ENHO_RESPONSE])

        list_cmd = self.list('SAPCLI_ENH_IMPL')
        list_cmd.execute(conn, list_cmd)

        self.assertConsoleContents(
                self.console,
                stdout='SAPCLI_BADI_IMPL true ZCL_SAPCLI_BADI_IMPL SAPCLI_BADI_DEF  false false SAPCLI badi\n')

    def test_default_action_all_badis(self):
        conn = Connection([OK_ENHO_RESPONSE])

        list_cmd = self.default_action('-i', 'SAPCLI_ENH_IMPL')
        list_cmd.execute(conn, list_cmd)

        self.assertConsoleContents(
                self.console,
                stdout='SAPCLI_BADI_IMPL true ZCL_SAPCLI_BADI_IMPL SAPCLI_BADI_DEF  false false SAPCLI badi\n')

    def test_set_active_no_change(self):
        with patch('sap.cli.badi._get_enhancement_implementation') as mock_getter:
            mock_badi = MagicMock()
            type(mock_badi).is_active_implementation = PropertyMock(return_value=True)

            mock_implementation_obj = MagicMock()
            mock_implementation_obj.__getitem__.return_value = mock_badi

            mock_implementations = PropertyMock(return_value=mock_implementation_obj)

            mock_badis_obj = Mock()
            type(mock_badis_obj).implementations = mock_implementations

            mock_badis = PropertyMock(return_value=mock_badis_obj)

            mock_spec_obj = Mock()
            type(mock_spec_obj).badis = mock_badis

            mock_specific = PropertyMock(return_value=mock_spec_obj)

            mock_enho_obj = MagicMock()
            type(mock_enho_obj).specific = mock_specific

            mock_getter.return_value = mock_enho_obj

            set_active_cmd = self.set_active('SAPCLI_ENH_IMPL', 'SAPCLI_BADI_IMPL', True)
            set_active_cmd.execute(None, set_active_cmd)

            mock_getter.assert_called_once_with(None, set_active_cmd)

            mock_implementation_obj.__getitem__.assert_called_once_with('SAPCLI_BADI_IMPL')

        self.assertConsoleContents(self.console, stdout='''Nothing to do! The BAdI SAPCLI_BADI_IMPL\'s Active is already: true
''')


    def test_set_active_false(self):
        ok_active_enho_response = Response(
            status_code=200,
            text=ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4.replace('enho:active="false"', 'enho:active="true"'),
            content_type='application/vnd.sap.adt.enh.enhoxhb.v4+xml'
        )

        conn = Connection([ok_active_enho_response, LOCK_RESPONSE_OK, OK_ENHO_RESPONSE, EMPTY_RESPONSE_OK])

        set_active_cmd = self.set_active('SAPCLI_ENH_IMPL', 'SAPCLI_BADI_IMPL', False)
        set_active_cmd.execute(conn, set_active_cmd)

        self.assertIn('enho:active="false"', conn.execs[2].body.decode('utf8'))

        self.assertConsoleContents(self.console, stdout='''Updating:
* SAPCLI_ENH_IMPL/SAPCLI_BADI_IMPL
''')

    def test_set_active_true(self):
        ok_inactive_enho_response = Response(
            status_code=200,
            text=ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4.replace('enho:active="true"', 'enho:active="false"'),
            content_type='application/vnd.sap.adt.enh.enhoxhb.v4+xml'
        )

        conn = Connection([ok_inactive_enho_response, LOCK_RESPONSE_OK, OK_ENHO_RESPONSE, EMPTY_RESPONSE_OK])

        set_active_cmd = self.set_active('SAPCLI_ENH_IMPL', 'SAPCLI_BADI_IMPL', True)
        set_active_cmd.execute(conn, set_active_cmd)

        self.assertIn('enho:active="true"', conn.execs[2].body.decode('utf8'))

        self.assertConsoleContents(self.console, stdout='''Updating:
* SAPCLI_ENH_IMPL/SAPCLI_BADI_IMPL
''')

    def test_set_active_invalid(self):
        set_active_cmd = self.set_active('SAPCLI_ENH_IMPL', 'SAPCLI_BADI_IMPL', True)
        set_active_cmd.active = 'foo'

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            set_active_cmd.execute(None, set_active_cmd)

        self.assertEqual(str(caught.exception), 'BUG: unexpected value of the argument active: foo')

    def test_set_active_unknown_badi(self):
        conn = Connection([OK_ENHO_RESPONSE, LOCK_RESPONSE_OK, OK_ENHO_RESPONSE, EMPTY_RESPONSE_OK])

        set_active_cmd = self.set_active('SAPCLI_ENH_IMPL', 'UKNONWN_BADI', True)

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            set_active_cmd.execute(conn, set_active_cmd)

        self.assertEqual(str(caught.exception), 'The BAdI UKNONWN_BADI not found in the enhancement implementation SAPCLI_ENH_IMPL')

    def test_set_active_with_activation(self):
        ok_inactive_enho_response = Response(
            status_code=200,
            text=ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4.replace('enho:active="true"', 'enho:active="false"'),
            content_type='application/vnd.sap.adt.enh.enhoxhb.v4+xml'
        )

        ok_active_enho_response = Response(
            status_code=200,
            text=ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4.replace('enho:active="false"', 'enho:active="true"'),
            content_type='application/vnd.sap.adt.enh.enhoxhb.v4+xml'
        )

        conn = Connection([
            ok_inactive_enho_response, # GET original object
            LOCK_RESPONSE_OK,  # POST lock
            OK_ENHO_RESPONSE,  # PUT updated
            EMPTY_RESPONSE_OK, # POST unlock
            EMPTY_RESPONSE_OK, # POST activate
            ok_active_enho_response, # GET the object again
        ])

        set_active_cmd = self.set_active('SAPCLI_ENH_IMPL', 'SAPCLI_BADI_IMPL', True, '-a')
        set_active_cmd.execute(conn, set_active_cmd)

        self.assertConsoleContents(self.console, stdout='''Updating:
* SAPCLI_ENH_IMPL/SAPCLI_BADI_IMPL
Activating:
* SAPCLI_ENH_IMPL
Activation has finished
Warnings: 0
Errors: 0
''')
