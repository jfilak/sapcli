import unittest

from unittest.mock import patch, call, Mock, MagicMock

import sap.rfc.stc as stc
from sap.rfc.bapi import BAPIError
from sap.rfc.types import TRUE


class BAPIreturValueBuilder(object):

    def __init__(self):
        self._value = list()

    @property
    def value(self):
        return self._value

    def add_message(self, typ, message):
        self._value.append({'ID': 'ID', 'NUMBER': '777', 'TYPE': typ, 'MESSAGE': message})
        return self

    def add_error(self, message):
        return self.add_message('E', message)

    def add_warning(self, message):
        return self.add_message('W', message)

    def add_abort(self, message):
        return self.add_message('A', message)

    def add_info(self, message):
        return self.add_message('I', message)


def build_log_response(log, content_type, bapiret):
    return { 'E_LOG': log, 'E_CONTENT_TYPE': content_type, 'ET_RETURN': bapiret }


def build_session_begin_response(session_id, bapiret):
    return {'E_SESSION_ID': session_id, 'ET_RETURN': bapiret}


class STCBaseCase(unittest.TestCase):

    def conn_call(self, *args, **kwargs):
        return next(self.conn_call_return_value)

    def setUp(self):
        self.conn = Mock()
        self.conn.call = Mock()
        self.conn.call.side_effect = self.conn_call

    def set_conn_call_return_value(self, return_value):
        if not isinstance(return_value, list):
            return_value = [return_value]

        self.conn_call_return_value = iter(return_value)


class TestTmSessionBegin(STCBaseCase):

    def test_with_expected_exception(self):
        bapirettab = BAPIreturValueBuilder().add_error('error').add_error('bar').value
        self.set_conn_call_return_value(build_session_begin_response('', bapirettab))

        with self.assertRaises(BAPIError) as caught:
            stc.tm_session_begin(self.conn, 'SCENARIO', [])

        self.assertEqual(str(caught.exception), 'E/ID/777: error\nE/ID/777: bar')


class TestTmGetLog(STCBaseCase):

    def run_with_expected_exception(self, log, content_type, bapiret, exp_error_message):
        self.set_conn_call_return_value(build_log_response(log, content_type, bapiret))

        with self.assertRaises(RuntimeError) as caught:
            stc.tm_session_get_log(self.conn, 'ID')

        self.assertEqual(str(caught.exception), exp_error_message)

    def test_tm_get_log_no_erros(self):
        self.set_conn_call_return_value(build_log_response('foo', 'application/xml', BAPIreturValueBuilder().value))
        resp = stc.tm_session_get_log(self.conn, 'ID')

        self.assertEqual(resp.raw, 'foo')
        self.assertEqual(resp.mime, 'application/xml')

    def test_tm_get_log_erros(self):
        self.run_with_expected_exception(
            None,
            None,
            BAPIreturValueBuilder().add_error('first').add_error('second').value,
            'System response:\nE first\nE second\n')

    def test_tm_get_log_aborts(self):
        self.run_with_expected_exception(
            None,
            None,
            BAPIreturValueBuilder().add_abort('first').value,
            'System response:\nA first\n')

    def test_tm_get_log_wt_warning_wo_logs(self):
        self.run_with_expected_exception(
            None,
            None,
            BAPIreturValueBuilder().add_warning('first').value,
            'No Log returned:\nW first\n')

    def test_tm_get_log_wo_logs_wo_bapiret(self):
        self.run_with_expected_exception(
            None,
            None,
            BAPIreturValueBuilder().value,
            'No Log returned:\n')


class TestSessionLogs(unittest.TestCase):

    def test_session_logs_constructor_and_properties(self):
        session_logs = stc.SessionLogs('foo', 'plain/txt')
        self.assertEqual(session_logs.raw, 'foo')
        self.assertEqual(session_logs.mime, 'plain/txt')

    def test_session_logs_constructor_and_properties(self):
        session_logs = stc.SessionLogs('''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
    <VERSION>1.2</VERSION>
    <SESSION>
      <EXEC_INFO>
        <item>
          <EXEC_ID>20191126162756.012812</EXEC_ID>
          <PERIOD>M</PERIOD>
          <PERIOD_DESCR>Maintenance</PERIOD_DESCR>
          <BATCH/>
          <BATCH_DESCR>Online processing</BATCH_DESCR>
          <API>X</API>
          <API_DESCR>API call</API_DESCR>
          <USER>DDIC</USER>
          <JOBNAME/>
          <JOBCOUNT/>
          <SID>C50</SID>
          <CLNT>000</CLNT>
          <HOST>dlms4hana</HOST>
          <STATUS>01</STATUS>
          <STATUS_DESCR>Waiting to be executed</STATUS_DESCR>
          <LAST_UPDATE>20191126162756.201085</LAST_UPDATE>
          <DURATION>0.0</DURATION>
          <LOG/>
          <TASKS>
            <item>
              <TASKNAME>CL_STCT_SC_PREPARE_SICK</TASKNAME>
              <LNR>1</LNR>
            </item>
          </TASKS>
        </item>
      </EXEC_INFO>
      <TOP_TASKS>
        <item>
          <TASKNAME>CL_STCT_SC_CONFIG_TMS_SINGLE</TASKNAME>
          <LNR>1</LNR>
        </item>
      </TOP_TASKS>
      <TASKLIST>
        <item>
          <TASK>
            <TYPE>CLAS</TYPE>
            <TASKNAME>FIRST</TASKNAME>
            <LNR>1</LNR>
          </TASK>
          <LOG>
            <STCTM_S_LOG>
              <TYPE>S</TYPE>
              <MESSAGE>LINE 1</MESSAGE>
            </STCTM_S_LOG>
            <STCTM_S_LOG>
              <TYPE>S</TYPE>
              <MESSAGE>LINE 2</MESSAGE>
            </STCTM_S_LOG>
          </LOG>
        </item>
        <item>
          <TASK>
            <TYPE>CLAS</TYPE>
            <TASKNAME>SECOND</TASKNAME>
            <LNR>2</LNR>
          </TASK>
          <LOG>
            <STCTM_S_LOG>
              <TYPE>S</TYPE>
              <MESSAGE>Line 3</MESSAGE>
            </STCTM_S_LOG>
            <STCTM_S_LOG>
              <TYPE>S</TYPE>
              <MESSAGE>Line 4</MESSAGE>
            </STCTM_S_LOG>
          </LOG>
        </item>
      </TASKLIST>
    </SESSION>
  </asx:values>
</asx:abap>''', 'application/xml')

        task_messages = session_logs.get_task_messages('FIRST', 1)
        self.assertEqual(task_messages, [{'TYPE': 'S', 'MESSAGE': 'LINE 1'}, {'TYPE': 'S', 'MESSAGE': 'LINE 2'}])


class TestTaskID(unittest.TestCase):

    def test_task_id_ctor_empty(self):
        task_id = stc.TaskID()
        self.assertEqual(task_id.name, None)
        self.assertEqual(task_id.lnr, None)
        self.assertEqual(task_id.key, 'None:None')

    def test_task_id_ctor_values(self):
        task_id = stc.TaskID(name='foo', lnr=1)
        self.assertEqual(task_id.name, 'foo')
        self.assertEqual(task_id.lnr, 1)
        self.assertEqual(task_id.key, 'foo:1')

    def test_task_name_setter_getter_key(self):
        task_id = stc.TaskID()

        task_id.name = 'foo'
        self.assertEqual(task_id.name, 'foo')
        self.assertEqual(task_id.lnr, None)
        self.assertEqual(task_id.key, 'foo:None')

        task_id.name = 'bar'
        self.assertEqual(task_id.name, 'bar')
        self.assertEqual(task_id.lnr, None)
        self.assertEqual(task_id.key, 'bar:None')

    def test_task_lnr_setter_getter_key(self):
        task_id = stc.TaskID()

        task_id.lnr = 1
        self.assertEqual(task_id.name, None)
        self.assertEqual(task_id.lnr, 1)
        self.assertEqual(task_id.key, 'None:1')

        task_id.lnr = 2
        self.assertEqual(task_id.name, None)
        self.assertEqual(task_id.lnr, 2)
        self.assertEqual(task_id.key, 'None:2')

    def test_task_set(self):
        task_id = stc.TaskID()

        task_id.set('TASKNAME', 'foo')
        task_id.set('LNR', 1)

        self.assertEqual(task_id.name, 'foo')
        self.assertEqual(task_id.lnr, 1)
        self.assertEqual(task_id.key, 'foo:1')


class TestGetSessionTasks(unittest.TestCase):

    @patch('sap.rfc.stc.tm_session_get_status')
    def test_get_session_tasks(self, fake_get_status):
        fake_get_status.return_value = {'ET_TASKLIST': (1, 2, 3)}

        tasks = stc.get_session_tasks('conn', 'session')

        self.assertEqual(tasks, [1, 2, 3])


class TestGetSessionTaskLNR(unittest.TestCase):

    def setUp(self):
        self.session_id = 'CL_SES_01'
        self.task_name = 'CL_TASK'

    @patch('sap.rfc.stc.get_session_tasks')
    def do_test(self, tasks, fake_get_tasks):
        fake_get_tasks.return_value = tasks
        return stc.get_session_task_lnr('conn', self.session_id, self.task_name)

    def assertNotFoundMessage(self, caught):
        self.assertEqual(str(caught.exception),
                         'Task {task} was not found in Session {session}'.format(task=self.task_name, session=self.session_id))

    def assertMultipleOccurrencesMessage(self, caught):
        self.assertEqual(str(caught.exception),
                         'Task {task} has several line occurrences'.format(task=self.task_name))

    def test_get_session_task_lnr_empty_tasks(self):
        with self.assertRaises(ValueError) as caught:
            self.do_test([])

        self.assertNotFoundMessage(caught)

    def test_get_session_task_lnr_not_found(self):
        with self.assertRaises(ValueError) as caught:
            self.do_test([{'TASKNAME': 'foo', 'LNR': 1}])

        self.assertNotFoundMessage(caught)

    def test_get_session_task_lnr_multiple(self):
        with self.assertRaises(RuntimeError) as caught:
            self.do_test([{'TASKNAME': self.task_name, 'LNR': 1},
                          {'TASKNAME': self.task_name, 'LNR': 2}])

        self.assertMultipleOccurrencesMessage(caught)

    def test_get_session_task_ok(self):
        lnr = self.do_test([{'TASKNAME': self.task_name, 'LNR': 3}])
        self.assertEqual(lnr, 3)


class TestTaskParametersBuilder(unittest.TestCase):

    def setUp(self):
        self.task_parameter_builder = stc.TaskParametersBuilder()

    def test_task_parameters_set_parameter_once(self):
        ret = self.task_parameter_builder.set_parameter('foo', 'bar')
        self.assertEqual(ret, self.task_parameter_builder, msg='set_parameter returns itself')

        res = ret.build()
        self.assertEqual(res, [{'FIELDNAME': 'foo', 'VALUE': 'bar'}])

    def test_task_parameters_set_parameter_twice(self):
        ret = self.task_parameter_builder.set_parameter('result', 'success')
        ret.set_parameter('outcome', 'victory')

        res = ret.build()
        self.assertEqual(res,
            [{'FIELDNAME': 'result', 'VALUE': 'success'},
             {'FIELDNAME': 'outcome', 'VALUE': 'victory'},
            ])


class TestTask(unittest.TestCase):

    def setUp(self):
        self.conn = Mock()
        self.sid = 'CL_SC_123'
        self.task_name = 'CL_TASK'
        self.task_lnr = '01'
        self.task = stc.Task(self.conn, self.sid, self.task_name, self.task_lnr)

    @patch('sap.rfc.stc.tm_task_skip')
    def test_skip(self, fake_skip):
        self.task.skip()

        fake_skip.assert_called_once_with(self.conn, self.sid, self.task_name, self.task_lnr)

    @patch('sap.rfc.stc.tm_task_skip')
    def test_skip_fail(self, fake_skip):
        fake_skip.return_value = {
            'E_SKIPPED': '',
            'ET_RETURN': [{'MESSAGE':'cannot skip'}]
        }

        with self.assertRaises(RuntimeError) as caught:
            self.task.skip()

        fake_skip.assert_called_once_with(self.conn, self.sid, self.task_name, self.task_lnr)
        self.assertEqual(str(caught.exception), 'cannot skip')

    @patch('sap.rfc.stc.tm_task_unskip')
    def test_unskip(self, fake_unskip):
        self.task.unskip()

        fake_unskip.assert_called_once_with(self.conn, self.sid, self.task_name, self.task_lnr)

    @patch('sap.rfc.stc.tm_task_unskip')
    def test_unskip(self, fake_unskip):
        fake_unskip.return_value = {
            'E_UNSKIPPED': '',
            'ET_RETURN': [{'MESSAGE':'cannot unskip'}]
        }

        with self.assertRaises(RuntimeError) as caught:
            self.task.unskip()

        fake_unskip.assert_called_once_with(self.conn, self.sid, self.task_name, self.task_lnr)
        self.assertEqual(str(caught.exception), 'cannot unskip')


    @patch('sap.rfc.stc.tm_task_set_parameter')
    def test_set_parameter(self, fake_set_parameter):
        self.task.set_parameter('foo', 'bar')

        fake_set_parameter.assert_called_once_with(
            self.conn,
            self.sid,
            self.task_name,
            self.task_lnr,
            [stc.build_task_parameter('foo', 'bar')]
        )

    @patch('sap.rfc.stc.tm_task_set_parameter')
    def test_set_parameters(self, fake_set_parameter):
        parameters = stc.TaskParametersBuilder().set_parameter('result', 'success').set_parameter('outcome', 'victory').build()
        self.task.set_parameters(parameters)

        fake_set_parameter.assert_called_once_with(
            self.conn,
            self.sid,
            self.task_name,
            self.task_lnr,
            parameters
        )


class TestTaskList(unittest.TestCase):

    def setUp(self):
        self.conn = Mock()
        self.session_id = '123'
        self.task_single_name = 'CL_TASK'
        self.task_single_lnr = 1
        self.task_multi_name = 'CL_MULTI'
        self.task_multi_lnr_1 = 1
        self.task_multi_lnr_2 = 2

        self.task_list = stc.TaskList(
            [stc.Task(self.conn, self.session_id, self.task_single_name, self.task_single_lnr),
             stc.Task(self.conn, self.session_id, self.task_multi_name, self.task_multi_lnr_1),
             stc.Task(self.conn, self.session_id, self.task_multi_name, self.task_multi_lnr_2)]
        )

    def assertTaskEqualSingle(self, task):
        self.assertEqual(task._conn, self.conn)
        self.assertEqual(task.name, self.task_single_name)
        self.assertEqual(task.lnr, self.task_single_lnr)

    def assertCallArgsListAllTasks(self, call_args_list):
        self.assertEqual(call_args_list,
                         [call(self.conn, self.session_id, self.task_single_name, self.task_single_lnr),
                          call(self.conn, self.session_id, self.task_multi_name, self.task_multi_lnr_1),
                          call(self.conn, self.session_id, self.task_multi_name, self.task_multi_lnr_2)])

    def test_get_item_excat_match(self):
        found_task = self.task_list[self.task_single_name, self.task_single_lnr]

        self.assertTaskEqualSingle(found_task)

    def test_get_item_match_wo_lnr(self):
        found_task = self.task_list[self.task_single_name]

        self.assertTaskEqualSingle(found_task)

    def test_get_item_multiple_error(self):
        with self.assertRaises(RuntimeError):
            found_task = self.task_list[self.task_multi_name]

    def test_get_item_name_not_found_error(self):
        with self.assertRaises(ValueError):
            found_task = self.task_list['No_such_task']

    def test_get_item_lnr_not_found_error(self):
        with self.assertRaises(ValueError):
            found_task = self.task_list[self.task_single_name, self.task_single_lnr + 1]

    @patch('sap.rfc.stc.tm_task_skip')
    def test_skip_matching_asterisk(self, fake_skip):
        self.task_list.skip_matching('*')

        self.assertCallArgsListAllTasks(fake_skip.call_args_list)

    @patch('sap.rfc.stc.tm_task_unskip')
    def test_unskip_matching_asterisk(self, fake_unskip):
        self.task_list.unskip_matching('*')

        self.assertCallArgsListAllTasks(fake_unskip.call_args_list)


class TestSessionStatus(unittest.TestCase):

    def setUp(self):
        self.status_description = 'Mock status'
        self.task_status_code = stc.STC_TASK_STATUS.TO_BE_EXECUTED
        self.task_status_description = 'To be executed'

        self.current_task = Mock()
        self.response = {
            'E_STATUS': None,
            'E_STATUS_DESCR': self.status_description,
            'ES_CURRENT_TASK': {
              'STATUS': self.task_status_code,
              'STATUS_DESCR': self.task_status_description,
            }
        }

    def test_status_wrappers(self):
        status = stc.SessionStatus(self.response, self.current_task)
        self.assertEqual(status.description, self.status_description)

        self.assertEqual(status.task_status, (self.task_status_code, self.task_status_description))

    def test_is_failure(self):
        for status_code in stc.SessionStatus.FAILURE_CODES:
            self.response['E_STATUS'] = status_code
            status = stc.SessionStatus(self.response, self.current_task)
            self.assertTrue(status.is_failure, msg='Code: {code}'.format(code=status_code))

    def test_is_running_status_to_be_executed(self):
        self.response['E_STATUS'] = stc.STC_SESSION_STATUS.TO_BE_EXECUTED
        status = stc.SessionStatus(self.response, self.current_task)
        self.assertTrue(status.is_running)

    def test_is_running_status_execution_scheduled(self):
        self.response['E_STATUS'] = stc.STC_SESSION_STATUS.EXECUTION_SCHEDULED
        status = stc.SessionStatus(self.response, self.current_task)
        self.assertTrue(status.is_running)

    def test_is_running_status_running(self):
        self.response['E_STATUS'] = stc.STC_SESSION_STATUS.RUNNING
        status = stc.SessionStatus(self.response, self.current_task)
        self.assertTrue(status.is_running)

    def test_was_started_to_be(self):
        self.response['E_STATUS'] = stc.STC_SESSION_STATUS.TO_BE_EXECUTED
        status = stc.SessionStatus(self.response, self.current_task)
        self.assertFalse(status.was_started)

    def test_was_started_no_need(self):
        self.response['E_STATUS'] = stc.STC_SESSION_STATUS.NO_NEED_TO_BE_EXECUTED
        status = stc.SessionStatus(self.response, self.current_task)
        self.assertFalse(status.was_started)

    def test_has_finished(self):
        for status_code in stc.SessionStatus.FINISHED_CODES:
            self.response['E_STATUS'] = status_code
            status = stc.SessionStatus(self.response, self.current_task)
            self.assertTrue(status.has_finished, msg='Code: {code}'.format(code=status_code))

    def test_current_task(self):
        status = stc.SessionStatus(self.response, self.current_task)
        self.assertEqual(status.current_task, self.current_task)


class TestSessionState(unittest.TestCase):

    def setUp(self):
        self.conn = Mock()
        self.data = Mock()
        self.state = stc.SessionState(self.conn, self.data)

    def test_session_state_ctor(self):
        self.assertEqual(self.state._conn, self.conn)
        self.assertEqual(self.state._data, self.data)

    def test_session_state_create(self):
        with self.assertRaises(NotImplementedError):
            self.state.create()

    def test_session_state_resume(self):
        with self.assertRaises(NotImplementedError):
            self.state.resume()

    def test_session_state_refresh(self):
        with self.assertRaises(NotImplementedError):
            self.state.refresh()

    def test_session_state_get_task_list(self):
        with self.assertRaises(NotImplementedError):
            self.state.get_task_list()

    def test_session_state_get_id(self):
        with self.assertRaises(NotImplementedError):
            self.state.get_id()

    def test_session_state_was_started(self):
        with self.assertRaises(NotImplementedError):
            self.state.was_started()


class TestSessionStateNew(unittest.TestCase):

    def setUp(self):
        self.conn = Mock()
        self.data = stc.SessionData('SCENARIO')
        self.state = stc.SessionStateNew(self.conn, self.data)

    @patch('sap.rfc.stc.tm_session_begin')
    def test_session_state_new_create(self, fake_begin):
        fake_begin.return_value = {'E_SESSION_ID': '123'}

        new_state = self.state.create()

        self.assertIsInstance(new_state, stc.SessionStateCreated)
        self.assertEqual(new_state.get_id(), '123')
        self.assertEqual(self.data.scenario, 'SCENARIO')
        self.assertEqual(self.data.session_id, '123')
        self.assertIsNone(self.data.task_list)

        fake_begin.assert_called_once_with(self.conn, self.data.scenario, [], init_only=TRUE)

    def test_session_state_new_was_started(self):
        self.assertFalse(self.state.was_started())


class TestSessionStateCreated(unittest.TestCase):

    def setUp(self):
        self.conn = Mock()
        self.scenario = 'CL_SOME_LIST'
        self.session_id = 'CL_SOME_LIST_RUNXYZ'
        self.status_code = '02'
        self.status_task_name = 'CL_TASK'
        self.status_task_lnr = 1

        self.status_task = {
            'TASKNAME': self.status_task_name,
            'LNR': self.status_task_lnr,
            'STATUS': '01',
            'STATUS_DESCR': 'Whatever Task Status from unittests',
            'DESCRIPTION': 'Unittest fake task',
        }

        self.data = stc.SessionData(self.scenario, session_id=self.session_id)
        self.state = stc.SessionStateCreated(self.conn, self.data)

        self.session_status = {
            'E_STATUS': self.status_code,
            'E_STATUS_DESCR': 'Whatever Session Status from unittests',
            'ES_CURRENT_TASK': self.status_task,
            'ET_TASKLIST': [self.status_task],
        }

    def assertStatusCurrentTask(self, task):
        self.assertEqual(task.name, self.status_task_name)
        self.assertEqual(task.lnr, self.status_task_lnr)

    def assertStatus(self, status):
        self.assertEqual(status.code, self.status_code)
        self.assertStatusCurrentTask(status.current_task)

    def assertStatusTaskList(self, task_list):
        self.assertEqual(len(task_list), 1)
        self.assertStatusCurrentTask(task_list[0])

    @patch('sap.rfc.stc.tm_session_resume')
    def test_resume(self, fake_resume):
        self.state.resume()

        fake_resume.assert_called_once_with(self.conn, self.session_id)

    @patch('sap.rfc.stc.tm_session_get_status')
    def test_refresh(self, fake_status):
        fake_status.return_value = self.session_status

        status = self.state.refresh()

        self.assertStatus(status)

    @patch('sap.rfc.stc.tm_session_get_status')
    def test_refresh_no_current_task(self, fake_status):
        fake_status.return_value = self.session_status
        self.status_task['TASKNAME'] = ''

        status = self.state.refresh()

        self.assertIsNone(status.current_task)
        self.assertEqual(status.code, self.status_code)

    @patch('sap.rfc.stc.tm_session_get_status')
    def test_get_task_list_before_refresh(self, fake_status):
        fake_status.return_value = self.session_status

        task_list = self.state.get_task_list()
        self.assertStatusTaskList(task_list)

    def test_get_task_list_after_refresh(self):
        with patch('sap.rfc.stc.tm_session_get_status') as fake_status:
            fake_status.return_value = self.session_status
            self.state.refresh()

        task_list = self.state.get_task_list()
        self.assertStatusTaskList(task_list)

    @patch('sap.rfc.stc.tm_session_get_status')
    def test_get_status_before_refresh(self, fake_status):
        fake_status.return_value = self.session_status

        status = self.state.get_status()

        self.assertStatus(status)

    def test_get_status_after_refresh(self):
        with patch('sap.rfc.stc.tm_session_get_status') as fake_status:
            fake_status.return_value = self.session_status
            self.state.refresh()

        status = self.state.get_status()
        self.assertStatus(status)

    @patch('sap.rfc.stc.tm_session_get_status')
    def test_get_id(self, fake_status):
        fake_status.return_value = self.session_status

        self.state.refresh()

        self.assertEqual(self.state.get_id(), self.session_id)

    @patch('sap.rfc.stc.tm_session_get_status')
    def test_was_started(self, fake_status):
        fake_status.return_value = self.session_status

        self.assertTrue(self.state.was_started)

    @patch('sap.rfc.stc.tm_session_get_log')
    def test_get_logs(self, fake_logs):
        fake_logs.return_value = Mock()

        logs = self.state.get_logs()

        self.assertTrue(logs, fake_logs.return_value)


#class TestSessionStateFactory(unittest.TestCase):

#class TestSessionData(unittest.TestCase):

class TestSession(unittest.TestCase):

    @patch('sap.rfc.stc.SessionStateFactory.new')
    def setUp(self, fake_new_state):
        self.state = Mock()

        self.state.refresh = Mock()
        self.state.refresh.retur_value = Mock()

        self.state.get_logs = Mock()
        self.state.get_logs.return_value = {'E_LOGS': 'data'}

        self.status = ('01', 'Description')
        self.state.get_status = Mock()
        self.state.get_status.return_value = Mock()
        self.state.get_status.return_value.code = self.status[0]
        self.state.get_status.return_value.description = self.status[1]

        fake_new_state.return_value = self.state

        self.conn = Mock()
        self.scenario = 'SCENARIO'
        self.session = stc.Session(self.conn, self.scenario)

    def test_create(self):
        self.session.create()
        self.state.create.assert_called_once()

    def test_resume(self):
        self.session.resume()
        self.state.resume.assert_called_once()

    def test_refresh(self):
        status = self.session.refresh()
        self.assertEqual(status, self.state.refresh.return_value)
        self.state.refresh.assert_called_once()

    def test_get_logs(self):
        logs = self.session.get_logs()

        self.assertEqual(logs, self.state.get_logs.return_value)
        self.state.get_logs.assert_called_once()

    def test_session_id(self):
        self.assertEqual(self.session.session_id, self.state.get_id())

    def test_was_started(self):
        self.assertEqual(self.session.was_started, self.state.was_started())

    def test_task_list(self):
        self.assertEqual(self.session.task_list, self.state.get_task_list())

    def test_status(self):
        self.assertEqual(self.session.status, self.status)

    @patch('sap.rfc.stc.SessionStateFactory.new')
    def test_for_scenario_given_conn(self, fake_new_state):
        self.session.task_list
        fake_new_state.return_value = self.state

        session = stc.Session.for_scenario(self.scenario, conn=self.conn)

        fake_new_state.assert_called_once_with(self.conn, session._data)
        fake_new_state.return_value.create.assert_called_once()
