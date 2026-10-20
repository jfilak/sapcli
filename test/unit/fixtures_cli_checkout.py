FUNCTION_GROUP_XML = '''<?xml version="1.0" encoding="utf-8"?>
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

FUNCTION_INCLUDE_1_XML = '''<?xml version="1.0" encoding="utf-8"?>
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

FUNCTION_INCLUDE_2_XML = '''<?xml version="1.0" encoding="utf-8"?>
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

FUNCTION_MODULE_1_CODE = '''FUNCTION test_function_1
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

FUNCTION_MODULE_1_CODE_ABAPGIT = '''FUNCTION test_function_1.
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

FUNCTION_MODULE_2_CODE = '''FUNCTION test_function_2
  IMPORTING
     VALUE(IMPORT_PARAM_1) TYPE  STRING.

    Write 'Hello World'.
ENDFUNCTION.'''

FUNCTION_MODULE_2_CODE_ABAPGIT = '''FUNCTION test_function_2.
*"--------------------------------------------------------------------
*"*"Local Interface:
*"  IMPORTING
*"     VALUE(IMPORT_PARAM_1) TYPE  STRING
*"--------------------------------------------------------------------

    Write 'Hello World'.

ENDFUNCTION.
'''

TTYP_SORTED_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <ROWTYPE>BAPIRET2</ROWTYPE>
    <ROWKIND>S</ROWKIND>
    <DATATYPE>STRU</DATATYPE>
    <ACCESSMODE>S</ACCESSMODE>
    <KEYDEF>K</KEYDEF>
    <KEYKIND>U</KEYKIND>
    <KEYFDCOUNT>0002</KEYFDCOUNT>
    <DDTEXT>Test table type</DDTEXT>
   </DD40V>
   <DD42V>
    <DD42V>
     <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
     <KEYFDPOS>0001</KEYFDPOS>
     <KEYFIELD>TYPE</KEYFIELD>
    </DD42V>
    <DD42V>
     <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
     <KEYFDPOS>0002</KEYFDPOS>
     <KEYFIELD>ID</KEYFIELD>
    </DD42V>
   </DD42V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_PREDEFINED_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DATATYPE>CHAR</DATATYPE>
    <LENG>000001</LENG>
    <ACCESSMODE>T</ACCESSMODE>
    <KEYDEF>D</KEYDEF>
    <KEYKIND>N</KEYKIND>
    <DDTEXT>Test table type</DDTEXT>
   </DD40V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_STRING_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>D</DDLANGUAGE>
    <DATATYPE>STRG</DATATYPE>
    <ACCESSMODE>T</ACCESSMODE>
    <KEYDEF>D</KEYDEF>
    <KEYKIND>N</KEYKIND>
    <DDTEXT>Tabelle von Strings</DDTEXT>
   </DD40V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_SECONDARY_KEYS_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <ROWTYPE>/AIF/CDATA_S</ROWTYPE>
    <ROWKIND>S</ROWKIND>
    <DATATYPE>STRU</DATATYPE>
    <ACCESSMODE>T</ACCESSMODE>
    <KEYDEF>D</KEYDEF>
    <KEYKIND>N</KEYKIND>
    <DDTEXT>Table for changed data (fields)</DDTEXT>
   </DD40V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DDLS_NAME = 'ZSAPCLI_CDS'

DDLS_ADT_GET_RESPONSE_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<ddl:ddlSource xmlns:ddl="http://www.sap.com/adt/ddic/ddlsources" ddl:source_origin="0" ddl:source_type="view" ddl:source_type_description="View Entity" ddl:source_origin_description="ABAP Development Tools" abapsource:sourceUri="source/main" abapsource:fixPointArithmetic="false" abapsource:activeUnicodeCheck="false" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:name="{DDLS_NAME}" adtcore:type="DDLS/DF" adtcore:changedAt="2026-10-20T07:45:34Z" adtcore:version="active" adtcore:createdAt="2026-10-20T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="Test CDS view" adtcore:language="EN" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:packageName="$TMP" adtcore:description="Local objects"/>
</ddl:ddlSource>
'''

DDLS_SOURCE_CODE = f'''@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Test CDS view'
define view entity {DDLS_NAME}
  as select from tadir
{{
  pgmid,
  object,
  obj_name
}}
'''

DDLS_ABAPGIT_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DDLS" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DDLS>
    <DDLNAME>{DDLS_NAME}</DDLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DDTEXT>Test CDS view</DDTEXT>
    <SOURCE_TYPE>W</SOURCE_TYPE>
   </DDLS>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DDLS_NO_SOURCE_TYPE_ABAPGIT_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DDLS" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DDLS>
    <DDLNAME>{DDLS_NAME}</DDLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DDTEXT>Test CDS view</DDTEXT>
   </DDLS>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DCLS_NAME = 'ZSAPCLI_DCL'

DCLS_ADT_GET_RESPONSE_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<dcl:dclSource xmlns:dcl="http://www.sap.com/adt/acm/dclsources" abapsource:sourceUri="source/main" abapsource:fixPointArithmetic="false" abapsource:activeUnicodeCheck="false" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:abapLanguageVersion="standard" adtcore:name="{DCLS_NAME}" adtcore:type="DCLS/DL" adtcore:changedAt="2026-10-20T13:21:01Z" adtcore:version="active" adtcore:createdAt="2026-10-20T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="Test access control" adtcore:language="EN" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:packageName="$TMP" adtcore:description="Local objects"/>
</dcl:dclSource>
'''

DCLS_SOURCE_CODE = f'''@EndUserText.label: 'Test access control'
@MappingRole: true
define role {DCLS_NAME} {{
  grant select on {DDLS_NAME}
    where ( object ) = aspect pfcg_auth( s_develop, objtype, actvt = '03' );
}}'''

DCLS_ABAPGIT_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DCLS" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DCLS>
    <DCLNAME>{DCLS_NAME}</DCLNAME>
    <DCLLANGUAGE>E</DCLLANGUAGE>
    <DDTEXT>Test access control</DDTEXT>
   </DCLS>
  </asx:values>
 </asx:abap>
</abapGit>
'''
