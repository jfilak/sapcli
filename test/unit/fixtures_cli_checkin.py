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

PACKAGE_DEVC_LANGUAGE_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DEVC" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DEVC>
    <CTEXT>Test Package</CTEXT>
    <LANGUAGE>E</LANGUAGE>
    <MASTERLANG>E</MASTERLANG>
    <PACKTYPE>H</PACKTYPE>
    <SRV_CHECK>X</SRV_CHECK>
   </DEVC>
  </asx:values>
 </asx:abap>
</abapGit>'''

PACKAGE_DEVC_UNKNOWN_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DEVC" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DEVC>
    <CTEXT>Test Package</CTEXT>
    <FUTURE_FIELD>X</FUTURE_FIELD>
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

DDLX_NAME = 'ZSAPCLI_DDLX'

DDLX_XML = f'''<?xml version="1.0" encoding="utf-8"?>
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

# abapGit reads ABAP_LANGU_VERSION of the workbench object metadata
DDLX_ABAP_LANGUAGE_VERSION_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DDLX" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DDLX>
    <METADATA>
     <NAME>{DDLX_NAME}</NAME>
     <DESCRIPTION>Test metadata extension</DESCRIPTION>
     <MASTER_LANGUAGE>EN</MASTER_LANGUAGE>
     <ABAP_LANGU_VERSION>5</ABAP_LANGU_VERSION>
    </METADATA>
   </DDLX>
  </asx:values>
 </asx:abap>
</abapGit>
'''

# abapGit writes the source code as it is - without the trailing new line
DDLX_SOURCE_CODE = f'''@Metadata.layer: #CORE
annotate entity {DDLS_NAME} with
{{
  @UI.lineItem: [{{ position: 10 }}]
  pgmid;
}}'''

DDLX_ADT_NEW_OBJECT_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<ddlx:ddlxSource xmlns:ddlx="http://www.sap.com/adt/ddic/ddlxsources" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DDLX/EX" adtcore:description="Test metadata extension" adtcore:language="EN" adtcore:name="{DDLX_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
</ddlx:ddlxSource>'''

DDLX_ADT_ALREADY_EXISTS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="com.sap.adt"/><type id="ExceptionResourceAlreadyExists"/><message lang="EN">Resource Metadata Extension {DDLX_NAME} does already exist.</message><localizedMessage lang="EN">Resource Metadata Extension {DDLX_NAME} does already exist.</localizedMessage><properties/></exc:exception>'''

BDEF_NAME = 'ZSAPCLI_BDEF'

# abapGit stores the workbench object metadata as returned by ADT
BDEF_XML = f'''<?xml version="1.0" encoding="utf-8"?>
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
      <HREF>./{BDEF_NAME.lower()}/source/main</HREF>
      <REL>http://www.sap.com/adt/relations/source</REL>
      <TYPE>text/plain</TYPE>
      <TITLE>Source Content</TITLE>
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

BDEF_SOURCE_CODE = f'''managed implementation in class zbp_sapcli_bdef unique;
strict ( 2 );

define behavior for {DDLS_NAME} alias Root
persistent table tadir
lock master
authorization master ( instance )
{{
  create;
  update;
  delete;
}}'''

BDEF_ADT_NEW_OBJECT_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="BDEF/BDO" adtcore:description="Test behavior definition" adtcore:language="EN" adtcore:name="{BDEF_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
</blue:blueSource>'''

BDEF_ADT_ALREADY_EXISTS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="com.sap.adt"/><type id="ExceptionResourceAlreadyExists"/><message lang="EN">Resource Behavior Definition {BDEF_NAME} does already exist.</message><localizedMessage lang="EN">Resource Behavior Definition {BDEF_NAME} does already exist.</localizedMessage><properties/></exc:exception>'''

TABL_NAME = 'ZSAPCLI_STRUCT'

# The same content as abapGit writes - including the fields COMPTYPE,
# SHLPORIGIN, and VALEXI which checkin does not need
TABL_XML = f'''<?xml version="1.0" encoding="utf-8"?>
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
     <SHLPORIGIN>D</SHLPORIGIN>
     <COMPTYPE>E</COMPTYPE>
    </DD03P>
    <DD03P>
     <FIELDNAME>IS_OFFLINE</FIELDNAME>
     <ROLLNAME>XFELD</ROLLNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <VALEXI>X</VALEXI>
     <SHLPORIGIN>F</SHLPORIGIN>
     <COMPTYPE>E</COMPTYPE>
    </DD03P>
    <DD03P>
     <FIELDNAME>CREATED_AT</FIELDNAME>
     <ROLLNAME>TIMESTAMPL</ROLLNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <COMPTYPE>E</COMPTYPE>
    </DD03P>
   </DD03P_TABLE>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TABL_SOURCE_CODE = f'''@EndUserText.label : 'Test structure'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
define structure {TABL_NAME.lower()} {{

  repo_key     : abap.char(12);
  abap_package : devclass;
  is_offline   : xfeld;
  created_at   : timestampl;

}}'''

TABL_ALL_FEATURES_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TABL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD02V>
    <TABNAME>{TABL_NAME}</TABNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <TABCLASS>INTTAB</TABCLASS>
    <DDTEXT>Developer's structure</DDTEXT>
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
     <COMPTYPE>E</COMPTYPE>
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
     <DDTEXT>Developer's note</DDTEXT>
    </DD03P>
   </DD03P_TABLE>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TABL_ALL_FEATURES_SOURCE_CODE = f'''@EndUserText.label : 'Developer''s structure'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
define structure {TABL_NAME.lower()} {{

  include zsapcli_incl;
  include zsapcli_incl with suffix _x;
  admin    : include zsapcli_admin;
  waers    : abap.cuky;
  @Semantics.amount.currencyCode : '{TABL_NAME.lower()}.waers'
  amount   : abap.curr(15,2);
  @Semantics.amount.currencyCode : '{TABL_NAME.lower()}.waers'
  wrbtr    : wrbtr;
  meins    : abap.unit(3);
  @Semantics.quantity.unitOfMeasure : '{TABL_NAME.lower()}.meins'
  quantity : abap.quan(13,3);
  counter  : abap.int4;
  @EndUserText.label : 'Developer''s note'
  note     : abap.string(0);

}}'''


def tabl_xml(dd02v_fields, dd03p_fields):
    """Returns abapGit XML of a structure with the given fields"""

    return f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TABL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD02V>
    <TABNAME>{TABL_NAME}</TABNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
{dd02v_fields}
    <DDTEXT>Test structure</DDTEXT>
    <MASTERLANG>E</MASTERLANG>
   </DD02V>
   <DD03P_TABLE>
    <DD03P>
{dd03p_fields}
     <ADMINFIELD>0</ADMINFIELD>
    </DD03P>
   </DD03P_TABLE>
  </asx:values>
 </asx:abap>
</abapGit>
'''


TABL_NO_EXCLASS_XML = tabl_xml('    <TABCLASS>INTTAB</TABCLASS>',
                               '     <FIELDNAME>REPO_KEY</FIELDNAME>\n     <ROLLNAME>DEVCLASS</ROLLNAME>')

TABL_NO_EXCLASS_SOURCE_CODE = f'''@EndUserText.label : 'Test structure'
define structure {TABL_NAME.lower()} {{

  repo_key : devclass;

}}'''

TABL_TRANSPARENT_XML = tabl_xml('    <TABCLASS>TRANSP</TABCLASS>',
                                '     <FIELDNAME>REPO_KEY</FIELDNAME>\n     <ROLLNAME>DEVCLASS</ROLLNAME>')

TABL_UNKNOWN_EXCLASS_XML = tabl_xml('    <TABCLASS>INTTAB</TABCLASS>\n    <EXCLASS>9</EXCLASS>',
                                    '     <FIELDNAME>REPO_KEY</FIELDNAME>\n     <ROLLNAME>DEVCLASS</ROLLNAME>')

TABL_REFERENCE_XML = tabl_xml('    <TABCLASS>INTTAB</TABCLASS>',
                              '     <FIELDNAME>OBJECT</FIELDNAME>\n     <ROLLNAME>CL_ABAP_TYPEDESCR</ROLLNAME>\n'
                              '     <COMPTYPE>R</COMPTYPE>\n     <REFTYPE>C</REFTYPE>')

TABL_UNKNOWN_DATATYPE_XML = tabl_xml('    <TABCLASS>INTTAB</TABCLASS>',
                                     '     <FIELDNAME>STAMP</FIELDNAME>\n     <DATATYPE>UTCL</DATATYPE>')

TABL_APPEND_XML = tabl_xml('    <TABCLASS>INTTAB</TABCLASS>',
                           '     <FIELDNAME>.APPEND</FIELDNAME>\n     <PRECFIELD>ZSAPCLI_APPEND</PRECFIELD>')

TABL_UNKNOWN_REFERENCE_XML = tabl_xml('    <TABCLASS>INTTAB</TABCLASS>',
                                      '     <FIELDNAME>WRBTR</FIELDNAME>\n     <ROLLNAME>WRBTR</ROLLNAME>\n'
                                      f'     <REFTABLE>{TABL_NAME}</REFTABLE>\n     <REFFIELD>WAERS</REFFIELD>')

TABL_FOREIGN_KEYS_XML = TABL_XML.replace('''   </DD03P_TABLE>
''', '''   </DD03P_TABLE>
   <DD08V_TABLE>
    <DD08V>
     <FIELDNAME>ABAP_PACKAGE</FIELDNAME>
     <CHECKTABLE>TDEVC</CHECKTABLE>
    </DD08V>
   </DD08V_TABLE>
''')

TABL_ADT_NEW_OBJECT_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="TABL/DS" adtcore:description="Test structure" adtcore:language="EN" adtcore:name="{TABL_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER" adtcore:version="inactive">
<adtcore:packageRef adtcore:name="$TMP"/>
</blue:blueSource>'''

TABL_ADT_ALREADY_EXISTS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="com.sap.adt"/><type id="ExceptionResourceAlreadyExists"/><message lang="EN">Resource Structure {TABL_NAME} does already exist.</message><localizedMessage lang="EN">Resource Structure {TABL_NAME} does already exist.</localizedMessage><properties/></exc:exception>'''

TABL_DELIMITED_GROUP_XML = tabl_xml('    <TABCLASS>INTTAB</TABCLASS>',
                                    '     <FIELDNAME>.INCLUDE</FIELDNAME>\n     <PRECFIELD>SYCH_BDL_DRAFT_ADMIN_INC</PRECFIELD>\n'
                                    '     <GROUPNAME>%ADMIN</GROUPNAME>')

TABL_DELIMITED_GROUP_SOURCE_CODE = f'''@EndUserText.label : 'Test structure'
define structure {TABL_NAME.lower()} {{

  "%admin" : include sych_bdl_draft_admin_inc;

}}'''

# The sample serialized by abapGit including the byte order mark
DOMA_XML = '''﻿<?xml version="1.0" encoding="utf-8"?>
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

DOMA_ALL_FIELDS_XML = '''<?xml version="1.0" encoding="utf-8"?>
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
    <DOMMASTER>E</DOMMASTER>
    <OUTPUTSTYLE>01</OUTPUTSTYLE>
    <AMPMFORMAT>X</AMPMFORMAT>
   </DD01V>
   <DD07V_TAB>
    <DD07V>
     <VALPOS>0007</VALPOS>
     <DDLANGUAGE>E</DDLANGUAGE>
     <DOMVALUE_L>A</DOMVALUE_L>
     <DDTEXT>Alpha</DDTEXT>
    </DD07V>
    <DD07V>
     <VALPOS>0009</VALPOS>
     <DDLANGUAGE>E</DDLANGUAGE>
     <DOMVALUE_L>B</DOMVALUE_L>
     <DOMVALUE_H>C</DOMVALUE_H>
     <DDTEXT>Range</DDTEXT>
    </DD07V>
   </DD07V_TAB>
   <DD01L_EXTRA>
    <ABAP_LANGUAGE_VERSION>X</ABAP_LANGUAGE_VERSION>
   </DD01L_EXTRA>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DOMA_TRANSLATIONS_XML = '''<?xml version="1.0" encoding="utf-8"?>
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
   <I18N_LANGS>
    <LANGU>D</LANGU>
   </I18N_LANGS>
  </asx:values>
 </asx:abap>
</abapGit>
'''


DTEL_XML = '''﻿<?xml version="1.0" encoding="utf-8"?>
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


DTEL_DOMAIN_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DTEL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD04V>
    <ROLLNAME>ZAGT_TEST_DTEL</ROLLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DOMNAME>ZABAPGIT_UNIT_TEST</DOMNAME>
    <MEMORYID>ZSAPCLI</MEMORYID>
    <LOGFLAG>X</LOGFLAG>
    <HEADLEN>30</HEADLEN>
    <SCRLEN1>08</SCRLEN1>
    <SCRLEN2>15</SCRLEN2>
    <SCRLEN3>25</SCRLEN3>
    <DDTEXT>Domain &amp; labels</DDTEXT>
    <REPTEXT>Heading</REPTEXT>
    <SCRTEXT_S>Short</SCRTEXT_S>
    <SCRTEXT_M>Medium</SCRTEXT_M>
    <SCRTEXT_L>Long</SCRTEXT_L>
    <DTELMASTER>E</DTELMASTER>
    <SHLPNAME>ZSAPCLI_SHLP</SHLPNAME>
    <SHLPFIELD>VALUE</SHLPFIELD>
    <DEFFDNAME>DOMAIN_VALUE</DEFFDNAME>
    <REFKIND>D</REFKIND>
    <LTRFLDDIS>X</LTRFLDDIS>
    <BIDICTRLC>X</BIDICTRLC>
    <NOHISTORY>X</NOHISTORY>
   </DD04V>
   <DD04L_EXTRA>
    <ABAP_LANGUAGE_VERSION>X</ABAP_LANGUAGE_VERSION>
   </DD04L_EXTRA>
  </asx:values>
 </asx:abap>
</abapGit>
'''


DTEL_TRANSLATIONS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DTEL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD04V>
    <ROLLNAME>ZAGT_TEST_DTEL</ROLLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DDTEXT>testing</DDTEXT>
    <DATATYPE>CHAR</DATATYPE>
    <LENG>000001</LENG>
   </DD04V>
   <I18N_LANGS>
    <LANGU>D</LANGU>
   </I18N_LANGS>
  </asx:values>
 </asx:abap>
</abapGit>
'''


DTEL_REFERENCE_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DTEL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD04V>
    <ROLLNAME>ZAGT_TEST_DTEL</ROLLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DOMNAME>CL_ABAP_TYPEDESCR</DOMNAME>
    <DDTEXT>testing</DDTEXT>
    <REFKIND>R</REFKIND>
    <REFTYPE>C</REFTYPE>
   </DD04V>
  </asx:values>
 </asx:abap>
</abapGit>
'''
