"""ADT System Information wrappers"""

from xml.etree import ElementTree

from sap.adt.core import Connection


XMLNS_ATOM = '{http://www.w3.org/2005/Atom}'

JSON_KEY_MAPPING = {
    'systemID': 'SID',
}


# pylint: disable=too-few-public-methods
class SystemInfoEntry:
    """A single entry from the system information feed"""

    def __init__(self, identity, title):
        self.identity = identity
        self.title = title


class SystemInformation:
    """Parsed system information from ADT"""

    def __init__(self, entries):
        self._entries = {entry.identity: entry for entry in entries}

    @property
    def entries(self):
        """Returns a list of all system information entries"""
        return list(self._entries.values())

    def get(self, identity):
        """Returns the title for the given identity or None if not found"""
        entry = self._entries.get(identity)
        return entry.title if entry else None

    def __iter__(self):
        return iter(self._entries.values())


def _fetch_xml_entries(connection):
    """Fetch entries from the Atom feed endpoint /sap/bc/adt/system/information"""

    resp = connection.execute(
        'GET',
        'system/information',
        accept='application/atom+xml;type=feed',
    )

    root = ElementTree.fromstring(resp.text)

    entries = []
    for entry_elem in root.findall(f'{XMLNS_ATOM}entry'):
        identity = entry_elem.find(f'{XMLNS_ATOM}id').text
        title = entry_elem.find(f'{XMLNS_ATOM}title').text
        entries.append(SystemInfoEntry(identity, title))

    return entries


def _fetch_json_entries(connection):
    """Fetch entries from the JSON endpoint /sap/bc/adt/core/http/systeminformation"""

    resp = connection.execute(
        'GET',
        'core/http/systeminformation',
        accept='application/vnd.sap.adt.core.http.systeminformation.v1+json'
    )

    data = resp.json()

    return [SystemInfoEntry(JSON_KEY_MAPPING.get(key, key), value) for key, value in data.items()]


def get_information(connection: Connection) -> SystemInformation:
    """Fetch system information from ADT endpoints

       Sends GET requests to /sap/bc/adt/system/information and
       /sap/bc/adt/core/http/systeminformation, merges the results
       into a single SystemInformation object. Entries from the XML
       endpoint take precedence over entries from the JSON endpoint
       if the same key exists in both.
    """

    xml_entries = _fetch_xml_entries(connection)
    json_entries = _fetch_json_entries(connection)

    merged = {entry.identity: entry for entry in json_entries}
    for entry in xml_entries:
        merged[entry.identity] = entry

    return SystemInformation(list(merged.values()))
