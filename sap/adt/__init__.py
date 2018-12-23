"""Base classes for ADT functionality modules"""

import requests
from requests.auth import HTTPBasicAuth

from sap import get_logger
from sap.adt.errors import HTTPRequestError

def mod_log():
    return get_logger()


class Connection(object):
    """ADT Connection"""

    def __init__(self, host, client, user, passwd, port=None, ssl=True):

        if ssl:
            protocol = 'https'
            if port is None:
                port = '443'
        else:
            protocol = 'http'
            if port is None:
                port = '80'

        self._adt_uri = 'sap/bc/adt'
        self._base_url = '{protocol}://{host}:{port}/{adt_uri}'.format(
            protocol=protocol, host=host, port=port, adt_uri=self._adt_uri)
        self._query_args = 'sap-client={client}&saml2=disabled'.format(
            client=client)
        self._auth = HTTPBasicAuth(user, passwd)
        self._session = None

    @property
    def uri(self):
        return self._adt_uri

    def _build_adt_url(self, adt_uri):
        return '{base_url}/{adt_uri}?{query_args}'.format(
            base_url=self._base_url, adt_uri=adt_uri,
            query_args=self._query_args)

    @staticmethod
    def _execute_with_session(session, method, url, headers=None, body=None):
        req = requests.Request(method.upper(), url, data=body, headers=headers)
        req = session.prepare_request(req)

        mod_log().debug('Executing %s %s', method, url)
        res = session.send(req)

        if res.status_code >= 400:
            raise HTTPRequestError(req, res)

        return res

    def _get_session(self):
        if self._session is None:
            self._session = requests.Session()
            self._session.auth = self._auth

            url = self._build_adt_url('core/discovery')

            response = Connection._execute_with_session(self._session, 'GET', url, headers={'x-csrf-token': 'Fetch'})

            self._session.headers.update({'x-csrf-token': response.headers['x-csrf-token']})

        return self._session


    def execute(self, method, adt_uri, headers=None, body=None):
        session = self._get_session()

        url = self._build_adt_url(adt_uri)

        return Connection._execute_with_session(self._session, method, url, headers=headers, body=body)


    def get_text(self, relativeuri):
        return self.execute('GET', relativeuri, headers={'Accept': 'text/plain'}).text


class ADTObjectType(object):

    def __init__(self, code, basepath, xmlnamespace, mimetype, typeuris):
        self._code = code
        self._basepath = basepath
        self._xmlnamespace = xmlnamespace
        self._mimetype = mimetype
        self._typeuris = typeuris

    @property
    def code(self):
        return self._code

    @property
    def basepath(self):
        return self._basepath

    @property
    def mimetype(self):
        return self._mimetype

    @property
    def xmlnamespace(self):
        return self._mimetype

    def get_uri_for_type(self, mimetype):
        try:
            return '/' + self._typeuris[mimetype]
        except KeyError:
            raise SAPCliError('Object {type} does not support plain \'text\' format')


class ADTObject(object):

    def __init__(self, connection, name, metadata=None):
        self._connection = connection
        self._name = name
        self._metadata = metadata

    @property
    def connection(self):
        return self._connection

    @property
    def objtype(self):
        return self.__class__.OBJTYPE

    @property
    def name(self):
        return self._name

    @property
    def package(self):
        return self._metadata.package

    @property
    def description(self):
        return self._metadata.description

    @property
    def language(self):
        return self._metadata.language

    @property
    def master_language(self):
        return self._metadata.master_language

    @property
    def master_system(self):
        return self._metadata.master_system

    @property
    def responsible(self):
        return self._metadata.responsible

    @property
    def uri(self):
        return self.objtype.basepath + '/' + self.name

    @property
    def text(self):
        text_uri = self.objtype.get_uri_for_type('text/plain')

        return self._connection.get_text('{objuri}{text_uri}'.format(
            objuri=self.uri, name=self._name, text_uri=text_uri))

    @text.setter
    def text(self, data):
        raise SAPCliError('Object {}'.format)


class Program(ADTObject):

    OBJTYPE = ADTObjectType(
        'PROG/P',
        'programs/programs',
        ('program', 'http://www.sap.com/adt/programs/programs'),
        'application/vnd.sap.adt.programs.programs.v2+xml',
        {'text/plain': 'source/main'}
    )

    def __init__(self, connection, name, metadata=None):
        super(Program, self).__init__(connection, name, metadata)

#    @staticmethod
#    def create()
        # POST /sap/bc/adt/programs/programs

    #@text.setter
    #def text(self, connection, content, metadata):
    # POST /sap/bc/adt/programs/validation?objname=ZTEST_REPORT&packagename=%24TMP&description=test+reports&objtype=PROG%2FP HTTP/1.1
    #    return


class Class(ADTObject):

    OBJTYPE = ADTObjectType(
        'CLAS/I',
        'oo/classes',
        ('class', 'http://www.sap.com/adt/oo/claases'),
        'application/vnd.sap.adt.oo.classes.v2+xml',
        {'text/plain': 'source/main'}
    )

    def __init__(self, connection, name, metadata=None):
        super(Class, self).__init__(connection, name, metadata)


class AUnit(object):

    def __init__(self, connection):
        self._connection = connection

    @staticmethod
    def build_tested_object_uri(connection, adt_object):
        return '/' + connection.uri + '/' + adt_object.uri

    @staticmethod
    def build_test_configuration(adt_object_uri):
        test_config = '''<?xml version="1.0" encoding="UTF-8"?>
<aunit:runConfiguration xmlns:aunit="http://www.sap.com/adt/aunit">
  <external>
    <coverage active="false"/>
  </external>
  <options>
    <uriType value="semantic"/>
    <testDeterminationStrategy sameProgram="true" assignedTests="false" appendAssignedTestsPreview="true"/>
    <testRiskLevels harmless="true" dangerous="true" critical="true"/>
    <testDurations short="true" medium="true" long="true"/>
  </options>
  <adtcore:objectSets xmlns:adtcore="http://www.sap.com/adt/core">
    <objectSet kind="inclusive">
      <adtcore:objectReferences>
        <adtcore:objectReference adtcore:uri="'''

        test_config += adt_object_uri

        test_config += '''"/>
      </adtcore:objectReferences>
    </objectSet>
  </adtcore:objectSets>
</aunit:runConfiguration>'''

        return test_config

    def execute(self, adt_object):
        adt_object_uri = AUnit.build_tested_object_uri(self._connection, adt_object)
        test_config = AUnit.build_test_configuration(adt_object_uri)

        return self._connection.execute('POST', 'abapunit/testruns',
            headers={'Content-Type': 'application/vnd.sap.adt.abapunit.testruns.config.v4+xml'},
            body=test_config)


class Package(ADTObject):

    OBJTYPE = ADTObjectType(
        'DEVC/K',
        'packages',
        ('pak', 'http://www.sap.com/adt/packages'),
        'application/vnd.sap.adt.packages.v1+xml',
        {}
    )

    def __init__(self, connection, name, metadata=None):
        super(Package, self).__init__(connection, name, metadata)
