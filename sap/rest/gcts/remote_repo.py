"""gCTS Remote repo wrapper"""

from enum import Enum

from sap import get_logger

from sap.rest.errors import HTTPRequestError

from sap.rest.gcts.errors import exception_from_http_error, SAPCliError


def mod_log():
    """ADT Module logger"""

    return get_logger()


def _set_configuration_key(config, key, value):
    item = next((cfg for cfg in config if cfg['key'] == key), None)
    if item:
        item['value'] = value
    else:
        config.append({'key': key, 'value': value})
    return config


def _config_list_to_dict(config):

    return dict(((cfg['key'], cfg.get('value', '')) for cfg in config))


def _config_dict_to_list(config):

    return [{'key': key, 'value': value} for key, value in config.items()]


def _http_to_gcts_error(func):

    def try_except_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPRequestError as ex:
            raise exception_from_http_error(ex) from ex

    return try_except_wrapper


class _RepositoryHttpProxy:

    def __init__(self, connection, name):
        self.url_prefix = f'repository/{name}'
        self.connection = connection

    def _build_url(self, path):
        url = self.url_prefix
        if path is not None:
            url = f'{url}/{path}'

        return url

    @_http_to_gcts_error
    def get(self, path=None, params=None):
        """Execute HTTP GET."""

        return self.connection.execute('GET', self._build_url(path), params=params)

    @_http_to_gcts_error
    def get_json(self, path=None, params=None):
        """Execute HTTP GET with Accept: application/json and get only the JSON part."""

        return self.connection.get_json(self._build_url(path), params=params)

    @_http_to_gcts_error
    def post(self, path=None):
        """Execute HTTP POST"""

        return self.connection.execute('POST', self._build_url(path))

    @_http_to_gcts_error
    def post_obj_as_json(self, path, json, accept=None):
        """Execute HTTP POST with content of the given object formatted as JSON"""

        return self.connection.post_obj_as_json(self._build_url(path), json, accept=accept)

    @_http_to_gcts_error
    def delete(self, path=None):
        """Execute HTTP DELETE"""

        return self.connection.execute('DELETE', self._build_url(path))


class RepoActivitiesQueryParams:
    """Wrapper for query parameters of repository activities call"""

    class Operation(Enum):
        """Repository activity operations"""

        COMMIT = 'COMMIT'
        PULL = 'PULL'
        CHECKOUT = 'CHECKOUT'
        CLONE = 'CLONE'

    def __init__(self):
        self._params = {}

        self.set_limit(10)
        self.set_offset(0)

    @staticmethod
    def allowed_operations():
        """Return the list of possible operations"""

        return RepoActivitiesQueryParams.Operation.__members__

    def set_limit(self, value: 'int') -> 'RepoActivitiesQueryParams':
        """Set the limit"""

        self._params['limit'] = str(value)
        return self

    def set_offset(self, value: 'int') -> 'RepoActivitiesQueryParams':
        """Set the offset"""

        self._params['offset'] = str(value)
        return self

    def set_tocommit(self, value: 'str') -> 'RepoActivitiesQueryParams':
        """Set the toCommit. If None, remove from parameters"""

        if not value:
            try:
                del self._params['toCommit']
            except KeyError:
                pass
        else:
            self._params['toCommit'] = value

        return self

    def set_fromcommit(self, value: 'str') -> 'RepoActivitiesQueryParams':
        """Set the fromCommit. If None, remove from parameters"""

        if not value:
            try:
                del self._params['fromCommit']
            except KeyError:
                pass
        else:
            self._params['fromCommit'] = value

        return self

    def set_operation(self, value: 'str') -> 'RepoActivitiesQueryParams':
        """Set the type. If None, remove from parameters"""

        if not value:
            try:
                del self._params['type']
            except KeyError:
                pass
        else:
            if value not in RepoActivitiesQueryParams.allowed_operations():
                raise SAPCliError(f'Invalid gCTS Activity Operation: {value}')

            self._params['type'] = value

        return self

    def get_params(self) -> dict:
        """Get the query parameters"""

        return self._params


# pylint: disable=R0904
class Repository:
    """A proxy to gCTS repository"""

    EDITABLE_PROPERTIES = {'name', 'rid', 'role', 'type', 'vsid', 'status', 'url'}

    def __init__(self, connection, name, data=None):
        self._http = _RepositoryHttpProxy(connection, name)
        self._name = name
        self._data = data

        self._config = None
        if self._data:
            self._config = self._data.get('config', None)

    def _fetch_data(self):
        mod_log().debug('Fetching data of the repository "%s"', self._name)

        response = self._http.get_json()

        result = response['result']

        mod_log().debug('Fetched data of the repository "%s": %s', self._name, result)

        return result

    def _update_configuration(self, key, value):
        if self._config is None:
            self._config = []

        self._config = _set_configuration_key(self._config, key, value)
        return self._config

    def _get_item(self, item, default=None, fetch=False):
        if self._data is None or fetch:
            self._data = self._fetch_data()

        return self._data.get(item, default)

    def _set_item(self, key, new_value):
        if self._get_item(key, fetch=True) == new_value:
            return None

        response = self._http.post_obj_as_json(path=None, json={key: new_value})
        self._data[key] = new_value

        return response

    def wipe_data(self):
        """Clears cached data"""

        self._data = None
        self._config = None

    @property
    def name(self):
        """Returns the repository's name"""

        return self._name

    @property
    def rid(self):
        """Returns the repository's RID"""

        return self._get_item('rid')

    @property
    def status(self):
        """Returns the repository's status"""

        return self._get_item('status')

    @property
    def vsid(self):
        """Returns the repository's vSID"""

        return self._get_item('vsid')

    @property
    def is_cloned(self):
        """Returns True if the repository is cloned, otherwise False"""

        return self.status != 'CREATED'

    @property
    def url(self):
        """Returns the repository's URL"""

        return self._get_item('url')

    @property
    def branch(self):
        """Returns the repository's current URL"""

        return self._get_item('branch')

    @property
    def head(self):
        """Returns the repository's RID"""

        return self._get_item('currentCommit')

    @property
    def configuration(self):
        """Returns the current repository configuration"""

        if self._config is None:
            self._config = self._get_item('config')

        return _config_list_to_dict(self._config)

    @property
    def role(self):
        """Returns the repository's ROLE"""

        return self._get_item('role')

    def create(self, url, vsid, config=None, role='SOURCE', typ='GITHUB'):
        """Creates the repository

           Raises:
             GCTSRequestError
             GCTSRepoAlreadyExistsError
        """

        repo = self._data or {}

        repo.update({
            'rid': self._name,
            'name': self._name,
            'vsid': vsid,
            'url': url,
            'role': role,
            'type': typ,
            'connection': 'ssl'
        })

        if config:
            repo_config = _config_list_to_dict(repo.get('config', []))
            repo_config.update(config)
            request_config = _config_dict_to_list(repo_config)
            repo['config'] = request_config

        create_request = {
            'repository': self.name,
            'data': repo
        }

        try:
            response = self._http.connection.post_obj_as_json('repository', create_request, accept='application/json')
        except HTTPRequestError as ex:
            raise exception_from_http_error(ex) from ex

        result = response.json()['repository']
        if self._data:
            self._data.update(result)
        else:
            self._data = result

    def set_config(self, key, value):
        """Sets configuration value

           Raises:
             GCTSRequestError
             GCTSRepoAlreadyExistsError
        """

        self._http.post_obj_as_json('config', {
            'key': key,
            'value': value
        })

        self._update_configuration(key, value)

    def get_config(self, key):
        """Returns configuration value

           Raises:
             GCTSRequestError
             GCTSRepoAlreadyExistsError
        """

        config = self.configuration

        if config is not None and key in config:
            return config[key]

        response = self._http.get_json(f'config/{key}')
        try:
            value = response['result']['value']
        except KeyError:
            mod_log().debug('gCTS did not return value of the config: %s', key)
            return None

        self._update_configuration(key, value)
        return value

    def delete_config(self, key):
        """Returns configuration value

           Raises:
             GCTSRequestError
        """

        config = self.configuration

        if config is not None and key in config:
            del config[key]

        self._http.delete(f'config/{key}')

    def clone(self):
        """Clones the repository on the configured system

           Raises:
             GCTSRequestError
             GCTSRepoAlreadyExistsError
        """

        response = self._http.post('clone')

        self.wipe_data()
        return response

    def checkout(self, branch):
        """Checks out the given branch of the repo on the configured system"""

        response = self._http.get(f'branches/{self.branch}/switch', params={'branch': branch})

        self.wipe_data()
        return response.json()['result']

    def log(self):
        """Returns commits of the repository"""

        json_body = self._http.get_json('getCommit')

        return json_body['commits']

    def pull(self):
        """Pulls the repo on the configured system"""

        json_body = self._http.get_json('pullByCommit')

        self.wipe_data()

        return json_body

    def delete(self):
        """Deletes the repo from the configured system"""

        response = self._http.delete()

        self.wipe_data()
        return response

    def activities(self, history_params: RepoActivitiesQueryParams):
        """Fetches gCTS repository activities (not git logs)"""

        response = self._http.get_json('getHistory', params=history_params.get_params())
        if not response:
            return []

        result = response.get('result')
        if not result:
            raise SAPCliError('A successful gcts getHistory request did not return result')

        return result

    def commit_transport(self, corrnr, message, description=None):
        """Turns a transport into a commit"""

        commit = {
            'message': message,
            'autoPush': 'true',
            'objects': [{'object': corrnr, 'type': 'TRANSPORT'}]
        }

        if description:
            commit['description'] = description

        response = self._http.post_obj_as_json('commit', commit)

        self.wipe_data()
        return response

    def set_url(self, url):
        """Sets repository URL"""

        return self._set_item('url', url)

    def set_item(self, property_name, value):
        """Sets property of repository"""

        if property_name not in self.EDITABLE_PROPERTIES:
            raise SAPCliError(f'Cannot edit property "{property_name}".')

        return self._set_item(property_name, value)

    def create_branch(self, branch_name, symbolic=False, peeled=False, local_only=False):
        """Create new branch"""

        def _call_create(branch_type):
            body = {
                'branch': branch_name,
                'type': branch_type,
                'isSymbolic': symbolic,
                'isPeeled': peeled,
            }

            return self._http.post_obj_as_json('branches', json=body)

        response = _call_create('local') if local_only else _call_create('global')
        return response.json()['branch']

    def delete_branch(self, branch_name: str):
        """Delete branch of repository"""

        return self._http.delete(f'branches/{branch_name}').json()

    def list_branches(self):
        """List branches of repository"""

        response = self._http.get_json('branches')
        branches = response.get('branches')
        if branches is None:
            raise SAPCliError("gCTS response does not contain 'branches'")

        return branches
