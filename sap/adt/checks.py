"""Object Checks ADT wrappers"""

from fnmatch import fnmatch

from sap.adt.objects import ADTObjectType, XMLNamespace, xmlns_adtcore_ancestor
from sap.adt.marshalling import Marshal
from sap.adt.annotations import OrderedClassMembers, XmlNodeAttributeProperty, XmlListNodeProperty, XmlElementKind, \
    XmlContainer, XmlNodeProperty


XMLNS_CHKRUN = XMLNamespace('chkrun', 'http://www.sap.com/adt/checkrun')
XMLNS_CHKRUN_WITH_ADTCORE = xmlns_adtcore_ancestor('chkrun', 'http://www.sap.com/adt/checkrun')


# pylint: disable=too-few-public-methods
class Reporter(metaclass=OrderedClassMembers):
    """ADT Object Checks Run Reporter"""

    name = XmlNodeAttributeProperty('chkrun:name')
    supported_types = XmlListNodeProperty('chkrun:supportedType', kind=XmlElementKind.TEXT)

    def __init__(self, name=None):
        self.name = name

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

    def add_object(self, adt_object):
        """Adds the give object to the list"""

        self.objects = CheckObject(adt_object.full_adt_uri)


class CheckMessage(metaclass=OrderedClassMembers):
    """Run Check result message"""

    uri = XmlNodeAttributeProperty('chkrun:uri')
    typ = XmlNodeAttributeProperty('chkrun:type')
    short_text = XmlNodeAttributeProperty('chkrun:shortText')
    category = XmlNodeAttributeProperty('chkrun:category')


# pylint: disable=invalid-name
CheckMessageList = XmlContainer.define('chkrun:checkMessage', CheckMessage)


class CheckReport(metaclass=OrderedClassMembers):
    """Group of messages for a single reporter"""

    reporter = XmlNodeAttributeProperty('chkrun:reporter')
    triggering_uri = XmlNodeAttributeProperty('chkrun:triggeringUri')
    status = XmlNodeAttributeProperty('chkrun:status')
    status_text = XmlNodeAttributeProperty('chkrun:statusText')
    messages = XmlNodeProperty('chkrun:checkMessageList')

    def __init__(self):
        self.messages = CheckMessageList()


# pylint: disable=invalid-name
CheckReportList = XmlContainer.define('chkrun:checkReport', CheckReport)
CheckReportList.objtype = ADTObjectType(None,
                                        'checkruns',
                                        XMLNS_CHKRUN,
                                        'application/vnd.sap.adt.checkmessages+xml',
                                        None,
                                        'checkRunReports')


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

    resp = connection.execute('POST', object_list.objtype.basepath,
                              accept=CheckReportList.objtype.mimetype,
                              content_type=object_list.objtype.mimetype,
                              params={'reporters': reporter.name},
                              body=xml)

    report_list = CheckReportList()
    Marshal.deserialize(resp.text, report_list)

    return report_list
