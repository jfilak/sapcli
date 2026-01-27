"""Test sap.rest.gcts.activities module"""

import unittest
from unittest.mock import patch, Mock

from sap.errors import SAPCliError
from sap.rest.errors import HTTPRequestError
from sap.rest.gcts.activities import (
    get_activity_rc,
    is_checkout_activity_success,
    is_clone_activity_success,
)

class TestIsCheckoutActivitySuccess(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mock_repo = Mock()

    @patch('sap.rest.gcts.activities.get_activity_rc')
    def test_is_checkout_activity_success_successful(self, mock_get_activity_rc):
        """Test is_checkout_activity_success when checkout is successful (return code 4)"""
        mock_get_activity_rc.return_value = 4

        result = is_checkout_activity_success(self.mock_repo, lambda rc: self.assertEqual(rc, 4))

        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams
        mock_get_activity_rc.assert_called_once_with(
            self.mock_repo,
            RepoActivitiesQueryParams.Operation.BRANCH_SW
        )

        self.assertTrue(result)

    @patch('sap.rest.gcts.activities.get_activity_rc')
    def test_is_checkout_activity_success_unsuccessful(self, mock_get_activity_rc):
        """Test is_checkout_activity_success when checkout fails (return code > 4)"""
        code = 5
        mock_get_activity_rc.return_value = code

        result = is_checkout_activity_success(self.mock_repo, lambda rc: self.assertEqual(rc, code))

        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams
        mock_get_activity_rc.assert_called_once_with(
            self.mock_repo,
            RepoActivitiesQueryParams.Operation.BRANCH_SW
        )

        self.assertFalse(result)


class TestIsClonedActivitySuccess(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.mock_repo = Mock()

    @patch('sap.rest.gcts.activities.get_activity_rc')
    def test_is_clone_activity_success_successful(self, mock_get_activity_rc):
        mock_get_activity_rc.return_value = 4

        result = is_clone_activity_success(self.mock_repo, lambda rc: self.assertEqual(rc, 4))

        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams
        mock_get_activity_rc.assert_called_once_with(
            self.mock_repo,
            RepoActivitiesQueryParams.Operation.CLONE
        )

        self.assertTrue(result)


    @patch('sap.rest.gcts.activities.get_activity_rc')
    def test_is_clone_activity_success_unsuccessful(self, mock_get_activity_rc):
        code = 5
        mock_get_activity_rc.return_value = code

        result = is_clone_activity_success(self.mock_repo, lambda rc: self.assertEqual(rc, code))

        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams
        mock_get_activity_rc.assert_called_once_with(
            self.mock_repo,
            RepoActivitiesQueryParams.Operation.CLONE
        )

        self.assertFalse(result)


class TestGetActivityRc(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mock_repo = Mock()
        self.mock_repo.rid = 'test_repo'

    def test_get_activity_rc_successful(self):
        """Test get_activity_rc when activities returns a valid result with return code"""
        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams

        self.mock_repo.activities.return_value = [{'rc': '0'}]

        operation = RepoActivitiesQueryParams.Operation.CLONE
        result = get_activity_rc(self.mock_repo, operation)

        self.assertEqual(result, 0)

        self.mock_repo.activities.assert_called_once()
        call_args = self.mock_repo.activities.call_args[0][0]
        self.assertEqual(call_args.get_params()['type'], operation.value)

    def test_get_activity_rc_http_error(self):
        """Test get_activity_rc when repo.activities raises HTTPRequestError"""
        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams

        fake_response = Mock()
        fake_response.text = 'Connection failed'
        fake_response.status_code = 500

        http_error = HTTPRequestError(None, fake_response)
        self.mock_repo.activities.side_effect = http_error

        operation = RepoActivitiesQueryParams.Operation.CLONE

        with self.assertRaises(SAPCliError) as context:
            get_activity_rc(self.mock_repo, operation)

        error_message = str(context.exception)
        self.assertIn('Unable to obtain activities of repository: "test_repo"', error_message)
        self.assertIn('Connection failed', error_message)

        self.mock_repo.activities.assert_called_once()

    def test_get_activity_rc_empty_activities(self):
        """Test get_activity_rc when activities returns empty list"""
        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams

        self.mock_repo.activities.return_value = []

        operation = RepoActivitiesQueryParams.Operation.CLONE

        with self.assertRaises(SAPCliError) as context:
            get_activity_rc(self.mock_repo, operation)

        error_message = str(context.exception)
        self.assertIn(f'Expected {operation.value} activity is empty! Repository: "test_repo"', error_message)

        self.mock_repo.activities.assert_called_once()

    def test_get_activity_rc_multiple_activities(self):
        """Test get_activity_rc when activities returns more than one result"""
        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams

        self.mock_repo.activities.return_value = [{'rc': '0'}, {'rc': '4'}]

        operation = RepoActivitiesQueryParams.Operation.CLONE

        with self.assertRaises(SAPCliError) as context:
            get_activity_rc(self.mock_repo, operation)

        error_message = str(context.exception)
        self.assertIn(f'Multiple {operation.value} activities found! Repository: "test_repo"', error_message)

        self.mock_repo.activities.assert_called_once()

    def test_get_activity_rc_missing_rc_defaults_to_zero(self):
        """Test get_activity_rc when activity has no 'rc' key - should default to 0"""
        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams

        self.mock_repo.activities.return_value = [{'state': 'SUCCESS'}]

        operation = RepoActivitiesQueryParams.Operation.CLONE
        result = get_activity_rc(self.mock_repo, operation)

        self.assertEqual(result, 0)

    def test_get_activity_rc_none_rc(self):
        """Test get_activity_rc when rc is explicitly None"""
        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams

        self.mock_repo.activities.return_value = [{'rc': None}]

        operation = RepoActivitiesQueryParams.Operation.CLONE

        with self.assertRaises(SAPCliError) as context:
            get_activity_rc(self.mock_repo, operation)

        error_message = str(context.exception)
        self.assertIn(f'Activity {operation.value} has invalid "rc" = None', error_message)

    def test_get_activity_rc_invalid_string_rc(self):
        """Test get_activity_rc when rc is a non-numeric string"""
        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams

        self.mock_repo.activities.return_value = [{'rc': 'not-a-number'}]

        operation = RepoActivitiesQueryParams.Operation.CLONE

        with self.assertRaises(SAPCliError) as context:
            get_activity_rc(self.mock_repo, operation)

        error_message = str(context.exception)
        self.assertIn(f'Activity {operation.value} has invalid "rc" = not-a-number', error_message)

    def test_get_activity_rc_integer_rc(self):
        """Test get_activity_rc when rc is already an integer (the default from .get)"""
        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams

        self.mock_repo.activities.return_value = [{'rc': 4}]

        operation = RepoActivitiesQueryParams.Operation.CLONE
        result = get_activity_rc(self.mock_repo, operation)

        self.assertEqual(result, 4)
