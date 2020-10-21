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
        super().__init__()

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

    return dict(((cfg['key'], cfg.get('value', '')) for cfg in config))


def _config_dict_to_list(config):

    return [{'key': key, 'value': value} for key, value in config.items()]


class Repository:
    """A proxy to gCTS repository"""

    def __init__(self, connection, name, data=None):
        self._connection = connection
        self._name = name
        self._data = data

    def _fetch_data(self):
        mod_log().debug('Fetching data of the repository "%s"', self._name)

        try:
            response = self._connection.get_json(f'repository/{self._name}')
        except HTTPRequestError as ex:
            raise GCTSRequestError(ex.response.json()) from ex

        result = response['result']

        mod_log().debug('Fetched data of the repository "%s": %s', self._name, result)

        return result

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
    def is_cloned(self):
        """Returns the repository's RID"""

        status = self._get_item('status')
        return status != 'CREATED'

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
            response = self._connection.post_obj_as_json('repository', create_request, accept='application/json')
        except HTTPRequestError as ex:
            messages = ex.response.json()

            log = messages.get('log', None)
            if log and log[0].get('message', '').endswith('Error action CREATE_REPOSITORY Repository already exists'):
                raise GCTSRepoAlreadyExistsError(messages) from ex

            raise GCTSRequestError(messages) from ex

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

        try:
            self._connection.post_obj_as_json(f'repository/{self.name}/config', {
                'key': key,
                'value': value
            })
        except HTTPRequestError as ex:
            raise GCTSRequestError(ex.response.json()) from ex

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
            raise GCTSRequestError(ex.response.json()) from ex

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
            raise GCTSRequestError(ex.response.json()) from ex

        self.wipe_data()
        return response

    def checkout(self, branch):
        """Checks out the given branch of the repo on the configured system"""

        url = f'repository/{self.rid}/branches/{self.branch}/switch'

        try:
            response = self._connection.execute('GET', url, params={'branch': branch})
        except HTTPRequestError as ex:
            raise GCTSRequestError(ex.response.json()) from ex

        self.wipe_data()

        return response.json()['result']

    def log(self):
        """Pulls the repo on the configured system"""

        url = f'repository/{self.rid}/getCommit'

        try:
            json_body = self._connection.get_json(url)
        except HTTPRequestError as ex:
            raise GCTSRequestError(ex.response.json()) from ex

        return json_body['commits']

    def pull(self):
        """Pulls the repo on the configured system"""

        url = f'repository/{self.rid}/pullByCommit'

        params = None
        commits = self.log()
        if commits:
            params = {'request': commits[0]['id']}

        try:
            json_body = self._connection.get_json(url, params=params)
        except HTTPRequestError as ex:
            raise GCTSRequestError(ex.response.json()) from ex

        self.wipe_data()

        return json_body

    def delete(self):
        """Deletes the repo from the configured system"""

        try:
            response = self._connection.execute('DELETE', f'repository/{self.name}')
        except HTTPRequestError as ex:
            raise GCTSRequestError(ex.response.json()) from ex

        self.wipe_data()
        return response


def simple_fetch_repos(connection):
    """Returns list of repositories in the target systems defined by the given
       connection.
    """

    try:
        response = connection.get_json('repository')
    except HTTPRequestError as ex:
        raise GCTSRequestError(ex.response.json()) from ex

    result = response.get('result', [])
    return [Repository(connection, repo['name'], data=repo) for repo in result]


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

        repo.wipe_data()

    if not repo.is_cloned:
        repo.clone()
    else:
        mod_log().info('Not cloning the repository "%s": already performed')

    return repo


def simple_checkout(connection, branch, name=None, repo=None):
    """Checks out the given branch in the given repository on the give system"""

    if repo is None:
        repo = Repository(connection, name)

    return repo.checkout(branch)


def simple_log(connection, name=None, repo=None):
    """Returns log history of the given repository on the give system"""

    if repo is None:
        repo = Repository(connection, name)

    return repo.log()


def simple_pull(connection, name=None, repo=None):
    """Pulls the given repository on the give system"""

    if repo is None:
        repo = Repository(connection, name)

    return repo.pull()


def simple_delete(connection, name):
    """Deletes the given repository on the give system"""

    return Repository(connection, name).delete()
