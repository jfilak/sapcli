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

PROG_WITH_TEXTS_XML = '''<?xml version="1.0" encoding="utf-8"?>
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
     <ID>I</ID>
     <KEY>001</KEY>
     <ENTRY>Hello, world!</ENTRY>
     <LENGTH>20</LENGTH>
    </item>
    <item>
     <ID>I</ID>
     <KEY>002</KEY>
     <ENTRY>a=b</ENTRY>
     <LENGTH>10</LENGTH>
    </item>
    <item>
     <ID>R</ID>
     <ENTRY>Test program desc</ENTRY>
     <LENGTH>17</LENGTH>
    </item>
    <item>
     <ID>S</ID>
     <KEY>P_MATNR</KEY>
     <ENTRY>.</ENTRY>
     <LENGTH>17</LENGTH>
     <SPLIT>D</SPLIT>
    </item>
   </TPOOL>
  </asx:values>
 </asx:abap>
</abapGit>'''

INCLUDE_WITH_TEXTS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_PROG" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <PROGDIR>
    <NAME>TEST_INCLUDE</NAME>
    <SUBC>I</SUBC>
   </PROGDIR>
   <TPOOL>
    <item>
     <ID>I</ID>
     <KEY>001</KEY>
     <ENTRY>Hello, world!</ENTRY>
     <LENGTH>20</LENGTH>
    </item>
    <item>
     <ID>R</ID>
     <ENTRY>Test include desc</ENTRY>
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

PROG_WITH_CUA_XML = '''<?xml version="1.0" encoding="utf-8"?>
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
   <CUA>
    <ADM>
     <PFKCODE>000001</PFKCODE>
    </ADM>
    <STA>
     <RSMPE_STAT>
      <CODE>DECIDE_DIALOG</CODE>
      <MODAL>P</MODAL>
      <PFKCODE>000001</PFKCODE>
      <BUTCODE>0001</BUTCODE>
      <INT_NOTE>Dialog toolbar</INT_NOTE>
     </RSMPE_STAT>
    </STA>
    <FUN>
     <RSMPE_FUNT>
      <CODE>OK</CODE>
      <TEXTNO>001</TEXTNO>
      <TEXT_TYPE>S</TEXT_TYPE>
      <TEXT_NAME>ICON_OKAY</TEXT_NAME>
      <ICON_ID>@0V@</ICON_ID>
      <FUN_TEXT>Continue</FUN_TEXT>
      <ICON_TEXT>Continue</ICON_TEXT>
     </RSMPE_FUNT>
    </FUN>
    <BUT>
     <RSMPE_BUT>
      <PFK_CODE>000001</PFK_CODE>
      <CODE>0001</CODE>
      <NO>01</NO>
      <PFNO>00</PFNO>
     </RSMPE_BUT>
    </BUT>
    <PFK>
     <RSMPE_PFK>
      <CODE>000001</CODE>
      <PFNO>00</PFNO>
      <FUNCODE>OK</FUNCODE>
      <FUNNO>001</FUNNO>
     </RSMPE_PFK>
    </PFK>
    <SET>
     <RSMPE_STAF>
      <STATUS>DECIDE_DIALOG</STATUS>
      <FUNCTION>OK</FUNCTION>
     </RSMPE_STAF>
    </SET>
    <DOC>
     <RSMPE_ATRT>
      <OBJ_TYPE>P</OBJ_TYPE>
      <OBJ_CODE>000001</OBJ_CODE>
      <MODAL>P</MODAL>
      <INT_NOTE>Dialog FK settings</INT_NOTE>
     </RSMPE_ATRT>
    </DOC>
   </CUA>
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
