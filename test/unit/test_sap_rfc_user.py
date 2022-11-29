#!/usr/bin/env python3

import datetime

import unittest
from unittest.mock import Mock, call, patch

from sap.rfc.bapi import BAPIError, BAPIReturn
from sap.rfc.user import add_to_dict_if_not_none, add_to_dict_if_not_present, today_sap_date, \
         UserBuilder, UserRoleAssignmentBuilder, UserProfileAssignmentBuilder, UserManager

from test_sap_rfc_bapi import (
        create_bapiret_error,
        create_bapiret_info
)


class SAPRFCUserAux(unittest.TestCase):

    def test_add_to_dict_if_not_none_none(self):
        target = dict()

        ret = add_to_dict_if_not_none(target, 'key', None)

        self.assertNotIn('key', target)
        self.assertFalse(ret)

    def test_add_to_dict_if_not_none_not_none(self):
        target = dict()

        ret = add_to_dict_if_not_none(target, 'key', 'value')

        self.assertIn('key', target)
        self.assertEqual(target, {'key': 'value'})
        self.assertTrue(ret)

    def test_add_to_dict_if_not_present_yes(self):
        target = dict()

        ret = add_to_dict_if_not_present(target, 'key', 'value')

        self.assertIn('key', target)
        self.assertEqual(target, {'key': 'value'})
        self.assertTrue(ret)

    def test_add_to_dict_if_not_present_no(self):
        target = {'key': 'value'}

        ret = add_to_dict_if_not_present(target, 'key', 'foo')

        self.assertIn('key', target)
        self.assertEqual(target, {'key': 'value'})
        self.assertFalse(ret)

class TestUserBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = UserBuilder()

    def test_no_parameters_provided(self):
        params = self.builder.build_rfc_params()

        date = datetime.date.today().strftime('%Y%m%d')

        self.assertEqual(
            params,
            {'LOGONDATA': {
                    'GLTGV': date,
                    'GLTGB': '20991231'
                },
             'ADDRESS': {
                    'FIRSTNAME': '',
                    'LASTNAME':'',
                    'E_MAIL': ''
                },
             'ALIAS': {'USERALIAS': ''},
             'PASSWORD': {'BAPIPWD': ''}
            }
        )

    def test_valid_from_value_error(self):
        with self.assertRaises(ValueError):
            self.builder.set_valid_from(datetime.date.today())

    def test_valid_to_value_error(self):
        with self.assertRaises(ValueError):
            self.builder.set_valid_to(datetime.date.today())

    def test_all_parameters_provided(self):
        username = 'FOO'
        first_name = 'First'
        last_name = 'Last'
        email_address = 'email@example.org'
        password = 'Password'
        alias = 'HTTP_ALIAS'
        typ = 'S'
        group = 'DEVELOPER'
        start_date = '20200101'
        end_date = '20201231'

        self.assertEqual(self.builder, self.builder.set_username(username))
        self.assertEqual(self.builder, self.builder.set_first_name(first_name))
        self.assertEqual(self.builder, self.builder.set_last_name(last_name))
        self.assertEqual(self.builder, self.builder.set_email_address(email_address))
        self.assertEqual(self.builder, self.builder.set_password(password))
        self.assertEqual(self.builder, self.builder.set_alias(alias))
        self.assertEqual(self.builder, self.builder.set_type(typ))
        self.assertEqual(self.builder, self.builder.set_group(group))
        self.assertEqual(self.builder, self.builder.set_valid_from(start_date))
        self.assertEqual(self.builder, self.builder.set_valid_to(end_date))

        params = self.builder.build_rfc_params()

        self.assertEqual(params, {
            'USERNAME': username,
            'ALIAS': {
                'USERALIAS': alias
            },
            'ADDRESS': {
                'FIRSTNAME': first_name,
                'LASTNAME': last_name,
                'E_MAIL': email_address
            },
            'PASSWORD': {
                'BAPIPWD': password
            },
            'LOGONDATA': {
                'USTYP': typ,
                'CLASS': group,
                'GLTGV': start_date,
                'GLTGB': end_date
            }
        })

    def test_change_parameters_password(self):
        username = 'FOO'
        password = 'Password'

        self.assertEqual(self.builder, self.builder.set_username(username))
        self.assertEqual(self.builder, self.builder.set_password(password))

        params = self.builder.build_change_rfc_params()

        self.assertEqual(params, {
            'USERNAME': username,
            'PASSWORD': {
                'BAPIPWD': password
            },
            'PASSWORDX': {
                'BAPIPWD': 'X'
            }
        })

    def test_change_parameters_no_password(self):
        username = 'FOO'

        self.assertEqual(self.builder, self.builder.set_username(username))

        params = self.builder.build_change_rfc_params()

        self.assertEqual(params, {
            'USERNAME': username,
        })

    def test_change_parameters_alias(self):
        username = 'FOO'
        alias = 'FOOBAR'

        self.assertEqual(self.builder, self.builder.set_username(username))
        self.assertEqual(self.builder, self.builder.set_alias(alias))

        params = self.builder.build_change_rfc_params()

        self.assertEqual(params, {
            'USERNAME': username,
            'ALIAS': {
                'USERALIAS': alias
            },
            'ALIASX': {
                'BAPIALIAS': 'X'
            }
        })


class TestUserRoleAssignmentBuilder(unittest.TestCase):

    def setUp(self):
        self.username = 'LOGON'
        self.builder = UserRoleAssignmentBuilder(self.username)

    def test_no_parameters_provided(self):
        params = self.builder.build_rfc_params()
        self.assertIsNone(params)

    def test_all_parameters_provided(self):
        self.assertEqual(self.builder, self.builder.add_roles(['1', '2', '3']))

        params = self.builder.build_rfc_params()

        start_date = today_sap_date()
        self.maxDiff = None
        self.assertEqual(params, {
            'USERNAME': self.username,
            'ACTIVITYGROUPS': [
                {'AGR_NAME': '1',
                 'FROM_DAT': start_date,
                 'TO_DAT': '20991231'
                },
                {'AGR_NAME': '2',
                 'FROM_DAT': start_date,
                 'TO_DAT': '20991231'
                },
                {'AGR_NAME': '3',
                 'FROM_DAT': start_date,
                 'TO_DAT': '20991231'
                }
            ]
        })


class TestUserProfileAssignmentBuilder(unittest.TestCase):

    def setUp(self):
        self.username = 'LOGON'
        self.builder = UserProfileAssignmentBuilder(self.username)

    def test_no_parameters_provided(self):
        params = self.builder.build_rfc_params()
        self.assertIsNone(params)

    def test_all_parameters_provided(self):
        self.assertEqual(self.builder, self.builder.add_profiles(['1', '2', '3']))

        params = self.builder.build_rfc_params()

        start_date = today_sap_date()
        self.maxDiff = None
        self.assertEqual(params, {
            'USERNAME': self.username,
            'PROFILES': [
                {'BAPIPROF': '1',
                },
                {'BAPIPROF': '2',
                },
                {'BAPIPROF': '3',
                }
            ]
        })


class TestUserManager(unittest.TestCase):

    def setUp(self):
        self.bapirettab = []
        self.response = {'RETURN': self.bapirettab}

        self.connection = Mock()
        self.connection.call = Mock()
        self.connection.call.return_value = self.response

        self.username = 'logon'
        self.manager = UserManager()

    def test_user_builder(self):
        self.assertIsNotNone(self.manager.user_builder())

    def test_user_role_assignment_builder(self):
        builder = self.manager.user_role_assignment_builder(self.username)
        self.assertIsNotNone(builder)
        self.assertEqual(builder._user, self.username)

    def test_user_profile_assignment_builder(self):
        builder = self.manager.user_profile_assignment_builder(self.username)
        self.assertIsNotNone(builder)
        self.assertEqual(builder._user, self.username)

    def test_create_user_no_error(self):
        user_builder = self.manager.user_builder()
        user_builder.set_username(self.username)

        self.bapirettab.append(create_bapiret_info('Created'))

        retval = self.manager.create_user(self.connection, user_builder)

        self.connection.call.assert_called_once_with('BAPI_USER_CREATE1', **user_builder.build_rfc_params())

        self.assertEqual(str(retval), str(BAPIReturn(self.bapirettab)))

    def test_create_user_with_error(self):
        user_builder = self.manager.user_builder()
        user_builder.set_username(self.username)

        self.bapirettab.append(create_bapiret_error('Error message'))

        with self.assertRaises(BAPIError) as caught:
            self.manager.create_user(self.connection, user_builder)

        self.connection.call.assert_called_once()

        self.assertEqual(str(caught.exception), 'Error(ERR|333): Error message')
        self.assertEqual(caught.exception.response, self.response)

    def test_assign_roles_no_error(self):
        builder = self.manager.user_role_assignment_builder(self.username)

        builder.add_roles(['foo'])

        self.manager.assign_roles(self.connection, builder)

        self.connection.call.assert_called_once_with('BAPI_USER_ACTGROUPS_ASSIGN', **builder.build_rfc_params())

    def test_assign_profiles_no_error(self):
        builder = self.manager.user_profile_assignment_builder(self.username)

        builder.add_profiles(['foo'])

        self.manager.assign_profiles(self.connection, builder)

        self.connection.call.assert_called_once_with('BAPI_USER_PROFILES_ASSIGN', **builder.build_rfc_params())

    def test_fetch_user_ok(self):
        retval = self.manager.fetch_user_details(self.connection, 'KAJ')

        self.connection.call.assert_called_once_with('BAPI_USER_GET_DETAIL', USERNAME='KAJ')
        self.assertEqual(retval, self.connection.call.return_value)

    def test_fetch_user_fail(self):
        self.bapirettab.append(create_bapiret_error('Error message'))

        with self.assertRaises(BAPIError) as caught:
            self.manager.fetch_user_details(self.connection, 'KAJ')

    def test_change_user_ok(self):
        user_builder = self.manager.user_builder()
        user_builder.set_username(self.username)

        self.bapirettab.append(create_bapiret_info('Changed'))

        retval = self.manager.change_user(self.connection, user_builder)

        self.assertEqual(self.connection.call.call_count, 2)

        self.connection.call.assert_has_calls([call('BAPI_USER_GET_DETAIL', USERNAME=user_builder.get_username()),
                                               call('BAPI_USER_CHANGE', **user_builder.build_change_rfc_params())])

        self.assertEqual(str(retval), str(BAPIReturn(self.bapirettab)))

    def test_create_user_and_set_productive_pass_ok(self):
        user_builder = self.manager.user_builder()
        user_builder.set_username(self.username)
        user_builder.set_productive_password(True)
        user_builder.set_password('UnitTestPass')
        user_builder.set_type('A')

        self.bapirettab.append(create_bapiret_info('Created'))

        mock_message_pwd_changed = {'TYPE': 'S', 'ID': 'NFO', 'NUMBER': '777', 'MESSAGE': 'Password Changed'}

        with patch('sap.rfc.user.UserManager._call_user_change_password', return_value={'RETURN': mock_message_pwd_changed}) as mock_call_user_change_pwd:
            retval = self.manager.create_user(self.connection, user_builder)

        mock_call_user_change_pwd.assert_called_once()

        self.connection.call.assert_called_once_with('BAPI_USER_CREATE1', **user_builder.build_rfc_params())

        self.assertEqual(str(retval), str(BAPIReturn(self.bapirettab)))

    def test_change_user_and_set_productive_pass_ok(self):
        user_builder = self.manager.user_builder()
        user_builder.set_username(self.username)
        user_builder.set_productive_password(True)
        user_builder.set_password('UnitTestPass')

        self.bapirettab.append(create_bapiret_info('Changed'))

        mock_message_pwd_changed = {'TYPE': 'S', 'ID': 'NFO', 'NUMBER': '777', 'MESSAGE': 'Password Changed'}

        with patch('sap.rfc.user.UserManager.fetch_user_details', return_value={'LOGONDATA': {'USTYP': 'A'}}) as mock_fetch_user_details, \
             patch('sap.rfc.user.UserManager._call_user_change_password', return_value={'RETURN': mock_message_pwd_changed}) as mock_call_user_change_pwd:
            retval = self.manager.change_user(self.connection, user_builder)

        mock_fetch_user_details.assert_called_once()
        mock_call_user_change_pwd.assert_called_once()

        self.connection.call.assert_called_once_with('BAPI_USER_CHANGE', USERNAME='logon', PASSWORD={'BAPIPWD': 'DummyPwd123!'}, PASSWORDX={'BAPIPWD': 'X'})

        self.assertEqual(str(retval), str(BAPIReturn(self.bapirettab)))

    def test_change_user_fail(self):
        user_builder = self.manager.user_builder()
        user_builder.set_username(self.username)

        self.bapirettab.append(create_bapiret_error('Error message'))

        with self.assertRaises(BAPIError) as caught:
            self.manager.change_user(self.connection, user_builder)
