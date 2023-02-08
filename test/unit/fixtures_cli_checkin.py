PACKAGE_DEVC_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DEVC" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DEVC>
    <CTEXT>Test Package</CTEXT>
    <SRV_CHECK>X</SRV_CHECK>
   </DEVC>
  </asx:values>
 </asx:abap>
</abapGit>'''

CLAS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_CLAS" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <VSEOCLASS>
    <CLSNAME>TEST CLASS</CLSNAME>
    <LANGU>E</LANGU>
    <DESCRIPT>Test description</DESCRIPT>
    <STATE>1</STATE>
    <CLSCCINCL>X</CLSCCINCL>
    <FIXPT>X</FIXPT>
    <UNICODE>X</UNICODE>
    <WITH_UNIT_TESTS>X</WITH_UNIT_TESTS>
   </VSEOCLASS>
  </asx:values>
 </asx:abap>
</abapGit>'''

INTF_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_INTF" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <VSEOINTERF>
    <CLSNAME>TEST_INTF</CLSNAME>
    <LANGU>E</LANGU>
    <DESCRIPT>Test intf descr</DESCRIPT>
    <EXPOSURE>2</EXPOSURE>
    <STATE>1</STATE>
    <UNICODE>X</UNICODE>
   </VSEOINTERF>
  </asx:values>
 </asx:abap>
</abapGit>'''

PROG_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_PROG" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <PROGDIR>
    <NAME>TEST_PROG</NAME>
    <SUBC>1</SUBC>
    <RLOAD>E</RLOAD>
    <FIXPT>X</FIXPT>
    <UCCHECK>X</UCCHECK>
   </PROGDIR>
   <TPOOL>
    <item>
     <ID>R</ID>
     <ENTRY>Test program desc</ENTRY>
     <LENGTH>17</LENGTH>
    </item>
   </TPOOL>
  </asx:values>
 </asx:abap>
</abapGit>'''

INVALID_TYPE_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_PROG" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <PROGDIR>
    <NAME>TEST_PROG</NAME>
    <SUBC>X</SUBC>
    <RLOAD>E</RLOAD>
    <FIXPT>X</FIXPT>
    <UCCHECK>X</UCCHECK>
   </PROGDIR>
   <TPOOL>
    <item>
     <ID>R</ID>
     <ENTRY>Test program desc</ENTRY>
     <LENGTH>17</LENGTH>
    </item>
   </TPOOL>
  </asx:values>
 </asx:abap>
</abapGit>'''

INCLUDE_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_PROG" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <PROGDIR>
    <NAME>TEST_INCLUDE</NAME>
    <SUBC>I</SUBC>
    <RLOAD>E</RLOAD>
    <FIXPT>X</FIXPT>
    <UCCHECK>X</UCCHECK>
   </PROGDIR>
   <TPOOL>
    <item>
     <ID>R</ID>
     <ENTRY>Test include desc</ENTRY>
     <LENGTH>17</LENGTH>
    </item>
   </TPOOL>
  </asx:values>
 </asx:abap>
</abapGit>'''
