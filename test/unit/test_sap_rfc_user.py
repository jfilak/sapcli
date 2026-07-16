#!/usr/bin/env python3

import datetime

import unittest
from unittest.mock import Mock, call, patch

from sap.errors import SAPCliError
from sap.rfc.bapi import BAPIError, BAPIReturn
from sap.rfc.user import add_to_dict_if_not_none, add_to_dict_if_not_present, today_sap_date, \
         UserBuilder, UserRoleAssignmentBuilder, UserProfileAssignmentBuilder, UserManager, \
         UserPasswordManager

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
             'PASSWORD': {'BAPIPWD': ''},
             'SNC': {}
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
            'SNC': {},
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

    def test_set_snc_methods_return_self(self):
        self.assertEqual(self.builder, self.builder.set_snc_name('p:CN=FOO'))
        self.assertEqual(self.builder, self.builder.set_snc_permit_password(True))

    def test_email_address_only(self):
        # set_email_address must not crash when called before other
        # address setters (regression: it used self._address directly).
        self.assertEqual(self.builder, self.builder.set_email_address('email@example.org'))

        params = self.builder.build_rfc_params()

        self.assertEqual(params['ADDRESS'], {
            'FIRSTNAME': '',
            'LASTNAME': '',
            'E_MAIL': 'email@example.org'
        })

    def test_create_parameters_with_snc(self):
        username = 'FOO'
        snc_name = 'p:CN=FOO, OU=Bar, O=Example, C=US'

        self.builder.set_username(username)
        self.builder.set_snc_name(snc_name)
        self.builder.set_snc_permit_password(True)

        params = self.builder.build_rfc_params()

        self.assertEqual(params['SNC'], {
            'PNAME': snc_name,
            'GUIFLAG': 'X'
        })

    def test_change_parameters_snc_name_only(self):
        username = 'FOO'
        snc_name = 'p:CN=FOO'

        self.builder.set_username(username)
        self.builder.set_snc_name(snc_name)

        params = self.builder.build_change_rfc_params()

        self.assertEqual(params, {
            'USERNAME': username,
            'SNC': {
                'PNAME': snc_name
            },
            'SNCX': {
                'PNAME': 'X'
            }
        })

    def test_change_parameters_snc_permit_password_true(self):
        username = 'FOO'

        self.builder.set_username(username)
        self.builder.set_snc_permit_password(True)

        params = self.builder.build_change_rfc_params()

        self.assertEqual(params, {
            'USERNAME': username,
            'SNC': {
                'GUIFLAG': 'X'
            },
            'SNCX': {
                'GUIFLAG': 'X'
            }
        })

    def test_change_parameters_snc_permit_password_false(self):
        username = 'FOO'

        self.builder.set_username(username)
        self.builder.set_snc_permit_password(False)

        params = self.builder.build_change_rfc_params()

        # Turning the flag off must still be transmitted (SNCX marks it as
        # modified) but with an empty value.
        self.assertEqual(params, {
            'USERNAME': username,
            'SNC': {
                'GUIFLAG': ''
            },
            'SNCX': {
                'GUIFLAG': 'X'
            }
        })

    def test_change_parameters_snc_name_and_permit_password(self):
        username = 'FOO'
        snc_name = 'p:CN=FOO'

        self.builder.set_username(username)
        self.builder.set_snc_name(snc_name)
        self.builder.set_snc_permit_password(True)

        params = self.builder.build_change_rfc_params()

        self.assertEqual(params, {
            'USERNAME': username,
            'SNC': {
                'PNAME': snc_name,
                'GUIFLAG': 'X'
            },
            'SNCX': {
                'PNAME': 'X',
                'GUIFLAG': 'X'
            }
        })

    def test_change_parameters_no_snc(self):
        username = 'FOO'

        self.builder.set_username(username)

        params = self.builder.build_change_rfc_params()

        self.assertNotIn('SNC', params)
        self.assertNotIn('SNCX', params)

    def test_change_snc_params_are_copies(self):
        # build_change_rfc_params must not leak the builder's internal
        # mutable SNCX dict to the caller.
        self.builder.set_username('FOO')
        self.builder.set_snc_name('p:CN=FOO')

        params = self.builder.build_change_rfc_params()
        params['SNCX']['PNAME'] = 'TAMPERED'

        fresh_params = self.builder.build_change_rfc_params()
        self.assertEqual(fresh_params['SNCX'], {'PNAME': 'X'})

    def test_new_setters_return_self(self):
        self.assertEqual(self.builder, self.builder.set_reference_user('REF'))
        self.assertEqual(self.builder, self.builder.set_security_policy('POLICY'))
        self.assertEqual(self.builder, self.builder.set_company('COMP'))
        self.assertEqual(self.builder, self.builder.set_company_template_orgtype(True))
        self.assertEqual(self.builder, self.builder.set_sapuser_uuid('UUID'))

    # -- REF_USER -----------------------------------------------------------

    def test_create_parameters_with_reference_user(self):
        self.builder.set_username('FOO')
        self.builder.set_reference_user('TEMPLATE')

        params = self.builder.build_rfc_params()

        self.assertEqual(params['REF_USER'], {'REF_USER': 'TEMPLATE'})
        self.assertNotIn('REF_USERX', params)

    def test_change_parameters_with_reference_user(self):
        self.builder.set_username('FOO')
        self.builder.set_reference_user('TEMPLATE')

        params = self.builder.build_change_rfc_params()

        self.assertEqual(params, {
            'USERNAME': 'FOO',
            'REF_USER': {'REF_USER': 'TEMPLATE'},
            'REF_USERX': {'REF_USER': 'X'}
        })

    def test_change_parameters_no_reference_user(self):
        self.builder.set_username('FOO')

        params = self.builder.build_change_rfc_params()

        self.assertNotIn('REF_USER', params)
        self.assertNotIn('REF_USERX', params)

    # -- LOGONDATA.SECURITY_POLICY ------------------------------------------

    def test_create_parameters_with_security_policy(self):
        self.builder.set_username('FOO')
        self.builder.set_security_policy('SECPOL')

        params = self.builder.build_rfc_params()

        self.assertEqual(params['LOGONDATA']['SECURITY_POLICY'], 'SECPOL')

    def test_change_parameters_with_security_policy(self):
        self.builder.set_username('FOO')
        self.builder.set_security_policy('SECPOL')

        params = self.builder.build_change_rfc_params()

        # Only the explicitly modified LOGONDATA field must be transmitted so
        # that the validity dates and other fields are not reset.
        self.assertEqual(params, {
            'USERNAME': 'FOO',
            'LOGONDATA': {'SECURITY_POLICY': 'SECPOL'},
            'LOGONDATAX': {'SECURITY_POLICY': 'X'}
        })

    def test_change_parameters_security_policy_does_not_leak_validity(self):
        self.builder.set_username('FOO')
        self.builder.set_valid_to('20301231')
        self.builder.set_security_policy('SECPOL')

        params = self.builder.build_change_rfc_params()

        self.assertEqual(params['LOGONDATA'], {'SECURITY_POLICY': 'SECPOL'})
        self.assertEqual(params['LOGONDATAX'], {'SECURITY_POLICY': 'X'})

    def test_change_parameters_no_security_policy(self):
        self.builder.set_username('FOO')

        params = self.builder.build_change_rfc_params()

        self.assertNotIn('LOGONDATA', params)
        self.assertNotIn('LOGONDATAX', params)

    # -- COMPANY ------------------------------------------------------------

    def test_create_parameters_with_company(self):
        self.builder.set_username('FOO')
        self.builder.set_company('EXAMPLE CORP')
        self.builder.set_company_template_orgtype(True)

        params = self.builder.build_rfc_params()

        self.assertEqual(params['COMPANY'], {
            'COMPANY': 'EXAMPLE CORP',
            'TEMPLATE_ORGTYPE': 'X'
        })
        self.assertNotIn('COMPANYX', params)

    def test_create_parameters_company_template_orgtype_false(self):
        self.builder.set_username('FOO')
        self.builder.set_company('EXAMPLE CORP')
        self.builder.set_company_template_orgtype(False)

        params = self.builder.build_rfc_params()

        self.assertEqual(params['COMPANY'], {
            'COMPANY': 'EXAMPLE CORP',
            'TEMPLATE_ORGTYPE': ''
        })

    def test_change_parameters_with_company(self):
        self.builder.set_username('FOO')
        self.builder.set_company('EXAMPLE CORP')

        params = self.builder.build_change_rfc_params()

        # BAPIUSCOMX only exposes an X-flag for COMPANY (not TEMPLATE_ORGTYPE).
        self.assertEqual(params, {
            'USERNAME': 'FOO',
            'COMPANY': {'COMPANY': 'EXAMPLE CORP'},
            'COMPANYX': {'COMPANY': 'X'}
        })

    def test_change_parameters_no_company(self):
        self.builder.set_username('FOO')

        params = self.builder.build_change_rfc_params()

        self.assertNotIn('COMPANY', params)
        self.assertNotIn('COMPANYX', params)

    # -- SAPUSER_UUID -------------------------------------------------------

    def test_create_parameters_with_sapuser_uuid(self):
        self.builder.set_username('FOO')
        self.builder.set_sapuser_uuid('0123456789abcdef')

        params = self.builder.build_rfc_params()

        self.assertEqual(params['SAPUSER_UUID'], {'SAP_UID': '0123456789abcdef'})
        self.assertNotIn('SAPUSER_UUIDX', params)

    def test_change_parameters_with_sapuser_uuid(self):
        self.builder.set_username('FOO')
        self.builder.set_sapuser_uuid('0123456789abcdef')

        params = self.builder.build_change_rfc_params()

        self.assertEqual(params, {
            'USERNAME': 'FOO',
            'SAPUSER_UUID': {'SAP_UID': '0123456789abcdef'},
            'SAPUSER_UUIDX': {'SAP_UID': 'X'}
        })

    def test_change_parameters_no_sapuser_uuid(self):
        self.builder.set_username('FOO')

        params = self.builder.build_change_rfc_params()

        self.assertNotIn('SAPUSER_UUID', params)
        self.assertNotIn('SAPUSER_UUIDX', params)


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
        user_builder.set_password('UnitTestPass', True)
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
        user_builder.set_password('UnitTestPass', True)

        self.bapirettab.append(create_bapiret_info('Changed'))

        mock_message_pwd_changed = {'TYPE': 'S', 'ID': 'NFO', 'NUMBER': '777', 'MESSAGE': 'Password Changed'}

        with patch('sap.rfc.user.UserManager.fetch_user_details', return_value={'LOGONDATA': {'USTYP': 'A'}}) as mock_fetch_user_details, \
             patch('sap.rfc.user.UserManager._call_user_change_password', return_value={'RETURN': mock_message_pwd_changed}) as mock_call_user_change_pwd, \
             patch.dict('os.environ', {'SAPCLI_ABAP_USER_DUMMY_PASSWORD': 'UnitTestPass999!'}) as mock_environ:
            retval = self.manager.change_user(self.connection, user_builder)

        mock_fetch_user_details.assert_called_once()
        mock_call_user_change_pwd.assert_called_once()

        self.connection.call.assert_called_once_with('BAPI_USER_CHANGE', USERNAME='logon', PASSWORD={'BAPIPWD': 'UnitTestPass999!'}, PASSWORDX={'BAPIPWD': 'X'})

        self.assertEqual(str(retval), str(BAPIReturn(self.bapirettab)))

    def test_change_user_and_set_productive_pass_fail(self):
        same_password = 'UnitTestPass'
        
        user_builder = self.manager.user_builder()
        user_builder.set_username(self.username)
        user_builder.set_password(same_password, True)

        self.bapirettab.append(create_bapiret_info('Changed'))
        retval = None

        with patch('sap.rfc.user.UserManager.fetch_user_details', return_value={'LOGONDATA': {'USTYP': 'A'}}) as mock_fetch_user_details, \
             patch.dict('os.environ', {'SAPCLI_ABAP_USER_DUMMY_PASSWORD': same_password}) as mock_environ, \
             self.assertRaises(SAPCliError):
            retval = self.manager.change_user(self.connection, user_builder)

        self.assertIsNone(retval)

    def test_change_user_fail(self):
        user_builder = self.manager.user_builder()
        user_builder.set_username(self.username)

        self.bapirettab.append(create_bapiret_error('Error message'))

        with self.assertRaises(BAPIError) as caught:
            self.manager.change_user(self.connection, user_builder)


class TestUserPasswordManager(unittest.TestCase):

    def setUp(self):
        self.userPasswordManager = UserPasswordManager()

    def _test_wrong_use_productive_password_flag(self):
        self.userPasswordManager._use_productive_password = False
        self.userPasswordManager._password = 'UnitTest'
        self.userPasswordManager._user_type = 'A'
        self.assertEqual(self.userPasswordManager.is_productive_password_needed(), False)

    def _test_wrong_password(self):
        self.userPasswordManager._use_productive_password = True
        self.userPasswordManager._password = ''
        self.userPasswordManager._user_type = 'A'
        self.assertEqual(self.userPasswordManager.is_productive_password_needed(), False)

    def _test_wrong_user_type(self):
        self.userPasswordManager._use_productive_password = True
        self.userPasswordManager._password = 'UnitTest'
        self.userPasswordManager._user_type = 'B'
        self.assertEqual(self.userPasswordManager.is_productive_password_needed(), False)

    def _test_valid_attributes_with_user_type_A(self):
        self.userPasswordManager._use_productive_password = True
        self.userPasswordManager._password = 'UnitTest'
        self.userPasswordManager._user_type = 'A'
        self.assertEqual(self.userPasswordManager.is_productive_password_needed(), True)

    def _test_valid_attributes_with_user_type_C(self):
        self.userPasswordManager._use_productive_password = True
        self.userPasswordManager._password = 'UnitTest'
        self.userPasswordManager._user_type = 'C'
        self.assertEqual(self.userPasswordManager.is_productive_password_needed(), True)

    def test_is_productive_password_needed(self):
        self._test_wrong_use_productive_password_flag()
        self._test_wrong_password()
        self._test_wrong_user_type()
        self._test_valid_attributes_with_user_type_A()
        self._test_valid_attributes_with_user_type_C()
