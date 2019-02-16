import sap.adt
from mock import Response


EMPTY_RESPONSE_OK = Response(text='', status_code=200, headers={})

LOCK_RESPONSE_OK = Response(text='<sap><LOCK_HANDLE>win</LOCK_HANDLE></sap>',
                            status_code=200,
                            headers={'Content-Type': 'dataname=com.sap.adt.lock.Result'})

TASK_NUMBER='1A2B3C4D5E'
TRANSPORT_NUMBER='E5D4C3B2A1'

TASK_RELEASE_OK_RESPONSE = f'''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:useraction="newreleasejobs" tm:releasetimestamp="20190212191502 " tm:number="{TASK_NUMBER}">
  <tm:releasereports>
    <chkrun:checkReport xmlns:chkrun="http://www.sap.com/adt/checkrun" chkrun:reporter="transportrelease" chkrun:triggeringUri="/sap/bc/adt/cts/transportrequests/{TASK_NUMBER}" chkrun:status="released" chkrun:statusText="Transport request/task {TASK_NUMBER} was successfully released"/>
  </tm:releasereports>
</tm:root>'''

TRASNPORT_RELEASE_OK_RESPONSE = f'''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:useraction="newreleasejobs" tm:releasetimestamp="20190212191502 " tm:number="{TRANSPORT_NUMBER}">
  <tm:releasereports>
    <chkrun:checkReport xmlns:chkrun="http://www.sap.com/adt/checkrun" chkrun:reporter="transportrelease" chkrun:triggeringUri="/sap/bc/adt/cts/transportrequests/{TRANSPORT_NUMBER}" chkrun:status="released" chkrun:statusText="Transport request/task {TRANSPORT_NUMBER} was successfully released"/>
  </tm:releasereports>
</tm:root>'''


class DummyADTObject(sap.adt.ADTObject):

    OBJTYPE = sap.adt.ADTObjectType(
        'DUMMY/S',
        'awesome/success',
        ('win', 'http://www.example.com/never/lose'),
        'application/super.cool.txt+xml',
        {'text/plain': 'no/bigdeal'},
        'dummies'
    )

    def __init__(self, connection='noconnection', name='noobject', metadata='nometadata'):
        super(DummyADTObject, self).__init__(connection, name, metadata)


