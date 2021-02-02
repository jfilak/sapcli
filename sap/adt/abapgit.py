"""Abapgit ADT wrappers"""

from xml.etree import ElementTree
from xml.sax.saxutils import escape


ABAPGIT_REPO_XML_SPACE = '{http://www.sap.com/adt/abapgit/repositories}'
ABAPGIT_OBJECT_XML_SPACE = '{http://www.sap.com/adt/abapgit/abapObjects}'


def repo_request_body(props):
    """Creates repository Wraps content in repository xml envelope"""

    content = '\n'.join(
        f'  <abapgitrepo:{pair[0]}>{escape(pair[1])}</abapgitrepo:{pair[0]}>'
        for pair in props.items()
        if pair[1] is not None)

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<abapgitrepo:repository xmlns:abapgitrepo="http://www.sap.com/adt/abapgit/repositories">
{content}
</abapgitrepo:repository>'''


def get_repo_text(repository, element_key):
    """Gets repository element text"""

    return repository.find(f'{ABAPGIT_REPO_XML_SPACE}{element_key}').text


class Repository:
    """Abapgit repository abstraction"""

    @staticmethod
    def link(connection, props):
        """Create abapgit repository by linking abab package to remote repository"""

        return connection.execute(
            'POST',
            'abapgit/repos',
            content_type='application/abapgit.adt.repo.v3+xml',
            body=repo_request_body(props)
        )

    def __init__(self, connection, package_name):
        self._connection = connection
        self._package_name = package_name
        self._repo = None

    def fetch(self):
        """Fetches actual data from ABAP system"""

        response = self._connection.execute(
            'GET',
            'abapgit/repos',
            accept='application/abapgit.adt.repos.v2+xml'
        )

        root = ElementTree.fromstring(response.text)

        try:
            self._repo = next(repo for repo in list(root)
                              if get_repo_text(repo, 'package') == self._package_name)
        except StopIteration as no_exist:
            raise KeyError(f'Repository for package {self._package_name} not found.') from no_exist

    def pull(self, props):
        """Triggers pull operation"""

        if props.get('branchName') is None:
            props['branchName'] = self._get_repo().find(f'{ABAPGIT_REPO_XML_SPACE}branchName').text

        response = self._connection.execute(
            'POST',
            self._get_link('pull_link'),
            content_type='application/abapgit.adt.repo.v3+xml',
            body=repo_request_body(props)
        )

        if response.status_code != 202:
            raise RuntimeError(f'Failed to trigger pull: {response.text}')

    def get_status(self):
        """Gets repository status code"""

        return get_repo_text(self._get_repo(), 'status')

    def get_status_text(self):
        """Gets repository status text"""

        return get_repo_text(self._get_repo(), 'statusText')

    def get_error_log(self):
        """Gets errors from repository log"""

        response = self._connection.execute(
            'GET',
            self._get_link('log_link'),
            accept='application/abapgit.adt.repo.object.v2+xml'
        )

        log = ElementTree.fromstring(response.text)

        def text(element, key):
            return element.find(f'{ABAPGIT_OBJECT_XML_SPACE}{key}').text

        return '\n'.join(
            f'{text(obj, "msgType")}: {text(obj, "type")} {text(obj, "name")}:  {text(obj, "msgText")}'
            for obj in log.findall(f'{ABAPGIT_OBJECT_XML_SPACE}abapObject')
            if text(obj, 'msgType') != 'S')

    def _get_repo(self):
        """Gets ababpgit repository info, fetches from server if not already fetched"""
        if self._repo is None:
            self.fetch()

        return self._repo

    def _get_link(self, link_type):
        """Gets link of given type, changed to relative path /sap/bc/adt/"""

        url = next(link.attrib["href"] for link
                   in self._get_repo().findall('{http://www.w3.org/2005/Atom}link')
                   if link.attrib["type"] == link_type)

        prefix = '/sap/bc/adt/'
        return url[len(prefix):] if url.startswith(prefix) else url
