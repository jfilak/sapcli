'''ADT Abapgit wraper tests.'''
#!/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import unittest
import unittest.mock as mock

import sap.adt.abapgit

SAMPLE_REPO_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<abapgitrepo:repositories xmlns:abapgitrepo="http://www.sap.com/adt/abapgit/repositories">
  <abapgitrepo:repository>
    <abapgitrepo:key>000000000001</abapgitrepo:key>
    <abapgitrepo:package>PKG</abapgitrepo:package>
    <abapgitrepo:url>https://u.rl/something.git</abapgitrepo:url>
    <abapgitrepo:branchName>refs/heads/master</abapgitrepo:branchName>
    <abapgitrepo:status>E</abapgitrepo:status>
    <abapgitrepo:statusText>Pulled with errors</abapgitrepo:statusText>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/abapgit/repos/000000000001/pull" rel="http://www.sap.com/adt/abapgit/relations/pull" type="pull_link"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/abapgit/repos/000000000001/log/0242AC1100021EEB97920079A4FEDA20" rel="http://www.sap.com/adt/abapgit/relations/log" type="log_link"/>
  </abapgitrepo:repository>
</abapgitrepo:repositories>'''

SAMPLE_LOG_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<abapObjects:abapObjects xmlns:abapObjects="http://www.sap.com/adt/abapgit/abapObjects">
  <abapObjects:abapObject>
    <abapObjects:type>CLAS</abapObjects:type>
    <abapObjects:name>CL_SOMETHING</abapObjects:name>
    <abapObjects:status>E</abapObjects:status>
    <abapObjects:msgType>E</abapObjects:msgType>
    <abapObjects:msgText>Test objects cannot be created in foreign namespaces</abapObjects:msgText>
  </abapObjects:abapObject>
  <abapObjects:abapObject>
    <abapObjects:type>DEVC</abapObjects:type>
    <abapObjects:name>PKG</abapObjects:name>
    <abapObjects:status>S</abapObjects:status>
    <abapObjects:msgType>S</abapObjects:msgType>
    <abapObjects:msgText>Object PKG imported</abapObjects:msgText>
  </abapObjects:abapObject>
</abapObjects:abapObjects>
'''


def sample_connection():
    response = mock.MagicMock()
    response.text = SAMPLE_REPO_XML
    connection = mock.MagicMock()
    connection.execute = mock.Mock(return_value=response)
    return connection


class TestAbapgitRepository(unittest.TestCase):
    '''Abapgit Repository class tests'''

    def test_repository_init(self):
        connection = 'CONN'
        package_name = 'PKG'
        repo = sap.adt.abapgit.Repository(connection, package_name)
        self.assertIs(repo._connection, connection)
        self.assertIs(repo._package_name, package_name)

    def test_repository_fetch_valid(self):
        connection = sample_connection()
        repo = sap.adt.abapgit.Repository(connection, 'PKG')
        repo.fetch()

        connection.execute.assert_called_once_with(
            'GET', 'abapgit/repos', accept='application/abapgit.adt.repos.v2+xml')
        self.assertIsNotNone(repo._repo)
        self.assertEqual(repo.get_status(), 'E')
        self.assertEqual(repo.get_status_text(), 'Pulled with errors')

    def test_repository_fetch_invalid(self):
        repo = sap.adt.abapgit.Repository(sample_connection(), 'NO_PKG')
        with self.assertRaises(KeyError):
            repo.fetch()

    def test_repository_link(self):
        connection = sample_connection()
        sap.adt.abapgit.Repository.link(connection, {
            'package': 'PKG',
            'url': 'URL',
        })

        connection.execute.assert_called_once_with(
            'POST',
            'abapgit/repos',
            content_type='application/abapgit.adt.repo.v3+xml',
            body='''<?xml version="1.0" encoding="UTF-8"?>
<abapgitrepo:repository xmlns:abapgitrepo="http://www.sap.com/adt/abapgit/repositories">
  <abapgitrepo:package>PKG</abapgitrepo:package>
  <abapgitrepo:url>URL</abapgitrepo:url>
</abapgitrepo:repository>''')

    def test_repository_pull_valid(self):
        connection = sample_connection()
        repo = sap.adt.abapgit.Repository(connection, 'PKG')
        repo.fetch()

        response = mock.MagicMock()
        response.status_code = 202
        connection.execute = mock.Mock(return_value=response)

        repo.pull({
            'remoteUser': 'user',
            'remotePassword': 'password'
        })

        connection.execute.assert_called_once_with(
            'POST',
            'abapgit/repos/000000000001/pull',
            content_type='application/abapgit.adt.repo.v3+xml',
            body='''<?xml version="1.0" encoding="UTF-8"?>
<abapgitrepo:repository xmlns:abapgitrepo="http://www.sap.com/adt/abapgit/repositories">
  <abapgitrepo:remoteUser>user</abapgitrepo:remoteUser>
  <abapgitrepo:remotePassword>password</abapgitrepo:remotePassword>
  <abapgitrepo:branchName>refs/heads/master</abapgitrepo:branchName>
</abapgitrepo:repository>''')

    def test_repository_pull_invalid(self):
        connection = sample_connection()
        repo = sap.adt.abapgit.Repository(connection, 'PKG')
        repo.fetch()

        response = mock.MagicMock()
        response.text = 'text'
        connection.execute = mock.Mock(return_value=response)

        with self.assertRaises(RuntimeError):
            repo.pull({})

    def test_repository_get_status(self):
        connection = sample_connection()
        repo = sap.adt.abapgit.Repository(connection, 'PKG')
        self.assertEqual(repo.get_status(), 'E')
        connection.execute.assert_called_once()

    def test_repository_get_error_log(self):
        connection = sample_connection()
        repo = sap.adt.abapgit.Repository(connection, 'PKG')
        repo.fetch()

        response = mock.MagicMock()
        response.text = SAMPLE_LOG_XML
        connection.execute = mock.Mock(return_value=response)

        log = repo.get_error_log()
        self.assertEqual(log, 'E: CLAS CL_SOMETHING:  Test objects cannot be created in foreign namespaces')
