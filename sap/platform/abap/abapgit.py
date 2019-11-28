"""ABAP Git ABAP types and utilities"""

import sap.platform.abap
from sap.platform.abap import Structure, StringTable, XMLSerializers


FOLDER_LOGIC_FULL = 'FULL'
FOLDER_LOGIC_PREFIX = 'PREFIX'


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
