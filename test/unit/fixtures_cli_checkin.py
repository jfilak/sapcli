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

CLAS_WITH_DESCRIPTIONS_SUB_XML = '''<?xml version="1.0" encoding="utf-8"?>
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
   </VSEOCLASS>
   <DESCRIPTIONS_SUB>
    <SEOSUBCOTX>
     <CMPNAME>EXPAND_FUGR_TADIR_TO_FUNC</CMPNAME>
     <SCONAME>ZCX_ABAPGIT_EXCEPTION</SCONAME>
     <LANGU>E</LANGU>
     <DESCRIPT>abapGit - Exception</DESCRIPT>
    </SEOSUBCOTX>
   </DESCRIPTIONS_SUB>
  </asx:values>
 </asx:abap>
</abapGit>'''

CLAS_WITH_TPOOL_XML = '''<?xml version="1.0" encoding="utf-8"?>
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
   </VSEOCLASS>
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
   </TPOOL>
   <DESCRIPTIONS_SUB>
    <SEOSUBCOTX>
     <CMPNAME>EXPAND_FUGR_TADIR_TO_FUNC</CMPNAME>
     <SCONAME>ZCX_ABAPGIT_EXCEPTION</SCONAME>
     <LANGU>E</LANGU>
     <DESCRIPT>abapGit - Exception</DESCRIPT>
    </SEOSUBCOTX>
   </DESCRIPTIONS_SUB>
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

INTF_WITH_DESCRIPTIONS_SUB_XML = '''<?xml version="1.0" encoding="utf-8"?>
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
   <DESCRIPTIONS_SUB>
    <SEOSUBCOTX>
     <CMPNAME>GET_USED_OBJECTS</CMPNAME>
     <SCONAME>IV_OBJECT_NAME</SCONAME>
     <LANGU>E</LANGU>
     <DESCRIPT>Object Name</DESCRIPT>
    </SEOSUBCOTX>
   </DESCRIPTIONS_SUB>
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

TTYP_STANDARD_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <ROWTYPE>BAPIRET2</ROWTYPE>
    <ROWKIND>S</ROWKIND>
    <DATATYPE>STRU</DATATYPE>
    <ACCESSMODE>T</ACCESSMODE>
    <KEYDEF>D</KEYDEF>
    <KEYKIND>N</KEYKIND>
    <DDTEXT>Test table type</DDTEXT>
   </DD40V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_SORTED_XML = '''<?xml version="1.0" encoding="utf-8"?>
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
     <ROWTYPEPOS>0001</ROWTYPEPOS>
     <KEYFIELD>TYPE</KEYFIELD>
    </DD42V>
    <DD42V>
     <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
     <KEYFDPOS>0002</KEYFDPOS>
     <ROWTYPEPOS>0002</ROWTYPEPOS>
     <KEYFIELD>ID</KEYFIELD>
    </DD42V>
   </DD42V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_PREDEFINED_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DATATYPE>STRG</DATATYPE>
    <ACCESSMODE>T</ACCESSMODE>
    <KEYDEF>D</KEYDEF>
    <KEYKIND>N</KEYKIND>
    <DDTEXT>Test table type</DDTEXT>
    <TYPELEN>000008</TYPELEN>
   </DD40V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_SECONDARY_KEYS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <ROWTYPE>BAPIRET2</ROWTYPE>
    <ROWKIND>S</ROWKIND>
    <DATATYPE>STRU</DATATYPE>
    <ACCESSMODE>T</ACCESSMODE>
    <KEYDEF>D</KEYDEF>
    <KEYKIND>N</KEYKIND>
    <KEYFDCOUNT>0001</KEYFDCOUNT>
    <DDTEXT>Test table type</DDTEXT>
   </DD40V>
   <DD42V>
    <DD42V>
     <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
     <SECKEYNAME>BY_ID</SECKEYNAME>
     <KEYFDPOS>0001</KEYFDPOS>
     <ROWTYPEPOS>0002</ROWTYPEPOS>
     <KEYFIELD>ID</KEYFIELD>
    </DD42V>
   </DD42V>
   <DD43V>
    <DD43V>
     <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
     <SECKEYNAME>BY_ID</SECKEYNAME>
     <DDLANGUAGE>E</DDLANGUAGE>
     <ACCESSMODE>S</ACCESSMODE>
     <KIND>K</KIND>
     <KEYDESCRIPTION>Messages by ID</KEYDESCRIPTION>
    </DD43V>
   </DD43V>
   <DD40L_EXTRA>
    <ABAP_LANGUAGE_VERSION>X</ABAP_LANGUAGE_VERSION>
   </DD40L_EXTRA>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_RANGE_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <ROWTYPE>/AIF/NRT_MSGGUID_RANGE_S</ROWTYPE>
    <ROWKIND>S</ROWKIND>
    <DATATYPE>STRU</DATATYPE>
    <ACCESSMODE>T</ACCESSMODE>
    <KEYDEF>D</KEYDEF>
    <KEYKIND>N</KEYKIND>
    <DDTEXT>Range table for /aif/nrt_msgguid_e</DDTEXT>
    <TTYPKIND>R</TTYPKIND>
    <RANGE_CTYP>/AIF/NRT_MSGGUID_E</RANGE_CTYP>
    <CTDATATYPE>RAW</CTDATATYPE>
    <CTLENG>000016</CTLENG>
   </DD40V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DDLS_NAME = 'ZSAPCLI_CDS'

DDLS_XML = f'''<?xml version="1.0" encoding="utf-8"?>
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

# abapGit writes the fields only if they are not initial
DDLS_ALL_FIELDS_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DDLS" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DDLS>
    <DDLNAME>{DDLS_NAME}</DDLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DDTEXT>Test CDS view</DDTEXT>
    <PARENTNAME>ZSAPCLI_CDS_PARENT</PARENTNAME>
    <SOURCE_TYPE>W</SOURCE_TYPE>
    <SOURCE_ORIGIN>1</SOURCE_ORIGIN>
    <ABAP_LANGUAGE_VERSION>5</ABAP_LANGUAGE_VERSION>
   </DDLS>
  </asx:values>
 </asx:abap>
</abapGit>
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

DDLS_ADT_NEW_OBJECT_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<ddl:ddlSource xmlns:ddl="http://www.sap.com/adt/ddic/ddlsources" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DDLS/DF" adtcore:description="Test CDS view" adtcore:language="EN" adtcore:name="{DDLS_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
</ddl:ddlSource>'''

DDLS_ADT_ALREADY_EXISTS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="com.sap.adt"/><type id="ExceptionResourceAlreadyExists"/><message lang="EN">Resource Data Definition {DDLS_NAME} does already exist.</message><localizedMessage lang="EN">Resource Data Definition {DDLS_NAME} does already exist.</localizedMessage><properties/></exc:exception>'''

DCLS_NAME = 'ZSAPCLI_DCL'

DCLS_XML = f'''<?xml version="1.0" encoding="utf-8"?>
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

# abapGit writes ABAP_LANGUAGE_VERSION depending on the repository settings
DCLS_ABAP_LANGUAGE_VERSION_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DCLS" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DCLS>
    <DCLNAME>{DCLS_NAME}</DCLNAME>
    <DCLLANGUAGE>E</DCLLANGUAGE>
    <DDTEXT>Test access control</DDTEXT>
    <ABAP_LANGUAGE_VERSION>5</ABAP_LANGUAGE_VERSION>
   </DCLS>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DCLS_SOURCE_CODE = f'''@EndUserText.label: 'Test access control'
@MappingRole: true
define role {DCLS_NAME} {{
  grant select on {DDLS_NAME}
    where ( object ) = aspect pfcg_auth( s_develop, objtype, actvt = '03' );
}}
'''

DCLS_ADT_NEW_OBJECT_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<dcl:dclSource xmlns:dcl="http://www.sap.com/adt/acm/dclsources" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DCLS/DL" adtcore:description="Test access control" adtcore:language="EN" adtcore:name="{DCLS_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
</dcl:dclSource>'''

DCLS_ADT_ALREADY_EXISTS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="com.sap.adt"/><type id="ExceptionResourceAlreadyExists"/><message lang="EN">Resource Access Control {DCLS_NAME} does already exist.</message><localizedMessage lang="EN">Resource Access Control {DCLS_NAME} does already exist.</localizedMessage><properties/></exc:exception>'''
