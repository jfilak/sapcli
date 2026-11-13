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
       <STEXT>ABAP Package Name</STEXT>
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

CHECKOUT_FUNCTION_GROUP_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_FUGR" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <AREAT>TEST FUNCTION GROUP</AREAT>
   <INCLUDES>
    <SOBJ_NAME>TEST_INCLUDE_1TOP</SOBJ_NAME>
    <SOBJ_NAME>TEST_INCLUDE_2</SOBJ_NAME>
   </INCLUDES>
   <FUNCTIONS>
    <item>
     <FUNCNAME>TEST_FUNCTION_1</FUNCNAME>
     <SHORT_TEXT>Test function 1 description.</SHORT_TEXT>
     <IMPORT>
      <RSIMP>
       <PARAMETER>IMPORT_PARAM_1</PARAMETER>
       <DEFAULT>&apos;/src/&apos;</DEFAULT>
       <OPTIONAL>X</OPTIONAL>
       <TYP>STRING</TYP>
      </RSIMP>
      <RSIMP>
       <PARAMETER>IMPORT_PARAM_2</PARAMETER>
       <TYP>STRING</TYP>
      </RSIMP>
     </IMPORT>
     <CHANGING>
      <RSCHA>
       <PARAMETER>CHANGING_PARAM_1</PARAMETER>
       <REFERENCE>X</REFERENCE>
       <TYP>BAPIRET2</TYP>
      </RSCHA>
      <RSCHA>
       <PARAMETER>CHANGING_PARAM_2</PARAMETER>
       <DEFAULT>&apos;default&apos;</DEFAULT>
       <OPTIONAL>X</OPTIONAL>
       <TYP>BAPIRET2</TYP>
      </RSCHA>
     </CHANGING>
     <EXPORT>
      <RSEXP>
       <PARAMETER>EXPORT_PARAM_1</PARAMETER>
       <TYP>BAPIRET2</TYP>
      </RSEXP>
      <RSEXP>
       <PARAMETER>EXPORT_PARAM_2</PARAMETER>
       <REFERENCE>X</REFERENCE>
       <TYP>STRING</TYP>
      </RSEXP>
     </EXPORT>
     <TABLES>
      <RSTBL>
       <PARAMETER>TABLES_PARAM_1</PARAMETER>
       <TYP>BAPIRET2</TYP>
      </RSTBL>
      <RSTBL>
       <PARAMETER>TABLES_PARAM_2</PARAMETER>
       <OPTIONAL>X</OPTIONAL>
       <TYP>BAPIRET2</TYP>
      </RSTBL>
      <RSTBL>
       <PARAMETER>TABLES_PARAM_3</PARAMETER>
       <TYP>BAPIRET2_T</TYP>
      </RSTBL>
     </TABLES>
     <EXCEPTION>
      <RSEXC>
       <EXCEPTION>TEST_EXCEPTION</EXCEPTION>
      </RSEXC>
     </EXCEPTION>
     <DOCUMENTATION>
      <RSFDO>
       <PARAMETER>IMPORT_PARAM_1</PARAMETER>
       <KIND>P</KIND>
      </RSFDO>
      <RSFDO>
       <PARAMETER>IMPORT_PARAM_2</PARAMETER>
       <KIND>P</KIND>
      </RSFDO>
      <RSFDO>
       <PARAMETER>EXPORT_PARAM_1</PARAMETER>
       <KIND>P</KIND>
      </RSFDO>
      <RSFDO>
       <PARAMETER>EXPORT_PARAM_2</PARAMETER>
       <KIND>P</KIND>
      </RSFDO>
      <RSFDO>
       <PARAMETER>TABLES_PARAM_1</PARAMETER>
       <KIND>P</KIND>
      </RSFDO>
      <RSFDO>
       <PARAMETER>TABLES_PARAM_2</PARAMETER>
       <KIND>P</KIND>
      </RSFDO>
      <RSFDO>
       <PARAMETER>TABLES_PARAM_3</PARAMETER>
       <KIND>P</KIND>
      </RSFDO>
      <RSFDO>
       <PARAMETER>CHANGING_PARAM_1</PARAMETER>
       <KIND>P</KIND>
      </RSFDO>
      <RSFDO>
       <PARAMETER>CHANGING_PARAM_2</PARAMETER>
       <KIND>P</KIND>
      </RSFDO>
      <RSFDO>
       <PARAMETER>TEST_EXCEPTION</PARAMETER>
       <KIND>X</KIND>
      </RSFDO>
     </DOCUMENTATION>
    </item>
    <item>
     <FUNCNAME>TEST_FUNCTION_2</FUNCNAME>
     <REMOTE_CALL>R</REMOTE_CALL>
     <SHORT_TEXT>Test function 2 description.</SHORT_TEXT>
     <IMPORT>
      <RSIMP>
       <PARAMETER>IMPORT_PARAM_1</PARAMETER>
       <TYP>STRING</TYP>
      </RSIMP>
     </IMPORT>
     <DOCUMENTATION>
      <RSFDO>
       <PARAMETER>IMPORT_PARAM_1</PARAMETER>
       <KIND>P</KIND>
      </RSFDO>
     </DOCUMENTATION>
    </item>
   </FUNCTIONS>
  </asx:values>
 </asx:abap>
</abapGit>
'''

CHECKOUT_FUNCTION_INCLUDE_1_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <PROGDIR>
    <NAME>TEST_INCLUDE_1TOP</NAME>
    <DBAPL>S</DBAPL>
    <SUBC>I</SUBC>
    <FIXPT>X</FIXPT>
    <LDBNAME>D$S</LDBNAME>
    <UCCHECK>X</UCCHECK>
    <RLOAD>E</RLOAD>
    <DBNA>D$</DBNA>
    <APPL>S</APPL>
   </PROGDIR>
  </asx:values>
 </asx:abap>
</abapGit>
'''

CHECKOUT_FUNCTION_INCLUDE_2_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <PROGDIR>
    <NAME>TEST_INCLUDE_2</NAME>
    <SUBC>I</SUBC>
    <UCCHECK>X</UCCHECK>
    <RLOAD>E</RLOAD>
    <APPL>S</APPL>
   </PROGDIR>
   <TPOOL>
    <item>
     <ID>R</ID>
     <ENTRY>Test include 2 description.</ENTRY>
     <LENGTH>27</LENGTH>
    </item>
   </TPOOL>
  </asx:values>
 </asx:abap>
</abapGit>
'''

CHECKOUT_FUNCTION_MODULE_1_CODE = '''FUNCTION test_function_1
  IMPORTING
     VALUE(IMPORT_PARAM_1) TYPE  STRING DEFAULT '/src/'
     VALUE(IMPORT_PARAM_2) TYPE  STRING
  CHANGING
     REFERENCE(CHANGING_PARAM_1) TYPE  BAPIRET2
     VALUE(CHANGING_PARAM_2) TYPE  BAPIRET2 DEFAULT 'default'
  EXPORTING
     VALUE(EXPORT_PARAM_1) TYPE  BAPIRET2
     REFERENCE(EXPORT_PARAM_2) TYPE  STRING
  TABLES
      TABLES_PARAM_1 TYPE  BAPIRET2
      TABLES_PARAM_2 TYPE  BAPIRET2 OPTIONAL
      TABLES_PARAM_3 TYPE  BAPIRET2_T
  EXCEPTIONS
      TEST_EXCEPTION.

    Write 'Hello World'.
ENDFUNCTION.'''

CHECKOUT_FUNCTION_MODULE_1_CODE_ABAPGIT = '''FUNCTION test_function_1.
*"--------------------------------------------------------------------
*"*"Local Interface:
*"  IMPORTING
*"     VALUE(IMPORT_PARAM_1) TYPE  STRING DEFAULT '/src/'
*"     VALUE(IMPORT_PARAM_2) TYPE  STRING
*"  CHANGING
*"     REFERENCE(CHANGING_PARAM_1) TYPE  BAPIRET2
*"     VALUE(CHANGING_PARAM_2) TYPE  BAPIRET2 DEFAULT 'default'
*"  EXPORTING
*"     VALUE(EXPORT_PARAM_1) TYPE  BAPIRET2
*"     REFERENCE(EXPORT_PARAM_2) TYPE  STRING
*"  TABLES
*"     TABLES_PARAM_1 TYPE  BAPIRET2
*"     TABLES_PARAM_2 TYPE  BAPIRET2 OPTIONAL
*"     TABLES_PARAM_3 TYPE  BAPIRET2_T
*"  EXCEPTIONS
*"     TEST_EXCEPTION
*"--------------------------------------------------------------------

    Write 'Hello World'.

ENDFUNCTION.
'''

CHECKOUT_FUNCTION_MODULE_2_CODE = '''FUNCTION test_function_2
  IMPORTING
     VALUE(IMPORT_PARAM_1) TYPE  STRING.

    Write 'Hello World'.
ENDFUNCTION.'''

CHECKOUT_FUNCTION_MODULE_2_CODE_ABAPGIT = '''FUNCTION test_function_2.
*"--------------------------------------------------------------------
*"*"Local Interface:
*"  IMPORTING
*"     VALUE(IMPORT_PARAM_1) TYPE  STRING
*"--------------------------------------------------------------------

    Write 'Hello World'.

ENDFUNCTION.
'''
