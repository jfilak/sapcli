"""ABAP Workbench functionality"""

from sap.adt.objects import (XMLNamespace, ADTObjectType, OrderedClassMembers,
                             ADTObjectReferences, ADTObjectReference)

from sap.adt.annotations import xml_element, xml_attribute, xml_text_node_property, \
    XmlNodeAttributeProperty, XmlNodeProperty, XmlContainer
from sap.adt.marshalling import Marshal

from sap import get_logger
from sap.errors import SAPCliError


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


def _send_activate(connection, request, params):

    return connection.execute(
        'POST',
        'activation',
        params=params,
        headers={
            'Accept': 'application/xml',
            'Content-Type': 'application/xml'
        },
        body=Marshal().serialize(request)
    )


class CheckeMessageText(metaclass=OrderedClassMembers):
    """Wrapper for Activation message text"""

    value = xml_text_node_property('txt')

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other

        return super(CheckeMessageText, self).__eq__(other)

    def __ne__(self, other):
        if isinstance(other, str):
            return self.value != other

        return super(CheckeMessageText, self).__ne__(other)


class CheckMessage(metaclass=OrderedClassMembers):
    """Run Check result message"""

    # pylint: disable=too-few-public-methods
    class Type:
        """Message types"""

        WARNING = 'W'
        ERROR = 'E'

    obj_descr = XmlNodeAttributeProperty('objDescr')
    typ = XmlNodeAttributeProperty('type')
    line = XmlNodeAttributeProperty('line')
    href = XmlNodeAttributeProperty('href')
    force_supported = XmlNodeAttributeProperty('forceSupported')
    short_text = XmlNodeProperty('shortText', factory=CheckeMessageText)

    @property
    def is_error(self):
        """Returns true if the message represents Error"""

        return self.typ == CheckMessage.Type.ERROR


XMLNS_CHKL = XMLNamespace('chkl', 'http://www.sap.com/abapxml/checklis')


# pylint: disable=invalid-name
CheckMessageList = XmlContainer.define('msg', CheckMessage)
CheckMessageList.objtype = ADTObjectType(None,
                                         None,
                                         XMLNS_CHKL,
                                         None,
                                         None,
                                         'messages')


class ActivationError(SAPCliError):
    """Exception for failed activations"""

    def __init__(self, message, response):
        super(ActivationError, self).__init__(message)

        self.response = response


def mass_activate(connection, references):
    """Activates the given objects and raise ActivationError in case of any error."""

    resp = _send_activate(connection, references, activation_params(pre_audit_requested=True))

    if 'application/vnd.sap.adt.inactivectsobjects.v1+xml' in resp.headers.get('Content-Type', ''):
        ioc = Marshal.deserialize(resp.text, IOCList())
        get_logger().debug(ioc.entries)
        request = ADTObjectReferences([entry.object.reference for entry in ioc.entries
                                       if entry.object is not None and entry.object.deleted == 'false'])
        resp = _send_activate(connection, request, activation_params(pre_audit_requested=False))

    if resp.text:
        raise ActivationError(f'Could not activate: {resp.text}', resp)


def try_mass_activate(connection, references):
    """Calls the function mass_activate but catches the exception and returns
       the messages.
    """

    try:
        mass_activate(connection, references)
        return None
    except ActivationError as ex:
        resp = ex.response

        if 'application/xml' not in resp.headers.get('Content-Type', ''):
            raise ex

        messages = CheckMessageList()
        Marshal.deserialize(resp.text, messages)

        return messages


def activate(adt_object):
    """Activates the given object"""

    references = ADTObjectReferences()
    references.add_object(adt_object)

    mass_activate(adt_object.connection, references)


def fetch_inactive_objects(connection):
    """Returns list of inactive objects"""

    resp = connection.execute('GET', 'activation/inactiveobjects')
    return Marshal.deserialize(resp.text, IOCList())
