import sap.adt
from mock import Response


LOCK_RESPONSE_OK = Response(text='<sap><LOCK_HANDLE>win</LOCK_HANDLE></sap>',
                            status_code=200,
                            headers={'Content-Type': 'dataname=com.sap.adt.lock.Result'})


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


