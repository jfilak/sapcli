"""Object Checks ADT wrappers"""

from fnmatch import fnmatch

from sap.adt.objects import ADTObjectType, XMLNamespace
from sap.adt.marshalling import Marshal
from sap.adt.annotations import OrderedClassMembers, XmlNodeAttributeProperty, XmlListNodeProperty, XmlElementKind, \
    XmlContainer


XMLNS_CHKRUN = XMLNamespace('chkrun', 'http://www.sap.com/adt/checkrun')


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


def fetch_reporters(connection):
    """Returns the list of supported ADT reporters"""

    reporters = ReportersContainer()

    resp = connection.execute('GET', reporters.objtype.basepath, accept=reporters.objtype.mimetype)

    Marshal.deserialize(resp.text, reporters)

    return reporters.items
