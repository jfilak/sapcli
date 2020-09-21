"""gCTS REST calls"""

from sap import get_logger

from sap.errors import SAPCliError
from sap.rest.errors import HTTPRequestError


def mod_log():
    """ADT Module logger"""

    return get_logger()


class GCTSRequestError(SAPCliError):
    """Base gCTS error type"""

    def __init__(self, messages):
        super(GCTSRequestError, self).__init__()

        self.messages = messages

    def __repr__(self):
        return f'gCTS exception: {self.messages["exception"]}'

    def __str__(self):
        return repr(self)


class GCTSRepoAlreadyExistsError(GCTSRequestError):
    """A repository already exists"""

    # pylint: disable=unnecessary-pass
    pass


def package_name_from_url(url):
    """Parse out Package name from a repo git url"""

    url_repo_part = url.split('/')[-1]

    if url_repo_part.endswith('.git'):
        return url_repo_part[:-4]

    return url_repo_part


def _set_configuration_key(config, key, value):
    item = next((cfg for cfg in config if cfg['key'] == key), None)
    if item:
        item['value'] = value
    else:
        config.append({'key': key, 'value': value})
    return config


def _config_list_to_dict(config):

    return dict(((cfg['key'], cfg['value']) for cfg in config))


def _config_dict_to_list(config):

    return [{'key': key, 'value': value} for key, value in config.items()]


class Repository:
    """A proxy to gCTS repository"""

    def __init__(self, connection, name, data=None):
        self._connection = connection
        self._name = name
        self._data = data

    def _fetch_data(self):
        try:
            response = self._connection.get_json(f'repository/{self._name}')
        except HTTPRequestError as ex:
            raise GCTSRequestError(ex.response.json())

        return response['result']

    def _update_configuration(self, key, value):
        if self._data is None:
            self._data = {}

        config = self._data.get('config', [])
        config = _set_configuration_key(config, key, value)
        self._data['config'] = config
        return config

    def _get_item(self, item, default=None, fetch=False):
        if self._data is None or fetch:
            self._data = self._fetch_data()

        return self._data.get(item, default)

    def wipe_data(self):
        """Clears cached data"""

        self._data = None

    @property
    def name(self):
        """Returns the repository's name"""

        return self._name

    @property
    def rid(self):
        """Returns the repository's RID"""

        return self._get_item('rid')

    @property
    def url(self):
        """Returns the repository's URL"""

        return self._get_item('url')

    @property
    def branch(self):
        """Returns the repository's current URL"""

        return self._get_item('branch')

    @property
    def configuration(self):
        """Returns the current repository configuration"""

        return _config_list_to_dict(self._get_item('config'))

    def create(self, url, vsid, config=None):
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
            'role': 'SOURCE',
            'type': 'GITHUB',
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
            return self._connection.post_obj_as_json('repository', create_request)
        except HTTPRequestError as ex:
            messages = ex.response.json()

            log = messages.get('log', None)
            if log and log[0].get('message', '').startswith('Error action CREATE_REPOSITORY Repository already exists'):
                raise GCTSRepoAlreadyExistsError(messages)

            raise GCTSRequestError(messages)

    def set_config(self, key, value):
        """Sets configuration value

           Raises:
             GCTSRequestError
             GCTSRepoAlreadyExistsError
        """

        try:
            self._connection.post_obj_as_json(f'repository/{self.name}/config', {
                'key': key,
                'value': value
            })
        except HTTPRequestError as ex:
            raise GCTSRequestError(ex.response.json())

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

        try:
            response = self._connection.execute('GET',
                                                f'repository/{self.name}/config/{key}',
                                                accept='application/json')
        except HTTPRequestError as ex:
            raise GCTSRequestError(ex.response.json())

        value = response.json()['result']['value']
        config = self._update_configuration(key, value)
        return value

    def clone(self):
        """Clones the repository on the configured system

           Raises:
             GCTSRequestError
             GCTSRepoAlreadyExistsError
        """

        try:
            response = self._connection.execute('POST', f'repository/{self._name}/clone')
        except HTTPRequestError as ex:
            raise GCTSRequestError(ex.response.json())

        self.wipe_data()
        return response

    def checkout(self, branch):
        """Checks out the given branch of the repo on the configured system"""

        url = f'repository/{self.rid}/branches/{self.branch}/switch'

        try:
            response = self._connection.execute('GET', url, params={'branch': branch})
        except HTTPRequestError as ex:
            raise GCTSRequestError(ex.response.json())

        self.wipe_data()
        return response

    def delete(self):
        """Deletes the repo from the configured system"""

        try:
            response = self._connection.execute('DELETE', f'repository/{self.name}')
        except HTTPRequestError as ex:
            raise GCTSRequestError(ex.response.json())

        self.wipe_data()
        return response


def simple_fetch_repos(connection):
    """Returns list of repositories in the target systems defined by the given
       connection.
    """

    try:
        response = connection.get_json('repository')
    except HTTPRequestError as ex:
        raise GCTSRequestError(ex.response.json())

    return [Repository(connection, repo['name'], data=repo) for repo in response['result']]


def simple_clone(connection, url, name, vsid='6IT', start_dir='src/', vcs_token=None, error_exists=True):
    """Creates and clones the repository in the target systems"""

    config = {}

    if start_dir:
        config['VCS_TARGET_DIR'] = start_dir

    if vcs_token:
        config['CLIENT_VCS_AUTH_TOKEN'] = vcs_token

    repo = Repository(connection, name)

    try:
        repo.create(url, vsid, config=config)
    except GCTSRepoAlreadyExistsError as ex:
        if error_exists:
            raise ex

        mod_log().debug(ex)
        mod_log().info(str(ex))

    repo.clone()
    return repo


def simple_checkout(connection, name, branch):
    """Checks out the given branch in the given repository on the give system"""

    return Repository(connection, name).checkout(branch)


def simple_delete(connection, name):
    """Deletes the given repository on the give system"""

    return Repository(connection, name).delete()
