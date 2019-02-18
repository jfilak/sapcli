#!/usr/bin/env python3

import unittest
from functools import partial
import xml.sax

import sap.adt.cts
from sap.adt.cts import Element

from mock import Connection, Response, Request
from fixtures_adt import (
    TASK_NUMBER,
    TRANSPORT_NUMBER,
    TASK_RELEASE_OK_RESPONSE,
    TRASNPORT_RELEASE_OK_RESPONSE,
    SHORTENED_WORKBENCH_XML
)

ABAP_OBJECT_ATTRIBUTES = {
    'tm:pgmid': 'LIMU',
    'tm:type': 'TABD',
    'tm:name': 'FOO',
    'tm:wbtype': 'TABL/DS',
    'tm:dummy_uri': '/sap/bc/adt/cts/transportrequests/reference?obj_name=FOO&amp;obj_wbtype=TABD&amp;pgmid=LIMU',
    'tm:obj_info': 'Table Definition',
    'tm:obj_desc': 'Object Description',
    'tm:position': '000001',
    'tm:lock_status': 'X',
    'tm:img_activity': ''
}

FOREIGN_ABAP_OBJECT_ATTRIBUTES = {
    'tm:pgmid': 'LIMU',
    'tm:type': 'TABD',
    'tm:name': 'FOO',
    'tm:wbtype': 'TABL/DS',
    'tm:dummy_uri': '/sap/bc/adt/cts/transportrequests/reference?obj_name=FOO&amp;obj_wbtype=TABD&amp;pgmid=LIMU',
    'tm:obj_info': 'Table Definition',
    'tm:obj_desc': 'Object Description',
}

NO_DESC_ABAP_OBJECT_ATTRIBUTES = {
    'tm:pgmid': 'LIMU',
    'tm:type': 'TABD',
    'tm:name': 'FOO',
    'tm:wbtype': 'TABL/DS',
    'tm:dummy_uri': '/sap/bc/adt/cts/transportrequests/reference?obj_name=FOO&amp;obj_wbtype=TABD&amp;pgmid=LIMU',
    'tm:obj_info': 'Object Info',
}

NO_WBTYPE_ABAP_OBJECT_ATTRIBUTES = {
    'tm:pgmid': 'LIMU',
    'tm:type': 'TABD',
    'tm:name': 'FOO',
    'tm:dummy_uri': '/sap/bc/adt/cts/transportrequests/reference?obj_name=FOO&amp;pgmid=LIMU',
    'tm:obj_info': 'Object Info',
}

WORKBENCH_ABAP_OBJECT = sap.adt.cts.WorkbenchABAPObject(
    pgmid='LIMU',
    type='TABD',
    name='FOO',
    wbtype='TABL/DS',
    description='Object Description',
    locked=True
)

FOREIGN_WORKBENCH_ABAP_OBJECT = sap.adt.cts.WorkbenchABAPObject(
    pgmid='LIMU',
    type='TABD',
    name='FOO',
    wbtype='TABL/DS',
    description='Object Description',
    locked=False
)

NO_DESC_WORKBENCH_ABAP_OBJECT = sap.adt.cts.WorkbenchABAPObject(
    pgmid='LIMU',
    type='TABD',
    name='FOO',
    wbtype='TABL/DS',
    description='Object Info',
    locked=False
)

NO_WTYPE_WORKBENCH_ABAP_OBJECT = sap.adt.cts.WorkbenchABAPObject(
    pgmid='LIMU',
    type='TABD',
    name='FOO',
    wbtype='',
    description='Object Info',
    locked=False
)

TASK_ATTRIBUTES = {
    'tm:number': TASK_NUMBER,
    'tm:parent': TRANSPORT_NUMBER,
    'tm:owner': 'FILAK',
    'tm:desc': 'Task Description',
    'tm:type': 'Development/Correction',
    'tm:status': 'D',
    'tm:target': '',
    'tm:target_desc': '',
    'tm:cts_project': '',
    'tm:cts_project_desc': '',
    'tm:lastchanged_timestamp': '20190212190504',
    'tm:uri': f'/sap/bc/adt/vit/wb/object_type/%20%20%20%20rq/object_name/{TASK_NUMBER}'
}

NW_752_SP2_TASK_ATTRIBUTES = {
    'tm:number': TASK_NUMBER,
    'tm:owner': 'FILAK',
    'tm:desc': 'Task Description',
    'tm:status': 'D',
    'tm:uri': f'/sap/bc/adt/vit/wb/object_type/%20%20%20%20rq/object_name/{TASK_NUMBER}'
}

TRANSPORT_ATTRIBUTES = {
    'tm:number': TRANSPORT_NUMBER,
    'tm:parent': '',
    'tm:owner': 'FILAK',
    'tm:desc': 'Transport Description',
    'tm:type': 'K',
    'tm:status': 'D',
    'tm:target': '',
    'tm:target_desc': '',
    'tm:cts_project': '',
    'tm:cts_project_desc': '',
    'tm:lastchanged_timestamp': '20190206110506',
    'tm:uri': f'/sap/bc/adt/vit/wb/object_type/%20%20%20%20rq/object_name/{TRANSPORT_NUMBER}'
}

NW_752_SP2_TRANSPORT_ATTRIBUTES = {
    'tm:number': TRANSPORT_NUMBER,
    'tm:owner': 'FILAK',
    'tm:desc': 'Transport Description',
    'tm:status': 'D',
    'tm:uri': f'/sap/bc/adt/vit/wb/object_type/%20%20%20%20rq/object_name/{TRANSPORT_NUMBER}'
}

class TestADTCTS(unittest.TestCase):

    def test_workbench_params(self):
        """Sanity checking the function generating dictionary with HTTP
           parameters for workbench request.
        """

        exp_params = {
            'user': 'anzeiger',
            'target': 'true',
            'requestType': 'KWT',
            'requestStatus': 'DR'
        }

        act_params = sap.adt.cts.workbench_params('anzeiger')

        self.assertEqual(act_params, exp_params)


class TestADTCTSWorkbenchRequest(unittest.TestCase):

    def test_workbench_request_init(self):
        """Just to make sure init populates all the properties."""

        wbr = sap.adt.cts.AbstractWorkbenchRequest('connection', 'num_wb1', 'user_owner', 'description')

        self.assertEqual(wbr._connection, 'connection')
        self.assertEqual(wbr.number, 'num_wb1')
        self.assertEqual(wbr.owner, 'user_owner')
        self.assertEqual(wbr.description, 'description')

    def test_workbench_transport_init(self):
        wbr = sap.adt.cts.WorkbenchTransport(['1', '2'], 'connection', 'num_wb1', 'user_owner', 'description')

        self.assertEqual(wbr.tasks, ['1', '2'])
        self.assertEqual(wbr._connection, 'connection')
        self.assertEqual(wbr.number, 'num_wb1')
        self.assertEqual(wbr.owner, 'user_owner')
        self.assertEqual(wbr.description, 'description')

    def test_workbench_task_init(self):
        wbr = sap.adt.cts.WorkbenchTask('parent', ['1', '2'], 'connection', 'num_wb1', 'user_owner', 'description')

        self.assertEqual(wbr._connection, 'connection')
        self.assertEqual(wbr.transport, 'parent')
        self.assertEqual(wbr.objects, ['1', '2'])
        self.assertEqual(wbr.number, 'num_wb1')
        self.assertEqual(wbr.owner, 'user_owner')
        self.assertEqual(wbr.description, 'description')

    def do_check_release(self, factory):
        """Check it correctly builds the URL with parameters and returns
           the expected data.
        """

        connection = Connection([Response(TASK_RELEASE_OK_RESPONSE, 200, {})])

        wbr = factory(connection, TASK_NUMBER)
        resp = wbr.release()

        self.assertEqual(
            connection.execs,
            [Request('POST',
                     f'/sap/bc/adt/cts/transportrequests/{TASK_NUMBER}/newreleasejobs',
                     {'Accept': 'application/vnd.sap.adt.transportorganizer.v1+xml'},
                     None,
                     None)])

        self.assertEqual(resp, TASK_RELEASE_OK_RESPONSE)

    def test_workbench_request_release(self):
        "AbstractWorkbenchRequest can be released"""

        self.do_check_release(sap.adt.cts.AbstractWorkbenchRequest)

    def test_workbench_transport_release(self):
        "WorkbenchTransport can be released"""

        self.do_check_release(partial(sap.adt.cts.WorkbenchTransport, None))

    def test_workbench_task_release(self):
        "WorkbenchTask can be released"""

        self.do_check_release(partial(sap.adt.cts.WorkbenchTask, None, None))


class TestADTCTSWorkbenchResponseHandler(unittest.TestCase):

    def process_abap_object_xml(self, abap_object_elem):
        self.objects.append(abap_object_elem)

    def process_task_xml(self, task_elem):
        self.tasks.append(task_elem)

    def process_transport_xml(self, transport_elem):
        self.transports.append(transport_elem)

    def test_simplified_xml(self):
        self.objects = []
        self.tasks = []
        self.transports = []

        handler = sap.adt.cts.WorkbenchResponseHandler(self)
        xml.sax.parseString(SHORTENED_WORKBENCH_XML, handler)

        self.assertEqual(self.objects, [])
        self.assertEqual(self.tasks, [])

        transport = self.transports[0]
        task = transport.children[0]
        abap_object = task.children[0]

        self.assertEqual(abap_object.attributes['tm:pgmid'], 'LIMU')
        self.assertEqual(task.attributes['tm:number'], TASK_NUMBER)
        self.assertEqual(transport.attributes['tm:number'], TRANSPORT_NUMBER)
        self.assertEqual(transport.children[0].attributes['tm:number'], TASK_NUMBER)
        self.assertEqual(transport.children[0].children[0].attributes['tm:pgmid'], 'LIMU')


class TestADTCTSWorkbenchBuilder(unittest.TestCase):

    def assert_task_equal(self, task, connection='noconnection'):
        self.assertEqual(task.number, TASK_NUMBER)
        self.assertEqual(task.description, 'Task Description')
        self.assertEqual(task.status, 'D')
        self.assertEqual(task.owner, 'FILAK')
        self.assertEqual(task._connection, connection)
        self.assertEqual(task.transport, TRANSPORT_NUMBER)
        self.assertEqual(task.objects, [WORKBENCH_ABAP_OBJECT])

    def assert_trasport_equal(self, transport, connection='noconnection'):
        self.assertEqual(len(transport.tasks), 1)

        self.assertEqual(transport.number, TRANSPORT_NUMBER)
        self.assertEqual(transport.description, 'Transport Description')
        self.assertEqual(transport.status, 'D')
        self.assertEqual(transport.owner, 'FILAK')
        self.assertEqual(transport._connection, connection)

    def test_process_abap_object_foreign(self):
        builder = sap.adt.cts.WorkbenchBuilder('noconnection')
        wb_object = builder.process_abap_object_xml(Element(FOREIGN_ABAP_OBJECT_ATTRIBUTES, []))

        self.assertEqual(wb_object, FOREIGN_WORKBENCH_ABAP_OBJECT)

    def test_process_abap_object_foreign(self):
        builder = sap.adt.cts.WorkbenchBuilder('noconnection')
        wb_object = builder.process_abap_object_xml(Element(NO_DESC_ABAP_OBJECT_ATTRIBUTES, []))

        self.assertEqual(wb_object, NO_DESC_WORKBENCH_ABAP_OBJECT)

    def test_process_abap_object_no_wbtype(self):
        builder = sap.adt.cts.WorkbenchBuilder('noconnection')
        wb_object = builder.process_abap_object_xml(Element(NO_WBTYPE_ABAP_OBJECT_ATTRIBUTES, []))

        self.assertEqual(wb_object, NO_WTYPE_WORKBENCH_ABAP_OBJECT)

    def test_process_abap_object(self):
        builder = sap.adt.cts.WorkbenchBuilder('noconnection')
        wb_object = builder.process_abap_object_xml(Element(ABAP_OBJECT_ATTRIBUTES, []))

        self.assertEqual(wb_object, WORKBENCH_ABAP_OBJECT)

    def test_process_task(self):
        builder = sap.adt.cts.WorkbenchBuilder('noconnection')
        task = builder.process_task_xml(Element(TASK_ATTRIBUTES, [Element(ABAP_OBJECT_ATTRIBUTES, [])]))

        self.assert_task_equal(task)

    def test_process_transport(self):
        builder = sap.adt.cts.WorkbenchBuilder('noconnection')

        abap_object_elem = Element(ABAP_OBJECT_ATTRIBUTES, [])
        task_elem = Element(TASK_ATTRIBUTES, [abap_object_elem])

        transport = builder.process_transport_xml(Element(TRANSPORT_ATTRIBUTES,[task_elem]))
        self.assert_trasport_equal(transport)
        self.assert_task_equal(transport.tasks[0])

    def test_process_task_752_sp2(self):
        builder = sap.adt.cts.WorkbenchBuilder('noconnection')
        task = builder.process_task_xml(Element(TASK_ATTRIBUTES, [Element(ABAP_OBJECT_ATTRIBUTES, [])]))

        self.assert_task_equal(task)

    def test_process_transport_752_sp2(self):
        builder = sap.adt.cts.WorkbenchBuilder('noconnection')

        abap_object_elem = Element(ABAP_OBJECT_ATTRIBUTES, [])
        task_elem = Element(NW_752_SP2_TASK_ATTRIBUTES, [abap_object_elem])

        transport = builder.process_transport_xml(Element(NW_752_SP2_TRANSPORT_ATTRIBUTES, [task_elem]))
        self.assert_trasport_equal(transport)
        self.assert_task_equal(transport.tasks[0])

    def test_get_transport_requests(self):
        connection = Connection([Response(SHORTENED_WORKBENCH_XML, 200, {})])
        workbench = sap.adt.cts.Workbench(connection)

        transport = workbench.get_transport_requests(user='FILAK')

        self.assertEqual(
            connection.execs,
            [Request('GET',
                     f'/sap/bc/adt/cts/transportrequests',
                     {'Accept': 'application/vnd.sap.adt.transportorganizer.v1+xml'},
                     None,
                     sap.adt.cts.workbench_params('FILAK'))])

        self.assert_trasport_equal(transport[0], connection)
        self.assert_task_equal(transport[0].tasks[0], connection)


if __name__ == '__main__':
    unittest.main()
