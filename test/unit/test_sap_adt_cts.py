#!/usr/bin/env python3

import unittest

import sap.adt.cts

from mock import Connection, Response, Request

FIXTURE_TASK_NUMBER='1A2B3C4D5E'

FIXTURE_RELEASE_OK_RESPONSE = f'''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:useraction="newreleasejobs" tm:releasetimestamp="20190212191502 " tm:number="{FIXTURE_TASK_NUMBER}">
  <tm:releasereports>
    <chkrun:checkReport xmlns:chkrun="http://www.sap.com/adt/checkrun" chkrun:reporter="transportrelease" chkrun:triggeringUri="/sap/bc/adt/cts/transportrequests/{FIXTURE_TASK_NUMBER}" chkrun:status="released" chkrun:statusText="Transport request/task {FIXTURE_TASK_NUMBER} was successfully released"/>
  </tm:releasereports>
</tm:root>'''


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

    def test_workbench_request_release(self):
        """Check it correctly builds the URL with parameters and returns
           the expected data.
        """

        connection = Connection([Response(FIXTURE_RELEASE_OK_RESPONSE, 200, {})])

        wbr = sap.adt.cts.AbstractWorkbenchRequest(connection, FIXTURE_TASK_NUMBER)
        resp = wbr.release()

        self.assertEqual(
            connection.execs,
            [Request('POST',
                     f'/sap/bc/adt/cts/transportrequests/{FIXTURE_TASK_NUMBER}/newreleasejobs',
                     {'Accept': 'application/vnd.sap.adt.transportorganizer.v1+xml'},
                     None,
                     None)])

        self.assertEqual(resp, FIXTURE_RELEASE_OK_RESPONSE)


if __name__ == '__main__':
    unittest.main()
