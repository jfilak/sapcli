#!/usr/bin/env python3

import re
import unittest
from unittest.mock import patch, Mock
from functools import partial
import xml.sax
from xml.sax.saxutils import escape

import sap.adt.cts
from sap.adt.cts import Element, WorkbenchABAPObject, TransportTypes
from sap.errors import SAPCliError

from mock import Connection, Response, Request
from fixtures_adt import (
    TASK_NUMBER,
    TRANSPORT_NUMBER,
    TASK_RELEASE_OK_RESPONSE,
    TASK_RELEASE_ERR_RESPONSE,
    TASK_CREATE_OK_RESPONSE,
    TRASNPORT_RELEASE_OK_RESPONSE,
    TRANSPORT_CREATE_OK_RESPONSE,
    SHORTENED_WORKBENCH_XML,
    SHORTENED_TRANSPORT_XML,
    SHORTENED_TASK_XML
)


CTS_OWNER='FILAK'


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

NO_OBJINFO_ABAP_OBJECT_ATTRIBUTES = {
    'tm:pgmid': 'R3TR',
    'tm:type': 'SUSH',
    'tm:name': '81680085',
    'tm:dummy_uri': '/sap/bc/adt/cts/transportrequests/reference?obj_name=81680085&amp;pgmid=R3TR',
}

WORKBENCH_ABAP_OBJECT = sap.adt.cts.WorkbenchABAPObject(
    pgmid='LIMU',
    type='TABD',
    name='FOO',
    wbtype='TABL/DS',
    description='Object Description',
    locked=True,
    position='000001'
)

FOREIGN_WORKBENCH_ABAP_OBJECT = sap.adt.cts.WorkbenchABAPObject(
    pgmid='LIMU',
    type='TABD',
    name='FOO',
    wbtype='TABL/DS',
    description='Object Description',
    locked=False,
    position='000000'
)

NO_DESC_WORKBENCH_ABAP_OBJECT = sap.adt.cts.WorkbenchABAPObject(
    pgmid='LIMU',
    type='TABD',
    name='FOO',
    wbtype='TABL/DS',
    description='Object Info',
    locked=False,
    position='000000'
)

NO_WTYPE_WORKBENCH_ABAP_OBJECT = sap.adt.cts.WorkbenchABAPObject(
    pgmid='LIMU',
    type='TABD',
    name='FOO',
    wbtype='',
    description='Object Info',
    locked=False,
    position='000000'
)

NO_OBJINFO_WORKBENCH_ABAP_OBJECT = sap.adt.cts.WorkbenchABAPObject(
    pgmid='R3TR',
    type='SUSH',
    name='81680085',
    wbtype='',
    description='(PGMID=R3TR,TYPE=SUSH,NAME=81680085)',
    locked=False,
    position='000000'
)

TASK_ATTRIBUTES = {
    'tm:number': TASK_NUMBER,
    'tm:parent': TRANSPORT_NUMBER,
    'tm:owner': CTS_OWNER,
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
    'tm:owner': CTS_OWNER,
    'tm:desc': 'Task Description',
    'tm:status': 'D',
    'tm:uri': f'/sap/bc/adt/vit/wb/object_type/%20%20%20%20rq/object_name/{TASK_NUMBER}'
}

TRANSPORT_ATTRIBUTES = {
    'tm:number': TRANSPORT_NUMBER,
    'tm:parent': '',
    'tm:owner': CTS_OWNER,
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
    'tm:owner': CTS_OWNER,
    'tm:desc': 'Transport Description',
    'tm:status': 'D',
    'tm:uri': f'/sap/bc/adt/vit/wb/object_type/%20%20%20%20rq/object_name/{TRANSPORT_NUMBER}'
}

class TestTransportTypes(unittest.TestCase):

    def test_workbench_constant(self):
        self.assertEqual(TransportTypes.Workbench, 'K')

    def test_customizing_constant(self):
        self.assertEqual(TransportTypes.Customizing, 'W')

    def test_transport_of_copies_constant(self):
        self.assertEqual(TransportTypes.TransportOfCopies, 'T')

    def test_development_correction_constant(self):
        self.assertEqual(TransportTypes.DevelopmentCorrection, 'S')

    def test_repair_constant(self):
        self.assertEqual(TransportTypes.Repair, 'R')

    def test_human_readable_workbench(self):
        self.assertEqual(TransportTypes.human_readable('K'), 'workbench')

    def test_human_readable_customizing(self):
        self.assertEqual(TransportTypes.human_readable('W'), 'customizing')

    def test_human_readable_transport_of_copies(self):
        self.assertEqual(TransportTypes.human_readable('T'), 'transport-of-copies')

    def test_human_readable_development_correction(self):
        self.assertEqual(TransportTypes.human_readable('S'), 'development-correction')

    def test_human_readable_repair(self):
        self.assertEqual(TransportTypes.human_readable('R'), 'repair')

    def test_human_readable_already_translated(self):
        self.assertEqual(TransportTypes.human_readable('workbench'), 'workbench')

    def test_human_readable_unknown_raises_error(self):
        with self.assertRaises(SAPCliError) as cm:
            TransportTypes.human_readable('X')
        self.assertEqual(str(cm.exception), 'Unknown transport type code: X')

    def test_from_human_readable_workbench(self):
        self.assertEqual(TransportTypes.from_human_readable('workbench'), 'K')

    def test_from_human_readable_customizing(self):
        self.assertEqual(TransportTypes.from_human_readable('customizing'), 'W')

    def test_from_human_readable_transport_of_copies(self):
        self.assertEqual(TransportTypes.from_human_readable('transport-of-copies'), 'T')

    def test_from_human_readable_development_correction(self):
        self.assertEqual(TransportTypes.from_human_readable('development-correction'), 'S')

    def test_from_human_readable_repair(self):
        self.assertEqual(TransportTypes.from_human_readable('repair'), 'R')

    def test_from_human_readable_already_code(self):
        self.assertEqual(TransportTypes.from_human_readable('K'), 'K')

    def test_from_human_readable_unknown_raises_error(self):
        with self.assertRaises(SAPCliError) as cm:
            TransportTypes.from_human_readable('invalid')
        self.assertEqual(str(cm.exception), 'Unknown transport type: invalid')

    def test_list_types(self):
        types = TransportTypes.list_types()
        self.assertIn('workbench', types)
        self.assertIn('customizing', types)
        self.assertIn('transport-of-copies', types)
        self.assertIn('development-correction', types)
        self.assertIn('repair', types)
        self.assertEqual(len(types), 5)

    def test_list_types_help(self):
        help_str = TransportTypes.list_types_help()
        self.assertIn('K/workbench', help_str)
        self.assertIn('W/customizing', help_str)
        self.assertIn('T/transport-of-copies', help_str)
        self.assertIn('S/development-correction', help_str)
        self.assertIn('R/repair', help_str)


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

        wbr = sap.adt.cts.AbstractWorkbenchRequest('connection', 'num_wb1', 'user_owner', 'description', 'R', 'target')

        self.assertEqual(wbr._connection, 'connection')
        self.assertEqual(wbr.number, 'num_wb1')
        self.assertEqual(wbr.owner, 'user_owner')
        self.assertEqual(wbr.description, 'description')
        self.assertEqual(wbr.target, 'target')

        self.assertEqual(wbr.status, 'R')
        self.assertTrue(wbr.is_released)

    def test_workbench_request_init_with_status(self):
        """Just to make sure init fill status with ? if no provided"""

        wbr = sap.adt.cts.AbstractWorkbenchRequest('connection', 'num_wb1', 'user_owner', 'description', None, 'target')

        self.assertEqual(wbr.status, '?')
        self.assertFalse(wbr.is_released)

    def test_workbench_transport_init(self):
        wbr = sap.adt.cts.WorkbenchTransport(['1', '2'], 'connection', 'num_wb1', 'user_owner', 'description')

        self.assertEqual(wbr.tasks, ['1', '2'])
        self.assertEqual(wbr._connection, 'connection')
        self.assertEqual(wbr.number, 'num_wb1')
        self.assertEqual(wbr.owner, 'user_owner')
        self.assertEqual(wbr.description, 'description')

    def test_workbench_transport_get_type_default(self):
        """Test default transport type is Workbench (K)"""
        wbr = sap.adt.cts.WorkbenchTransport([], 'connection', 'num_wb1')
        self.assertEqual(wbr.get_type(), 'K')

    def test_workbench_transport_get_type_with_tmtype(self):
        """Test transport type can be set via tmtype parameter"""
        wbr = sap.adt.cts.WorkbenchTransport([], 'connection', 'num_wb1', tmtype='W')
        self.assertEqual(wbr.get_type(), 'W')

    def test_workbench_transport_get_type_customizing(self):
        """Test customizing transport type"""
        wbr = sap.adt.cts.WorkbenchTransport([], 'connection', 'num_wb1', tmtype=TransportTypes.Customizing)
        self.assertEqual(wbr.get_type(), 'W')

    def test_workbench_transport_get_type_transport_of_copies(self):
        """Test transport of copies type"""
        wbr = sap.adt.cts.WorkbenchTransport([], 'connection', 'num_wb1', tmtype=TransportTypes.TransportOfCopies)
        self.assertEqual(wbr.get_type(), 'T')

    def test_workbench_transport_get_type_development_correction(self):
        """Test development correction type"""
        wbr = sap.adt.cts.WorkbenchTransport([], 'connection', 'num_wb1', tmtype=TransportTypes.DevelopmentCorrection)
        self.assertEqual(wbr.get_type(), 'S')

    def test_workbench_transport_get_type_repair(self):
        """Test repair type"""
        wbr = sap.adt.cts.WorkbenchTransport([], 'connection', 'num_wb1', tmtype=TransportTypes.Repair)
        self.assertEqual(wbr.get_type(), 'R')

    def test_workbench_task_init(self):
        wbr = sap.adt.cts.WorkbenchTask('parent', ['1', '2'], 'connection', 'num_wb1', 'user_owner', 'description')

        self.assertEqual(wbr._connection, 'connection')
        self.assertEqual(wbr.transport, 'parent')
        self.assertEqual(wbr.objects, ['1', '2'])
        self.assertEqual(wbr.number, 'num_wb1')
        self.assertEqual(wbr.owner, 'user_owner')
        self.assertEqual(wbr.description, 'description')

    def test_workbench_internal(self):

        wbr = sap.adt.cts.AbstractWorkbenchRequest('connection', 'num_wb1', 'user_owner', 'description', None, 'target')

        with self.assertRaises(NotImplementedError):
            wbr.get_type()

        with self.assertRaises(NotImplementedError):
            wbr._deserialize("No data")

        with self.assertRaises(NotImplementedError):
            wbr._release_children()

        with self.assertRaises(NotImplementedError):
            wbr._reassign_children("No owner")

        with self.assertRaises(NotImplementedError):
            wbr._delete_children()

        with self.assertRaises(NotImplementedError):
            wbr._create_request()

        with self.assertRaises(ValueError):
            wbr._copy("No copy on string")


class TestADTCTSWorkbenchRequestSetup(unittest.TestCase):

    def setUp(self):
        self.connection = Connection()

        self.object_1_1 = sap.adt.cts.WorkbenchABAPObject(
            pgmid='R3TR',
            type='CLAS',
            name='CL_FOO',
            wbtype='CLAS/AU',
            description='just a class',
            locked=True,
            position='000000'
        )

        self.object_1_2 = sap.adt.cts.WorkbenchABAPObject(
            pgmid='R3TR',
            type='CLAS',
            name='CL_BAR',
            wbtype='CLAS/CC',
            description='just another class & special char inside',
            locked=True,
            position='000001'
        )

        self.object_2_1 = sap.adt.cts.WorkbenchABAPObject(
            pgmid='LIMU',
            type='TABD',
            name='TADIR',
            wbtype='TABD/DS',
            description='just a table',
            locked=True,
            position='000000'
        )

        self.object_2_2 = sap.adt.cts.WorkbenchABAPObject(
            pgmid='LIMU',
            type='TABD',
            name='USR02',
            wbtype='TABD/DS',
            description='just another table',
            locked=True,
            position='000001'
        )

        self.transport_id = 'NPLK007000'

        self.task_1 = sap.adt.cts.WorkbenchTask(
            self.transport_id,
            [self.object_1_1, self.object_1_2],
            self.connection,
            number='NPLK007001',
            owner='ANZEIGER'
        )

        self.task_2 = sap.adt.cts.WorkbenchTask(
            self.transport_id,
            [self.object_2_1, self.object_2_2],
            self.connection,
            number='NPLK007002',
            owner='TESTER'
        )

        self.task_3 = sap.adt.cts.WorkbenchTask(
            self.transport_id,
            [],
            self.connection,
            number='NPLK007003',
            owner='TESTER',
            status='R'
        )

        self.transport = sap.adt.cts.WorkbenchTransport(
            [self.task_1, self.task_2, self.task_3],
            self.connection,
            number=self.transport_id,
            owner='TESTER'
        )


class TestADTCTSWorkbenchRequestRelease(TestADTCTSWorkbenchRequestSetup):

    def request_for_cts_task(self, task):
        return Request.post(
            f'/sap/bc/adt/cts/transportrequests/{task.number}/newreleasejobs',
            accept='application/vnd.sap.adt.transportorganizer.v1+xml'
        )

    def test_release_task(self):
        self.connection.set_responses(
            Response(status_code=200, text=TASK_RELEASE_OK_RESPONSE)
        )

        report = self.task_1.release()
        self.assertEqual(self.connection.execs, [self.request_for_cts_task(self.task_1)])
        self.assertEqual(str(report), f'Transport request/task {TASK_NUMBER} was successfully released')
        self.assertTrue(report.release_was_successful)

    def test_release_task_children_no_action(self):
        self.task_1._release_children()
        self.assertEqual(len(self.connection.execs), 0)

    def test_release_transport(self):
        self.connection.set_responses(
            Response(status_code=200, text=TRASNPORT_RELEASE_OK_RESPONSE)
        )

        self.transport.release()
        self.assertEqual(self.connection.execs, [self.request_for_cts_task(self.transport)])

    def test_release_transport_recursive(self):
        self.connection.set_responses(
            Response(status_code=200, text=TASK_RELEASE_OK_RESPONSE),
            Response(status_code=200, text=TASK_RELEASE_OK_RESPONSE),
            Response(status_code=200, text=TRASNPORT_RELEASE_OK_RESPONSE)
        )

        self.transport.release(recursive=True)

        self.assertEqual(
            self.connection.execs,
            [   self.request_for_cts_task(self.task_1),
                self.request_for_cts_task(self.task_2),
                self.request_for_cts_task(self.transport)
            ]
        )

    def test_release_task_error(self):
        self.connection.set_responses(
            Response(status_code=200, text=TASK_RELEASE_ERR_RESPONSE)
        )

        with self.assertRaises(sap.adt.cts.CTSReleaseError) as caught:
            self.task_2.release()

        self.assertEqual(str(caught.exception), f'Failed to release WorkbenchTask {self.task_2.number}: Error')


class TestADTCTSWorkbenchRequestDelete(TestADTCTSWorkbenchRequestSetup):

    def test_delete_task(self):
        self.task_1.delete()
        self.assertEqual(
            self.connection.execs,
            [Request.delete('/sap/bc/adt/cts/transportrequests/NPLK007001')]
        )

    def test_delete_transport(self):
        self.transport.delete()
        self.assertEqual(
            self.connection.execs,
            [Request.delete('/sap/bc/adt/cts/transportrequests/NPLK007000')]
        )


    def test_delete_transport_recursive(self):
        self.transport.delete(recursive=True)
        self.assertEqual(
            self.connection.execs,
            [   Request.put(
                    uri='/sap/bc/adt/cts/transportrequests/NPLK007001',
                    body=f'''<?xml version="1.0" encoding="ASCII"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:number="NPLK007001" tm:useraction="removeobject">
  <tm:request>
    <tm:abap_object tm:name="{self.object_1_1.name}" tm:obj_desc="{escape(self.object_1_1.description)}" tm:pgmid="{self.object_1_1.pgmid}" tm:type="{self.object_1_1.type}" tm:position="{self.object_1_1.position}"/>
  </tm:request>
</tm:root>'''
                ),
                Request.put(
                    uri='/sap/bc/adt/cts/transportrequests/NPLK007001',
                    body=f'''<?xml version="1.0" encoding="ASCII"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:number="NPLK007001" tm:useraction="removeobject">
  <tm:request>
    <tm:abap_object tm:name="{self.object_1_2.name}" tm:obj_desc="{escape(self.object_1_2.description)}" tm:pgmid="{self.object_1_2.pgmid}" tm:type="{self.object_1_2.type}" tm:position="{self.object_1_2.position}"/>
  </tm:request>
</tm:root>'''
                ),
                Request.delete('/sap/bc/adt/cts/transportrequests/NPLK007001'),
                Request.put(
                    uri='/sap/bc/adt/cts/transportrequests/NPLK007002',
                    body=f'''<?xml version="1.0" encoding="ASCII"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:number="NPLK007002" tm:useraction="removeobject">
  <tm:request>
    <tm:abap_object tm:name="{self.object_2_1.name}" tm:obj_desc="{escape(self.object_2_1.description)}" tm:pgmid="{self.object_2_1.pgmid}" tm:type="{self.object_2_1.type}" tm:position="{self.object_2_1.position}"/>
  </tm:request>
</tm:root>'''
                ),
                Request.put(
                    uri='/sap/bc/adt/cts/transportrequests/NPLK007002',
                    body=f'''<?xml version="1.0" encoding="ASCII"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:number="NPLK007002" tm:useraction="removeobject">
  <tm:request>
    <tm:abap_object tm:name="{self.object_2_2.name}" tm:obj_desc="{escape(self.object_2_2.description)}" tm:pgmid="{self.object_2_2.pgmid}" tm:type="{self.object_2_2.type}" tm:position="{self.object_2_2.position}"/>
  </tm:request>
</tm:root>'''
                ),
                Request.delete('/sap/bc/adt/cts/transportrequests/NPLK007002'),
                Request.delete('/sap/bc/adt/cts/transportrequests/NPLK007000'),
            ]
        )


class TestADTCTSWorkbenchRequestCreate(TestADTCTSWorkbenchRequestSetup):

    def test_create_task(self):
        self.connection.set_responses(
            Response(status_code=201, text=TASK_CREATE_OK_RESPONSE)
        )

        self.task_1._number = None
        self.task_1._transport = self.transport.number
        self.task_1.create()
        self.maxDiff = None

        self.assertEqual(len(self.connection.execs), 1)
        self.connection.execs[0].assertEqual(
            Request.post_text(
                uri=f'/sap/bc/adt/cts/transportrequests/{self.task_1.transport}/tasks',
                accept='application/vnd.sap.adt.transportorganizer.v1+xml',
                body=f'''<?xml version="1.0" encoding="ASCII"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:number="{self.task_1.transport}" tm:targetuser="{self.task_1.owner}" tm:useraction="newtask"/>
'''
            ),
            asserter=self
        )
        self.assertEqual(self.task_1.number, TASK_NUMBER)

    def test_create_transport(self):
        self.connection.set_responses(
            Response(status_code=201, text=TRANSPORT_CREATE_OK_RESPONSE)
        )

        self.transport._number = None
        self.transport.create()
        self.maxDiff = None
        self.assertEqual(
            self.connection.execs,
            [   Request.post_text(
                    uri='/sap/bc/adt/cts/transportrequests',
                    accept='application/vnd.sap.adt.transportorganizer.v1+xml',
                    body=f'''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:useraction="newrequest">
  <tm:request tm:desc="{self.transport.description}" tm:type="K" tm:target="{self.transport.target}" tm:cts_project="">
    <tm:task tm:owner="{self.transport.owner}"/>
  </tm:request>
</tm:root>
'''
                )
            ]
        )
        self.assertEqual(self.transport.number, TRANSPORT_NUMBER)

    def test_create_transport_with_customizing_type(self):
        """Test creating transport with customizing type (W)"""
        self.connection.set_responses(
            Response(status_code=201, text=TRANSPORT_CREATE_OK_RESPONSE)
        )

        transport = sap.adt.cts.WorkbenchTransport(
            [self.task_1, self.task_2],
            self.connection,
            number=None,
            owner='TESTER',
            description='Customizing Transport',
            target='LOCAL',
            tmtype=TransportTypes.Customizing
        )
        transport.create()
        self.maxDiff = None
        self.assertEqual(
            self.connection.execs,
            [   Request.post_text(
                    uri='/sap/bc/adt/cts/transportrequests',
                    accept='application/vnd.sap.adt.transportorganizer.v1+xml',
                    body='''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:useraction="newrequest">
  <tm:request tm:desc="Customizing Transport" tm:type="W" tm:target="LOCAL" tm:cts_project="">
    <tm:task tm:owner="TESTER"/>
  </tm:request>
</tm:root>
'''
                )
            ]
        )
        self.assertEqual(transport.number, TRANSPORT_NUMBER)

    def test_create_transport_with_repair_type(self):
        """Test creating transport with repair type (R)"""
        self.connection.set_responses(
            Response(status_code=201, text=TRANSPORT_CREATE_OK_RESPONSE)
        )

        transport = sap.adt.cts.WorkbenchTransport(
            [],
            self.connection,
            number=None,
            owner='TESTER',
            description='Repair Transport',
            target='LOCAL',
            tmtype=TransportTypes.Repair
        )
        transport.create()
        self.maxDiff = None
        self.assertEqual(
            self.connection.execs,
            [   Request.post_text(
                    uri='/sap/bc/adt/cts/transportrequests',
                    accept='application/vnd.sap.adt.transportorganizer.v1+xml',
                    body='''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:useraction="newrequest">
  <tm:request tm:desc="Repair Transport" tm:type="R" tm:target="LOCAL" tm:cts_project="">
    <tm:task tm:owner="TESTER"/>
  </tm:request>
</tm:root>
'''
                )
            ]
        )
        self.assertEqual(transport.number, TRANSPORT_NUMBER)


class TestADTCTSWorkbenchRequestReassign(TestADTCTSWorkbenchRequestSetup):

    def test_reassign_task(self):
        self.task_1.reassign('FILAK')
        self.maxDiff = None
        self.assertEqual(
            self.connection.execs,
            [   Request.put(
                    uri='/sap/bc/adt/cts/transportrequests/NPLK007001',
                    body=f'''<?xml version="1.0" encoding="ASCII"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm"
 tm:number="NPLK007001"
 tm:targetuser="FILAK"
 tm:useraction="changeowner"/>'''
                )
            ]
        )

    def test_reassign_transport(self):
        self.transport.reassign('FILAK')
        self.maxDiff = None
        self.assertEqual(
            self.connection.execs,
            [   Request.put(
                    uri='/sap/bc/adt/cts/transportrequests/NPLK007000',
                    body=f'''<?xml version="1.0" encoding="ASCII"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm"
 tm:number="NPLK007000"
 tm:targetuser="FILAK"
 tm:useraction="changeowner"/>'''
                )
            ]
        )

    def test_reassign_transport_recursive(self):
        self.transport.reassign('FILAK', recursive=True)
        self.maxDiff = None
        self.assertEqual(
            self.connection.execs,
            [   Request.put(
                    uri='/sap/bc/adt/cts/transportrequests/NPLK007001',
                    body=f'''<?xml version="1.0" encoding="ASCII"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm"
 tm:number="NPLK007001"
 tm:targetuser="FILAK"
 tm:useraction="changeowner"/>'''),
                Request.put(
                    uri='/sap/bc/adt/cts/transportrequests/NPLK007002',
                    body=f'''<?xml version="1.0" encoding="ASCII"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm"
 tm:number="NPLK007002"
 tm:targetuser="FILAK"
 tm:useraction="changeowner"/>'''),
                Request.put(
                    uri='/sap/bc/adt/cts/transportrequests/NPLK007000',
                    body=f'''<?xml version="1.0" encoding="ASCII"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm"
 tm:number="NPLK007000"
 tm:targetuser="FILAK"
 tm:useraction="changeowner"/>''')
            ]
        )


class TestADTCTSWorkbenchRequestFetch(TestADTCTSWorkbenchRequestSetup):

    def test_fetch_task(self):
        self.connection.set_responses(
            Response(status_code=200, text=SHORTENED_TASK_XML)
        )

        task = sap.adt.cts.WorkbenchTask(None, [], self.connection, TASK_NUMBER)
        task.fetch()

        self.assertEqual(task.transport, TRANSPORT_NUMBER)
        self.assertEqual(task.description, 'Task Description')
        self.assertEqual(task.owner, 'FILAK')
        self.assertEqual(task.objects, [WorkbenchABAPObject(pgmid='LIMU', type='FUNC', name='TR_REQ_CHECK_OBJECTS_AND_KEYS', wbtype='FUGR/FF', description='Prüfe Objekte und Schlüssel in einem Auftrag', locked=True, position='000001')])
        self.assertEqual(task._status, 'D')

        self.assertIsNone(task.target)

    def test_fetch_transport(self):
        self.connection.set_responses(
            Response(status_code=200, text=SHORTENED_TRANSPORT_XML)
        )

        transport = sap.adt.cts.WorkbenchTransport([], self.connection, TRANSPORT_NUMBER)
        transport.fetch()

        self.assertEqual(transport.description, 'Transport Description')
        self.assertEqual(transport.owner, 'FILAK')
        self.assertEqual(transport._status, 'D')
        self.assertEqual(transport.target, 'CTS_TARGET')

        self.assertEqual(len(transport.tasks), 1)
        task = transport.tasks[0]
        self.assertEqual(task.description, 'Task Description')
        self.assertEqual(task.owner, 'FILAK')
        self.assertEqual(task._status, 'D')

        self.assertIsNone(task.target)


class TestADTCTSWorkbenchTask(TestADTCTSWorkbenchRequestSetup):

    def test_get_type(self):
        self.assertEqual(self.task_1.get_type(), 'T')


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
        self.assertEqual(task.owner, CTS_OWNER)
        self.assertEqual(task._connection, connection)
        self.assertEqual(task.transport, TRANSPORT_NUMBER)
        self.assertEqual(task.objects, [WORKBENCH_ABAP_OBJECT])

    def assert_trasport_equal(self, transport, connection='noconnection'):
        self.assertEqual(len(transport.tasks), 1)

        self.assertEqual(transport.number, TRANSPORT_NUMBER)
        self.assertEqual(transport.description, 'Transport Description')
        self.assertEqual(transport.status, 'D')
        self.assertEqual(transport.owner, CTS_OWNER)
        self.assertEqual(transport._connection, connection)

    def test_process_abap_object_foreign(self):
        builder = sap.adt.cts.WorkbenchBuilder('noconnection')
        wb_object = builder.process_abap_object_xml(Element(FOREIGN_ABAP_OBJECT_ATTRIBUTES, []))

        self.assertEqual(wb_object, FOREIGN_WORKBENCH_ABAP_OBJECT)

    def test_process_abap_object_no_desc(self):
        builder = sap.adt.cts.WorkbenchBuilder('noconnection')
        wb_object = builder.process_abap_object_xml(Element(NO_DESC_ABAP_OBJECT_ATTRIBUTES, []))

        self.assertEqual(wb_object, NO_DESC_WORKBENCH_ABAP_OBJECT)

    def test_process_abap_object_no_wbtype(self):
        builder = sap.adt.cts.WorkbenchBuilder('noconnection')
        wb_object = builder.process_abap_object_xml(Element(NO_WBTYPE_ABAP_OBJECT_ATTRIBUTES, []))

        self.assertEqual(wb_object, NO_WTYPE_WORKBENCH_ABAP_OBJECT)

    def test_process_abap_object_no_objinfo(self):
        builder = sap.adt.cts.WorkbenchBuilder('noconnection')
        wb_object = builder.process_abap_object_xml(Element(NO_OBJINFO_ABAP_OBJECT_ATTRIBUTES, []))

        self.assertEqual(wb_object, NO_OBJINFO_WORKBENCH_ABAP_OBJECT)

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

        transport = workbench.get_transport_requests(user=CTS_OWNER)

        self.assertEqual(
            connection.execs,
            [Request('GET',
                     f'/sap/bc/adt/cts/transportrequests',
                     {'Accept': 'application/vnd.sap.adt.transportorganizertree.v1+xml, application/vnd.sap.adt.transportorganizer.v1+xml'},
                     None,
                     sap.adt.cts.workbench_params(CTS_OWNER))])

        self.assert_trasport_equal(transport[0], connection)
        self.assert_task_equal(transport[0].tasks[0], connection)

    @patch('sap.adt.cts.Workbench.get_transport_requests')
    def test_fetch_transport_requests_no_transports(self, fake_get_transports):
        workbench = sap.adt.cts.Workbench(Mock())

        fake_get_transports.return_value = []

        transport = workbench.fetch_transport_request('NPLK123456')

        self.assertIsNone(transport)
        fake_get_transports.assert_called_once_with(user=None)

    @patch('sap.adt.cts.Workbench.get_transport_requests')
    def test_fetch_transport_requests_with_user(self, fake_get_transports):
        workbench = sap.adt.cts.Workbench(Mock())

        fake_get_transports.return_value = []

        transport = workbench.fetch_transport_request('NPLK123456', user='anzeiger')

        self.assertIsNone(transport)
        fake_get_transports.assert_called_once_with(user='anzeiger')

    @patch('sap.adt.cts.Workbench.get_transport_requests')
    def test_fetch_transport_requests_different_transports(self, fake_get_transports):
        workbench = sap.adt.cts.Workbench(Mock())

        wbr = sap.adt.cts.AbstractWorkbenchRequest('connection', 'num_wb1', 'user_owner', 'description')

        fake_get_transports.return_value = [wbr]

        transport = workbench.fetch_transport_request('NPLK123456')

        self.assertIsNone(transport)

    @patch('sap.adt.cts.Workbench.get_transport_requests')
    def test_fetch_transport_requests_found_transports(self, fake_get_transports):
        workbench = sap.adt.cts.Workbench(Mock())

        wbr_1 = sap.adt.cts.AbstractWorkbenchRequest('connection', 'num_wb1', 'user_owner', 'description')
        wbr_2 = sap.adt.cts.AbstractWorkbenchRequest('connection', 'NPLK123456', 'user_owner', 'description')

        fake_get_transports.return_value = [wbr_1, wbr_2]

        transport = workbench.fetch_transport_request('NPLK123456')

        self.assertIsNotNone(transport)
        self.assertEqual(transport.number, 'NPLK123456')


if __name__ == '__main__':
    unittest.main()
