"""STC RFC API wrappers and helpers"""

from collections import defaultdict
from fnmatch import fnmatch

import xml.sax
from xml.sax.handler import ContentHandler

from sap.rfc.types import TRUE, FALSE
from sap.rfc.bapi import BAPIError


# pylint: disable=invalid-name, too-few-public-methods
class STC_SESSION_STATUS:
    """STC Session Status codes"""

    # 01  Waiting to be executed
    TO_BE_EXECUTED = '01'
    # 03  Running
    RUNNING = '03'
    # 05  Stopped
    STOPPED = '05'
    # 06  Manual activities required
    MANUAL_ACTIVITIES_REQUIRED = '06'
    # 07  Does not need to be executed
    NO_NEED_TO_BE_EXECUTED = '07'
    # 08  Execution scheduled
    EXECUTION_SCHEDULED = '08'
    # 10  Finished successfully
    FINISHED_SUCCESSFULLY = '10'
    # 11  Finished with warnings
    FINISHED_WITH_WARNINGS = '11'
    # 12  Errors occurred
    ERRORS_OCCURRED = '12'
    # 13  Aborted
    ABORTED = '13'


class SessionStatus:
    """STC Sessions status"""

    FINISHED_CODES = [
        STC_SESSION_STATUS.FINISHED_SUCCESSFULLY,
        STC_SESSION_STATUS.FINISHED_WITH_WARNINGS,
    ]

    FAILURE_CODES = [
        STC_SESSION_STATUS.STOPPED,
        STC_SESSION_STATUS.ERRORS_OCCURRED,
        STC_SESSION_STATUS.ABORTED,
    ]

    RUNNING_CODES = [
        STC_SESSION_STATUS.TO_BE_EXECUTED,
        STC_SESSION_STATUS.EXECUTION_SCHEDULED,
        STC_SESSION_STATUS.RUNNING,
    ]

    def __init__(self, response, current_task):
        self._response = response
        self._current_task = current_task

        self._code = response['E_STATUS']
        self._code_descr = response['E_STATUS_DESCR']

    def __str__(self):
        return '{code}({description})'.format(code=self._code,
                                              description=self._response['E_STATUS_DESCR'])

    @property
    def code(self):
        """Status code"""

        return self._code

    @property
    def description(self):
        """Status description"""

        return self._code_descr

    @property
    def task_status(self):
        """Current task status tuple (code, description)"""

        task_data = self._response['ES_CURRENT_TASK']
        return (task_data['STATUS'], task_data['STATUS_DESCR'])

    @property
    def is_failure(self):
        """True if this status belongs to failure statuses"""

        return self._code in SessionStatus.FAILURE_CODES

    @property
    def is_running(self):
        """True if this status belongs to running statuses"""

        return self._code in SessionStatus.RUNNING_CODES

    @property
    def was_started(self):
        """True if this status belongs to the statuses denoting the corresponding session has started"""

        return self._code not in [STC_SESSION_STATUS.TO_BE_EXECUTED, STC_SESSION_STATUS.NO_NEED_TO_BE_EXECUTED]

    @property
    def has_finished(self):
        """True if this status belongs to the statuses denoting the corresponding session has finished"""

        return self._code in SessionStatus.FINISHED_CODES

    @property
    def current_task(self):
        """Current task's RFC response dict"""

        return self._current_task


# pylint: disable=invalid-name, too-few-public-methods
class STC_TASK_STATUS:
    """STC Task status codes"""

    # 01  Waiting to be executed
    TO_BE_EXECUTED = '01'
    # 02  Shall not be executed
    NOT_TO_BE_EXECUTED = '02'
    # 03  Currently executing
    RUNNING = '03'
    # 05  Execution prevented
    EXECUTION_PREVENTED = '05'
    # 06  Manual activities required
    MANUAL_ACTIVITIES_REQUIRED = '06'
    # 07  Execution not supported
    NOT_SUPPORTED = '07'
    # 10  Executed successfully
    SUCCESSFULL = '10'
    # 11  Ended with warning
    SUCCESSFULL_WARNINGS = '11'
    # 12  Failed
    FAILED = '12'
    # 13  Aborted
    ABORTED = '13'


class TaskID:
    """STC Task ID helps keeping Name and Line Number together and in sync"""

    def __init__(self, name=None, lnr=None):
        self._name = name
        self._lnr = int(lnr) if lnr is not None else None
        self._key = None

    def _invalidate_key(self):
        self._key = None

    def set(self, key, value):
        """Assign the given value by key which can be either TASKNAME or LNR"""

        if key == 'TASKNAME':
            self.name = value
            return

        if key == 'LNR':
            self.lnr = int(value)
            return

        raise RuntimeError('Unknown key: ' + key)

    @property
    def name(self):
        """The Name part of the ID"""

        return self._name

    @name.setter
    def name(self, value):
        """Sets the Name part of the ID and invalidets Line Number"""

        self._invalidate_key()
        self._name = value

    @property
    def lnr(self):
        """The Line Number part of the ID"""
        return self._lnr

    @lnr.setter
    def lnr(self, value):
        """Sets the Line Number part of the ID and invalidets Name"""

        self._invalidate_key()
        self._lnr = value

    @property
    def key(self):
        """Task key generated from the task ID"""

        if self._key is None:
            self._key = '%s:%s' % (self._name, self._lnr)

        return self._key


class SessionLogsXMLContentHandler(ContentHandler):
    """Parses STC Sessions logs"""

    def __init__(self, storage):
        super().__init__()

        self.storage = storage
        self.task_list = False
        self.task_id = None
        self.message = None
        self.content = None

    # pylint: disable=too-many-return-statements
    def startElement(self, name, attrs):
        if name == 'TASKLIST':
            self.task_list = True
            return

        if not self.task_list:
            return

        if name == 'TASK':
            self.task_id = TaskID()
            return

        if self.task_id is None:
            return

        if name in ['TASKNAME', 'LNR']:
            self.content = ''
            return

        if name == 'STCTM_S_LOG':
            self.message = dict()
            return

        if self.message is None:
            return

        if name in ['TYPE', 'MESSAGE']:
            self.content = ''
            return

    def characters(self, content):
        if self.content is None:
            return

        self.content += content

    def endElement(self, name):
        if name in ['TYPE', 'MESSAGE']:
            if self.message is None:
                return

            self.message[name] = self.content
            self.content = None

        if self.task_id is not None and name in ['TASKNAME', 'LNR']:
            self.task_id.set(name, self.content)
            self.content = None

        if name == 'STCTM_S_LOG':
            logs = self.storage['TASKLIST'][self.task_id.key]['LOGS']
            logs.append(self.message)
            self.message = None
            return

        if name == 'item' and self.task_id is not None:
            self.task_id = None
            return

        if name == 'TASKLIST':
            self.task_list = False
            return


def parse_logs_xml(logs):
    """Parses STC session logs and returns inth form of a dict"""

    # pylint: disable=unnecessary-lambda
    storage = {'TASKLIST': defaultdict(lambda: defaultdict(lambda: list()))}
    xml.sax.parseString(logs, SessionLogsXMLContentHandler(storage))
    return storage


class SessionLogs:
    """STC Session logs"""

    def __init__(self, logs, content_type):
        self._logs = logs
        self._content_type = content_type
        self._data = None

    @property
    def raw(self):
        """The XML content"""

        return self._logs

    @property
    def mime(self):
        """The type of raw content"""

        return self._content_type

    def _get_data(self):
        if self._data is None:
            self._data = parse_logs_xml(self._logs)

        return self._data

    def get_task_messages(self, task_name, lnr):
        """Returns messages"""

        data = self._get_data()
        return data['TASKLIST'][TaskID(task_name, lnr).key]['LOGS']


def build_task_parameter(fieldname, value):
    """Creates a parameter for an STC task"""

    return {'FIELDNAME': fieldname, 'VALUE': value}


def build_session_parameter(taskname, lnr, fieldname, value):
    """Creates a parameter for an STC task in an STC session"""

    task_parameter = build_task_parameter(fieldname, value)

    task_parameter['TASKNAME'] = taskname
    task_parameter['LNR'] = int(lnr)

    return task_parameter


def parse_session_parameter_str_list(session_parameter_str_list):
    """Creates STC session parameters from the string definition:
          [task name],[line nr],[field name],[value]
       and rerturns the parsed list.
    """

    parameters = list()
    for in_param in session_parameter_str_list:
        in_param_parts = in_param.split(',')

        if len(in_param_parts) != 4:
            raise RuntimeError('Does not match the format "task name,line nr,field name,value": ' + in_param)

        try:
            line_nr = int(in_param_parts[1])
        except ValueError as ex:
            raise RuntimeError('The value "line nr" (2nd field) must be a number: ' + in_param) from ex

        parameters.append(build_session_parameter(in_param_parts[0], line_nr, in_param_parts[2], in_param_parts[3]))

    return parameters


def tm_session_begin(conn, scenario, parameters, init_only=FALSE):
    """"Creates a new session based on the scenario"""

    ret = conn.call('STC_TM_SESSION_BEGIN',
                    I_SCENARIO_ID=scenario,
                    I_INIT_ONLY=init_only,
                    I_IGNORE_SCENARIO_DIFF=' ',
                    I_IGNORE_LANGU_DIFF=' ',
                    I_IGNORE_SCENARIO_OBSOLETE=' ',
                    IT_PARAMETER=parameters,
                    IS_EXEC_SETTINGS={'CHECKRUN': ' ',
                                      'BATCH': ' ',
                                      'ASYNC': ' ',
                                      'TRACE': ' ',
                                      'BATCH_TARGET': ' '})

    BAPIError.raise_for_error(ret['ET_RETURN'], ret)

    return ret


def tm_session_get_parameters(conn, session_id):
    """"Returns parameters of the Session with the given ID"""

    return conn.call('STC_TM_SESSION_GET_PARAMETERS', I_SESSION_ID=session_id)


def tm_session_get_log(conn, session_id):
    """"Returns logs of the Session with the given ID"""

    ret = conn.call('STC_TM_SESSION_GET_LOG', I_SESSION_ID=session_id, I_FORMAT='XML')

    messages = ret['ET_RETURN']
    messages_string = ''
    if messages:
        do_raise = False
        for msg in messages:
            if msg['TYPE'] in ['E', 'A']:
                do_raise = True
            messages_string += '{} {}\n'.format(msg['TYPE'], msg['MESSAGE'])

        if do_raise:
            raise RuntimeError('System response:\n{}'.format(messages_string))

    logs = ret['E_LOG']
    if not logs:
        raise RuntimeError('No Log returned:\n{}'.format(messages_string))

    return SessionLogs(logs, ret['E_CONTENT_TYPE'])


def tm_get_session_list(conn):
    """"Returns list of STC sessions"""

    ret = conn.call('STC_TM_GET_SESSION_LIST')
    return ret['ET_SESSION']


def tm_session_get_status(conn, session_id):
    """"Returns status of the Session with the given ID"""

    return conn.call('STC_TM_SESSION_GET_STATUS', I_SESSION_ID=session_id)


def tm_task_set_parameter(conn, session_id, taskname, lnr, parameters):
    """"Sets the task paramters of the Session with the given ID"""

    return conn.call('STC_TM_TASK_SET_PARAMETER',
                     I_SESSION_ID=session_id,
                     I_TASKNAME=taskname,
                     I_LNR=lnr,
                     IT_PARAMETER=parameters)


def tm_task_skip(conn, session_id, taskname, lnr, skip_dep_tasks='X'):
    """"Marks the task of the Session with the given ID as skipped"""

    return conn.call('STC_TM_TASK_SKIP',
                     I_SESSION_ID=session_id,
                     I_TASKNAME=taskname,
                     I_LNR=lnr,
                     I_SKIP_DEP_TASKS=skip_dep_tasks)


def tm_task_unskip(conn, session_id, taskname, lnr):
    """"Marks the task of the Session with the given ID as for execution"""

    return conn.call('STC_TM_TASK_UNSKIP',
                     I_SESSION_ID=session_id,
                     I_TASKNAME=taskname,
                     I_LNR=lnr)


def tm_session_resume(conn, session_id):
    """"Resumes the Session with the given ID"""

    response = conn.call('STC_TM_SESSION_RESUME',
                         I_SESSION_ID=session_id,
                         IS_EXEC_SETTINGS={'CHECKRUN': ' ',
                                           'BATCH': 'X',
                                           'ASYNC': 'X',
                                           'TRACE': ' ',
                                           'BATCH_TARGET': ' '})

    BAPIError.raise_for_error(response['ET_RETURN'], response)

    status = SessionStatus(response, None)

    return status


class TaskParametersBuilder:
    """Task parameters"""

    def __init__(self):
        self._parameters = list()

    def set_parameter(self, name, value):
        """Adds a new parameter"""

        self._parameters.append(build_task_parameter(name, value))
        return self

    def build(self):
        """Returns the built parameters"""

        return list(self._parameters)


class Task:
    """STC Session Task proxy"""

    def __init__(self, conn, sid, name, lnr):
        self._conn = conn
        self._sid = sid
        self._name = name
        self._lnr = lnr

    @property
    def name(self):
        """Task name"""

        return self._name

    @property
    def lnr(self):
        """Task Line Number"""

        return self._lnr

    def skip(self):
        """Mark the task skipped"""

        ret = tm_task_skip(self._conn, self._sid, self._name, self._lnr)

        if not ret['E_SKIPPED']:
            raise RuntimeError(ret['ET_RETURN'][0]['MESSAGE'])

    def unskip(self):
        """Mark the task executed"""

        ret = tm_task_unskip(self._conn, self._sid, self._name, self._lnr)

        if not ret['E_UNSKIPPED']:
            raise RuntimeError(ret['ET_RETURN'][0]['MESSAGE'])

    def set_parameter(self, name, value):
        """Set the task parameter"""

        self.set_parameters(TaskParametersBuilder().set_parameter(name, value).build())

    def set_parameters(self, parameters):
        """Set multiple parameters"""

        tm_task_set_parameter(self._conn, self._sid, self._name, self._lnr, parameters)


class TaskList:
    """Session taks list proxy"""

    def __init__(self, tasks):
        self._tasks = tasks

    def __len__(self):
        return len(self._tasks)

    def __iter__(self):
        return iter(self._tasks)

    def __getitem__(self, name):
        selected = None

        if isinstance(name, int):
            # !!! Be aware of return here !!!
            return self._tasks[name]

        if isinstance(name, str):
            lnr = None
        elif isinstance(name, tuple):
            name, lnr = name
        else:
            RuntimeError('Type {typ} cannot be key'.format(typ=type(name)))

        for task in self._tasks:
            if task.name == name:
                if lnr is not None:
                    if lnr == task.lnr:
                        return task
                else:
                    if selected is not None:
                        raise RuntimeError('Task {name}:{lnr} has several line occurrences'.format(name=name, lnr=lnr))

                    selected = task

                continue

        if selected is None:
            raise ValueError('Task {name}:{lnr} was not found in the Session'.format(name=name, lnr=lnr))

        return selected

    # pylint: disable=no-self-use
    def _match(self, task, pattern):
        return fnmatch(task.name, pattern)

    def skip_matching(self, pattern):
        """Mark tasks matching the patter skipped"""

        for task in self._tasks:
            if self._match(task, pattern):
                task.skip()

    def unskip_matching(self, pattern):
        """Mark tasks matching the patter executed"""

        for task in self._tasks:
            if self._match(task, pattern):
                task.unskip()


# pylint: disable=too-few-public-methods
class SessionStateError:
    """Session state error"""

    # pylint: disable=unnecessary-pass
    pass


class SessionState:
    """Base class for STC Sessions states"""

    def __init__(self, conn, data):
        self._conn = conn
        self._data = data

    # pylint: disable=no-method-argument
    def _state_error(self):
        raise NotImplementedError()

    def create(self):
        """Creates session"""

        self._state_error()

    def resume(self):
        """Resumes session"""

        self._state_error()

    def refresh(self):
        """Refreshes session"""

        self._state_error()

    def get_logs(self):
        """Returns session"""

        self._state_error()

    def get_task_list(self):
        """Returns task list"""

        self._state_error()

    def get_id(self):
        """Returns STC ID"""

        self._state_error()

    def was_started(self):
        """Returns True if the state represents a started session; otherwise False"""

        self._state_error()


class SessionStateNew(SessionState):
    """Implementation of the new state"""

    def _state_error(self):
        return SessionStateError('The session has not been created yet')

    def create(self):
        ret = tm_session_begin(self._conn, self._data.scenario, [], init_only=TRUE)
        self._data.session_id = ret['E_SESSION_ID']
        return SessionStateFactory.created(self._conn, self._data)

    def was_started(self):
        return False


class SessionStateCreated(SessionState):
    """Implementation of the created state"""

    def _state_error(self):
        return SessionStateError('The session has already been created')

    def resume(self):
        tm_session_resume(self._conn, self._data.session_id)
        return self

    def refresh(self):
        status = tm_session_get_status(self._conn, self._data.session_id)

        tasks = [Task(self._conn, self._data.session_id, task['TASKNAME'], task['LNR'])
                 for task in status['ET_TASKLIST']]
        self._data.task_list = TaskList(tasks)

        current_task = None

        current_task_info = status['ES_CURRENT_TASK']
        current_task_name = current_task_info['TASKNAME']

        if current_task_name:
            current_task = self._data.task_list[current_task_name, current_task_info['LNR']]

        # pylint: disable=attribute-defined-outside-init
        self._status = SessionStatus(status, current_task)
        return self._status

    def get_task_list(self):
        if self._data.task_list is None:
            self.refresh()

        return self._data.task_list

    def get_status(self):
        """Returns the current status implementation"""

        if not hasattr(self, '_status'):
            self.refresh()

        return self._status

    def get_id(self):
        return self._data.session_id

    def was_started(self):
        return self.get_status().was_started

    def get_logs(self):
        return tm_session_get_log(self._conn, self._data.session_id)


class SessionStateFactory:
    """Builds sessions states"""

    @staticmethod
    def new(conn, data):
        """Builds the new state"""

        return SessionStateNew(conn, data)

    @staticmethod
    def created(conn, data):
        """Builds the created state"""

        return SessionStateCreated(conn, data)


# pylint: disable=too-few-public-methods
class SessionData:
    """Session data envelope"""

    def __init__(self, scenario, session_id=None, task_list=None):
        self.scenario = scenario
        self.session_id = session_id
        self.task_list = task_list


class Session:
    """Session proxy"""

    def __init__(self, conn, scenario):
        self._conn = conn
        self._data = SessionData(scenario=scenario, session_id=None, task_list=None)
        self._state = SessionStateFactory.new(self._conn, self._data)

    def create(self):
        """Attempts to create the session if the current state supports it"""
        self._state = self._state.create()

    def resume(self):
        """Attempts to resume the session if the current state supports it"""

        self._state = self._state.resume()

    def refresh(self):
        """Attempts to refresh the session if the current state supports it"""

        return self._state.refresh()

    def get_logs(self):
        """Attempts to return logs of the session if the current state supports it"""

        return self._state.get_logs()

    @property
    def status(self):
        """Current session status tuple (code, description)"""

        status = self._state.get_status()
        return (status.code, status.description)

    @property
    def session_id(self):
        """Session ID if the current state supports it"""

        return self._state.get_id()

    @property
    def was_started(self):
        """Returns True if the session was started"""

        return self._state.was_started()

    @property
    def task_list(self):
        """Returns task list if the session has it"""

        return self._state.get_task_list()

    @staticmethod
    def for_scenario(scenario, conn):
        """Creates a new STC session for scenario"""

        session = Session(conn, scenario)
        session.create()

        return session


def get_session_tasks(conn, session_id):
    """Retrieves the session's tasks and returns them in a list"""

    status = tm_session_get_status(conn, session_id)
    return list(status['ET_TASKLIST'])


def get_session_task_lnr(conn, session_id, task_name):
    """Returns task's LNR if the task_name has a single occurrence
       in the give session tasks.
    """

    task_lnr = None

    for task in get_session_tasks(conn, session_id):
        if task['TASKNAME'] != task_name:
            continue

        if task_lnr is not None:
            raise RuntimeError('Task {} has several line occurrences'.format(task_name))

        task_lnr = task['LNR']

    if task_lnr is None:
        raise ValueError('Task {} was not found in Session {}'.format(task_name, session_id))

    return task_lnr
