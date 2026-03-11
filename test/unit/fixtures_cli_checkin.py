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
    <DURATION_TYPE>1</DURATION_TYPE>
    <RISK_LEVEL>2</RISK_LEVEL>
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

FUNCTION_GROUP_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_FUGR" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <AREAT>Test function group</AREAT>
   <INCLUDES>
    <SOBJ_NAME>TEST_INCLUDE</SOBJ_NAME>
   </INCLUDES>
   <FUNCTIONS>
    <item>
     <FUNCNAME>TEST_FUNCTION_MODULE</FUNCNAME>
     <REMOTE_CALL>R</REMOTE_CALL>
     <SHORT_TEXT>Test function module</SHORT_TEXT>
     <IMPORT>
      <RSIMP>
       <PARAMETER>ABAP_PACKAGE</PARAMETER>
       <DEFAULT>&apos;&apos;</DEFAULT>
       <OPTIONAL>X</OPTIONAL>
       <TYP>DEVCLASS</TYP>
      </RSIMP>
     </IMPORT>
     <TABLES>
     </TABLES>
     <DOCUMENTATION>
      <RSFDO>
       <PARAMETER>ABAP_PACKAGE</PARAMETER>
       <KIND>P</KIND>
      </RSFDO>
     </DOCUMENTATION>
    </item>
   </FUNCTIONS>
  </asx:values>
 </asx:abap>
</abapGit>'''

FUNCTION_GROUP_XML_NO_RFC = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_FUGR" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <AREAT>Test function group</AREAT>
   <INCLUDES>
    <SOBJ_NAME>TEST_INCLUDE</SOBJ_NAME>
   </INCLUDES>
   <FUNCTIONS>
    <item>
     <FUNCNAME>TEST_FUNCTION_MODULE</FUNCNAME>
     <SHORT_TEXT>Test function module</SHORT_TEXT>
     <IMPORT>
      <RSIMP>
       <PARAMETER>ABAP_PACKAGE</PARAMETER>
       <DEFAULT>&apos;&apos;</DEFAULT>
       <OPTIONAL>X</OPTIONAL>
       <TYP>DEVCLASS</TYP>
      </RSIMP>
     </IMPORT>
     <TABLES>
     </TABLES>
     <DOCUMENTATION>
      <RSFDO>
       <PARAMETER>ABAP_PACKAGE</PARAMETER>
       <KIND>P</KIND>
      </RSFDO>
     </DOCUMENTATION>
    </item>
   </FUNCTIONS>
  </asx:values>
 </asx:abap>
</abapGit>'''

FUNCTION_MODULE_CODE_ABAPGIT = '''FUNCTION ztest_function_module.
*"----------------------------------------------------------------------
*"*"Local Interface:
*"  IMPORTING
*"     VALUE(ABAP_PACKAGE) TYPE  DEVCLASS OPTIONAL
*"  EXPORTING
*"     VALUE(RETURN) TYPE  BAPIRET2
*"  TABLES
*"      RETURN_TAB STRUCTURE  BAPIRET2 OPTIONAL
*"----------------------------------------------------------------------
    RETURN = 0.
ENDFUNCTION.'''

FUNCTION_MODULE_CODE_ADT = '''FUNCTION ztest_function_module
IMPORTING
VALUE(ABAP_PACKAGE) TYPE  DEVCLASS OPTIONAL
EXPORTING
VALUE(RETURN) TYPE  BAPIRET2
TABLES
RETURN_TAB TYPE  BAPIRET2 OPTIONAL
.
    RETURN = 0.
ENDFUNCTION.'''

FUNCTION_MODULE_CODE_NO_PARAMS_ABAPGIT = '''FUNCTION ztest_function_module.
*"----------------------------------------------------------------------
*"*"Local Interface:
*"----------------------------------------------------------------------
    RETURN = 0.
ENDFUNCTION.'''

FUNCTION_MODULE_CODE_NO_PARAMS_ADT = '''FUNCTION ztest_function_module
.
    RETURN = 0.
ENDFUNCTION.'''

FUNCTION_MODULE_CODE_ALL_PARAMS_ABAPGIT = '''FUNCTION ztest_function_module.
*"----------------------------------------------------------------------
*"*"Local Interface:
*"  IMPORTING
*"     VALUE(IMPORTING_PARAM) TYPE  STRING
*"  EXPORTING
*"     VALUE(EXPORTING_PARAM) TYPE  STRING
*"  CHANGING
*"     VALUE(CHANGING_PARAM) TYPE  STRING
*"  TABLES
*"     TABLES_PARAM STRUCTURE  STRING OPTIONAL
*"  EXCEPTIONS
*"      DIVISION_BY_ZERO
*"----------------------------------------------------------------------
    RETURN = 0.
ENDFUNCTION.'''

FUNCTION_MODULE_CODE_ALL_PARAMS_ADT = '''FUNCTION ztest_function_module
IMPORTING
VALUE(IMPORTING_PARAM) TYPE  STRING
CHANGING
VALUE(CHANGING_PARAM) TYPE  STRING
EXPORTING
VALUE(EXPORTING_PARAM) TYPE  STRING
TABLES
TABLES_PARAM TYPE  STRING OPTIONAL
EXCEPTIONS
DIVISION_BY_ZERO
.
    RETURN = 0.
ENDFUNCTION.'''
