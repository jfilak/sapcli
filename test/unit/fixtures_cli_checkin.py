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
