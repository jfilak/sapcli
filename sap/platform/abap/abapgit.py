"""ABAP Git ABAP types and utilities"""

import xml.sax

from sap import get_logger
import sap.errors

import sap.platform.abap
from sap.platform.abap import (
    Structure,
    StringTable,
    XMLSerializers,
    ABAPContentHandler
)


FOLDER_LOGIC_FULL = 'FULL'
FOLDER_LOGIC_PREFIX = 'PREFIX'


def mod_log():
    """ADT Module logger"""

    return get_logger()


# pylint: disable=invalid-name
class DOT_ABAP_GIT(Structure):
    """ABAP GIT ABAP structure"""

    # pylint: disable=invalid-name
    MASTER_LANGUAGE: str
    # pylint: disable=invalid-name
    STARTING_FOLDER: str
    # pylint: disable=invalid-name
    FOLDER_LOGIC: str
    # pylint: disable=invalid-name
    IGNORE: StringTable

    @staticmethod
    def for_new_repo(MASTER_LANGUAGE: str = 'E', STARTING_FOLDER: str = 'src', FOLDER_LOGIC: str = FOLDER_LOGIC_FULL):
        """Creates new instance of DOT_ABAP_GIT for new repository"""

        IGNORE = StringTable('/.gitignore', '/LICENSE', '/README.md', '/package.json', '/.travis.yml')

        return DOT_ABAP_GIT(MASTER_LANGUAGE=MASTER_LANGUAGE, STARTING_FOLDER=STARTING_FOLDER,
                            FOLDER_LOGIC=FOLDER_LOGIC, IGNORE=IGNORE)

    @staticmethod
    def from_xml(xml_contents):
        """Creates new instance of DOT_ABAP_GIT for XML data"""

        config = DOT_ABAP_GIT()
        sap.platform.abap.from_xml(config, xml_contents, root_elem='DATA')
        return config


# TODO: make it a context manager
class XMLWriter:
    """ABAP GIT XML writer"""

    def __init__(self, serializer, dest_file):
        self.dest_file = dest_file

        self.dest_file.write(f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="{serializer}" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
''')

    def add(self, abap):
        """Write the structure to the dest file"""

        XMLSerializers.abap_to_xml(abap, self.dest_file, '   ', row_name_getter=lambda x: 'item')

    def close(self):
        """Write the end sequence"""

        self.dest_file.write('''  </asx:values>
 </asx:abap>
</abapGit>
''')
        self.dest_file = None


class AGXMLObjectAdapter:
    """Implements Public API of ABAPBaseWriter"""

    def __init__(self, body_types):
        self.body_types = body_types
        self.body_type_index = 0

        self.results = {}

        self.current_body_type = self.body_types[self.body_type_index]
        self.current_body_name = self.current_body_type.__name__

        self.obj = 'Meta_Parent'

    def get_member_type(self, name):
        """Returns type of the given member"""

        if name != self.current_body_name:
            raise sap.errors.SAPCliError(f'Got unexpected tag {name} while expected {self.current_body_name}')

        mod_log().debug('Opening the object: %s', name)

        return self.current_body_type

    def start(self, name, attrs):
        """Would open Element"""

        raise sap.errors.SAPCliError(f'Meta abapGit XML Body adapter cannot be started: {name}')

    def set_child(self, name, child_obj):
        """Sets the member of the given name in the adapted object"""

        if name != self.current_body_name:
            raise sap.errors.SAPCliError(f'Got unexpected tag {name} while expected {self.current_body_name}')

        mod_log().debug('Saving the object: %s', name)
        self.results[name] = child_obj

        self.body_type_index += 1
        if self.body_type_index >= len(self.body_types):
            mod_log().debug('No more body members')
            return

        self.current_body_type = self.body_types[self.body_type_index]
        self.current_body_name = self.current_body_type.__name__
        mod_log().debug('Moving pointer the object: %s', name)

    def end(self, name, _):
        """Would close Elemen"""

        mod_log().debug('Closing Meta_Parent %s', name)


class AGXMLContentHandler(ABAPContentHandler):
    """SAX XML de-serializer"""

    def __init__(self, body_types):
        super().__init__(DOT_ABAP_GIT(), root_elem='_BogusNotMatchingTag')

        self.current = AGXMLObjectAdapter(body_types)


def from_xml(body_types, xml_contents):
    """abapGit's version of XML de-serialization"""

    parser = AGXMLContentHandler(body_types)
    xml.sax.parseString(xml_contents, parser)

    return parser.current.results
