"""ABAP Workbench functionality"""

from sap.adt.objects import XMLNamespace, ADTObjectType, OrderedClassMembers
from sap.adt.annotations import xml_element, xml_attribute
from sap.adt.marshalling import Marshal

from sap import get_logger
from sap.errors import SAPCliError


class IOCReference(metaclass=OrderedClassMembers):
    """Inactive Object Reference"""

    def __init__(self, uri=None, typ=None, name=None, parent_uri=None, description=None):
        self._uri = uri
        self._typ = typ
        self._name = name
        self._parent_uri = parent_uri
        self._description = description

    @xml_attribute('adtcore:uri')
    def uri(self):
        """Returns referenced object's URI"""

        return self._uri

    @uri.setter
    def uri(self, value):
        """Sets referenced object's URI"""

        self._uri = value

    @xml_attribute('adtcore:type')
    def typ(self):
        """Returns referenced object's type"""

        return self._typ

    @typ.setter
    def typ(self, value):
        """Sets referenced object's type"""

        self._typ = value

    @xml_attribute('adtcore:name')
    def name(self):
        """Returns referenced object's name"""

        return self._name

    @name.setter
    def name(self, value):
        """Sets referenced object's name"""

        self._name = value

    @xml_attribute('adtcore:parentUri')
    def parent_uri(self):
        """Returns referenced object's parent URI"""

        return self._parent_uri

    @parent_uri.setter
    def parent_uri(self, value):
        """Sets referenced object's parent URI"""

        self._parent_uri = value

    @xml_attribute('adtcore:description')
    def description(self):
        """Returns referenced object's description"""

        return self._description

    @description.setter
    def description(self, value):
        """Sets referenced object's description"""

        self._description = value


class IOCEntryData(metaclass=OrderedClassMembers):
    """Inactive Object or Transport"""

    def __init__(self, user='', linked=None, deleted=None):
        self._user = user
        self._linked = linked
        self._deleted = deleted
        self._reference = IOCReference()

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


class IOCObjecReferences(metaclass=OrderedClassMembers):
    """List of entries"""

    def __init__(self, entries):
        self._entries = entries

    # pylint: disable=no-self-use
    @property
    def objtype(self):
        """Monkey Patch ADTObject"""

        return ADTObjectType(None,
                             None,
                             XMLNamespace('adtcore', 'http://www.sap.com/adt/core'),
                             'application/xml',
                             None,
                             'objectReferences')

    @xml_element('adtcore:objectReference')
    def entries(self):
        """Get references"""

        return self._entries


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


def activate(adt_object):
    """Activates the given object"""

    request = IOCObjecReferences([IOCReference(uri=adt_object.full_adt_uri, name=adt_object.name.upper())])
    resp = _send_activate(adt_object, request, activation_params(pre_audit_requested=True))

    if 'application/vnd.sap.adt.inactivectsobjects.v1+xml' in resp.headers.get('Content-Type', ''):
        ioc = Marshal.deserialize(resp.text, IOCList())
        get_logger().debug(ioc.entries)
        request = IOCObjecReferences([entry.object.reference for entry in ioc.entries
                                      if entry.object is not None and entry.object.deleted == 'false'])
        resp = _send_activate(adt_object, request, activation_params(pre_audit_requested=False))

    if resp.text:
        raise SAPCliError(f'Could not activate the object {adt_object.name}: {resp.text}')
