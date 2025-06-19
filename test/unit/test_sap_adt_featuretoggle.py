#!/usr/bin/env python3

import unittest
from types import SimpleNamespace

import sap.adt.featuretoggle
from sap.errors import SAPCliError

from mock import (
    Connection,
    Response,
    Request,
)
from fixtures_adt_featuretoggle import (
    RESPONSE_FEATURE_TOGGLE_STATE_CLIENT_ON,
    RESPONSE_FEATURE_TOGGLE_STATE_CLIENT_OFF,
)


class TestFeatureToggle(unittest.TestCase):

    def feature_toggle_manager(self, responses):
        connection = Connection(responses)
        manager = sap.adt.featuretoggle.FeatureToggleManager(connection)
        return (manager, connection)

    def test_read_feature_toggle_on(self):
        manager, connection = self.feature_toggle_manager([RESPONSE_FEATURE_TOGGLE_STATE_CLIENT_ON])
        state = manager.fetch_feature_toggle_state("MY_LUCKY_TOGGLE")
        self.assertEqual(state.client_state, sap.adt.featuretoggle.FeatureToggleState.ON)
        self.assertTrue(state.is_on())
        self.assertFalse(state.is_off())

    def test_read_feature_toggle_off(self):
        manager, connection = self.feature_toggle_manager([RESPONSE_FEATURE_TOGGLE_STATE_CLIENT_OFF])
        state = manager.fetch_feature_toggle_state("MY_LUCKY_TOGGLE")
        self.assertEqual(state.client_state, sap.adt.featuretoggle.FeatureToggleState.OFF)
        self.assertFalse(state.is_on())
        self.assertTrue(state.is_off())

    def _assert_toggle_state(self, connection, expected_state):
        self.assertEqual(len(connection.execs), 1)
        connection.execs[0].assertEqual(
            Request.post_json(
                uri=f"/sap/bc/adt/sfw/featuretoggles/MY_LUCKY_TOGGLE/toggle",
                content_type="application/vnd.sap.adt.related.toggle.parameters.v1+asjson",
                body={
                    "TOGGLE_PARAMETERS": {
                        "IS_USER_SPECIFIC": False,
                        "STATE": expected_state,
                    }
                },
            ),
            self
         )

    def _assert_toggle_state_with_corrnr(self, connection, expected_state):
        self.assertEqual(len(connection.execs), 1)
        connection.execs[0].assertEqual(
            Request.post_json(
                uri=f"/sap/bc/adt/sfw/featuretoggles/MY_LUCKY_TOGGLE/toggle",
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

    def test_switch_feature_toggle_on(self):
        manager, connection = self.feature_toggle_manager([Response.ok()])
        state = manager.switch_feature_toggle_on("MY_LUCKY_TOGGLE")
        self._assert_toggle_state(connection, "on")

    def test_switch_feature_toggle_on_with_corrnr(self):
        manager, connection = self.feature_toggle_manager([Response.ok()])
        state = manager.switch_feature_toggle_on("MY_LUCKY_TOGGLE", corrnr="1234567890")
        self._assert_toggle_state_with_corrnr(connection, "on")

    def test_switch_feature_toggle_off(self):
        manager, connection = self.feature_toggle_manager([Response.ok()])
        state = manager.switch_feature_toggle_off("MY_LUCKY_TOGGLE")
        self._assert_toggle_state(connection, "off")

    def test_switch_feature_toggle_off_with_corrnr(self):
        manager, connection = self.feature_toggle_manager([Response.ok()])
        state = manager.switch_feature_toggle_off("MY_LUCKY_TOGGLE", corrnr="1234567890")
        self._assert_toggle_state_with_corrnr(connection, "off")

    def test_switch_feature_toggle_failure(self):
        """Test that SAPCliError is raised when toggle operation returns non-200 success status"""
        # Using 201 (Created) to bypass the connection's error handling (which triggers for >= 400)
        # but still trigger our feature toggle error check (which expects exactly 200)
        error_response = Response(
            status_code=201,
            text="Unexpected response"
        )
        manager, connection = self.feature_toggle_manager([error_response])

        with self.assertRaises(SAPCliError) as context:
            manager.switch_feature_toggle_on("MY_LUCKY_TOGGLE")

        self.assertIn("Failed to switch feature toggle MY_LUCKY_TOGGLE to on", str(context.exception))
        self.assertIn("Unexpected response", str(context.exception))

    def test_fetch_feature_toggle_state_url_quoting(self):
        """Test that feature toggle names with slashes are properly URL encoded"""
        manager, connection = self.feature_toggle_manager([RESPONSE_FEATURE_TOGGLE_STATE_CLIENT_ON])
        state = manager.fetch_feature_toggle_state("/MY/FT/AWESOME")

        self.assertEqual(len(connection.execs), 1)
        # Slashes should be encoded as %2F
        self.assertIn("%2FMY%2FFT%2FAWESOME", connection.execs[0].adt_uri)
        self.assertNotIn("/MY/FT/AWESOME", connection.execs[0].adt_uri)

    def test_switch_feature_toggle_on_url_quoting(self):
        """Test that feature toggle names with slashes are properly URL encoded when switching on"""
        manager, connection = self.feature_toggle_manager([Response.ok()])
        manager.switch_feature_toggle_on("/MY/FT/AWESOME")

        self.assertEqual(len(connection.execs), 1)
        # Slashes should be encoded as %2F
        self.assertIn("%2FMY%2FFT%2FAWESOME", connection.execs[0].adt_uri)
        self.assertNotIn("/MY/FT/AWESOME", connection.execs[0].adt_uri)

    def test_switch_feature_toggle_off_url_quoting(self):
        """Test that feature toggle names with slashes are properly URL encoded when switching off"""
        manager, connection = self.feature_toggle_manager([Response.ok()])
        manager.switch_feature_toggle_off("/MY/FT/AWESOME")

        self.assertEqual(len(connection.execs), 1)
        # Slashes should be encoded as %2F
        self.assertIn("%2FMY%2FFT%2FAWESOME", connection.execs[0].adt_uri)
        self.assertNotIn("/MY/FT/AWESOME", connection.execs[0].adt_uri)


class TestFeatureToggleState(unittest.TestCase):

    def test_from_string_on(self):
        state = sap.adt.featuretoggle.FeatureToggleState.from_string("on")
        self.assertEqual(state, sap.adt.featuretoggle.FeatureToggleState.ON)

    def test_from_string_off(self):
        state = sap.adt.featuretoggle.FeatureToggleState.from_string("off")
        self.assertEqual(state, sap.adt.featuretoggle.FeatureToggleState.OFF)

    def test_from_string_undefined(self):
        state = sap.adt.featuretoggle.FeatureToggleState.from_string("undefined")
        self.assertEqual(state, sap.adt.featuretoggle.FeatureToggleState.UNDEFINED)

    def test_from_string_invalid_value(self):
        """Test that ValueError is raised for invalid state values"""
        with self.assertRaises(ValueError) as context:
            sap.adt.featuretoggle.FeatureToggleState.from_string("invalid_state")

        self.assertIn("'invalid_state' is not a valid FeatureToggleState", str(context.exception))


if __name__ == '__main__':
    unittest.main()
