#!/usr/bin/env python3

import unittest
from io import StringIO

import sap.platform.abap


class PLAIN_STRUCT(sap.platform.abap.Structure):

    PYTHON: str
    LINUX: str


class STRUCT_WITH_STRING_TABLE(sap.platform.abap.Structure):

    PYTHON: str
    LINUX: str
    DISTROS: sap.platform.abap.StringTable


class TestSAPPlatformABAP(unittest.TestCase):

    def test_structure_init_without_values(self):
        plain = PLAIN_STRUCT()

        self.assertIsNone(plain.PYTHON)
        self.assertIsNone(plain.LINUX)

    def test_structure_init_with_all_values(self):
        plain = PLAIN_STRUCT(PYTHON='3.7', LINUX='Fedora')

        self.assertEqual(plain.PYTHON, '3.7')
        self.assertEqual(plain.LINUX, 'Fedora')

    def test_structure_init_with_some_values(self):
        plain = PLAIN_STRUCT(PYTHON='3.7')

        self.assertEqual(plain.PYTHON, '3.7')
        self.assertEqual(plain.LINUX, None)

        plain = PLAIN_STRUCT(LINUX='Fedora')

        self.assertEqual(plain.PYTHON, None)
        self.assertEqual(plain.LINUX, 'Fedora')

    def test_structure_init_with_extra_values(self):
        with self.assertRaises(TypeError) as caught:
            plain = PLAIN_STRUCT(JAVASCRIPT='@')

        self.assertEqual(str(caught.exception), 'PLAIN_STRUCT does not define member JAVASCRIPT')


class TestSAPPlatformABAPToXML(unittest.TestCase):

    def test_to_xml_plain_stucture(self):
        struct = PLAIN_STRUCT(PYTHON='theBest', LINUX='better')

        dest = StringIO()
        sap.platform.abap.to_xml(struct, dest)

        self.assertEqual(dest.getvalue(), '''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <PLAIN_STRUCT>
   <PYTHON>theBest</PYTHON>
   <LINUX>better</LINUX>
  </PLAIN_STRUCT>
 </asx:values>
</asx:abap>\n''')

    def test_to_xml_plain_stucture_changed_top(self):
        struct = PLAIN_STRUCT(PYTHON='theBest', LINUX='better')

        dest = StringIO()
        sap.platform.abap.to_xml(struct, dest, top_element='ROOT')

        self.assertEqual(dest.getvalue(), '''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <ROOT>
   <PYTHON>theBest</PYTHON>
   <LINUX>better</LINUX>
  </ROOT>
 </asx:values>
</asx:abap>\n''')

    def test_to_xml_stucture_with_string_table(self):
        struct = STRUCT_WITH_STRING_TABLE(PYTHON='theBest', LINUX='better',
                                          DISTROS=['Fedora', 'CentOS'])

        dest = StringIO()
        sap.platform.abap.to_xml(struct, dest)

        self.assertEqual(dest.getvalue(), '''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <STRUCT_WITH_STRING_TABLE>
   <PYTHON>theBest</PYTHON>
   <LINUX>better</LINUX>
   <DISTROS>
    <item>Fedora</item>
    <item>CentOS</item>
   </DISTROS>
  </STRUCT_WITH_STRING_TABLE>
 </asx:values>
</asx:abap>\n''')


if __name__ == '__main__':
    unittest.main()
