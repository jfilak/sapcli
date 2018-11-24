import sap.adt

class DummyADTObject(sap.adt.ADTObject):

    OBJTYPE = sap.adt.ADTObjectType(
        'DUMMY/S',
        'awesome/success',
        ('win', 'http://www.example.com/never/lose'),
        'application/super.cool.txt+xml',
        {'text/plain': 'no/bigdeal'}
    )

    def __init__(self):
        super(DummyADTObject, self).__init__('noconnection', 'noobject', 'nometadata')


