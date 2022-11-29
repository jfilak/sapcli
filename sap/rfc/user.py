"""User management over RFC"""

import datetime

from typing import Dict, Optional, Union, List

from sap.rfc.core import RFCParams
from sap.rfc.bapi import (
    BAPIError,
    BAPIReturn
)


UserId = str
UserAddress = Dict[str, str]


def add_to_dict_if_not_none(target_dict, target_key, value):
    """Adds the given value to the give dict as the given key
       only if the given value is not None.
    """

    if value is None:
        return False

    target_dict[target_key] = value
    return True


def add_to_dict_if_not_present(target_dict, target_key, value):
    """Adds the given value to the give dict as the given key
       only if the given key is not in the given dict yet.
    """

    if target_key in target_dict:
        return False

    target_dict[target_key] = value
    return True


def copy_dict_or_new(original: dict) -> dict:
    """Makes a copy of the original dict if not None;
       otherwise returns an empty dict.
    """

    if original is None:
        return {}

    return dict(original)


def sap_date_from(the_date: datetime.date) -> str:
    """Converts Python date to string"""

    return the_date.strftime('%Y%m%d')


def today_sap_date() -> str:
    """Returns SAP date string for today"""

    return sap_date_from(datetime.date.today())


class UserPasswordManager:
    """An utility class for handling productive password"""

    DUMMY_PASSWORD = 'DummyPwd123!'

    def __init__(self):
        self._use_productive_password = None
        self._password = None
        self._user_type = None

    def get_use_productive_password(self) -> bool:
        """Get if new password should be productive or not"""

        return self._use_productive_password

    def get_password(self) -> str:
        """Get user's new password"""

        return self._password

    def get_user_type(self) -> str:
        """Get user type"""

        return self._user_type

    def set_use_productive_password(self, use_productive_password: bool):
        """Set if new password should be productive or not"""

        self._use_productive_password = use_productive_password
        return self._use_productive_password

    def set_password(self, password):
        """Set user's new password"""

        self._password = password
        return self._password

    def set_user_type(self, user_type: str):
        """Set user type"""

        self._user_type = user_type
        return self._user_type

    def is_productive_password_requested(self) -> bool:
        """Is it requested to use a productive password for Dialog or Communications Data user"""

        return \
            self.get_use_productive_password() and \
            self.get_password() and \
            self.get_user_type() in ['A', 'C']     # A = Dialog, C = Communications Data


class UserBuilder:
    """An utility class for building SAP user parameters"""

    def __init__(self):
        self._username = None
        self._address = None
        self._logondata = None
        self._password = None
        self._alias = None
        self._userPasswordManager = UserPasswordManager()

    @property
    def _address_data(self) -> UserAddress:
        if self._address is None:
            self._address = {}

        return self._address

    @property
    def _password_data(self) -> Dict[str, str]:
        if self._password is None:
            self._password = {}

        return self._password

    @property
    def _alias_data(self) -> Dict[str, str]:
        if self._alias is None:
            self._alias = {}

        return self._alias

    @property
    def _logondata_data(self) -> Dict[str, str]:
        if self._logondata is None:
            self._logondata = {}

        return self._logondata

    def set_username(self, username: str):
        """Sets user name for logon"""

        self._username = username
        return self

    def set_first_name(self, first_name: str):
        """Sets user's first name"""

        self._address_data['FIRSTNAME'] = first_name
        return self

    def set_last_name(self, last_name: str):
        """Sets user's last name"""

        self._address_data['LASTNAME'] = last_name
        return self

    def set_email_address(self, email_address: str):
        """Sets user's email address"""

        self._address['E_MAIL'] = email_address
        return self

    def set_password(self, password: str):
        """Sets user's password - works only for the user type Service"""

        self._password_data['BAPIPWD'] = password
        self._userPasswordManager.set_password(password)
        return self

    def set_alias(self, alias: str):
        """Sets user's alias for HTTP authentication"""

        self._alias_data['USERALIAS'] = alias
        return self

    def set_type(self, typ: str):
        """Sets user's type"""

        self._logondata_data['USTYP'] = typ
        self._userPasswordManager.set_user_type(typ)
        return self

    def set_group(self, group: str):
        """Sets user group"""

        self._logondata_data['CLASS'] = group
        return self

    def set_valid_from(self, start_date: Union[str]):
        """Sets user's start validity date"""

        if isinstance(start_date, str):
            self._logondata_data['GLTGV'] = start_date
        else:
            raise ValueError()

        return self

    def set_valid_to(self, end_date: Union[str]):
        """Sets user's end validity date"""

        if isinstance(end_date, str):
            self._logondata_data['GLTGB'] = end_date
        else:
            raise ValueError()

        return self

    def set_productive_password(self, productive_password: bool):
        """Set productive password flag"""

        self._userPasswordManager.set_use_productive_password(productive_password)
        return self

    def get_username(self) -> str:
        """Get user's name"""

        return self._username

    def get_user_password_manager(self) -> UserPasswordManager:
        """Set user's password status"""

        return self._userPasswordManager

    def _rfc_params_add_username(self, params):
        add_to_dict_if_not_none(params, 'USERNAME', self._username)

    def _rfc_params_add_password(self, params):
        if self._userPasswordManager.is_productive_password_requested():
            password = copy_dict_or_new({'BAPIPWD': self._userPasswordManager.DUMMY_PASSWORD})
            add_to_dict_if_not_present(password, 'BAPIPWD', '')
            params['PASSWORD'] = password
        else:
            password = copy_dict_or_new(self._password)
            add_to_dict_if_not_present(password, 'BAPIPWD', '')
            params['PASSWORD'] = password

    def _rfc_params_add_alias(self, params):
        alias = copy_dict_or_new(self._alias)
        add_to_dict_if_not_present(alias, 'USERALIAS', '')
        params['ALIAS'] = alias

    def build_rfc_params(self) -> RFCParams:
        """Creates RFC parameters for Creating users"""

        params: RFCParams = {}

        self._rfc_params_add_username(params)

        address = copy_dict_or_new(self._address)
        add_to_dict_if_not_present(address, 'FIRSTNAME', '')
        add_to_dict_if_not_present(address, 'LASTNAME', '')
        add_to_dict_if_not_present(address, 'E_MAIL', '')
        params['ADDRESS'] = address

        self._rfc_params_add_password(params)

        self._rfc_params_add_alias(params)

        logondata = copy_dict_or_new(self._logondata_data)
        add_to_dict_if_not_present(logondata, 'GLTGV', today_sap_date())
        add_to_dict_if_not_present(logondata, 'GLTGB', '20991231')
        params['LOGONDATA'] = logondata

        return params

    def build_change_rfc_params(self) -> RFCParams:
        """Create RFC parameters fro Updating user"""

        params: RFCParams = {}
        self._rfc_params_add_username(params)

        if self._password:
            self._rfc_params_add_password(params)
            params['PASSWORDX'] = {'BAPIPWD': 'X'}

        if self._alias:
            self._rfc_params_add_alias(params)
            params['ALIASX'] = {'BAPIALIAS': 'X'}

        return params


class UserRoleAssignmentBuilder:
    """An utility class for building SAP user roles assignment parameters"""

    def __init__(self, user):
        self._user = user
        self._roles = []

    def add_roles(self, role_names: List[str]):
        """Set assigned roles name"""

        self._roles = role_names
        return self

    def build_rfc_params(self) -> Optional[RFCParams]:
        """Creates RFC parameters"""

        if not self._roles:
            return None

        rfc_table = []

        for role_name in self._roles:
            table_row = {'AGR_NAME': role_name}

            add_to_dict_if_not_present(table_row, 'FROM_DAT', today_sap_date())
            add_to_dict_if_not_present(table_row, 'TO_DAT', '20991231')

            rfc_table.append(table_row)

        return {
            'USERNAME': self._user,
            'ACTIVITYGROUPS': rfc_table
        }


class UserProfileAssignmentBuilder:
    """An utility class for building SAP user profiles assignment parameters"""

    def __init__(self, user):
        self._user = user
        self._profiles = []

    def add_profiles(self, profile_names: List[str]):
        """Set assigned profiles name"""

        self._profiles = profile_names
        return self

    def build_rfc_params(self) -> Optional[RFCParams]:
        """Creates RFC parameters"""

        if not self._profiles:
            return None

        rfc_table = []

        for profile_name in self._profiles:
            table_row = {'BAPIPROF': profile_name}
            rfc_table.append(table_row)

        return {
            'USERNAME': self._user,
            'PROFILES': rfc_table
        }


class UserManager:
    """Proxy to SAP API managing Users"""

    def _call_bapi_method(self, connection, method_name, kwargs):
        resp = connection.call(method_name, **kwargs)
        BAPIError.raise_for_error(resp['RETURN'], resp)
        return resp

    def _call_user_change_password(self, connection, params):
        return self._call_bapi_method(connection, 'SUSR_USER_CHANGE_PASSWORD_RFC', params)

    def _fetch_user_type(self, connection, username: UserId) -> str:
        bapi_return = self.fetch_user_details(connection, username)
        return bapi_return.get('LOGONDATA', {}).get('USTYP', '')

    def _change_user_password(self, connection, user_builder: UserBuilder) -> dict:
        user_pass_mgr = user_builder.get_user_password_manager()

        if user_pass_mgr.is_productive_password_requested():
            change_password_param = {
                'BNAME': user_builder.get_username(),
                'PASSWORD': user_pass_mgr.DUMMY_PASSWORD,
                'NEW_PASSWORD': user_pass_mgr.get_password(),
                'USE_BAPI_RETURN': 1
            }
            rfc_bapi_ret = self._call_user_change_password(connection, change_password_param)
            return rfc_bapi_ret['RETURN']

        return None

    def user_builder(self) -> UserBuilder:
        """Returns instance of User Parameters builder"""

        return UserBuilder()

    def fetch_user_details(self, connection, username: UserId) -> dict:
        """Creates a new user for the given user data"""

        return self._call_bapi_method(connection,
                                      'BAPI_USER_GET_DETAIL',
                                      {'USERNAME': username})

    def create_user(self, connection, user_builder: UserBuilder) -> BAPIReturn:
        """Creates a new user for the given user data"""

        rfc_ret = self._call_bapi_method(connection, 'BAPI_USER_CREATE1', user_builder.build_rfc_params())
        result = rfc_ret['RETURN']

        if not BAPIReturn(result).is_error:
            rfc_password_change_ret = self._change_user_password(connection, user_builder)
            if rfc_password_change_ret:
                result.append(rfc_password_change_ret)

        return BAPIReturn(result)

    def change_user(self, connection, user_builder: UserBuilder) -> BAPIReturn:
        """Updates user with the given user data"""

        rfc_user_type = self._fetch_user_type(connection, user_builder.get_username())
        user_pass_mgr = user_builder.get_user_password_manager()
        user_pass_mgr.set_user_type(rfc_user_type)

        rfc_ret = self._call_bapi_method(connection, 'BAPI_USER_CHANGE', user_builder.build_change_rfc_params())
        result = rfc_ret['RETURN']

        if not BAPIReturn(result).is_error:
            rfc_password_change_ret = self._change_user_password(connection, user_builder)
            if rfc_password_change_ret:
                result.append(rfc_password_change_ret)

        return BAPIReturn(result)

    def user_role_assignment_builder(self, username: str) -> UserRoleAssignmentBuilder:
        """Returns instance of User Role Assignment builder"""

        return UserRoleAssignmentBuilder(username)

    def assign_roles(self, connection, roles_builder: UserRoleAssignmentBuilder) -> None:
        """Assigns roles"""

        self._call_bapi_method(connection, 'BAPI_USER_ACTGROUPS_ASSIGN', roles_builder.build_rfc_params())

    def user_profile_assignment_builder(self, username: str) -> UserProfileAssignmentBuilder:
        """Returns instance of User Profile Assignment builder"""

        return UserProfileAssignmentBuilder(username)

    def assign_profiles(self, connection, profiles_builder: UserProfileAssignmentBuilder) -> None:
        """Assigns profiles"""

        self._call_bapi_method(connection, 'BAPI_USER_PROFILES_ASSIGN', profiles_builder.build_rfc_params())
