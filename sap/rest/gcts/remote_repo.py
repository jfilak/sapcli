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

    def __init__(self, connection, rid):
        self.url_prefix = f'repository/{rid}'
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

        target_url = self._build_url(path)
        try:
            return self.connection.get_json(target_url, params=params)
        except HTTPRequestError as ex:
            try:
                response_json = ex.response.json()
            except Exception as json_ex:
                mod_log().debug('Error while getting JSON from response: %s', str(json_ex))
                # Now lets continue as we never tried to analyze the JSON contents.
                # pylint: disable=W0707
                raise ex

            if response_json is None or 'result' not in response_json:
                # Re-use the exception because there is no JSON we can return.
                raise ex

            mod_log().warning('gCTS backend returned HTTP 500 with data for %s', target_url)
            return response_json

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
        CLONE = 'CLONE'
        BRANCH_SW = 'BRANCH_SW'

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


# pylint: disable=R0902
class RepositoryTask:
    """Represents a gCTS repository task with its definition, status, and parameters."""

    class TaskDefinition(Enum):
        """Task definition types"""

        CLONE_REPOSITORY = 'clone_repository'  # 0: Clone repository
        SWITCH_BRANCH = 'switch_branch'  # 1: Switch branch
        PULL_COMMIT = 'pull_commit'  # 2: Pull commit
        DEPLOY = 'deploy'  # 3: Deploy
        MERGE_BRANCH = 'merge_branch'  # 4: Merge branch
        MIGRATE_REPOSITORY = 'migrate_repository'  # 5: Migrate repository

    class TaskStatus(Enum):
        """Task definition types"""

        READY = 'READY'
        RUNNING = 'RUNNING'
        SCHEDULED = 'SCHEDULED'
        ABORTED = 'ABORTED'
        SUSPENDED = 'SUSPENDED'
        FINISHED = 'FINISHED'
        PRELIMINAR = 'PRELIMINAR'  # Task created as entity

    class TaskParameters:
        """Parameters structure for gCTS operations"""

        def __init__(self, branch=None, commit=None, deploy_scope=None,
                     merge_strategy=None, merge_fast_forward=None,
                     commit_message=None, objects=None, trkorr=None,
                     deploy_operation=None, layout=None):
            self.branch = branch
            self.commit = commit
            self.deploy_scope = deploy_scope
            self.merge_strategy = merge_strategy
            self.merge_fast_forward = merge_fast_forward
            self.commit_message = commit_message
            self.objects = objects
            self.trkorr = trkorr
            self.deploy_operation = deploy_operation
            self.layout = layout

        def to_dict(self):
            """Convert parameters to dictionary for API calls"""
            params = {}
            if self.branch is not None:
                params['branch'] = self.branch
            if self.commit is not None:
                params['commit'] = self.commit
            if self.deploy_scope is not None:
                params['deploy_scope'] = self.deploy_scope
            if self.merge_strategy is not None:
                params['merge_strategy'] = self.merge_strategy
            if self.merge_fast_forward is not None:
                params['merge_fast_forward'] = self.merge_fast_forward
            if self.commit_message is not None:
                params['commit_message'] = self.commit_message
            if self.objects is not None:
                params['objects'] = self.objects
            if self.trkorr is not None:
                params['trkorr'] = self.trkorr
            if self.deploy_operation is not None:
                params['deploy_operation'] = self.deploy_operation
            if self.layout is not None:
                params['layout'] = self.layout
            return params

    def __init__(self, data: dict = None):
        self._data = data or {}

    def update_data(self, data: dict):
        """Update internal task data from a dictionary returned by gCTS.

        The expected keys include: tid, rid, jobId, log, variant, name, type,
        status, createdBy, createdAt, changedBy, changedAt, startAt, scheduledAt.
        Unknown keys are stored as-is for forward compatibility.
        """

        self._data.update(data)

    # Accessors

    @property
    def tid(self):
        return self._data.get('tid')

    @property
    def rid(self):
        return self._data.get('rid')

    @property
    def jobId(self):
        return self._data.get('jobId')

    @property
    def log(self):
        return self._data.get('log')

    @property
    def variant(self):
        return self._data.get('variant')

    @property
    def name(self):
        return self._data.get('name')

    @property
    def type(self):
        return self._data.get('type')

    @property
    def status(self):
        return self._data.get('status')

    def get_status(self):
        """Return current task status value (string)."""
        return self.status

    @property
    def createdBy(self):
        return self._data.get('createdBy')

    @property
    def createdAt(self):
        return self._data.get('createdAt')

    @property
    def changedBy(self):
        return self._data.get('changedBy')

    @property
    def changedAt(self):
        return self._data.get('changedAt')

    @property
    def startAt(self):
        return self._data.get('startAt')

    @property
    def scheduledAt(self):
        return self._data.get('scheduledAt')


# pylint: disable=R0904
class Repository:
    """A proxy to gCTS repository"""

    EDITABLE_PROPERTIES = {'name', 'rid', 'role', 'type', 'vsid', 'status', 'url'}

    class ActivityReturnCode(Enum):
        """Repository activity return codes"""

        CLONE_SUCCESS = 4
        BRANCH_SW_SUCCES = 0

    def __init__(self, connection, rid, data=None):
        self._http = _RepositoryHttpProxy(connection, rid)
        self._rid = rid
        self._data = data

        self._config = None
        if self._data:
            self._config = self._data.get('config', None)

    def _fetch_data(self):
        mod_log().debug('Fetching data of the repository "%s"', self._rid)

        response = self._http.get_json()

        result = response['result']

        mod_log().debug('Fetched data of the repository "%s": %s', self._rid, result)

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

        return self._get_item('name')

    @property
    def rid(self):
        """Returns the repository's RID"""

        return self._rid

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

        if self._config is None:
            return {}

        return _config_list_to_dict(self._config)

    @property
    def role(self):
        """Returns the repository's ROLE"""

        return self._get_item('role')

    def set_role(self, role):
        """Sets repository ROLE"""

        return self._set_item('role', role)

    def create(self, url, vsid, config=None, role='SOURCE', typ='GITHUB'):
        """Creates the repository

           Raises:
             GCTSRequestError
             GCTSRepoAlreadyExistsError
        """

        repo = self._data or {}

        repo.update({
            'rid': self._rid,
            'name': self._rid,
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
            'repository': self._rid,
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

    def async_clone(self):
        """Clones the repository on the configured system

           Raises:
             GCTSRequestError
        """

        task = self.create_task(RepositoryTask.TaskDefinition.CLONE_REPOSITORY)
        mod_log().info('Clone task created: %s', task)
        self.schedule_task(task)
        mod_log().info('Clone task scheduled: %s', task)

        return task

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

    def commit(self, message, objects, description=None, autopush=False):
        """Creates a commit for the given objects"""

        commit = {
            'message': message,
            'autoPush': str(autopush).lower(),
            'objects': objects
        }

        if description:
            commit['description'] = description

        response = self._http.post_obj_as_json('commit', commit)

        self.wipe_data()
        return response

    def commit_transport(self, corrnr, message, description=None):
        """Turns a transport into a commit and pushes it"""

        # cl_cts_abap_vcs_transport_req=>prepare_object_list
        return self.commit(message, [{'object': corrnr, 'type': 'TRANSPORT'}], description=description, autopush=True)

    def commit_package(self, package, message, description=None):
        """Turns a package into a commit and pushes it"""

        # cl_cts_abap_vcs_transport_req=>prepare_object_list
        return self.commit(message, [{'object': package, 'type': 'FULL_PACKAGE'}], description=description,
                           autopush=True)

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

    def create_task(self, task_definition: RepositoryTask.TaskDefinition, parameters: RepositoryTask.TaskParameters = None):
        """Create task"""
        if self._rid is None:
            raise SAPCliError("Repository is not initialized")

        data = {
            'type': task_definition.value,
        }
        if parameters is not None:
            data['parameters'] = parameters.to_dict()

        response = self._http.post_obj_as_json('task', data)
        return RepositoryTask(response.json()['task'])

    def get_task_by_id(self, task_id: str):
        """Get task by ID"""

        response = self._http.get_json(f'task/{task_id}')
        return RepositoryTask(response.get('task'))

    def schedule_task(self, task: RepositoryTask):
        """Schedule task"""

        response = self._http.get_json(f'task/{task.tid}/schedule')
        task.update_data(response.get('task'))
        return task
