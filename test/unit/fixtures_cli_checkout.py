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

DDLX_NAME = 'ZSAPCLI_DDLX'

DDLX_ADT_GET_RESPONSE_XML = f'''<?xml version="1.0" encoding="UTF-8"?><ddlx:ddlxSource xmlns:ddlx="http://www.sap.com/adt/ddic/ddlxsources" abapsource:sourceUri="./{DDLX_NAME.lower()}/source/main" abapsource:fixPointArithmetic="false" abapsource:activeUnicodeCheck="false" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:abapLanguageVersion="standard" adtcore:name="{DDLX_NAME}" adtcore:type="DDLX/EX" adtcore:changedAt="2026-10-20T21:33:07Z" adtcore:version="active" adtcore:createdAt="2026-10-20T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="Test metadata extension" adtcore:language="EN" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:packageName="$TMP" adtcore:description="Local objects"/>
</ddlx:ddlxSource>'''

DDLX_SOURCE_CODE = f'''@Metadata.layer: #CORE
annotate entity {DDLS_NAME} with
{{
  @UI.lineItem: [{{ position: 10 }}]
  pgmid;
}}'''

DDLX_ABAPGIT_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DDLX" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DDLX>
    <METADATA>
     <NAME>{DDLX_NAME}</NAME>
     <DESCRIPTION>Test metadata extension</DESCRIPTION>
     <MASTER_LANGUAGE>EN</MASTER_LANGUAGE>
    </METADATA>
   </DDLX>
  </asx:values>
 </asx:abap>
</abapGit>
'''

BDEF_NAME = 'ZSAPCLI_BDEF'

# The file zroot_cds.bdef.xml of the repository abapGit-tests/BDEF with replaced name and description
BDEF_ABAPGIT_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_BDEF" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <BDEF>
    <NAME>{BDEF_NAME}</NAME>
    <TYPE>BDEF/BDO</TYPE>
    <DESCRIPTION>Test behavior definition</DESCRIPTION>
    <DESCRIPTION_TEXT_LIMIT>60</DESCRIPTION_TEXT_LIMIT>
    <LANGUAGE>EN</LANGUAGE>
    <LINKS>
     <item>
      <HREF>./{BDEF_NAME.lower()}/source/main/versions</HREF>
      <REL>http://www.sap.com/adt/relations/versions</REL>
      <TITLE>Historic versions</TITLE>
     </item>
     <item>
      <HREF>/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fbo%2Fbehaviordefinitions%2F{BDEF_NAME.lower()}</HREF>
      <REL>http://www.sap.com/adt/relations/informationsystem/abaplanguageversions</REL>
      <TYPE>application/vnd.sap.adt.nameditems.v1+xml</TYPE>
      <TITLE>Allowed ABAP language versions</TITLE>
     </item>
     <item>
      <HREF>./{BDEF_NAME.lower()}/source/main</HREF>
      <REL>http://www.sap.com/adt/relations/source</REL>
      <TYPE>text/plain</TYPE>
      <TITLE>Source Content</TITLE>
     </item>
     <item>
      <HREF>./{BDEF_NAME.lower()}/source/main</HREF>
      <REL>http://www.sap.com/adt/relations/source</REL>
      <TYPE>text/html</TYPE>
      <TITLE>Source Content (HTML)</TITLE>
     </item>
    </LINKS>
    <MASTER_LANGUAGE>EN</MASTER_LANGUAGE>
    <ABAP_LANGU_VERSION>X</ABAP_LANGU_VERSION>
    <SOURCE_URI>./{BDEF_NAME.lower()}/source/main</SOURCE_URI>
    <SOURCE_TYPE>ABAP_SOURCE</SOURCE_TYPE>
    <SOURCE_FIXED_POINT_ARITHMETIC>true</SOURCE_FIXED_POINT_ARITHMETIC>
    <SOURCE_UNICODE_CHECKS_ACTIVE>true</SOURCE_UNICODE_CHECKS_ACTIVE>
   </BDEF>
  </asx:values>
 </asx:abap>
</abapGit>
'''

BDEF_SOURCE_CODE = '''managed implementation in class zbp_sapcli_bdef unique;
strict ( 2 );

define behavior for ZSAPCLI_CDS alias Root
persistent table tadir
lock master
authorization master ( instance )
{
  create;
  update;
  delete;
}'''

TABL_NAME = 'ZSAPCLI_STRUCT'

TABL_ADT_GET_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue" abapsource:sourceUri="./{TABL_NAME.lower()}/source/main" abapsource:fixPointArithmetic="false" abapsource:activeUnicodeCheck="false" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:abapLanguageVersion="standard" adtcore:name="{TABL_NAME}" adtcore:type="TABL/DS" adtcore:changedAt="2026-10-21T11:38:40Z" adtcore:version="active" adtcore:createdAt="2026-10-21T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="Test structure" adtcore:language="EN" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link href="./{TABL_NAME.lower()}/source/main" rel="http://www.sap.com/adt/relations/source" type="text/plain" title="Source Content" etag="20261021113840001text/plain2" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:description="Local objects"/>
</blue:blueSource>'''

TABL_SOURCE_CODE = f'''@EndUserText.label : 'Test structure'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
define structure {TABL_NAME.lower()} {{

  repo_key     : abap.char(12);
  abap_package : devclass;
  is_offline   : xfeld;
  created_at   : timestampl;

}}'''

TABL_ABAPGIT_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TABL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD02V>
    <TABNAME>{TABL_NAME}</TABNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <TABCLASS>INTTAB</TABCLASS>
    <DDTEXT>Test structure</DDTEXT>
    <MASTERLANG>E</MASTERLANG>
    <EXCLASS>1</EXCLASS>
   </DD02V>
   <DD03P_TABLE>
    <DD03P>
     <FIELDNAME>REPO_KEY</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>C</INTTYPE>
     <INTLEN>000024</INTLEN>
     <DATATYPE>CHAR</DATATYPE>
     <LENG>000012</LENG>
     <MASK>  CHAR</MASK>
    </DD03P>
    <DD03P>
     <FIELDNAME>ABAP_PACKAGE</FIELDNAME>
     <ROLLNAME>DEVCLASS</ROLLNAME>
     <ADMINFIELD>0</ADMINFIELD>
    </DD03P>
    <DD03P>
     <FIELDNAME>IS_OFFLINE</FIELDNAME>
     <ROLLNAME>XFELD</ROLLNAME>
     <ADMINFIELD>0</ADMINFIELD>
    </DD03P>
    <DD03P>
     <FIELDNAME>CREATED_AT</FIELDNAME>
     <ROLLNAME>TIMESTAMPL</ROLLNAME>
     <ADMINFIELD>0</ADMINFIELD>
    </DD03P>
   </DD03P_TABLE>
  </asx:values>
 </asx:abap>
</abapGit>
'''

# Formatted differently than sapcli formats the source code on checkin and
# with comments to make sure checkout does not depend on the format
TABL_ALL_FEATURES_SOURCE_CODE = f'''@EndUserText.label:'Developer''s structure'
@AbapCatalog.enhancement.category: #EXTENSIBLE_ANY
// the structure for tests
define structure {TABL_NAME.lower()}
{{
  include zsapcli_incl;
  include zsapcli_incl with suffix _x;
  admin : include zsapcli_admin;
  /* currency
     key */
  waers : abap.cuky;
  @Semantics.amount.currencyCode : '{TABL_NAME.lower()}.waers'
  amount : abap.curr( 15, 2 );
  @Semantics.amount.currencyCode : '{TABL_NAME.lower()}.waers'
  wrbtr : wrbtr;
  meins : abap.unit(3); -- unit of measure
  @Semantics.quantity.unitOfMeasure : '{TABL_NAME.lower()}.meins'
  quantity : abap.quan(13,3);
  counter : abap.int4;
  @EndUserText.label : 'Developer''s note'
  note : abap.string(0);
  "/sapcli/flag" : abap.char(1);
}}
'''

TABL_ALL_FEATURES_ABAPGIT_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TABL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD02V>
    <TABNAME>{TABL_NAME}</TABNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <TABCLASS>INTTAB</TABCLASS>
    <DDTEXT>Test structure</DDTEXT>
    <MASTERLANG>E</MASTERLANG>
    <EXCLASS>4</EXCLASS>
   </DD02V>
   <DD03P_TABLE>
    <DD03P>
     <FIELDNAME>.INCLUDE</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <PRECFIELD>ZSAPCLI_INCL</PRECFIELD>
     <MASK>      S</MASK>
     <COMPTYPE>S</COMPTYPE>
    </DD03P>
    <DD03P>
     <FIELDNAME>.INCLU-_X</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <PRECFIELD>ZSAPCLI_INCL</PRECFIELD>
     <MASK>      S</MASK>
     <COMPTYPE>S</COMPTYPE>
    </DD03P>
    <DD03P>
     <FIELDNAME>.INCLUDE</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <PRECFIELD>ZSAPCLI_ADMIN</PRECFIELD>
     <MASK>      S</MASK>
     <COMPTYPE>S</COMPTYPE>
     <GROUPNAME>ADMIN</GROUPNAME>
    </DD03P>
    <DD03P>
     <FIELDNAME>WAERS</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>C</INTTYPE>
     <INTLEN>000010</INTLEN>
     <DATATYPE>CUKY</DATATYPE>
     <LENG>000005</LENG>
     <MASK>  CUKY</MASK>
    </DD03P>
    <DD03P>
     <FIELDNAME>AMOUNT</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>P</INTTYPE>
     <INTLEN>000008</INTLEN>
     <REFTABLE>{TABL_NAME}</REFTABLE>
     <REFFIELD>WAERS</REFFIELD>
     <DATATYPE>CURR</DATATYPE>
     <LENG>000015</LENG>
     <DECIMALS>000002</DECIMALS>
     <MASK>  CURR</MASK>
    </DD03P>
    <DD03P>
     <FIELDNAME>WRBTR</FIELDNAME>
     <ROLLNAME>WRBTR</ROLLNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <REFTABLE>{TABL_NAME}</REFTABLE>
     <REFFIELD>WAERS</REFFIELD>
    </DD03P>
    <DD03P>
     <FIELDNAME>MEINS</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>C</INTTYPE>
     <INTLEN>000006</INTLEN>
     <DATATYPE>UNIT</DATATYPE>
     <LENG>000003</LENG>
     <MASK>  UNIT</MASK>
    </DD03P>
    <DD03P>
     <FIELDNAME>QUANTITY</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>P</INTTYPE>
     <INTLEN>000007</INTLEN>
     <REFTABLE>{TABL_NAME}</REFTABLE>
     <REFFIELD>MEINS</REFFIELD>
     <DATATYPE>QUAN</DATATYPE>
     <LENG>000013</LENG>
     <DECIMALS>000003</DECIMALS>
     <MASK>  QUAN</MASK>
    </DD03P>
    <DD03P>
     <FIELDNAME>COUNTER</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>X</INTTYPE>
     <INTLEN>000004</INTLEN>
     <DATATYPE>INT4</DATATYPE>
     <LENG>000010</LENG>
     <MASK>  INT4</MASK>
    </DD03P>
    <DD03P>
     <FIELDNAME>NOTE</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>g</INTTYPE>
     <INTLEN>000008</INTLEN>
     <DATATYPE>STRG</DATATYPE>
     <MASK>  STRG</MASK>
     <DDTEXT>Developer&apos;s note</DDTEXT>
    </DD03P>
    <DD03P>
     <FIELDNAME>/SAPCLI/FLAG</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>C</INTTYPE>
     <INTLEN>000002</INTLEN>
     <DATATYPE>CHAR</DATATYPE>
     <LENG>000001</LENG>
     <MASK>  CHAR</MASK>
    </DD03P>
   </DD03P_TABLE>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DOMA_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DOMA" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD01V>
    <DOMNAME>ZABAPGIT_UNIT_TEST</DOMNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DATATYPE>CHAR</DATATYPE>
    <LENG>000010</LENG>
    <OUTPUTLEN>000010</OUTPUTLEN>
    <DDTEXT>Testing</DDTEXT>
   </DD01V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DOMA_ALL_FIELDS_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DOMA" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD01V>
    <DOMNAME>ZABAPGIT_UNIT_TEST</DOMNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DATATYPE>DEC</DATATYPE>
    <LENG>000011</LENG>
    <OUTPUTLEN>000015</OUTPUTLEN>
    <DECIMALS>000002</DECIMALS>
    <LOWERCASE>X</LOWERCASE>
    <SIGNFLAG>X</SIGNFLAG>
    <VALEXI>X</VALEXI>
    <ENTITYTAB>T000</ENTITYTAB>
    <CONVEXIT>ALPHA</CONVEXIT>
    <DDTEXT>All fields</DDTEXT>
    <OUTPUTSTYLE>01</OUTPUTSTYLE>
    <AMPMFORMAT>X</AMPMFORMAT>
   </DD01V>
   <DD07V_TAB>
    <DD07V>
     <VALPOS>0001</VALPOS>
     <DDLANGUAGE>E</DDLANGUAGE>
     <DOMVALUE_L>A</DOMVALUE_L>
     <DDTEXT>Alpha</DDTEXT>
    </DD07V>
    <DD07V>
     <VALPOS>0002</VALPOS>
     <DDLANGUAGE>E</DDLANGUAGE>
     <DOMVALUE_L>B</DOMVALUE_L>
     <DOMVALUE_H>C</DOMVALUE_H>
     <DDTEXT>Range</DDTEXT>
    </DD07V>
   </DD07V_TAB>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DOMA_RAWSTRING_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DOMA" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD01V>
    <DOMNAME>ZABAPGIT_UNIT_TEST</DOMNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DATATYPE>RSTR</DATATYPE>
    <DDTEXT>Raw string</DDTEXT>
   </DD01V>
  </asx:values>
 </asx:abap>
</abapGit>
'''


DTEL_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DTEL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD04V>
    <ROLLNAME>ZAGT_TEST_DTEL</ROLLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <HEADLEN>55</HEADLEN>
    <SCRLEN1>10</SCRLEN1>
    <SCRLEN2>20</SCRLEN2>
    <SCRLEN3>40</SCRLEN3>
    <DDTEXT>testing</DDTEXT>
    <REPTEXT>testing</REPTEXT>
    <SCRTEXT_S>testing</SCRTEXT_S>
    <SCRTEXT_M>testing</SCRTEXT_M>
    <SCRTEXT_L>testing</SCRTEXT_L>
    <DTELMASTER>E</DTELMASTER>
    <DATATYPE>CHAR</DATATYPE>
    <LENG>000001</LENG>
    <OUTPUTLEN>000001</OUTPUTLEN>
   </DD04V>
  </asx:values>
 </asx:abap>
</abapGit>
'''


DTEL_DOMAIN_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DTEL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD04V>
    <ROLLNAME>ZAGT_TEST_DTEL</ROLLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DOMNAME>SPRAS</DOMNAME>
    <MEMORYID>SPR</MEMORYID>
    <LOGFLAG>X</LOGFLAG>
    <HEADLEN>30</HEADLEN>
    <SCRLEN1>08</SCRLEN1>
    <SCRLEN2>15</SCRLEN2>
    <SCRLEN3>25</SCRLEN3>
    <DDTEXT>A &amp; B &lt;C&gt; &apos;D&apos; &quot;E&quot;</DDTEXT>
    <REPTEXT>Heading</REPTEXT>
    <SCRTEXT_S>Short</SCRTEXT_S>
    <SCRTEXT_M>Medium</SCRTEXT_M>
    <SCRTEXT_L>Long</SCRTEXT_L>
    <DTELMASTER>E</DTELMASTER>
    <SHLPNAME>H_T002</SHLPNAME>
    <SHLPFIELD>SPRAS</SHLPFIELD>
    <DEFFDNAME>DOMAIN_VALUE</DEFFDNAME>
    <REFKIND>D</REFKIND>
    <NOHISTORY>X</NOHISTORY>
   </DD04V>
  </asx:values>
 </asx:abap>
</abapGit>
'''


DTEL_STRING_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DTEL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD04V>
    <ROLLNAME>ZAGT_TEST_DTEL</ROLLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <HEADLEN>55</HEADLEN>
    <SCRLEN1>10</SCRLEN1>
    <SCRLEN2>20</SCRLEN2>
    <SCRLEN3>40</SCRLEN3>
    <DDTEXT>String</DDTEXT>
    <REPTEXT>String</REPTEXT>
    <SCRTEXT_S>String</SCRTEXT_S>
    <SCRTEXT_M>String</SCRTEXT_M>
    <SCRTEXT_L>String</SCRTEXT_L>
    <DTELMASTER>E</DTELMASTER>
    <DATATYPE>STRG</DATATYPE>
    <LTRFLDDIS>X</LTRFLDDIS>
    <BIDICTRLC>X</BIDICTRLC>
   </DD04V>
  </asx:values>
 </asx:abap>
</abapGit>
'''


DBTAB_NAME = 'ZSAPCLI_TNOMNT'

DBTAB_ADT_GET_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><blue:blueSource abapsource:sourceUri="./{DBTAB_NAME.lower()}/source/main" abapsource:fixPointArithmetic="false" abapsource:activeUnicodeCheck="false" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:abapLanguageVersion="standard" adtcore:name="{DBTAB_NAME}" adtcore:type="TABL/DT" adtcore:changedAt="2026-11-03T18:12:10Z" adtcore:version="active" adtcore:createdAt="2026-11-03T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="No maintenance" adtcore:language="EN" xmlns:blue="http://www.sap.com/wbobj/blue" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:adtcore="http://www.sap.com/adt/core"><atom:link href="./{DBTAB_NAME.lower()}/source/main/versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Ftables%2F{DBTAB_NAME.lower()}" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" type="application/vnd.sap.adt.nameditems.v1+xml" title="Allowed ABAP language versions" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="./{DBTAB_NAME.lower()}/source/main" rel="http://www.sap.com/adt/relations/source" type="text/plain" title="Source Content" etag="20261103181210001text/plain2" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="./{DBTAB_NAME.lower()}/source/main" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Source Content (HTML)" etag="" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/vit/wb/object_type/tabldt/object_name/{DBTAB_NAME}" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP Gui" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/ddic/db/settings/{DBTAB_NAME.lower()}" rel="http://www.sap.com/adt/relations/technicalsettings" type="application/vnd.sap.adt.table.settings.v2+xml" title="Technical Settings" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/vit/docu/object_type/tb/object_name/{DBTAB_NAME.lower()}?masterLanguage=E&amp;mode=edit" rel="http://www.sap.com/adt/relations/documentation" type="application/vnd.sap.sapgui" title="Documentation" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/vit/wb/object_type/tabldt/object_name/{DBTAB_NAME}#view=INDX" rel="http://www.sap.com/adt/relations/indexes" type="application/vnd.sap.sapgui" title="Index Overview" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/ddic/logs/db/ACTTABL{DBTAB_NAME}" rel="http://www.sap.com/adt/relations/ddic/activationlog" type="application/vnd.sap.adt.logs+xml" title="Activation Log" xmlns:atom="http://www.w3.org/2005/Atom"/><adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24sapcli_tabl" adtcore:type="DEVC/K" adtcore:name="$SAPCLI_TABL" adtcore:description="sapcli tables"/></blue:blueSource>'''

DBTAB_GENERIC_SOURCE_CODE = f'''@EndUserText.label : 'No maintenance'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #L
@AbapCatalog.dataMaintenance : #NOT_ALLOWED
define table {DBTAB_NAME.lower()} {{

  key area : abap.char(4) not null;
  key name : abap.char(30) not null;
  value    : abap.string(0);

}}
'''

DBTAB_GENERIC_ABAPGIT_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TABL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD02V>
    <TABNAME>{DBTAB_NAME}</TABNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <TABCLASS>TRANSP</TABCLASS>
    <DDTEXT>No maintenance</DDTEXT>
    <MASTERLANG>E</MASTERLANG>
    <MAINFLAG>N</MAINFLAG>
    <CONTFLAG>L</CONTFLAG>
    <EXCLASS>4</EXCLASS>
   </DD02V>
   <DD09L>
    <TABNAME>{DBTAB_NAME}</TABNAME>
    <AS4LOCAL>A</AS4LOCAL>
    <TABKAT>2</TABKAT>
    <TABART>APPL0</TABART>
    <PUFFERUNG>G</PUFFERUNG>
    <SCHFELDANZ>001</SCHFELDANZ>
    <BUFALLOW>X</BUFALLOW>
   </DD09L>
   <DD03P_TABLE>
    <DD03P>
     <FIELDNAME>AREA</FIELDNAME>
     <KEYFLAG>X</KEYFLAG>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>C</INTTYPE>
     <INTLEN>000008</INTLEN>
     <NOTNULL>X</NOTNULL>
     <DATATYPE>CHAR</DATATYPE>
     <LENG>000004</LENG>
     <MASK>  CHAR</MASK>
    </DD03P>
    <DD03P>
     <FIELDNAME>NAME</FIELDNAME>
     <KEYFLAG>X</KEYFLAG>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>C</INTTYPE>
     <INTLEN>000060</INTLEN>
     <NOTNULL>X</NOTNULL>
     <DATATYPE>CHAR</DATATYPE>
     <LENG>000030</LENG>
     <MASK>  CHAR</MASK>
    </DD03P>
    <DD03P>
     <FIELDNAME>VALUE</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>g</INTTYPE>
     <INTLEN>000008</INTLEN>
     <DATATYPE>STRG</DATATYPE>
     <MASK>  STRG</MASK>
    </DD03P>
   </DD03P_TABLE>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DBTAB_FULL_SOURCE_CODE = f'''@EndUserText.label : 'No maintenance'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #C
@AbapCatalog.dataMaintenance : #ALLOWED
define table {DBTAB_NAME.lower()} {{

  key client  : mandt not null;
  key id      : abap.numc(10) not null;
  @EndUserText.label : 'Amount'
  @Semantics.amount.currencyCode : '{DBTAB_NAME.lower()}.currency'
  amount      : abap.curr(15,2);
  currency    : abap.cuky;
  description : abap.char(40);
  include zzs_criteria;
  created_at  : abap.dats;

}}
'''

DBTAB_FULL_SETTINGS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><ts:tableSettings adtcore:name="{DBTAB_NAME}" adtcore:type="TABL/DTT" adtcore:changedAt="2026-11-03T18:12:00Z" adtcore:version="active" adtcore:createdAt="2026-11-03T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="No maintenance" adtcore:descriptionTextLimit="-1" adtcore:language="EN" xmlns:ts="http://www.sap.com/dictionary/table/settings" xmlns:adtcore="http://www.sap.com/adt/core"><adtcore:containerRef adtcore:uri="/sap/bc/adt/ddic/tables/{DBTAB_NAME.lower()}" adtcore:type="TABL/DT" adtcore:name="{DBTAB_NAME}"/><atom:link href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/vit/wb/object_type/tabldtt/object_name/{DBTAB_NAME}" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP Gui" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/ddic/logs/db/ACTTABT{DBTAB_NAME}" rel="http://www.sap.com/adt/relations/ddic/activationlog" type="application/vnd.sap.adt.logs+xml" title="Activation Log" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/classifications?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Ftables%2F{DBTAB_NAME.lower()}" rel="tableLoggingClassifications" type="application/vnd.sap.adt.classifications+xml" title="Table Logging Assessment Classifications" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="./{DBTAB_NAME.lower()}" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Landing Page (HTML)" xmlns:atom="http://www.w3.org/2005/Atom"/><ts:dataClassCategory>APPL2</ts:dataClassCategory><ts:sizeCategory>1</ts:sizeCategory><ts:buffering><ts:allowed>X</ts:allowed><ts:type>X</ts:type><ts:areaKeyFields>0</ts:areaKeyFields></ts:buffering><ts:storageType>C</ts:storageType><ts:sharingType/><ts:loadUnit/><ts:translation ts:value="" ts:isVisible="false" ts:isEditable="false" ts:granularity="2"/><ts:loggingEnabled>true</ts:loggingEnabled><ts:supportsLoggingAssessment>true</ts:supportsLoggingAssessment></ts:tableSettings>'''

DBTAB_FULL_ABAPGIT_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TABL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD02V>
    <TABNAME>{DBTAB_NAME}</TABNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <TABCLASS>TRANSP</TABCLASS>
    <DDTEXT>No maintenance</DDTEXT>
    <MASTERLANG>E</MASTERLANG>
    <MAINFLAG>X</MAINFLAG>
    <CONTFLAG>C</CONTFLAG>
    <EXCLASS>1</EXCLASS>
   </DD02V>
   <DD09L>
    <TABNAME>{DBTAB_NAME}</TABNAME>
    <AS4LOCAL>A</AS4LOCAL>
    <TABKAT>1</TABKAT>
    <TABART>APPL2</TABART>
    <PUFFERUNG>X</PUFFERUNG>
    <PROTOKOLL>X</PROTOKOLL>
    <BUFALLOW>X</BUFALLOW>
   </DD09L>
   <DD03P_TABLE>
    <DD03P>
     <FIELDNAME>CLIENT</FIELDNAME>
     <KEYFLAG>X</KEYFLAG>
     <ROLLNAME>MANDT</ROLLNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <NOTNULL>X</NOTNULL>
     <COMPTYPE>E</COMPTYPE>
    </DD03P>
    <DD03P>
     <FIELDNAME>ID</FIELDNAME>
     <KEYFLAG>X</KEYFLAG>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>N</INTTYPE>
     <INTLEN>000020</INTLEN>
     <NOTNULL>X</NOTNULL>
     <DATATYPE>NUMC</DATATYPE>
     <LENG>000010</LENG>
     <MASK>  NUMC</MASK>
    </DD03P>
    <DD03P>
     <FIELDNAME>AMOUNT</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>P</INTTYPE>
     <INTLEN>000008</INTLEN>
     <REFTABLE>{DBTAB_NAME}</REFTABLE>
     <REFFIELD>CURRENCY</REFFIELD>
     <DATATYPE>CURR</DATATYPE>
     <LENG>000015</LENG>
     <DECIMALS>000002</DECIMALS>
     <MASK>  CURR</MASK>
     <DDTEXT>Amount</DDTEXT>
    </DD03P>
    <DD03P>
     <FIELDNAME>CURRENCY</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>C</INTTYPE>
     <INTLEN>000010</INTLEN>
     <DATATYPE>CUKY</DATATYPE>
     <LENG>000005</LENG>
     <MASK>  CUKY</MASK>
    </DD03P>
    <DD03P>
     <FIELDNAME>DESCRIPTION</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>C</INTTYPE>
     <INTLEN>000080</INTLEN>
     <DATATYPE>CHAR</DATATYPE>
     <LENG>000040</LENG>
     <MASK>  CHAR</MASK>
    </DD03P>
    <DD03P>
     <FIELDNAME>.INCLUDE</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <PRECFIELD>ZZS_CRITERIA</PRECFIELD>
     <MASK>      S</MASK>
     <COMPTYPE>S</COMPTYPE>
    </DD03P>
    <DD03P>
     <FIELDNAME>CREATED_AT</FIELDNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <INTTYPE>D</INTTYPE>
     <INTLEN>000016</INTLEN>
     <DATATYPE>DATS</DATATYPE>
     <LENG>000008</LENG>
     <MASK>  DATS</MASK>
    </DD03P>
   </DD03P_TABLE>
  </asx:values>
 </asx:abap>
</abapGit>
'''
