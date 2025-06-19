#!/usr/bin/env python3

import unittest

import sap.cli.featuretoggle

from infra import generate_parse_args

from mock import (
    Connection,
    ConsoleOutputTestCase,
    PatcherTestCase,
    Response,
    Request,
)

from fixtures_adt_featuretoggle import (
    RESPONSE_FEATURE_TOGGLE_STATE_CLIENT_ON,
    RESPONSE_FEATURE_TOGGLE_STATE_CLIENT_OFF,
)

parse_args = generate_parse_args(sap.cli.featuretoggle.CommandGroup())

class TestFeatureToggle(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None
        self.patch_console(console=self.console)

        self.connection = Connection()

    def state(self, *args, **kwargs):
        return parse_args('state', *args, **kwargs)

    def on(self, *args, **kwargs):
        return parse_args('on', *args, **kwargs)

    def off(self, *args, **kwargs):
        return parse_args('off', *args, **kwargs)

    def test_state_on(self):
        self.connection.set_responses([RESPONSE_FEATURE_TOGGLE_STATE_CLIENT_ON])

        ftgl_id = 'MY_LUCKY_TOGGLE'
        args = self.state(ftgl_id)
        exit_code = args.execute(self.connection, args)
        self.assertEqual(exit_code, 0)

        self.assertConsoleContents(console=self.console, stdout='''Client 100: on
User TESTER: undefined
''')

    def test_state_off(self):
        self.connection.set_responses([RESPONSE_FEATURE_TOGGLE_STATE_CLIENT_OFF])

        ftgl_id = 'MY_LUCKY_TOGGLE'
        args = self.state(ftgl_id)
        exit_code = args.execute(self.connection, args)
        self.assertEqual(exit_code, 0)

        self.assertConsoleContents(console=self.console, stdout='''Client 100: off
User TESTER: undefined
''')

    def _assert_toggle_state_with_corrnr(self, connection, expected_state):
        self.assertEqual(len(connection.execs), 1)
        connection.execs[0].assertEqual(
            Request.post_json(
                uri=f"/sap/bc/adt/sfw/featuretoggles/my_lucky_toggle/toggle",
                content_type="application/vnd.sap.adt.related.toggle.parameters.v1+asjson",
                body={
                    "TOGGLE_PARAMETERS": {
                        "IS_USER_SPECIFIC": False,
                        "STATE": expected_state,
                        "TRANSPORT_REQUEST": "1234567890",
                    }
                },
            ),
            self
         )

    def test_toggle_on(self):
        self.connection.set_responses([Response.ok()])

        ftgl_id = 'MY_LUCKY_TOGGLE'
        args = self.on(ftgl_id, '--corrnr', '1234567890')
        exit_code = args.execute(self.connection, args)
        self.assertEqual(exit_code, 0)

        self.assertConsoleContents(console=self.console, stdout='')
        self._assert_toggle_state_with_corrnr(self.connection, "on")

    def test_toggle_off(self):
        self.connection.set_responses([Response.ok()])

        ftgl_id = 'MY_LUCKY_TOGGLE'
        args = self.off(ftgl_id, '--corrnr', '1234567890')
        exit_code = args.execute(self.connection, args)
        self.assertEqual(exit_code, 0)

        self.assertConsoleContents(console=self.console, stdout='')
        self._assert_toggle_state_with_corrnr(self.connection, "off")
