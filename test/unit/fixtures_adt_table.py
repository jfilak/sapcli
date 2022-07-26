TABLE_NAME = 'TEST_TABLE'

TABLE_DEFINITION_ADT_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue"
 abapsource:sourceUri="./{TABLE_NAME.lower()}/source/main"
 abapsource:fixPointArithmetic="false"
 abapsource:activeUnicodeCheck="false"
 adtcore:responsible="DEVELOPER"
 adtcore:masterLanguage="EN"
 adtcore:masterSystem="UIA"
 adtcore:abapLanguageVersion="standard"
 adtcore:name="{TABLE_NAME}"
 adtcore:type="TABL/DT"
 adtcore:changedAt="2012-04-04T17:28:01Z"
 adtcore:version="active"
 adtcore:createdAt="2010-08-11T22:00:00Z"
 adtcore:changedBy="DEVELOPER"
 adtcore:createdBy="DEVELOPER"
 adtcore:description="Test table"
 adtcore:language="EN"
 xmlns:abapsource="http://www.sap.com/adt/abapsource"
 xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
   href="./{TABLE_NAME.lower()}/source/main/versions"
   rel="http://www.sap.com/adt/relations/versions"
   title="Historic versions"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
   href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Ftables%2F{TABLE_NAME.lower()}"
   rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions"
   type="application/vnd.sap.adt.nameditems.v1+xml"
   title="Allowed ABAP language versions"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
   href="./{TABLE_NAME.lower()}/source/main"
   rel="http://www.sap.com/adt/relations/source"
   type="text/plain"
   title="Source Content"
   etag="20120404172801001text/plain2"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
   href="./{TABLE_NAME.lower()}/source/main"
   rel="http://www.sap.com/adt/relations/source"
   type="text/html" title="Source Content (HTML)" etag=""/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
   href="/sap/bc/adt/vit/wb/object_type/tabldt/object_name/{TABLE_NAME}"
   rel="self"
   type="application/vnd.sap.sapgui"
   title="Representation in SAP Gui"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
   href="/sap/bc/adt/ddic/db/settings/{TABLE_NAME.lower()}"
   rel="http://www.sap.com/adt/relations/technicalsettings"
   type="application/vnd.sap.adt.table.settings.v2+xml"
   title="Technical Settings"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
   href="/sap/bc/adt/vit/docu/object_type/tb/object_name/{TABLE_NAME.lower()}?masterLanguage=D&amp;mode=edit"
   rel="http://www.sap.com/adt/relations/documentation"
   type="application/vnd.sap.sapgui"
   title="Documentation"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
   href="/sap/bc/adt/vit/wb/object_type/tabldt/object_name/{TABLE_NAME}#view=INDX"
   rel="http://www.sap.com/adt/relations/indexes"
   type="application/vnd.sap.sapgui"
   title="Index Overview"/>
  <adtcore:packageRef
   adtcore:uri="/sap/bc/adt/packages/sadt_compatibility"
   adtcore:type="DEVC/K"
   adtcore:name="SADT_COMPATIBILITY"
   adtcore:description="ADT Central compatibility resource"/>
</blue:blueSource>'''

CREATE_TABLE_ADT_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="TABL/DT" adtcore:description="Test table" adtcore:language="EN" adtcore:name="{TABLE_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="ANZEIGER" adtcore:version="inactive">
<adtcore:packageRef adtcore:name="PACKAGE"/>
</blue:blueSource>'''

READ_TABLE_BODY = '''@EndUserText.label : 'SQSC Index Table for Repository Information System'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #L
@AbapCatalog.dataMaintenance : #RESTRICTED
define table sqsc_ris_index {

  key include wbobjtype not null;
  key object_key : seu_objkey not null;
  key proxy_name : sqlscprocname not null;
  key version    : r3state not null;

}'''

WRITE_TABLE_BODY = '''@EndUserText.label : 'test'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zjf_test {

  key client : abap.clnt;
  foo : abap.clnt;
}'''

FAKE_LOCK_HANDLE = 'lock_handle'

ACTIVATE_TABLE_BODY = f'''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/ddic/tables/{TABLE_NAME.lower()}" adtcore:name="{TABLE_NAME}"/>
</adtcore:objectReferences>'''
