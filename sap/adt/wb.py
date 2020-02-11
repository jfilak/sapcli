"""ABAP Workbench functionality"""

from sap.adt.objects import (XMLNamespace, ADTObjectType, OrderedClassMembers,
                             ADTObjectReferences, ADTObjectReference)

from sap.adt.annotations import xml_element, xml_attribute, xml_text_node_property, \
    XmlNodeAttributeProperty, XmlNodeProperty, XmlListNodeProperty
from sap.adt.marshalling import Marshal

from sap import get_logger
from sap.errors import SAPCliError


XMLNS_CHKL = XMLNamespace('chkl', 'http://www.sap.com/abapxml/checklis')


class IOCEntryData(metaclass=OrderedClassMembers):
    """Inactive Object or Transport"""

    def __init__(self, user='', linked=None, deleted=None):
        self._user = user
        self._linked = linked
        self._deleted = deleted
        self._reference = ADTObjectReference()

    @xml_element('ioc:ref')
    def reference(self):
        """Returns reference"""

        return self._reference

    @xml_attribute('ioc:user')
    def user(self):
        """Returns object owner"""

        return self._user

    @user.setter
    def user(self, value):
        """Sets object owner"""

        self._user = value

    @xml_attribute('ioc:linked')
    def linked(self):
        """Returns object's linked flag"""

        return self._linked

    @linked.setter
    def linked(self, value):
        """Sets object's linked flag"""

        self._linked = value

    @xml_attribute('ioc:deleted')
    def deleted(self):
        """Returns object's deleted flat"""

        return self._deleted

    @deleted.setter
    def deleted(self, value):
        """Sets object's deleted flag"""

        self._deleted = value

    @property
    def name(self):
        """Reference Object Name"""

        return self._reference.name

    @property
    def uri(self):
        """Reference Object URI"""

        return self._reference.uri

    @property
    def parent_uri(self):
        """Reference Parent Object URI"""

        return self._reference.parent_uri

    @property
    def typ(self):
        """Reference Object Type"""

        return self._reference.typ

    @property
    def description(self):
        """Reference Object Description"""

        return self._reference.description


class IOCEntry(metaclass=OrderedClassMembers):
    """Inactive CTS Object Entry"""

    def __init__(self):
        self._object = None
        self._transport = IOCEntryData

    @xml_element('ioc:object', factory=IOCEntryData)
    def object(self):
        """Returns object reference"""

        return self._object

    @object.setter
    def object(self, value):
        """Sets object reference"""

        self._object = value

    @xml_element('ioc:transport', factory=IOCEntryData)
    def transport(self):
        """Returns transport reference"""

        return self._transport

    @transport.setter
    def transport(self, value):
        """Sets transport reference"""

        self._transport = value


class IOCList(metaclass=OrderedClassMembers):
    """List of entries"""

    def __init__(self):
        self.entries = list()

    # pylint: disable=no-self-use
    @property
    def objtype(self):
        """Monkey Patch ADTObject"""

        return ADTObjectType(None,
                             None,
                             XMLNamespace('ioc', 'http://www.sap.com/abapxml/inactiveCtsObjects'),
                             'application/vnd.sap.adt.inactivectsobjects.v1+xml',
                             None,
                             'inactiveObjects')

    @xml_element('ioc:entry')
    def _new_entry(self):
        """Creates new list item"""

        get_logger().debug('Adding new Inactive Object Entry')
        entry = IOCEntry()
        self.entries.append(entry)
        return entry


def activation_params(pre_audit_requested=True):
    """Returns parameters for Activation of object"""

    return {'method': 'activate', 'preauditRequested': str(pre_audit_requested).lower()}


def _send_activate(adt_object, request, params):

    return adt_object.connection.execute(
        'POST',
        'activation',
        params=params,
        headers={
            'Accept': 'application/xml',
            'Content-Type': 'application/xml'
        },
        body=Marshal().serialize(request)
    )


class CheckMessageText(metaclass=OrderedClassMembers):
    """Activation Check response message"""

    value = xml_text_node_property('txt')

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other

        return super(CheckMessageText, self).__eq__(other)

    def __ne__(self, other):
        if isinstance(other, str):
            return self.value != other

        return super(CheckMessageText, self).__ne__(other)


# pylint: disable=too-few-public-methods
class CheckMessage(metaclass=OrderedClassMembers):
    """Run Check result message"""

    obj_descr = XmlNodeAttributeProperty('objDescr')
    typ = XmlNodeAttributeProperty('type')
    line = XmlNodeAttributeProperty('line')
    href = XmlNodeAttributeProperty('href')
    force_supported = XmlNodeAttributeProperty('forceSupported')
    short_text = XmlNodeProperty('shortText', factory=CheckMessageText)

    @property
    def is_error(self):
        """Returns true if the message is an error"""

        return self.typ == 'E'

    @property
    def is_warning(self):
        """Returns true if the message is an error"""

        return self.typ == 'W'


class CheckProperties(metaclass=OrderedClassMembers):
    """Run Check result properties"""

    checked = XmlNodeAttributeProperty('checkExecuted')
    activated = XmlNodeAttributeProperty('activationExecuted')
    generated = XmlNodeAttributeProperty('generationExecuted')

    def __init__(self):
        self.checked = None
        self.activated = None
        self.generated = None


class CheckResults(metaclass=OrderedClassMembers):
    """Activation Run Check Results"""

    objtype = ADTObjectType(None, None, XMLNS_CHKL, None, None, 'messages')

    properties = XmlNodeProperty('chkl:properties', factory=CheckProperties)
    messages = XmlListNodeProperty('msg', value=[], factory=CheckMessage)

    @property
    def has_errors(self):
        """Returns true if the results contains an error message"""

        return any((message.is_error for message in self.messages))

    @property
    def has_warnings(self):
        """Returns true if the results contains a warning message"""

        return any((message.is_warning for message in self.messages))

    @property
    def generated(self):
        """Returns true if the activation left the objects generated"""

        if self.properties is None:
            return not self.has_errors

        return self.properties.generated != 'false'


class ActivationError(SAPCliError):
    """Activation error.

    You can still decide on your own by analyzing
    contents of the member results and especially
    its property messages which is of type list of CheckMessage

    """

    def __init__(self, message, response, results):
        super(ActivationError, self).__init__(message)

        self.response = response
        self.results = results


def try_activate(adt_object):
    """Activates the given object and returns CheckResults with
    the activation results.
    """

    request = ADTObjectReferences()
    request.add_object(adt_object)

    resp = _send_activate(adt_object, request, activation_params(pre_audit_requested=True))

    if 'application/vnd.sap.adt.inactivectsobjects.v1+xml' in resp.headers.get('Content-Type', ''):
        ioc = Marshal.deserialize(resp.text, IOCList())
        get_logger().debug(ioc.entries)
        request = ADTObjectReferences([entry.object.reference for entry in ioc.entries
                                       if entry.object is not None and entry.object.deleted == 'false'])
        resp = _send_activate(adt_object, request, activation_params(pre_audit_requested=False))

    results = CheckResults()

    if resp.text:
        Marshal.deserialize(resp.text, results)

    return (results, resp)


def activate(adt_object):
    """Activates the given object and raises ActivationError
    in the case where activation didn't generate the object.
    """

    results, resp = try_activate(adt_object)

    if not results.generated:
        raise ActivationError(f'Could not activate: {resp.text}', resp, results)

    return results


def fetch_inactive_objects(connection):
    """Returns list of inactive objects"""

    resp = connection.execute('GET', 'activation/inactiveobjects')
    return Marshal.deserialize(resp.text, IOCList())
