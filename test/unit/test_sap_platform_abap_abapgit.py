#!/usr/bin/env python3

import unittest
from io import StringIO

from sap.platform.abap import Structure, InternalTable

import sap.platform.abap.abapgit


class SIMPLE_ABAP_STRUCT(Structure):

    FOO: str
    BAR: str


class SIMPLE_ABAP_STRUCT_TT(InternalTable[SIMPLE_ABAP_STRUCT]): pass


class TestXMLSerializer(unittest.TestCase):

    def test_full_file(self):
        dest = StringIO()

        writer = sap.platform.abap.abapgit.XMLWriter('LCL_PYTHON_SERIALIZER', dest)
        writer.add(SIMPLE_ABAP_STRUCT(FOO='BAR', BAR='FOO'))
        writer.add(SIMPLE_ABAP_STRUCT(FOO='GRC', BAR='BLAH'))
        writer.add(SIMPLE_ABAP_STRUCT_TT(SIMPLE_ABAP_STRUCT(FOO='ARG', BAR='DOH')))
        writer.close()

        self.assertEqual(dest.getvalue(), '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_PYTHON_SERIALIZER" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <SIMPLE_ABAP_STRUCT>
    <FOO>BAR</FOO>
    <BAR>FOO</BAR>
   </SIMPLE_ABAP_STRUCT>
   <SIMPLE_ABAP_STRUCT>
    <FOO>GRC</FOO>
    <BAR>BLAH</BAR>
   </SIMPLE_ABAP_STRUCT>
   <SIMPLE_ABAP_STRUCT_TT>
    <item>
     <FOO>ARG</FOO>
     <BAR>DOH</BAR>
    </item>
   </SIMPLE_ABAP_STRUCT_TT>
  </asx:values>
 </asx:abap>
</abapGit>
''')


class TestDOT_ABAP_GIT(unittest.TestCase):

    def test_dot_abap_git_from_xml(self):
        config = sap.platform.abap.abapgit.DOT_ABAP_GIT.from_xml('''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <DATA>
   <MASTER_LANGUAGE>E</MASTER_LANGUAGE>
   <STARTING_FOLDER>/backend/</STARTING_FOLDER>
   <FOLDER_LOGIC>FULL</FOLDER_LOGIC>
   <IGNORE>
    <item>/.gitignore</item>
    <item>/LICENSE</item>
    <item>/README.md</item>
    <item>/package.json</item>
    <item>/.travis.yml</item>
   </IGNORE>
  </DATA>
 </asx:values>
</asx:abap>''');

        self.assertEqual(config.MASTER_LANGUAGE, 'E')
        self.assertEqual(config.STARTING_FOLDER, '/backend/')
        self.assertEqual(config.FOLDER_LOGIC, 'FULL')
        self.assertEqual([itm for itm in config.IGNORE], ['/.gitignore', '/LICENSE', '/README.md', '/package.json', '/.travis.yml'])


if __name__ == '__main__':
    unittest.main()
