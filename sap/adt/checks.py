"""Object Checks ADT wrappers"""

from fnmatch import fnmatch

from sap.adt.objects import ADTObjectType, XMLNamespace, xmlns_adtcore_ancestor
from sap.adt.marshalling import Marshal
from sap.adt.annotations import OrderedClassMembers, XmlNodeAttributeProperty, XmlListNodeProperty, XmlElementKind, \
    XmlContainer


XMLNS_CHKRUN = XMLNamespace('chkrun', 'http://www.sap.com/adt/checkrun')
XMLNS_CHKRUN_WITH_ADTCORE = xmlns_adtcore_ancestor('chkrun', 'http://www.sap.com/adt/checkrun')


# pylint: disable=too-few-public-methods
class Reporter(metaclass=OrderedClassMembers):
    """ADT Object Checks Run Reporter"""

    name = XmlNodeAttributeProperty('chkrun:name')
    supported_types = XmlListNodeProperty('chkrun:supportedType', kind=XmlElementKind.TEXT)

    def supports_type(self, obj_code):
        """Returns true if the give object code is supported"""

        return any((fnmatch(obj_code, styp) for styp in self.supported_types))

    def supports_object(self, adt_obj):
        """Returns true if the given object is supported"""

        return self.supports_type(adt_obj.objtype.code)


# pylint: disable=invalid-name
ReportersContainer = XmlContainer.define('chkrun:reporter', Reporter)
ReportersContainer.objtype = ADTObjectType(None,
                                           'checkruns/reporters',
                                           XMLNS_CHKRUN,
                                           'application/vnd.sap.adt.reporters+xml',
                                           None,
                                           'checkReporters')


class CheckObject(metaclass=OrderedClassMembers):
    """ADT Check Object item for the run request"""

    uri = XmlNodeAttributeProperty('adtcore:uri')
    chkrun_version = XmlNodeAttributeProperty('chkrun:version', value='new')

    def __init__(self, uri):
        self.uri = uri


class CheckObjectList(metaclass=OrderedClassMembers):
    """ADT run request items"""

    objtype = ADTObjectType(None,
                            'checkruns',
                            XMLNS_CHKRUN_WITH_ADTCORE,
                            'application/vnd.sap.adt.checkobjects+xml',
                            None,
                            'checkObjectList')

    objects = XmlListNodeProperty('chkrun:checkObject')

    def __iter__(self):
        return iter(self.objects)

    def add_uri(self, uri):
        """Adds the give URI to the list"""

        self.objects = CheckObject(uri)

    def add_object(self, adt_object):
        """Adds the give object to the list"""

        self.add_uri(adt_object.full_adt_uri)


def fetch_reporters(connection):
    """Returns the list of supported ADT reporters"""

    reporters = ReportersContainer()

    resp = connection.execute('GET', reporters.objtype.basepath, accept=reporters.objtype.mimetype)

    Marshal.deserialize(resp.text, reporters)

    return reporters.items


def run_for_supported_objects(connection, reporter, adt_objects):
    """Runs the give checks for all supported adt objects"""

    object_list = CheckObjectList()

    for obj in adt_objects:
        if reporter.supports_object(obj):
            object_list.add_object(obj)

    xml = Marshal().serialize(object_list)

    connection.execute('POST', object_list.objtype.basepath,
                       accept='application/vnd.sap.adt.checkmessages+xml',
                       content_type=object_list.objtype.mimetype,
                       params={'reporters': reporter.name},
                       body=xml)
