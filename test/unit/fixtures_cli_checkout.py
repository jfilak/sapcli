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
