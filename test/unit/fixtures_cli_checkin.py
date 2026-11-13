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

TABL_POOL_XML = tabl_xml('    <TABCLASS>POOL</TABCLASS>',
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

DBTAB_NAME = 'ZSAPCLI_TNOMNT'

DBTAB_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TABL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD02V>
    <TABNAME>{DBTAB_NAME}</TABNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <TABCLASS>TRANSP</TABCLASS>
    <DDTEXT>TBAC Test - Uploaded criteria per solution to generate</DDTEXT>
    <CONTFLAG>A</CONTFLAG>
    <EXCLASS>1</EXCLASS>
   </DD02V>
   <DD09L>
    <TABNAME>{DBTAB_NAME}</TABNAME>
    <AS4LOCAL>A</AS4LOCAL>
    <TABKAT>0</TABKAT>
    <TABART>APPL1</TABART>
    <BUFALLOW>N</BUFALLOW>
   </DD09L>
   <DD03P_TABLE>
    <DD03P>
     <FIELDNAME>GEN_SOL_ID</FIELDNAME>
     <KEYFLAG>X</KEYFLAG>
     <ROLLNAME>ZZDE_SOLUTION_ID</ROLLNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <NOTNULL>X</NOTNULL>
     <COMPTYPE>E</COMPTYPE>
    </DD03P>
    <DD03P>
     <FIELDNAME>CRITERION</FIELDNAME>
     <KEYFLAG>X</KEYFLAG>
     <ROLLNAME>ZZDE_CRITERION</ROLLNAME>
     <ADMINFIELD>0</ADMINFIELD>
     <NOTNULL>X</NOTNULL>
     <COMPTYPE>E</COMPTYPE>
    </DD03P>
   </DD03P_TABLE>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DBTAB_SOURCE_CODE = f'''@EndUserText.label : 'TBAC Test - Uploaded criteria per solution to generate'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table {DBTAB_NAME.lower()} {{

  key gen_sol_id : zzde_solution_id not null;
  key criterion  : zzde_criterion not null;

}}'''

DBTAB_FULL_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TABL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD02V>
    <TABNAME>{DBTAB_NAME}</TABNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <TABCLASS>TRANSP</TABCLASS>
    <CLIDEP>X</CLIDEP>
    <LANGDEP>X</LANGDEP>
    <DDTEXT>Full table</DDTEXT>
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
     <DDTEXT>Test</DDTEXT>
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
     <SHLPORIGIN>T</SHLPORIGIN>
    </DD03P>
   </DD03P_TABLE>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DBTAB_FULL_SOURCE_CODE = f'''@EndUserText.label : 'Full table'
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

}}'''

DBTAB_GENERIC_XML = f'''<?xml version="1.0" encoding="utf-8"?>
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

DBTAB_GENERIC_SOURCE_CODE = f'''@EndUserText.label : 'No maintenance'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #L
@AbapCatalog.dataMaintenance : #NOT_ALLOWED
define table {DBTAB_NAME.lower()} {{

  key area : abap.char(4) not null;
  key name : abap.char(30) not null;
  value    : abap.string(0);

}}'''


def dbtab_settings_xml(data_class, size_category, allowed, buffering_type, area_key_fields, logging_enabled):
    """Returns the request of technical settings of the table DBTAB_NAME"""

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<ts:tableSettings xmlns:ts="http://www.sap.com/dictionary/table/settings" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="TABL/DTT" adtcore:description="No maintenance" adtcore:language="EN" adtcore:name="{DBTAB_NAME}" adtcore:version="active">
<ts:dataClassCategory>{data_class}</ts:dataClassCategory>
<ts:sizeCategory>{size_category}</ts:sizeCategory>
<ts:buffering>
<ts:allowed>{allowed}</ts:allowed>
<ts:type>{buffering_type}</ts:type>
<ts:areaKeyFields>{area_key_fields}</ts:areaKeyFields>
</ts:buffering>
<ts:storageType>C</ts:storageType>
<ts:sharingType></ts:sharingType>
<ts:loadUnit></ts:loadUnit>
<ts:loggingEnabled>{logging_enabled}</ts:loggingEnabled>
</ts:tableSettings>'''


DBTAB_SETTINGS_REQUEST_XML = dbtab_settings_xml('APPL1', '0', 'N', '', '0', 'false')

DBTAB_FULL_SETTINGS_REQUEST_XML = dbtab_settings_xml('APPL2', '1', 'X', 'X', '0', 'true')

DBTAB_GENERIC_SETTINGS_REQUEST_XML = dbtab_settings_xml('APPL0', '2', 'X', 'G', '1', 'false')

DBTAB_ADT_NEW_OBJECT_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="TABL/DT" adtcore:description="TBAC Test - Uploaded criteria per solution to generate" adtcore:language="EN" adtcore:name="{DBTAB_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER" adtcore:version="inactive">
<adtcore:packageRef adtcore:name="$TMP"/>
</blue:blueSource>'''

DBTAB_FOREIGN_KEYS_XML = DBTAB_XML.replace('''   </DD03P_TABLE>
''', '''   </DD03P_TABLE>
   <DD08V_TABLE>
    <DD08V>
     <FIELDNAME>CRITERION</FIELDNAME>
     <CHECKTABLE>ZSAPCLI_CHECK</CHECKTABLE>
    </DD08V>
   </DD08V_TABLE>
''')

DBTAB_KEY_INCLUDE_XML = DBTAB_XML.replace('''     <FIELDNAME>CRITERION</FIELDNAME>
     <KEYFLAG>X</KEYFLAG>
     <ROLLNAME>ZZDE_CRITERION</ROLLNAME>''', '''     <FIELDNAME>.INCLUDE</FIELDNAME>
     <KEYFLAG>X</KEYFLAG>
     <PRECFIELD>ZZS_CRITERIA</PRECFIELD>''')
