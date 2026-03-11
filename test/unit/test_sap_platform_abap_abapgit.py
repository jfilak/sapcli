#!/usr/bin/env python3

import unittest
from io import StringIO

from sap.errors import SAPCliError
from sap.platform.abap import Structure, ItemizedTable

import sap.platform.abap.abapgit
from sap.platform.abap.abapgit import OptionalBody


class SIMPLE_ABAP_STRUCT(Structure):

    FOO: str
    BAR: str


class SIMPLE_ABAP_STRUCT_TT(ItemizedTable[SIMPLE_ABAP_STRUCT]): pass


class TestXMLSerializer(unittest.TestCase):

    def test_full_file(self):
        dest = StringIO()
        table = sap.platform.abap.InternalTable.define('SIMPLE_TABLE', str)()
        table.append('<SIMPLE_OBJECT>FOO</SIMPLE_OBJECT>')
        table.append('<SIMPLE_OBJECT>BAR</SIMPLE_OBJECT>')

        writer = sap.platform.abap.abapgit.XMLWriter('LCL_PYTHON_SERIALIZER', dest)
        writer.add(table)
        writer.add(SIMPLE_ABAP_STRUCT(FOO='BAR', BAR='FOO'))
        writer.add(SIMPLE_ABAP_STRUCT(FOO='GRC', BAR='BLAH'))
        writer.add(SIMPLE_ABAP_STRUCT_TT(SIMPLE_ABAP_STRUCT(FOO='ARG', BAR='DOH')))
        writer.close()

        self.assertEqual(dest.getvalue(), '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_PYTHON_SERIALIZER" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <SIMPLE_TABLE>
    <SIMPLE_OBJECT>FOO</SIMPLE_OBJECT>
    <SIMPLE_OBJECT>BAR</SIMPLE_OBJECT>
   </SIMPLE_TABLE>
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

    def test_dot_abap_git_from_xml_with_name_and_version_constant(self):
        config = sap.platform.abap.abapgit.DOT_ABAP_GIT.from_xml('''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <DATA>
   <NAME>Z_MY_REPO</NAME>
   <MASTER_LANGUAGE>E</MASTER_LANGUAGE>
   <STARTING_FOLDER>/src/</STARTING_FOLDER>
   <FOLDER_LOGIC>PREFIX</FOLDER_LOGIC>
   <IGNORE>
    <item>/.gitignore</item>
   </IGNORE>
   <VERSION_CONSTANT>IF_VERSION=&gt;CO_VERSION</VERSION_CONSTANT>
  </DATA>
 </asx:values>
</asx:abap>''')

        self.assertEqual(config.NAME, 'Z_MY_REPO')
        self.assertEqual(config.MASTER_LANGUAGE, 'E')
        self.assertEqual(config.STARTING_FOLDER, '/src/')
        self.assertEqual(config.FOLDER_LOGIC, 'PREFIX')
        self.assertEqual([itm for itm in config.IGNORE], ['/.gitignore'])
        self.assertEqual(config.VERSION_CONSTANT, 'IF_VERSION=>CO_VERSION')

    def test_dot_abap_git_from_xml_without_name_and_version_constant(self):
        config = sap.platform.abap.abapgit.DOT_ABAP_GIT.from_xml('''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <DATA>
   <MASTER_LANGUAGE>E</MASTER_LANGUAGE>
   <STARTING_FOLDER>/src/</STARTING_FOLDER>
   <FOLDER_LOGIC>FULL</FOLDER_LOGIC>
   <IGNORE/>
  </DATA>
 </asx:values>
</asx:abap>''')

        self.assertIsNone(config.NAME)
        self.assertIsNone(config.VERSION_CONSTANT)


class ANOTHER_ABAP_STRUCT(Structure):

    FIRST: str
    SECOND: str


class TestAbapGitFromXml(unittest.TestCase):

    def test_abap_git_from_xml(self):
        SIMPLE_OBJECT = type('SIMPLE_OBJECT', (str,), {})

        parsed = sap.platform.abap.abapgit.from_xml([SIMPLE_OBJECT, SIMPLE_ABAP_STRUCT_TT], '''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
    <SIMPLE_OBJECT>FOO</SIMPLE_OBJECT>
    <SIMPLE_ABAP_STRUCT_TT>
      <item>
        <FOO>ARG</FOO>
        <BAR>DOH</BAR>
      </item>
      <item>
        <FOO>ARG2</FOO>
        <BAR>DOH2</BAR>
      </item>
    </SIMPLE_ABAP_STRUCT_TT>
  </asx:values>
</asx:abap>''')

        self.assertEqual(parsed['SIMPLE_OBJECT'], 'FOO')
        self.assertEqual(len(parsed['SIMPLE_ABAP_STRUCT_TT']), 2)
        self.assertEqual(parsed['SIMPLE_ABAP_STRUCT_TT'][0].FOO, 'ARG')
        self.assertEqual(parsed['SIMPLE_ABAP_STRUCT_TT'][0].BAR, 'DOH')
        self.assertEqual(parsed['SIMPLE_ABAP_STRUCT_TT'][1].FOO, 'ARG2')
        self.assertEqual(parsed['SIMPLE_ABAP_STRUCT_TT'][1].BAR, 'DOH2')


class TestOptionalBody(unittest.TestCase):

    def test_optional_body_name(self):
        optional = OptionalBody(SIMPLE_ABAP_STRUCT)
        self.assertEqual(optional.__name__, 'SIMPLE_ABAP_STRUCT')

    def test_optional_body_present(self):
        parsed = sap.platform.abap.abapgit.from_xml(
            [SIMPLE_ABAP_STRUCT, OptionalBody(ANOTHER_ABAP_STRUCT), SIMPLE_ABAP_STRUCT_TT],
            '''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
    <SIMPLE_ABAP_STRUCT>
      <FOO>hello</FOO>
      <BAR>world</BAR>
    </SIMPLE_ABAP_STRUCT>
    <ANOTHER_ABAP_STRUCT>
      <FIRST>one</FIRST>
      <SECOND>two</SECOND>
    </ANOTHER_ABAP_STRUCT>
    <SIMPLE_ABAP_STRUCT_TT>
      <item>
        <FOO>ARG</FOO>
        <BAR>DOH</BAR>
      </item>
    </SIMPLE_ABAP_STRUCT_TT>
  </asx:values>
</asx:abap>''')

        self.assertEqual(parsed['SIMPLE_ABAP_STRUCT'].FOO, 'hello')
        self.assertEqual(parsed['SIMPLE_ABAP_STRUCT'].BAR, 'world')
        self.assertEqual(parsed['ANOTHER_ABAP_STRUCT'].FIRST, 'one')
        self.assertEqual(parsed['ANOTHER_ABAP_STRUCT'].SECOND, 'two')
        self.assertEqual(len(parsed['SIMPLE_ABAP_STRUCT_TT']), 1)
        self.assertEqual(parsed['SIMPLE_ABAP_STRUCT_TT'][0].FOO, 'ARG')

    def test_optional_body_missing(self):
        parsed = sap.platform.abap.abapgit.from_xml(
            [SIMPLE_ABAP_STRUCT, OptionalBody(ANOTHER_ABAP_STRUCT), SIMPLE_ABAP_STRUCT_TT],
            '''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
    <SIMPLE_ABAP_STRUCT>
      <FOO>hello</FOO>
      <BAR>world</BAR>
    </SIMPLE_ABAP_STRUCT>
    <SIMPLE_ABAP_STRUCT_TT>
      <item>
        <FOO>ARG</FOO>
        <BAR>DOH</BAR>
      </item>
    </SIMPLE_ABAP_STRUCT_TT>
  </asx:values>
</asx:abap>''')

        self.assertEqual(parsed['SIMPLE_ABAP_STRUCT'].FOO, 'hello')
        self.assertNotIn('ANOTHER_ABAP_STRUCT', parsed)
        self.assertEqual(len(parsed['SIMPLE_ABAP_STRUCT_TT']), 1)

    def test_required_body_missing_raises_error(self):
        with self.assertRaises(SAPCliError) as cm:
            sap.platform.abap.abapgit.from_xml(
                [SIMPLE_ABAP_STRUCT, ANOTHER_ABAP_STRUCT, SIMPLE_ABAP_STRUCT_TT],
                '''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
    <SIMPLE_ABAP_STRUCT>
      <FOO>hello</FOO>
      <BAR>world</BAR>
    </SIMPLE_ABAP_STRUCT>
    <SIMPLE_ABAP_STRUCT_TT>
      <item>
        <FOO>ARG</FOO>
        <BAR>DOH</BAR>
      </item>
    </SIMPLE_ABAP_STRUCT_TT>
  </asx:values>
</asx:abap>''')

        self.assertEqual(str(cm.exception), 'Got unexpected tag SIMPLE_ABAP_STRUCT_TT')


if __name__ == '__main__':
    unittest.main()
