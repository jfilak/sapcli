"""User management over RFC"""

import datetime
from copy import deepcopy

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


def add_to_dict_or_merge(target_dict, target_key, value_dict):
    """Adds the given value to the give dict as the given key
       if the key is not in the give target dict, otherwise
       assume the dict value is a dictionary and attempt to merge
       wit the give value.
    """

    try:
        target_dict[target_key].update(value_dict)
    except KeyError:
        target_dict[target_key] = value_dict


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


class UserBuilder:
    """An utility class for building SAP user parameters"""

    def __init__(self, template: RFCParams=None):
        self._template = template
        self._username = None
        self._address = None
        self._logondata = None
        self._password = None
        self._alias = None

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

    def set_template(self, template: RFCParams):
        """Sets the default RFC params"""

        old = self._template
        self._template = template
        return old

    @property
    def username(self) -> str:
        """Returns user name for logon"""

        return self._username

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
        return self

    def set_alias(self, alias: str):
        """Sets user's alias for HTTP authentication"""

        if alias is None:
            alias = ""

        self._alias_data['USERALIAS'] = alias

        return self

    def set_type(self, typ: str):
        """Sets user's type"""

        self._logondata_data['USTYP'] = typ
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

    def _rfc_params_add_username(self, params):
        add_to_dict_if_not_none(params, 'USERNAME', self._username)

    def _rfc_params_add_password(self, params):
        password = copy_dict_or_new(self._password)
        add_to_dict_if_not_present(password, 'BAPIPWD', '')
        params['PASSWORD'] = password

    def build_rfc_params(self) -> RFCParams:
        """Creates RFC parameters for Creating users"""

        params = dict() if self._template is None else deepcopy(self._template)

        self._rfc_params_add_username(params)

        address = copy_dict_or_new(self._address)
        add_to_dict_if_not_present(address, 'FIRSTNAME', '')
        add_to_dict_if_not_present(address, 'LASTNAME', '')
        add_to_dict_if_not_present(address, 'E_MAIL', '')
        add_to_dict_or_merge(params, 'ADDRESS', address)

        self._rfc_params_add_password(params)

        alias = copy_dict_or_new(self._alias)
        add_to_dict_if_not_present(alias, 'USERALIAS', '')
        add_to_dict_or_merge(params, 'ALIAS', alias)

        logondata = copy_dict_or_new(self._logondata_data)
        add_to_dict_if_not_present(logondata, 'GLTGV', today_sap_date())
        add_to_dict_if_not_present(logondata, 'GLTGB', '20991231')
        add_to_dict_or_merge(params, 'LOGONDATA', logondata)

        return params

    def build_change_rfc_params(self) -> RFCParams:
        """Create RFC parameters fro Updating user"""

        params: RFCParams = {}
        self._rfc_params_add_username(params)

        if self._password:
            self._rfc_params_add_password(params)
            params['PASSWORDX'] = {'BAPIPWD': 'X'}

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

    @staticmethod
    def get_rfc_call_dict(user, rfc_roles) -> RFCParams:
        return {
            'USERNAME': user,
            'ACTIVITYGROUPS': rfc_roles
        }

    def build_rfc_params(self) -> RFCParams:
        """Creates RFC parameters"""

        if not self._roles:
            return None

        rfc_table = []

        for role_name in self._roles:
            table_row = {'AGR_NAME': role_name}

            add_to_dict_if_not_present(table_row, 'FROM_DAT', today_sap_date())
            add_to_dict_if_not_present(table_row, 'TO_DAT', '20991231')

            rfc_table.append(table_row)

        return UserRoleAssignmentBuilder.get_rfc_call_dict(self._user, rfc_table)


class UserProfileAssignmentBuilder:
    """An utility class for building SAP user profiles assignment parameters"""

    def __init__(self, user):
        self._user = user
        self._profiles = []

    def add_profiles(self, profile_names: List[str]):
        """Set assigned profiles name"""

        self._profiles = profile_names
        return self

    @staticmethod
    def get_rfc_call_dict(user, rfc_profiles) -> RFCParams:
        return {
            'USERNAME': user,
            'PROFILES': rfc_profiles
        }

    def build_rfc_params(self) -> RFCParams:
        """Creates RFC parameters"""

        if not self._profiles:
            return None

        rfc_table = []

        for profile_name in self._profiles:
            table_row = {'BAPIPROF': profile_name}
            rfc_table.append(table_row)

        return UserProfileAssignmentBuilder.get_rfc_call_dict(self._user, rfc_table)


class UserManager:
    """Proxy to SAP API managing Users"""

    # pylint: disable=no-self-use
    def _call_bapi_method(self, connection, method_name, kwargs):
        resp = connection.call(method_name, **kwargs)
        BAPIError.raise_for_error(resp['RETURN'], resp)
        return resp

    # pylint: disable=no-self-use
    def user_builder(self) -> UserBuilder:
        """Returns instance of User Parameters builder"""

        return UserBuilder()

    def fetch_user_details(self, connection, username: UserId) -> dict:
        """Creates a new user for the given user data"""

        return self._call_bapi_method(connection,
                                      'BAPI_USER_GET_DETAIL',
                                      {'USERNAME': username})

    def _create_user_with_params(self, connection, params: RFCParams):
        """Creates a new user for the given user data"""

        rfc_ret = self._call_bapi_method(connection, 'BAPI_USER_CREATE1', params)
        return BAPIReturn(rfc_ret['RETURN'])

    def create_user(self, connection, user_builder: UserBuilder) -> UserId:
        """Creates a new user for the given user data"""

        return self._create_user_with_params(connection, user_builder.build_rfc_params())

    def change_user(self, connection, user_builder: UserBuilder) -> UserId:
        """Updates user with the given user data"""

        rfc_ret = self._call_bapi_method(connection, 'BAPI_USER_CHANGE', user_builder.build_change_rfc_params())
        return BAPIReturn(rfc_ret['RETURN'])

    def copy_user(self, connection, orig_name: UserId, user_builder: UserBuilder):
        """Fetches the user orig_name and creates the user new_name
        """

        orig_data = self.fetch_user_details(connection, orig_name)

        del orig_data['ADMINDATA']
        del orig_data['IDENTITY']
        del orig_data['ISLOCKED']
        del orig_data['LASTMODIFIED']
        del orig_data['SYSTEMS']
        del orig_data['UCLASSSYS']

        logondata = orig_data['LOGONDATA']
        del logondata['PASSCODE']
        del logondata['PWDSALTEDHASH']

        roles = orig_data['ACTIVITYGROUPS']
        del orig_data['ACTIVITYGROUPS']

        profiles = orig_data['PROFILES']
        del orig_data['PROFILES']

        user_builder.set_template(orig_data)

        bapi_ret = self.create_user(connection, user_builder)

        if bapi_ret.is_error:
            return bapi_ret

        if roles:
            self._call_assign_roles(
                connection,
                UserRoleAssignmentBuilder.get_rfc_call_dict(
                    user_builder.username,
                    roles
                ))

        if profiles:
            self._call_assign_profiles(
                connection,
                UserProfileAssignmentBuilder.get_rfc_call_dict(
                    user_builder.username,
                    profiles
                ))


    # pylint: disable=no-self-use
    def user_role_assignment_builder(self, username: str) -> UserRoleAssignmentBuilder:
        """Returns instance of User Role Assignment builder"""

        return UserRoleAssignmentBuilder(username)

    def _call_assign_roles(self, connection, roles: RFCParams) -> None:
        """Assigns roles"""

        self._call_bapi_method(connection, 'BAPI_USER_ACTGROUPS_ASSIGN', roles)

    def assign_roles(self, connection, roles_builder: UserRoleAssignmentBuilder) -> None:
        """Assigns roles"""

        self._call_bapi_method(connection, roles_builder.build_rfc_params())

    # pylint: disable=no-self-use
    def user_profile_assignment_builder(self, username: str) -> UserProfileAssignmentBuilder:
        """Returns instance of User Profile Assignment builder"""

        return UserProfileAssignmentBuilder(username)

    def _call_assign_profiles(self, connection, profiles: RFCParams) -> None:
        """Assigns profiles"""

        self._call_bapi_method(connection, 'BAPI_USER_PROFILES_ASSIGN', profiles)

    def assign_profiles(self, connection, profiles_builder: UserProfileAssignmentBuilder) -> None:
        """Assigns profiles"""

        self._call_bapi_method(connection, profiles_builder.build_rfc_params())
