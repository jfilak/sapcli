
from enum import Enum
import logging as log
from sap import get_logger

from sap.rest.errors import HTTPRequestError

from sap.rest.gcts.errors import SAPCliError, GCTSRequestError, GCTSRepoCloneError, GCTSRepoNotExistsError


def mod_log():
    """ADT Module logger"""

    return get_logger()


def _http_to_gcts_error(func):

    def try_except_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPRequestError as ex:
            raise exception_from_http_error_for_task(ex) from ex

    return try_except_wrapper


def exception_from_http_error_for_task(http_error):
    """Converts HTTPRequestError to proper instance"""

    if 'application/json' not in http_error.response.headers.get('Content-Type', ''):
        return http_error

    messages = http_error.response.json()

    exception = messages.get('exception', None)

    if exception == 'No relation between system and repository':
        return GCTSRepoNotExistsError(messages)

    if exception == 'Cannot clone repository. Status is not CREATED':
        return GCTSRepoCloneError(messages)

    return GCTSRequestError(messages)


class _TaskHttpProxy:

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
        PRELIMINARY = 'PRELIMINARY'  # Task created as entity

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

    def __init__(self, connection, rid, data: dict = None):
        if not rid:
            raise ValueError("rid parameter is required")

        self._http = _TaskHttpProxy(connection, rid)
        self._rid = rid
        self._data = data or {}

    def update_data(self, data: dict):
        """Update internal task data from a dictionary returned by gCTS.

        The expected keys include: tid, rid, jobId, log, variant, name, type,
        status, createdBy, createdAt, changedBy, changedAt, startAt, scheduledAt.
        Unknown keys are stored as-is for forward compatibility.
        """
        # Define expected fields for validation
        expected_fields = {
            'tid', 'jobId', 'log', 'variant', 'name', 'type',
            'status', 'createdBy', 'createdAt', 'changedBy', 'changedAt',
            'startAt', 'scheduledAt', 'parameters'
        }

        # Filter data to only include expected fields
        filtered_data = {k: v for k, v in data.items() if k in expected_fields}

        self._data.update(filtered_data)

        log.info('--------------DATA-----------------------')
        log.info('---------------------------------------------')
        log.info(data)
        log.info('---------------------------------------------')
        log.info('--------------DATA-----------------------')

    # Accessors
    def to_dict(self):
        dictionary = dict(self._data)
        dictionary['rid'] = self._rid
        return dictionary

    @property
    def tid(self):
        return self._data.get('tid')

    @property
    def rid(self):
        return self._rid

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

    def create(self, task_definition: 'RepositoryTask.TaskDefinition', parameters: 'RepositoryTask.TaskParameters' = None):
        """Create task

        Raises:
            SAPCliError: If repository is not set
            GCTSRequestError: If task creation fails
            GCTSRepoNotExistsError: If repository does not exist
        """
        if self.rid is None:
            raise SAPCliError("Repository is not set")

        data = {
            'type': task_definition.value,
        }
        if parameters is not None:
            data['parameters'] = parameters.to_dict()

        response = self._http.post_obj_as_json('task', data)
        self.update_data(response.json()['task'])
        return self

    def get_by_id(self, task_id: str):
        """Get task by ID

        Raises:
            GCTSRequestError: If task retrieval fails
            GCTSRepoNotExistsError: If repository does not exist
        """

        response = self._http.get_json(f'task/{task_id}')
        self.update_data(response.get('task'))
        return self

    def delete(self):
        """Delete task

        Raises:
            GCTSRequestError: If task deletion fails
            GCTSRepoNotExistsError: If repository does not exist
        """

        self._http.delete(f'task/{self.tid}')
        return self

    def schedule_task(self):
        """Schedule task

        Raises:
            SAPCliError: If task is not set or is not in PRELIMINARY status
            GCTSRequestError: If task scheduling fails
            GCTSRepoNotExistsError: If repository does not exist
            GCTSRepoCloneError: If repository cannot be cloned by task
        """

        if self.tid is None:
            raise SAPCliError("Task is not set")
        if self.status != self.TaskStatus.PRELIMINARY.value:
            raise SAPCliError("Task is not in PRELIMINARY status")

        response = self._http.get_json(f'task/{self.tid}/schedule')
        self.update_data(response.get('task'))
        return self

    def get_list(self):
        """Get all tasks for the repository

        Raises:
            GCTSRequestError: If task list retrieval fails
            GCTSRepoNotExistsError: If repository does not exist
        """

        response = self._http.get_json('task')
        return response.get('tasks')
