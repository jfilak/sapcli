# pylint: disable=too-many-lines
"""Objects ADT functionality module"""

import re
from typing import NamedTuple
from urllib.parse import quote_plus

from sap.adt.core import mod_log
from sap.errors import SAPCliError

import sap.adt.marshalling
from sap.adt.annotations import xml_attribute, xml_element, XmlElementProperty, OrderedClassMembers


LOCK_ACCESS_MODE_MODIFY = 'MODIFY'


def mimetype_to_version(mime):
    """Converts Object MIME type to a version string"""

    if not mime.startswith('application/vnd.sap.'):
        return None

    smcln = mime.rfind(';')
    if smcln != -1:
        ver = mime[smcln + 1:]
        if ver.startswith('version='):
            return ver.split('=')[1]

    plus = mime.rfind('+')
    if plus == -1:
        raise SAPCliError('not a version + xml mime: ' + mime)

    dot = mime.rfind('.', 0, plus)
    if dot == -1:
        raise SAPCliError('not a version + xml mime: ' + mime)

    ver = mime[dot + 2:plus]
    if ver.isdigit():
        return ver

    return '0'


def find_mime_version(connection, objtype):
    """Returns the supported/required MIME version of the given objtype by
       the given connection.
    """

    mimes = connection.get_collection_types(objtype.basepath, objtype.mimetype)

    seri_mime = next((mime for mime in mimes if mime in objtype.all_mimetypes), None)
    if seri_mime is None:
        raise SAPCliError('Not supported mimes: {} not in {}'
                          .format(';'.join(mimes), ';'.join(objtype.all_mimetypes)))

    version = mimetype_to_version(seri_mime)
    return (seri_mime, version)


def lock_params(access_mode):
    """Returns parameters for Action Lock"""

    return {'_action': 'LOCK', 'accessMode': access_mode}


def unlock_params(lock_handle):
    """Returns parameters for Action Unlock"""

    return {'_action': 'UNLOCK', 'lockHandle': lock_handle}


def create_params(corrnr):
    """Returns parameters for Creation of object"""

    if corrnr is None:
        return None

    return {'corrNr': corrnr}


def modify_object_params(lock_handle, corrnr):
    """Returns parameters for object modification"""

    params = {'lockHandle': lock_handle}
    if corrnr is not None:
        params['corrNr'] = corrnr

    return params


class XMLNamespace:
    """XML Namespace definition"""

    def __init__(self, name, uri, parents=None):
        self._name = name
        self._uri = uri
        self._parents = parents

    @property
    def name(self):
        """Returns Namespace name"""

        return self._name

    @property
    def uri(self):
        """Returns Namespace URI"""

        return self._uri

    @property
    def parents(self):
        """Returns a list of parent Namespaces"""

        if self._parents is None:
            return []

        return self._parents.copy()


XMLNS_ADTCORE = XMLNamespace('adtcore', 'http://www.sap.com/adt/core')


def xmlns_adtcore_ancestor(name, uri):
    """Factory method returning a new namespace which has the namespace adtcore
       in the parent list.
    """

    return XMLNamespace(name, uri, parents=[XMLNS_ADTCORE])


# pylint: disable=too-many-instance-attributes
class ADTObjectType:
    """Common ADT object type attributes.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, code, basepath, xmlnamespace, mimetype, typeuris, xmlname, editor_factory=None):
        """Parameters:
            - code: ADT object code
            - basepath:
            - xmlnamespace: a tuple where the first item is a nick and
                            the second item is actually the namespace URI
            - mimetype: object MIME type - can be list
            - typeuris: patterns for the object format URL (text, xml, ...)
            - xmlname: something from ADT ;)
        """

        self._code = code
        self._basepath = basepath
        self._xmlnamespace = xmlnamespace
        self._mimetype = mimetype
        self._typeuris = typeuris
        self._xmlname = xmlname
        self._editor_factory = editor_factory

    def open_editor(self, instance, lock_handle, corrnr=None):
        """Returns a new instance of Editor for this object type
           and raises SAPCliError if the object type does not allow modifications.
        """

        if self._editor_factory is None:
            raise SAPCliError(f'Object {self._code}: modifications are not supported')

        return self._editor_factory(instance, lock_handle, corrnr=corrnr)

    @property
    def code(self):
        """ADT object code"""

        return self._code

    @property
    def basepath(self):
        """Object fragment of ADT URL"""

        return self._basepath

    @basepath.setter
    def basepath(self, value):
        """Sets Object fragment of ADT URL"""

        self._basepath = value

    @property
    def mimetype(self):
        """ADT object MIME type"""

        if isinstance(self._mimetype, list):
            return self._mimetype[0]

        return self._mimetype

    @property
    def all_mimetypes(self):
        """All supported ADT object MIME type"""

        if not isinstance(self._mimetype, list):
            return [self._mimetype]

        return self._mimetype

    @property
    def xmlnamespace(self):
        """A tuple (namespace nick, namespace URL)"""

        return self._xmlnamespace

    @property
    def xmlname(self):
        """XML element name"""

        return self._xmlname

    @property
    def xmlelement(self):
        """XML name prefixed with XML Namespace name"""

        return f'{self._xmlnamespace.name}:{self._xmlname}'

    def get_uri_for_type(self, mimetype):
        """Returns and an ADT URL fragment for the given MIME type.
        """

        try:
            return '/' + self._typeuris[mimetype]
        except KeyError:
            # pylint: disable=raise-missing-from
            raise SAPCliError('Object {type} does not support plain \'text\' format')


class ADTCoreData:
    """Common SAP object attributes.
    """

    class Reference(metaclass=OrderedClassMembers):
        """ADT Reference by Name"""

        def __init__(self, name=None):
            self._name = None if name is None else name.upper()

        @xml_attribute('adtcore:name')
        def name(self):
            """Returns reference name """

            return self._name

        @name.setter
        def name(self, value):
            """Sets reference name"""

            self._name = None if value is None else value.upper()

    # pylint: disable=too-many-arguments
    def __init__(self, package=None, description=None, language=None,
                 master_language=None, master_system=None, responsible=None,
                 package_reference=None):
        self._package = package
        self._description = description
        self._language = language
        self._master_language = master_language
        self._master_system = master_system
        self._responsible = responsible
        self._package_reference = ADTCoreData.Reference(name=package_reference)

    @property
    def package(self):
        """ABAP development package (DEVC)"""

        return self._package

    @property
    def description(self):
        """Object description"""

        return self._description

    @description.setter
    def description(self, value):
        """Object description setter"""

        self._description = value

    @property
    def language(self):
        """Language"""

        return self._language

    @language.setter
    def language(self, value):
        """Language"""

        self._language = value

    @property
    def master_language(self):
        """Original (master) language"""

        return self._master_language

    @master_language.setter
    def master_language(self, value):
        """Original (master) language"""

        self._master_language = value

    @property
    def master_system(self):
        """Original (master) system"""

        return self._master_system

    @master_system.setter
    def master_system(self, value):
        """Original (master) system setter"""

        self._master_system = value

    @property
    def responsible(self):
        """Object responsible person"""

        return self._responsible

    @responsible.setter
    def responsible(self, value):
        """Object responsible person setter"""

        self._responsible = value

    @property
    def package_reference(self):
        """The object's package reference"""

        return self._package_reference

    @package_reference.setter
    def package_reference(self, value):
        """Set the object's package reference"""

        self._package_reference = value


# pylint: disable=too-many-public-methods
class ADTObject(metaclass=OrderedClassMembers):
    """Abstract base class for ADT objects
    """

    def __init__(self, connection, name, metadata=None, active_status=None):
        """Parameters:
            - connection: ADT.Connection
            - name: string name
            - metadata: ADTCoreData
        """

        self._connection = connection
        self._name = name
        self._active_status = active_status

        self._metadata = metadata if metadata is not None else ADTCoreData()

        self._actions = None

    def __str__(self):
        return f'{self.objtype.code} {self.name}'

    @property
    def coredata(self):
        """ADT Core Data"""

        return self._metadata

    @property
    def connection(self):
        """ADT Connection"""

        return self._connection

    @property
    def objtype(self):
        """ADT type definition"""

        # pylint: disable=no-member
        return self.__class__.OBJTYPE

    @property
    def package(self):
        """ABAP development package"""

        return self._metadata.package

    @xml_attribute('adtcore:description')
    def description(self):
        """SAP object description"""

        return self._metadata.description

    @description.setter
    def description(self, value):
        """SAP object description setter"""

        self._metadata.description = value

    @xml_attribute('adtcore:language')
    def language(self):
        """SAP object language"""

        return self._metadata.language

    @language.setter
    def language(self, value):
        """Set SAP object language"""

        self._metadata.language = value

    @xml_attribute('adtcore:name')
    def name(self):
        """SAP Object name"""

        return self._name

    @name.setter
    def name(self, value):
        """Only for deserialization - cannot be used to rename object"""

        if value != self._name:
            raise SAPCliError(f'Deserializing wrong object: {self._name} != {value}')

    @xml_attribute('adtcore:masterLanguage')
    def master_language(self):
        """SAP object original (master) language"""

        return self._metadata.master_language

    @master_language.setter
    def master_language(self, value):
        """Set SAP object original (master) language"""

        self._metadata.master_language = value

    @xml_attribute('adtcore:masterSystem')
    def master_system(self):
        """SAP object original (master) system"""

        return self._metadata.master_system

    @master_system.setter
    def master_system(self, value):
        """SAP object original (master) system"""

        self._metadata.master_system = value

    @xml_attribute('adtcore:responsible')
    def responsible(self):
        """SAP object responsible"""

        return self._metadata.responsible

    @responsible.setter
    def responsible(self, value):
        """Set SAP object responsible"""

        self._metadata.responsible = value

    @property
    def uri(self):
        """ADT object URL fragment"""

        # pylint: disable=no-member
        return self.objtype.basepath + '/' + quote_plus(self.name.lower())

    @property
    def full_adt_uri(self):
        """Full local path of ADT URL"""

        return '/' + self._connection.uri + '/' + self.uri

    @property
    def text(self):
        """Downloads text representation of the SAP Object
           if the MIME Type 'text/plain'.
        """

        text_uri = self.objtype.get_uri_for_type('text/plain')

        return self._connection.get_text(f'{self.uri}{text_uri}').replace('\r\n', '\n')

    @xml_attribute('adtcore:version')
    def active(self):
        """Version in regards of activation"""

        return self._active_status

    @active.setter
    def active(self, value):
        """Version in regards of activation"""

        self._active_status = value

    @xml_element('adtcore:packageRef')
    def reference(self):
        """The object's package reference"""

        return self._metadata.package_reference

    def _get_mime_and_version(self):
        """Virtual function for returning the right version
        and MIME type. Useful for types which depend on other
        types ADT reports required version of the master type.
        """

        return find_mime_version(self._connection, self.objtype)

    def serialize(self):
        """Creates a text representation"""
        seri_mime, version = self._get_mime_and_version()

        marshal = sap.adt.marshalling.Marshal(object_schema_version=version)
        return (marshal.serialize(self), seri_mime + '; charset=utf-8')

    def create(self, corrnr=None):
        """Creates ADT object
        """

        xml, seri_mime = self.serialize()

        return self._connection.execute(
            'POST',
            self.objtype.basepath,
            headers={'Content-Type': seri_mime},
            params=create_params(corrnr),
            body=bytes(xml, 'utf-8'))

    def fetch(self):
        """Retrieve data from ADT"""

        resp = self._connection.execute('GET', self.uri)
        marshal = sap.adt.marshalling.Marshal()
        marshal.deserialize(resp.text, self)

    def lock(self):
        """Locks the object"""

        resp = self.connection.execute(
            'POST',
            self.uri,
            params=lock_params(LOCK_ACCESS_MODE_MODIFY),
            headers={
                'X-sap-adt-sessiontype': 'stateful',
                'Accept': ', '.join([
                    'application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.lock.result;q=0.8',
                    'application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.lock.result2;q=0.9'
                ])
            }
        )

        if 'dataname=com.sap.adt.lock.Result' not in resp.headers['Content-Type']:
            raise SAPCliError(f'Object {self.uri}: lock response does not have lock result\n' + resp.text)

        mod_log().debug(resp.text)

        # TODO: check encoding
        lock_handle = re.match('.*<LOCK_HANDLE>(.*)</LOCK_HANDLE>.*', resp.text)[1]
        mod_log().debug('LockHandle=%s', lock_handle)

        return lock_handle

    def unlock(self, lock_handle):
        """Unlocks the object"""

        self.connection.execute(
            'POST',
            self.uri,
            params=unlock_params(lock_handle),
            headers={
                'X-sap-adt-sessiontype': 'stateful',
            }
        )

    def open_editor(self, lock_handle=None, corrnr=None):
        """Creates editor and returns its instance

           The given lock_handle is passed to the new editor's instance.

           If the give lock_handle is None, the object is locked implicitly
           and must be unlocked explicitly via the method unlock() if not
           unlocked by the editor itself.

           The given corrnr is passed to the new editor's instance.
        """

        if lock_handle is None:
            lock_handle = self.lock()

        return self.objtype.open_editor(self, lock_handle, corrnr=corrnr)


class ADTObjectEditor:
    """Base Editor for ADT Object which implements common functionality"""

    def __init__(self, obj, lock_handle, corrnr=None):
        self._obj = obj
        self._lock_handle = lock_handle
        self._corrnr = corrnr

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._obj.unlock(self.lock_handle)

    @property
    def uri(self):
        """Returns the edit object's URI"""

        return self._obj.uri

    @property
    def mimetype(self):
        """Returns the edit object's MIME-TYPE"""

        return self._obj.objtype.mimetype

    @property
    def connection(self):
        """Returns the edit object's Connection"""

        return self._obj.connection

    def get_uri_for_type(self, mimetype):
        """Returns the edit object's URI for the given mimetype"""

        return self._obj.objtype.get_uri_for_type(mimetype)

    def serialize(self):
        """Serializes the object"""

        return self._obj.serialize()

    @property
    def lock_handle(self):
        """Lock Handle"""

        return self._lock_handle

    @property
    def corrnr(self):
        """Correction Number"""

        return self._corrnr

    def write(self, content):
        """Changes text of the object"""

        raise NotImplementedError('write')

    def push(self):
        """Pushes object's Attributes to ADT"""

        payload, mimetype = self.serialize()

        return self.connection.execute(
            'PUT',
            self.uri,
            headers={'Content-Type': mimetype},
            params=modify_object_params(self.lock_handle, self.corrnr),
            body=bytes(payload, 'utf-8'))


class ADTObjectSourceEditor(ADTObjectEditor):
    """Source Code actions"""

    # pylint: disable=no-self-use
    def get_headers(self):
        """Returns Request HTTP headers"""

        return {'Content-Type': 'text/plain; charset=utf-8'}

    def write(self, content):
        """Changes Source Code of the source object"""

        text_uri = self.uri + self.get_uri_for_type('text/plain')

        if content[-1] == '\n':
            content = content[:-1]

        data = bytes(content, 'utf-8')

        resp = self.connection.execute(
            'PUT',
            text_uri,
            params=modify_object_params(self.lock_handle, self.corrnr),
            headers=self.get_headers(),
            body=data)

        mod_log().debug("Write text response status: %i", resp.status_code)


class ADTObjectSourceEditorWithResponse(ADTObjectSourceEditor):
    """Source Code Editor evaluating response"""

    def get_headers(self):
        """Enrich Super's Headers with Accept"""

        headers = super().get_headers()
        headers['Accept'] = 'text/plain'
        return headers


class ADTObjectReference(metaclass=OrderedClassMembers):
    """ADT Object Reference"""

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


class ADTObjectReferences(metaclass=OrderedClassMembers):
    """List of ADT Object references"""

    def __init__(self, references=None):
        """:param references: A list of :clas:`ADTObjectReferences`"""

        self._refs = references

    # pylint: disable=no-self-use
    @property
    def objtype(self):
        """Monkey Patch ADTObject"""

        return ADTObjectType(None,
                             None,
                             XMLNS_ADTCORE,
                             'application/xml',
                             None,
                             'objectReferences')

    @xml_element('adtcore:objectReference')
    def references(self):
        """Get references

           :rtype: A list of :clas:`ADTObjectReferences`
        """

        return self._refs

    @property
    def _references(self):
        """A private property which intialiazes the returned list.

           The public property must not initialize the list because that could
           confuse the XML generator.
        """

        if self._refs is None:
            self._refs = []

        return self._refs

    def add_reference(self, object_reference):
        """Adds the given reference.

           :param object_reference:
        """

        self._references.append(object_reference)

        return object_reference

    def add_object(self, adt_object):
        """Turns the given adt_object into a reference and adds it.

           Tries to populate these reference fields:
            - uri = adt_object.uri
            - name = adt_object.name

           Leaves untouched these reference fields:
            - typ
            - parent_uri
            - description

           If you need to intialized the reference differently,
           please use the method add_reference.

           :param adt_object: An instance of ADTObject
           :rtype: The Object Reference :class:`ADTObjectReference`
        """

        reference = ADTObjectReference(
            uri=adt_object.full_adt_uri,
            name=adt_object.name.upper()
        )

        return self.add_reference(reference)


class ADTObjectSet(metaclass=OrderedClassMembers):
    """Set of ADT Objects stored in the form of ADT Object References"""

    def __init__(self, kind):
        """Plase use the static method new_inclusive.

           :param kind: string representing the kind
        """

        self._kind = kind
        self._references = ADTObjectReferences()

    @xml_attribute('kind')
    def kind(self):
        """Returns the kind of the set"""

        return self._kind

    @xml_element(XmlElementProperty.NAME_FROM_OBJECT)
    def references(self):
        """Returns the object references"""

        return self._references

    def add_object(self, adt_object):
        """Adds a reference to the give object

           :rtype: The object reference as an instance of :clas:`ADTObjectReference`
        """

        return self._references.add_object(adt_object)

    @staticmethod
    def new_inclusive():
        """Builds a new inclusive object set.

           :rtype: A instance of :class:`ADTObjectSet`
        """

        return ADTObjectSet('inclusive')


class ADTObjectSets(metaclass=OrderedClassMembers):
    """Wrapper class for object sets"""

    def __init__(self):
        self.objtype = ADTObjectType(None, None,
                                     XMLNS_ADTCORE,
                                     'application/xml',
                                     None,
                                     'objectSets')

        self._inclusive = None

    @xml_element('objectSet')
    def inclusive(self):
        """Returns the inclusive set.

           :rtype: None if the set is empty
        """

        return self._inclusive

    def include_object(self, adt_object):
        """Includes the give ADT Object

           :param adt_object: An instance of :clas:`ADTObject`
           :rtype: The object reference.
        """

        if self._inclusive is None:
            self._inclusive = ADTObjectSet.new_inclusive()

        return self._inclusive.add_object(adt_object)


class OOADTObjectBase(ADTObject):
    """Base class for Object Oriented ABAP Sources"""

    def __init__(self, connection, name, metadata):
        super().__init__(connection, name, metadata)

        self._modeled = None

    @xml_attribute('abapoo:modeled')
    def modeled(self):
        """ABAP OO flag modeled"""

        return self._modeled

    @modeled.setter
    def modeled(self, value):
        """ABAP OO flag modeled"""

        self._modeled = value == 'true'


class Interface(OOADTObjectBase):
    """ABAP Interface"""

    OBJTYPE = ADTObjectType(
        'INTF/OI',
        'oo/interfaces',
        xmlns_adtcore_ancestor('intf', 'http://www.sap.com/adt/oo/interfaces'),
        # application/vnd.sap.adt.oo.interfaces+xml, application/vnd.sap.adt.oo.interfaces.v2+xml
        'application/vnd.sap.adt.oo.interfaces.v2+xml',
        {'text/plain': 'source/main'},
        'abapInterface',
        editor_factory=ADTObjectSourceEditor
    )

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package


# pylint: disable=too-few-public-methods
class ClassIncludeMetadata(NamedTuple):
    """Class Include Type definition - partially implements ADTObjectType interface"""

    adt_name: str
    adt_type: str
    include_type: str
    source_uri: str

    def get_uri_for_type(self, mimetype):
        """Mimic ADTObjectType's implementation"""

        if mimetype != 'text/plain':
            raise SAPCliError(f'Class Source code can be only of "text/plain": {mimetype}')

        return self.source_uri


# pylint: disable=too-many-instance-attributes
class Class(OOADTObjectBase):
    """ABAP OO Class
    """

    OBJTYPE = ADTObjectType(
        'CLAS/OC',
        'oo/classes',
        xmlns_adtcore_ancestor('class', 'http://www.sap.com/adt/oo/classes'),
        'application/vnd.sap.adt.oo.classes.v2+xml',
        {'text/plain': 'source/main'},
        'abapClass',
        editor_factory=ADTObjectSourceEditorWithResponse
    )

    class Include(metaclass=OrderedClassMembers):
        """Class includes"""

        DefinitionsMetadata = ClassIncludeMetadata(
            'CLAS/OC', 'CLAS/OC', 'definitions', '/includes/definitions')

        ImplementationsMetadata = ClassIncludeMetadata(
            'CLAS/OC', 'CLAS/OC', 'implementations', '/includes/implementations')

        TestClassesMetadata = ClassIncludeMetadata(
            'CLAS/OC', 'CLAS/OC', 'testclasses', '/includes/testclasses')

        def __init__(self, clas, metadata):
            self._clas = clas
            self._metadata = metadata

        def __str__(self):
            return str(self._clas) + f'/{self._metadata.include_type}'

        @property
        def name(self):
            """Returns parent's Name for Class's writing multiple files"""

            return self._clas.name

        @property
        def uri(self):
            """Returns parent's URI for Class's open_editor()"""

            return self._clas.uri

        @property
        def full_adt_uri(self):
            """Returns parent's URI for Class's sap.adt.wb.activate()"""

            return self._clas.full_adt_uri

        @property
        def connection(self):
            """Returns parent's connection for Class's open_editor()"""

            return self._clas.connection

        @property
        def objtype(self):
            """Returns a stub ADTObjectType for Class's open_editor()"""

            return self._metadata

        @staticmethod
        def definitions(clas):
            """Include for Local Definitions"""

            return Class.Include(clas, Class.Include.DefinitionsMetadata)

        @staticmethod
        def implementations(clas):
            """Include for Local Implementations"""

            return Class.Include(clas, Class.Include.ImplementationsMetadata)

        @staticmethod
        def test_classes(clas):
            """Include for Test Class"""

            return Class.Include(clas, Class.Include.TestClassesMetadata)

        @xml_attribute('adtcore:name')
        def adt_name(self):
            """ADT Object name"""

            return self._metadata.adt_name

        @xml_attribute('adtcore:type')
        def adt_type(self):
            """ADT Object Type name"""

            return self._metadata.adt_type

        @xml_attribute('class:includeType')
        def include_type(self):
            """ADT Class include type"""

            return self._metadata.include_type

        @property
        def text(self):
            """Returns text"""

            return self._clas.connection.get_text(f'{self.uri}{self._metadata.source_uri}')

        def lock(self):
            """Calls parent's lock() for Class's open_editor()"""

            return self._clas.lock()

        def unlock(self, lock_handle):
            """Calls parent's unlock() for Class's open_editor()"""

            return self._clas.unlock(lock_handle)

        def open_editor(self, lock_handle=None, corrnr=None):
            """Changes source codes"""

            if lock_handle is None:
                lock_handle = self.lock()

            return self._clas.objtype.open_editor(self, lock_handle=lock_handle, corrnr=corrnr)

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package
        self._superclass = ADTCoreData.Reference()
        self._definitions = None
        self._implementations = None
        self._test_classes = None
        self._fixpntar = None
        self._final = 'true'
        self._visibility = 'public'

    @xml_attribute('class:final')
    def final(self):
        """Final flag"""

        return self._final

    @final.setter
    def final(self, value):
        """Final flag"""

        self._final = value == 'true'

    @xml_attribute('class:visibility')
    def visibility(self):
        """Visibility flag"""

        return self._visibility

    @visibility.setter
    def visibility(self, value):
        """Visibility flag"""

        self._visibility = value

    @xml_attribute('abapsource:fixPointArithmetic')
    def fix_point_arithmetic(self):
        """Fixed point arithmetic flag"""

        return self._fixpntar

    @fix_point_arithmetic.setter
    def fix_point_arithmetic(self, value):
        """Fixed point arithmetic flag"""

        self._fixpntar = value == 'true'

    @xml_element('class:include', deserialize=False)
    def include(self):
        """Class include"""

        return self.test_classes

    @xml_element('class:superClassRef')
    def super_class(self):
        """Super Class reference"""

        return self._superclass

    @property
    def definitions(self):
        """Local Definitions"""

        if self._definitions is None:
            self._definitions = Class.Include.definitions(self)

        return self._definitions

    @property
    def implementations(self):
        """Local Implementations"""

        if self._implementations is None:
            self._implementations = Class.Include.implementations(self)

        return self._implementations

    @property
    def test_classes(self):
        """Test Classes"""

        if self._test_classes is None:
            self._test_classes = Class.Include.test_classes(self)

        return self._test_classes

    def execute(self):
        """Calls if_oo_adt_classrun~main"""

        # pylint: disable=no-member
        name = self.name.lower()

        resp = self._connection.execute(
            'POST',
            'oo/classrun/' + quote_plus(name),
            headers={'Accept': 'text/plain'})

        return resp.text


class DataDefinition(ADTObject):
    """CDS View definition"""

    OBJTYPE = ADTObjectType(
        'DDLS/DF',
        'ddic/ddl/sources',
        xmlns_adtcore_ancestor('ddl', 'http://www.sap.com/adt/ddic/ddlsources'),
        # application/vnd.sap.adt.ddlSource.v2+xml, application/vnd.sap.adt.ddlSource+xml
        'application/vnd.sap.adt.ddlSource+xml',
        {'text/plain': 'source/main'},
        'ddlSource',
        editor_factory=ADTObjectSourceEditor
    )

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package
