STRUCTURE_NAME = 'TEST_STRUCTURE'

STRUCTURE_DEFINITION_ADT_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue"
  abapsource:sourceUri="./{STRUCTURE_NAME.lower()}/source/main"
  abapsource:fixPointArithmetic="false"
  abapsource:activeUnicodeCheck="false"
  adtcore:responsible="DEVELOPER"
  adtcore:masterLanguage="EN"
  adtcore:masterSystem="C50"
  adtcore:abapLanguageVersion="standard"
  adtcore:name="{STRUCTURE_NAME}"
  adtcore:type="TABL/DS"
  adtcore:changedAt="2023-09-11T11:38:40Z"
  adtcore:version="active"
  adtcore:createdAt="2023-09-11T00:00:00Z"
  adtcore:changedBy="DEVELOPER"
  adtcore:createdBy="DEVELOPER"
  adtcore:description="Test structure"
  adtcore:language="EN"
  xmlns:abapsource="http://www.sap.com/adt/abapsource"
  xmlns:adtcore="http://www.sap.com/adt/core">
    <atom:link href="./{STRUCTURE_NAME.lower()}/source/main/versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions" xmlns:atom="http://www.w3.org/2005/Atom"/>
    <atom:link href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Fstructures%2F{STRUCTURE_NAME.lower()}" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" type="application/vnd.sap.adt.nameditems.v1+xml" title="Allowed ABAP language versions" xmlns:atom="http://www.w3.org/2005/Atom"/>
    <atom:link href="./{STRUCTURE_NAME.lower()}/source/main" rel="http://www.sap.com/adt/relations/source" type="text/plain" title="Source Content" etag="20230911113840001text/plain2" xmlns:atom="http://www.w3.org/2005/Atom"/>
    <atom:link href="./{STRUCTURE_NAME.lower()}/source/main" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Source Content (HTML)" etag="" xmlns:atom="http://www.w3.org/2005/Atom"/>
    <atom:link href="/sap/bc/adt/vit/wb/object_type/tablds/object_name/{STRUCTURE_NAME}" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP Gui" xmlns:atom="http://www.w3.org/2005/Atom"/>
    <atom:link href="/sap/bc/adt/vit/docu/object_type/tb/object_name/{STRUCTURE_NAME.lower()}?masterLanguage=E&amp;mode=edit" rel="http://www.sap.com/adt/relations/documentation" type="application/vnd.sap.sapgui" title="Documentation" xmlns:atom="http://www.w3.org/2005/Atom"/>
    <atom:link href="/sap/bc/adt/ddic/logs/db/ACTTABL{STRUCTURE_NAME}" rel="http://www.sap.com/adt/relations/ddic/activationlog" type="application/vnd.sap.adt.logs+xml" title="Activation Log" xmlns:atom="http://www.w3.org/2005/Atom"/><adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24zlb_hex_playground" adtcore:type="DEVC/K" adtcore:name="PACKAGE" adtcore:description="HEX comparator playground"/>
</blue:blueSource>'''

CREATE_STRUCTURE_ADT_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="TABL/DS" adtcore:description="Test structure" adtcore:language="EN" adtcore:name="{STRUCTURE_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER" adtcore:version="inactive">
<adtcore:packageRef adtcore:name="PACKAGE"/>
</blue:blueSource>'''

READ_STRUCTURE_BODY = '''@EndUserText.label : 'Test structure'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
define structure test_structure {

  client : abap.clnt;
  foo : abap.clnt;

}'''

WRITE_STRUCTURE_BODY = '''@EndUserText.label : 'Test structure'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
define structure test_structure {

  client : abap.clnt;
  bar : abap.clnt;
}'''

FAKE_LOCK_HANDLE = 'lock_handle'

ACTIVATE_STRUCTURE_BODY = f'''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/ddic/structures/{STRUCTURE_NAME.lower()}" adtcore:name="{STRUCTURE_NAME}"/>
</adtcore:objectReferences>'''
