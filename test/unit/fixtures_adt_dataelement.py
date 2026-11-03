DATA_ELEMENT_NAME = 'TEST_DATA_ELEMENT'

DATA_ELEMENT_DEFINITION_ADT_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:wbobj xmlns:blue="http://www.sap.com/wbobj/dictionary/dtel" xmlns:adtcore="http://www.sap.com/adt/core" xmlns:dtel="http://www.sap.com/adt/dictionary/dataelements" adtcore:responsible="ANZEIGER" adtcore:masterLanguage="EN" adtcore:masterSystem="UIA" adtcore:abapLanguageVersion="standard" adtcore:name="{DATA_ELEMENT_NAME}" adtcore:type="DTEL/DE" adtcore:changedAt="2023-09-12T03:51:03Z" adtcore:version="active" adtcore:createdAt="2023-09-12T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="Test data element" adtcore:language="EN">
   <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions" />
   <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Fdataelements%2F{DATA_ELEMENT_NAME.lower()}" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" type="application/vnd.sap.adt.nameditems.v1+xml" title="Allowed ABAP language versions" />
   <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/vit/wb/object_type/dtelde/object_name/{DATA_ELEMENT_NAME}" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP Gui" />
   <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/vit/docu/object_type/de/object_name/{DATA_ELEMENT_NAME.lower()}?masterLanguage=E&amp;mode=edit" rel="http://www.sap.com/adt/relations/documentation" type="application/vnd.sap.sapgui" title="Documentation" />
   <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/ddic/logs/db/ACTDTEL{DATA_ELEMENT_NAME}" rel="http://www.sap.com/adt/relations/ddic/activationlog" type="application/vnd.sap.adt.logs+xml" title="Activation Log" />
   <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/package" adtcore:type="DEVC/K" adtcore:name="PACKAGE" adtcore:description="Package description" />
   <dtel:dataElement xmlns:dtel="http://www.sap.com/adt/dictionary/dataelements">
      <dtel:typeKind>predefinedAbapType</dtel:typeKind>
      <dtel:typeName></dtel:typeName>
      <dtel:dataType>STRING</dtel:dataType>
      <dtel:dataTypeLength>000000</dtel:dataTypeLength>
      <dtel:dataTypeDecimals>000000</dtel:dataTypeDecimals>
      <dtel:shortFieldLabel />
      <dtel:shortFieldLength>10</dtel:shortFieldLength>
      <dtel:shortFieldMaxLength>10</dtel:shortFieldMaxLength>
      <dtel:mediumFieldLabel />
      <dtel:mediumFieldLength>20</dtel:mediumFieldLength>
      <dtel:mediumFieldMaxLength>20</dtel:mediumFieldMaxLength>
      <dtel:longFieldLabel />
      <dtel:longFieldLength>40</dtel:longFieldLength>
      <dtel:longFieldMaxLength>40</dtel:longFieldMaxLength>
      <dtel:headingFieldLabel />
      <dtel:headingFieldLength>55</dtel:headingFieldLength>
      <dtel:headingFieldMaxLength>55</dtel:headingFieldMaxLength>
      <dtel:searchHelp />
      <dtel:searchHelpParameter />
      <dtel:setGetParameter />
      <dtel:defaultComponentName />
      <dtel:deactivateInputHistory>false</dtel:deactivateInputHistory>
      <dtel:changeDocument>false</dtel:changeDocument>
      <dtel:leftToRightDirection>false</dtel:leftToRightDirection>
      <dtel:deactivateBIDIFiltering>false</dtel:deactivateBIDIFiltering>
   </dtel:dataElement>
</blue:wbobj>'''

CREATE_DATA_ELEMENT_ADT_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:wbobj xmlns:blue="http://www.sap.com/wbobj/dictionary/dtel" xmlns:adtcore="http://www.sap.com/adt/core" xmlns:dtel="http://www.sap.com/adt/dictionary/dataelements" adtcore:type="DTEL/DE" adtcore:description="Test data element" adtcore:language="EN" adtcore:name="{DATA_ELEMENT_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="ANZEIGER" adtcore:version="inactive">
<adtcore:packageRef adtcore:name="PACKAGE"/>
<dtel:dataElement>
<dtel:typeKind/>
<dtel:typeName/>
<dtel:dataType/>
<dtel:dataTypeLength/>
<dtel:dataTypeDecimals/>
<dtel:shortFieldLabel/>
<dtel:shortFieldLength/>
<dtel:shortFieldMaxLength/>
<dtel:mediumFieldLabel/>
<dtel:mediumFieldLength/>
<dtel:mediumFieldMaxLength/>
<dtel:longFieldLabel/>
<dtel:longFieldLength/>
<dtel:longFieldMaxLength/>
<dtel:headingFieldLabel/>
<dtel:headingFieldLength/>
<dtel:headingFieldMaxLength/>
<dtel:searchHelp/>
<dtel:searchHelpParameter/>
<dtel:setGetParameter/>
<dtel:defaultComponentName/>
<dtel:deactivateInputHistory/>
<dtel:changeDocument/>
<dtel:leftToRightDirection/>
<dtel:deactivateBIDIFiltering/>
</dtel:dataElement>
</blue:wbobj>'''

READ_DATA_ELEMENT_BODY = DATA_ELEMENT_DEFINITION_ADT_XML

WRITE_DATA_ELEMENT_BODY = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:wbobj
    xmlns:adtcore="http://www.sap.com/adt/core"
    xmlns:atom="http://www.w3.org/2005/Atom"
    xmlns:blue="http://www.sap.com/wbobj/dictionary/dtel"
    xmlns:dtel="http://www.sap.com/adt/dictionary/dataelements" adtcore:changedAt="2023-09-11T05:22:51Z" adtcore:changedBy="DEVELOPER" adtcore:createdAt="2015-01-13T00:00:00Z" adtcore:createdBy="DEVELOPER" adtcore:description="Request Address" adtcore:language="EN" adtcore:name="{DATA_ELEMENT_NAME}" adtcore:type="DTEL/DE" adtcore:version="inactive" adtcore:abapLanguageVersion="standard" adtcore:masterLanguage="EN" adtcore:masterSystem="UIA" adtcore:responsible="ANZEIGER">
    <atom:link href="./{DATA_ELEMENT_NAME.lower()}?version=active" rel="http://www.sap.com/adt/relations/objectstates" title="Complementary active/inactive version"/>
    <atom:link href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions"/>
    <atom:link href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Fdataelements%2F{DATA_ELEMENT_NAME.lower()}" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" title="Allowed ABAP language versions" type="application/vnd.sap.adt.nameditems.v1+xml"/>
    <atom:link href="/sap/bc/adt/vit/wb/object_type/dtelde/object_name/{DATA_ELEMENT_NAME}" rel="self" title="Representation in SAP Gui" type="application/vnd.sap.sapgui"/>
    <atom:link href="/sap/bc/adt/vit/docu/object_type/de/object_name/%2fiwfnd%2fmet_request_add?masterLanguage=E&amp;mode=edit" rel="http://www.sap.com/adt/relations/documentation" title="Documentation" type="application/vnd.sap.sapgui"/>
    <atom:link href="/sap/bc/adt/ddic/logs/db/ACTDTEL-IWFND-MET_REQUEST_ADD" rel="http://www.sap.com/adt/relations/ddic/activationlog" title="Activation Log" type="application/vnd.sap.adt.logs+xml"/>
    <adtcore:packageRef adtcore:description="SAP GW Framework - Metering" adtcore:name="PACKAGE" adtcore:type="DEVC/K" adtcore:uri="/sap/bc/adt/packages/package"/>
    <dtel:dataElement>
        <dtel:typeKind>predefinedAbapType</dtel:typeKind>
        <dtel:typeName></dtel:typeName>
        <dtel:dataType>STRING</dtel:dataType>
        <dtel:dataTypeLength>6</dtel:dataTypeLength>
        <dtel:dataTypeDecimals>0</dtel:dataTypeDecimals>
        <dtel:shortFieldLabel>Req. Add.</dtel:shortFieldLabel>
        <dtel:shortFieldLength>10</dtel:shortFieldLength>
        <dtel:shortFieldMaxLength>10</dtel:shortFieldMaxLength>
        <dtel:mediumFieldLabel>Request Address</dtel:mediumFieldLabel>
        <dtel:mediumFieldLength>15</dtel:mediumFieldLength>
        <dtel:mediumFieldMaxLength>20</dtel:mediumFieldMaxLength>
        <dtel:longFieldLabel>Request Address</dtel:longFieldLabel>
        <dtel:longFieldLength>20</dtel:longFieldLength>
        <dtel:longFieldMaxLength>40</dtel:longFieldMaxLength>
        <dtel:headingFieldLabel>Request Address</dtel:headingFieldLabel>
        <dtel:headingFieldLength>55</dtel:headingFieldLength>
        <dtel:headingFieldMaxLength>55</dtel:headingFieldMaxLength>
        <dtel:searchHelp></dtel:searchHelp>
        <dtel:searchHelpParameter></dtel:searchHelpParameter>
        <dtel:setGetParameter></dtel:setGetParameter>
        <dtel:defaultComponentName></dtel:defaultComponentName>
        <dtel:deactivateInputHistory>false</dtel:deactivateInputHistory>
        <dtel:changeDocument>false</dtel:changeDocument>
        <dtel:leftToRightDirection>false</dtel:leftToRightDirection>
        <dtel:deactivateBIDIFiltering>false</dtel:deactivateBIDIFiltering>
    </dtel:dataElement>
</blue:wbobj>'''

DEFINE_DATA_ELEMENT_W_DOMAIN_BODY = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:wbobj xmlns:blue="http://www.sap.com/wbobj/dictionary/dtel" xmlns:adtcore="http://www.sap.com/adt/core" xmlns:dtel="http://www.sap.com/adt/dictionary/dataelements" adtcore:type="DTEL/DE" adtcore:description="Test data element" adtcore:language="EN" adtcore:name="{DATA_ELEMENT_NAME}" adtcore:abapLanguageVersion="standard" adtcore:masterLanguage="EN" adtcore:masterSystem="UIA" adtcore:responsible="ANZEIGER" adtcore:version="active">
<adtcore:packageRef adtcore:name="PACKAGE"/>
<dtel:dataElement>
<dtel:typeKind>domain</dtel:typeKind>
<dtel:typeName>ABC</dtel:typeName>
<dtel:dataType></dtel:dataType>
<dtel:dataTypeLength>0</dtel:dataTypeLength>
<dtel:dataTypeDecimals>0</dtel:dataTypeDecimals>
<dtel:shortFieldLabel>Tst DTEL</dtel:shortFieldLabel>
<dtel:shortFieldLength>10</dtel:shortFieldLength>
<dtel:shortFieldMaxLength>10</dtel:shortFieldMaxLength>
<dtel:mediumFieldLabel>Test Label Medium</dtel:mediumFieldLabel>
<dtel:mediumFieldLength>20</dtel:mediumFieldLength>
<dtel:mediumFieldMaxLength>20</dtel:mediumFieldMaxLength>
<dtel:longFieldLabel>Test Label Long</dtel:longFieldLabel>
<dtel:longFieldLength>40</dtel:longFieldLength>
<dtel:longFieldMaxLength>40</dtel:longFieldMaxLength>
<dtel:headingFieldLabel>Test Label Heading</dtel:headingFieldLabel>
<dtel:headingFieldLength>55</dtel:headingFieldLength>
<dtel:headingFieldMaxLength>55</dtel:headingFieldMaxLength>
<dtel:searchHelp></dtel:searchHelp>
<dtel:searchHelpParameter></dtel:searchHelpParameter>
<dtel:setGetParameter></dtel:setGetParameter>
<dtel:defaultComponentName></dtel:defaultComponentName>
<dtel:deactivateInputHistory>false</dtel:deactivateInputHistory>
<dtel:changeDocument>false</dtel:changeDocument>
<dtel:leftToRightDirection>false</dtel:leftToRightDirection>
<dtel:deactivateBIDIFiltering>false</dtel:deactivateBIDIFiltering>
</dtel:dataElement>
</blue:wbobj>'''

DEFINE_DATA_ELEMENT_W_PREDEFINED_ABAP_TYPE_BODY = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:wbobj xmlns:blue="http://www.sap.com/wbobj/dictionary/dtel" xmlns:adtcore="http://www.sap.com/adt/core" xmlns:dtel="http://www.sap.com/adt/dictionary/dataelements" adtcore:type="DTEL/DE" adtcore:description="Test data element" adtcore:language="EN" adtcore:name="{DATA_ELEMENT_NAME}" adtcore:abapLanguageVersion="standard" adtcore:masterLanguage="EN" adtcore:masterSystem="UIA" adtcore:responsible="ANZEIGER" adtcore:version="active">
<adtcore:packageRef adtcore:name="PACKAGE"/>
<dtel:dataElement>
<dtel:typeKind>predefinedAbapType</dtel:typeKind>
<dtel:typeName></dtel:typeName>
<dtel:dataType>STRING</dtel:dataType>
<dtel:dataTypeLength>200</dtel:dataTypeLength>
<dtel:dataTypeDecimals>0</dtel:dataTypeDecimals>
<dtel:shortFieldLabel>Tst DTEL</dtel:shortFieldLabel>
<dtel:shortFieldLength>10</dtel:shortFieldLength>
<dtel:shortFieldMaxLength>10</dtel:shortFieldMaxLength>
<dtel:mediumFieldLabel>Test Label Medium</dtel:mediumFieldLabel>
<dtel:mediumFieldLength>20</dtel:mediumFieldLength>
<dtel:mediumFieldMaxLength>20</dtel:mediumFieldMaxLength>
<dtel:longFieldLabel>Test Label Long</dtel:longFieldLabel>
<dtel:longFieldLength>40</dtel:longFieldLength>
<dtel:longFieldMaxLength>40</dtel:longFieldMaxLength>
<dtel:headingFieldLabel>Test Label Heading</dtel:headingFieldLabel>
<dtel:headingFieldLength>55</dtel:headingFieldLength>
<dtel:headingFieldMaxLength>55</dtel:headingFieldMaxLength>
<dtel:searchHelp></dtel:searchHelp>
<dtel:searchHelpParameter></dtel:searchHelpParameter>
<dtel:setGetParameter></dtel:setGetParameter>
<dtel:defaultComponentName></dtel:defaultComponentName>
<dtel:deactivateInputHistory>false</dtel:deactivateInputHistory>
<dtel:changeDocument>false</dtel:changeDocument>
<dtel:leftToRightDirection>false</dtel:leftToRightDirection>
<dtel:deactivateBIDIFiltering>false</dtel:deactivateBIDIFiltering>
</dtel:dataElement>
</blue:wbobj>'''

FAKE_LOCK_HANDLE = 'lock_handle'

ACTIVATE_DATA_ELEMENT_BODY = f'''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/ddic/dataelements/{DATA_ELEMENT_NAME.lower()}" adtcore:name="{DATA_ELEMENT_NAME}"/>
</adtcore:objectReferences>'''

ERROR_XML_DATA_ELEMENT_ALREADY_EXISTS=f'''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="com.sap.adt"/><type id="ExceptionResourceAlreadyExists"/><message lang="EN">Resource Data Element {DATA_ELEMENT_NAME} does already exist.</message><localizedMessage lang="EN">Resource Package $SAPCLI_TEST_ROOT does already exist.</localizedMessage><properties/></exc:exception>'''

# Domain ABC fixture for testing --expand feature
DOMAIN_ABC_NAME = 'ABC'
DOMAIN_ABC_ADT_GET_RESPONSE_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<doma:domain xmlns:doma="http://www.sap.com/dictionary/domain" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="SAP" adtcore:abapLanguageVersion="standard" adtcore:name="ABC" adtcore:type="DOMA/DD" adtcore:changedAt="2023-09-12T10:00:00Z" adtcore:version="active" adtcore:changedBy="SAP" adtcore:createdBy="DEVELOPER" adtcore:description="Test Domain ABC" adtcore:language="EN" xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/package" adtcore:type="DEVC/K" adtcore:name="PACKAGE"/>
  <doma:content>
    <doma:typeInformation>
      <doma:datatype>CHAR</doma:datatype>
      <doma:length>000010</doma:length>
      <doma:decimals>000000</doma:decimals>
    </doma:typeInformation>
    <doma:outputInformation>
      <doma:length>000010</doma:length>
      <doma:style>00</doma:style>
      <doma:conversionExit/>
      <doma:signExists>false</doma:signExists>
      <doma:lowercase>false</doma:lowercase>
      <doma:ampmFormat>false</doma:ampmFormat>
    </doma:outputInformation>
    <doma:valueInformation>
      <doma:appendExists>false</doma:appendExists>
      <doma:fixValues>
        <doma:fixValue>
          <doma:position>0001</doma:position>
          <doma:low>A</doma:low>
          <doma:high/>
          <doma:text>Option A</doma:text>
        </doma:fixValue>
        <doma:fixValue>
          <doma:position>0002</doma:position>
          <doma:low>B</doma:low>
          <doma:high/>
          <doma:text>Option B</doma:text>
        </doma:fixValue>
      </doma:fixValues>
    </doma:valueInformation>
  </doma:content>
</doma:domain>'''

DATA_ELEMENT_NEW_NAME = 'ZAGT_TEST_DTEL'

DATA_ELEMENT_ADT_NEW_OBJECT_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:wbobj xmlns:blue="http://www.sap.com/wbobj/dictionary/dtel" xmlns:adtcore="http://www.sap.com/adt/core" xmlns:dtel="http://www.sap.com/adt/dictionary/dataelements" adtcore:type="DTEL/DE" adtcore:description="testing" adtcore:language="EN" adtcore:name="{DATA_ELEMENT_NEW_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER" adtcore:version="inactive">
<adtcore:packageRef adtcore:name="$TMP"/>
<dtel:dataElement>
<dtel:typeKind/>
<dtel:typeName/>
<dtel:dataType/>
<dtel:dataTypeLength/>
<dtel:dataTypeDecimals/>
<dtel:shortFieldLabel/>
<dtel:shortFieldLength/>
<dtel:shortFieldMaxLength/>
<dtel:mediumFieldLabel/>
<dtel:mediumFieldLength/>
<dtel:mediumFieldMaxLength/>
<dtel:longFieldLabel/>
<dtel:longFieldLength/>
<dtel:longFieldMaxLength/>
<dtel:headingFieldLabel/>
<dtel:headingFieldLength/>
<dtel:headingFieldMaxLength/>
<dtel:searchHelp/>
<dtel:searchHelpParameter/>
<dtel:setGetParameter/>
<dtel:defaultComponentName/>
<dtel:deactivateInputHistory/>
<dtel:changeDocument/>
<dtel:leftToRightDirection/>
<dtel:deactivateBIDIFiltering/>
</dtel:dataElement>
</blue:wbobj>'''

DATA_ELEMENT_ADT_GET_NEW_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><blue:wbobj adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:abapLanguageVersion="standard" adtcore:name="{DATA_ELEMENT_NEW_NAME}" adtcore:type="DTEL/DE" adtcore:changedAt="2026-11-03T08:38:59Z" adtcore:version="new" adtcore:createdAt="2026-11-03T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="testing" adtcore:language="EN" xmlns:blue="http://www.sap.com/wbobj/dictionary/dtel" xmlns:adtcore="http://www.sap.com/adt/core"><atom:link href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Fdataelements%2F{DATA_ELEMENT_NEW_NAME.lower()}" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" type="application/vnd.sap.adt.nameditems.v1+xml" title="Allowed ABAP language versions" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/vit/wb/object_type/dtelde/object_name/{DATA_ELEMENT_NEW_NAME}" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP Gui" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/vit/docu/object_type/de/object_name/{DATA_ELEMENT_NEW_NAME.lower()}?masterLanguage=E&amp;mode=edit" rel="http://www.sap.com/adt/relations/documentation" type="application/vnd.sap.sapgui" title="Documentation" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="./{DATA_ELEMENT_NEW_NAME.lower()}" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Landing Page (HTML)" xmlns:atom="http://www.w3.org/2005/Atom"/><adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:description="Temporary Objects (never transported!)"/><dtel:dataElement xmlns:dtel="http://www.sap.com/adt/dictionary/dataelements"><dtel:typeKind>domain</dtel:typeKind><dtel:typeName/><dtel:dataType/><dtel:dataTypeLength>000000</dtel:dataTypeLength><dtel:dataTypeDecimals>000000</dtel:dataTypeDecimals><dtel:shortFieldLabel/><dtel:shortFieldLength>10</dtel:shortFieldLength><dtel:shortFieldMaxLength>10</dtel:shortFieldMaxLength><dtel:mediumFieldLabel/><dtel:mediumFieldLength>20</dtel:mediumFieldLength><dtel:mediumFieldMaxLength>20</dtel:mediumFieldMaxLength><dtel:longFieldLabel/><dtel:longFieldLength>40</dtel:longFieldLength><dtel:longFieldMaxLength>40</dtel:longFieldMaxLength><dtel:headingFieldLabel/><dtel:headingFieldLength>55</dtel:headingFieldLength><dtel:headingFieldMaxLength>55</dtel:headingFieldMaxLength><dtel:searchHelp/><dtel:searchHelpParameter/><dtel:setGetParameter/><dtel:defaultComponentName/><dtel:deactivateInputHistory>false</dtel:deactivateInputHistory><dtel:changeDocument>false</dtel:changeDocument><dtel:leftToRightDirection>false</dtel:leftToRightDirection><dtel:deactivateBIDIFiltering>false</dtel:deactivateBIDIFiltering></dtel:dataElement></blue:wbobj>'''

DATA_ELEMENT_ADT_DEFINE_SAMPLE_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:wbobj xmlns:blue="http://www.sap.com/wbobj/dictionary/dtel" xmlns:adtcore="http://www.sap.com/adt/core" xmlns:dtel="http://www.sap.com/adt/dictionary/dataelements" adtcore:type="DTEL/DE" adtcore:description="testing" adtcore:language="EN" adtcore:name="{DATA_ELEMENT_NEW_NAME}" adtcore:abapLanguageVersion="standard" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:responsible="DEVELOPER" adtcore:version="new">
<adtcore:packageRef adtcore:name="$TMP"/>
<dtel:dataElement>
<dtel:typeKind>predefinedAbapType</dtel:typeKind>
<dtel:typeName></dtel:typeName>
<dtel:dataType>CHAR</dtel:dataType>
<dtel:dataTypeLength>000001</dtel:dataTypeLength>
<dtel:dataTypeDecimals>0</dtel:dataTypeDecimals>
<dtel:shortFieldLabel>testing</dtel:shortFieldLabel>
<dtel:shortFieldLength>10</dtel:shortFieldLength>
<dtel:shortFieldMaxLength>10</dtel:shortFieldMaxLength>
<dtel:mediumFieldLabel>testing</dtel:mediumFieldLabel>
<dtel:mediumFieldLength>20</dtel:mediumFieldLength>
<dtel:mediumFieldMaxLength>20</dtel:mediumFieldMaxLength>
<dtel:longFieldLabel>testing</dtel:longFieldLabel>
<dtel:longFieldLength>40</dtel:longFieldLength>
<dtel:longFieldMaxLength>40</dtel:longFieldMaxLength>
<dtel:headingFieldLabel>testing</dtel:headingFieldLabel>
<dtel:headingFieldLength>55</dtel:headingFieldLength>
<dtel:headingFieldMaxLength>55</dtel:headingFieldMaxLength>
<dtel:searchHelp></dtel:searchHelp>
<dtel:searchHelpParameter></dtel:searchHelpParameter>
<dtel:setGetParameter></dtel:setGetParameter>
<dtel:defaultComponentName></dtel:defaultComponentName>
<dtel:deactivateInputHistory>false</dtel:deactivateInputHistory>
<dtel:changeDocument>false</dtel:changeDocument>
<dtel:leftToRightDirection>false</dtel:leftToRightDirection>
<dtel:deactivateBIDIFiltering>false</dtel:deactivateBIDIFiltering>
</dtel:dataElement>
</blue:wbobj>'''

DATA_ELEMENT_ADT_DEFINE_DOMAIN_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:wbobj xmlns:blue="http://www.sap.com/wbobj/dictionary/dtel" xmlns:adtcore="http://www.sap.com/adt/core" xmlns:dtel="http://www.sap.com/adt/dictionary/dataelements" adtcore:type="DTEL/DE" adtcore:description="Domain &amp; labels" adtcore:language="EN" adtcore:name="{DATA_ELEMENT_NEW_NAME}" adtcore:abapLanguageVersion="standard" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:responsible="DEVELOPER" adtcore:version="new">
<adtcore:packageRef adtcore:name="$TMP"/>
<dtel:dataElement>
<dtel:typeKind>domain</dtel:typeKind>
<dtel:typeName>ZABAPGIT_UNIT_TEST</dtel:typeName>
<dtel:dataType></dtel:dataType>
<dtel:dataTypeLength>0</dtel:dataTypeLength>
<dtel:dataTypeDecimals>0</dtel:dataTypeDecimals>
<dtel:shortFieldLabel>Short</dtel:shortFieldLabel>
<dtel:shortFieldLength>08</dtel:shortFieldLength>
<dtel:shortFieldMaxLength>10</dtel:shortFieldMaxLength>
<dtel:mediumFieldLabel>Medium</dtel:mediumFieldLabel>
<dtel:mediumFieldLength>15</dtel:mediumFieldLength>
<dtel:mediumFieldMaxLength>20</dtel:mediumFieldMaxLength>
<dtel:longFieldLabel>Long</dtel:longFieldLabel>
<dtel:longFieldLength>25</dtel:longFieldLength>
<dtel:longFieldMaxLength>40</dtel:longFieldMaxLength>
<dtel:headingFieldLabel>Heading</dtel:headingFieldLabel>
<dtel:headingFieldLength>30</dtel:headingFieldLength>
<dtel:headingFieldMaxLength>55</dtel:headingFieldMaxLength>
<dtel:searchHelp>ZSAPCLI_SHLP</dtel:searchHelp>
<dtel:searchHelpParameter>VALUE</dtel:searchHelpParameter>
<dtel:setGetParameter>ZSAPCLI</dtel:setGetParameter>
<dtel:defaultComponentName>DOMAIN_VALUE</dtel:defaultComponentName>
<dtel:deactivateInputHistory>true</dtel:deactivateInputHistory>
<dtel:changeDocument>true</dtel:changeDocument>
<dtel:leftToRightDirection>true</dtel:leftToRightDirection>
<dtel:deactivateBIDIFiltering>true</dtel:deactivateBIDIFiltering>
</dtel:dataElement>
</blue:wbobj>'''

DATA_ELEMENT_ADT_ALREADY_EXISTS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="com.sap.adt"/><type id="ExceptionResourceAlreadyExists"/><message lang="EN">Resource Data Element {DATA_ELEMENT_NEW_NAME} does already exist.</message><localizedMessage lang="EN">Resource Data Element {DATA_ELEMENT_NEW_NAME} does already exist.</localizedMessage><properties/></exc:exception>'''

DATA_ELEMENT_ADT_GET_SAMPLE_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><blue:wbobj adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:abapLanguageVersion="standard" adtcore:name="{DATA_ELEMENT_NEW_NAME}" adtcore:type="DTEL/DE" adtcore:changedAt="2026-11-03T08:44:17Z" adtcore:version="active" adtcore:createdAt="2026-11-03T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="testing" adtcore:language="EN" xmlns:blue="http://www.sap.com/wbobj/dictionary/dtel" xmlns:adtcore="http://www.sap.com/adt/core"><atom:link href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Fdataelements%2F{DATA_ELEMENT_NEW_NAME.lower()}" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" type="application/vnd.sap.adt.nameditems.v1+xml" title="Allowed ABAP language versions" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/vit/wb/object_type/dtelde/object_name/{DATA_ELEMENT_NEW_NAME}" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP Gui" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/vit/docu/object_type/de/object_name/{DATA_ELEMENT_NEW_NAME.lower()}?masterLanguage=E&amp;mode=edit" rel="http://www.sap.com/adt/relations/documentation" type="application/vnd.sap.sapgui" title="Documentation" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/ddic/logs/db/ACTDTEL{DATA_ELEMENT_NEW_NAME}" rel="http://www.sap.com/adt/relations/ddic/activationlog" type="application/vnd.sap.adt.logs+xml" title="Activation Log" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="./{DATA_ELEMENT_NEW_NAME.lower()}" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Landing Page (HTML)" xmlns:atom="http://www.w3.org/2005/Atom"/><adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:description="DTEL"/><dtel:dataElement xmlns:dtel="http://www.sap.com/adt/dictionary/dataelements"><dtel:typeKind>predefinedAbapType</dtel:typeKind><dtel:typeName/><dtel:dataType>CHAR</dtel:dataType><dtel:dataTypeLength>000001</dtel:dataTypeLength><dtel:dataTypeDecimals>000000</dtel:dataTypeDecimals><dtel:shortFieldLabel>testing</dtel:shortFieldLabel><dtel:shortFieldLength>10</dtel:shortFieldLength><dtel:shortFieldMaxLength>10</dtel:shortFieldMaxLength><dtel:mediumFieldLabel>testing</dtel:mediumFieldLabel><dtel:mediumFieldLength>20</dtel:mediumFieldLength><dtel:mediumFieldMaxLength>20</dtel:mediumFieldMaxLength><dtel:longFieldLabel>testing</dtel:longFieldLabel><dtel:longFieldLength>40</dtel:longFieldLength><dtel:longFieldMaxLength>40</dtel:longFieldMaxLength><dtel:headingFieldLabel>testing</dtel:headingFieldLabel><dtel:headingFieldLength>55</dtel:headingFieldLength><dtel:headingFieldMaxLength>55</dtel:headingFieldMaxLength><dtel:searchHelp/><dtel:searchHelpParameter/><dtel:setGetParameter/><dtel:defaultComponentName/><dtel:deactivateInputHistory>false</dtel:deactivateInputHistory><dtel:changeDocument>false</dtel:changeDocument><dtel:leftToRightDirection>false</dtel:leftToRightDirection><dtel:deactivateBIDIFiltering>false</dtel:deactivateBIDIFiltering></dtel:dataElement></blue:wbobj>'''

DATA_ELEMENT_ADT_GET_DOMAIN_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><blue:wbobj adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:abapLanguageVersion="standard" adtcore:name="{DATA_ELEMENT_NEW_NAME}" adtcore:type="DTEL/DE" adtcore:changedAt="2026-11-03T08:44:17Z" adtcore:version="active" adtcore:createdAt="2026-11-03T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="A &amp; B &lt;C&gt; 'D' &quot;E&quot;" adtcore:language="EN" xmlns:blue="http://www.sap.com/wbobj/dictionary/dtel" xmlns:adtcore="http://www.sap.com/adt/core"><atom:link href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Fdataelements%2F{DATA_ELEMENT_NEW_NAME.lower()}" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" type="application/vnd.sap.adt.nameditems.v1+xml" title="Allowed ABAP language versions" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/vit/wb/object_type/dtelde/object_name/{DATA_ELEMENT_NEW_NAME}" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP Gui" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/vit/docu/object_type/de/object_name/{DATA_ELEMENT_NEW_NAME.lower()}?masterLanguage=E&amp;mode=edit" rel="http://www.sap.com/adt/relations/documentation" type="application/vnd.sap.sapgui" title="Documentation" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/ddic/logs/db/ACTDTEL{DATA_ELEMENT_NEW_NAME}" rel="http://www.sap.com/adt/relations/ddic/activationlog" type="application/vnd.sap.adt.logs+xml" title="Activation Log" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="./{DATA_ELEMENT_NEW_NAME.lower()}" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Landing Page (HTML)" xmlns:atom="http://www.w3.org/2005/Atom"/><adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:description="DTEL"/><dtel:dataElement xmlns:dtel="http://www.sap.com/adt/dictionary/dataelements"><dtel:typeKind>domain</dtel:typeKind><dtel:typeName>SPRAS</dtel:typeName><dtel:dataType>LANG</dtel:dataType><dtel:dataTypeLength>000001</dtel:dataTypeLength><dtel:dataTypeDecimals>000000</dtel:dataTypeDecimals><dtel:shortFieldLabel>Short</dtel:shortFieldLabel><dtel:shortFieldLength>08</dtel:shortFieldLength><dtel:shortFieldMaxLength>10</dtel:shortFieldMaxLength><dtel:mediumFieldLabel>Medium</dtel:mediumFieldLabel><dtel:mediumFieldLength>15</dtel:mediumFieldLength><dtel:mediumFieldMaxLength>20</dtel:mediumFieldMaxLength><dtel:longFieldLabel>Long</dtel:longFieldLabel><dtel:longFieldLength>25</dtel:longFieldLength><dtel:longFieldMaxLength>40</dtel:longFieldMaxLength><dtel:headingFieldLabel>Heading</dtel:headingFieldLabel><dtel:headingFieldLength>30</dtel:headingFieldLength><dtel:headingFieldMaxLength>55</dtel:headingFieldMaxLength><dtel:searchHelp>H_T002</dtel:searchHelp><dtel:searchHelpParameter>SPRAS</dtel:searchHelpParameter><dtel:setGetParameter>SPR</dtel:setGetParameter><dtel:defaultComponentName>DOMAIN_VALUE</dtel:defaultComponentName><dtel:deactivateInputHistory>true</dtel:deactivateInputHistory><dtel:changeDocument>true</dtel:changeDocument><dtel:leftToRightDirection>false</dtel:leftToRightDirection><dtel:deactivateBIDIFiltering>false</dtel:deactivateBIDIFiltering></dtel:dataElement></blue:wbobj>'''

DATA_ELEMENT_ADT_GET_STRING_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><blue:wbobj adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:abapLanguageVersion="standard" adtcore:name="{DATA_ELEMENT_NEW_NAME}" adtcore:type="DTEL/DE" adtcore:changedAt="2026-11-03T08:44:17Z" adtcore:version="active" adtcore:createdAt="2026-11-03T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="String" adtcore:language="EN" xmlns:blue="http://www.sap.com/wbobj/dictionary/dtel" xmlns:adtcore="http://www.sap.com/adt/core"><atom:link href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Fdataelements%2F{DATA_ELEMENT_NEW_NAME.lower()}" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" type="application/vnd.sap.adt.nameditems.v1+xml" title="Allowed ABAP language versions" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/vit/wb/object_type/dtelde/object_name/{DATA_ELEMENT_NEW_NAME}" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP Gui" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/vit/docu/object_type/de/object_name/{DATA_ELEMENT_NEW_NAME.lower()}?masterLanguage=E&amp;mode=edit" rel="http://www.sap.com/adt/relations/documentation" type="application/vnd.sap.sapgui" title="Documentation" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/ddic/logs/db/ACTDTEL{DATA_ELEMENT_NEW_NAME}" rel="http://www.sap.com/adt/relations/ddic/activationlog" type="application/vnd.sap.adt.logs+xml" title="Activation Log" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="./{DATA_ELEMENT_NEW_NAME.lower()}" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Landing Page (HTML)" xmlns:atom="http://www.w3.org/2005/Atom"/><adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:description="DTEL"/><dtel:dataElement xmlns:dtel="http://www.sap.com/adt/dictionary/dataelements"><dtel:typeKind>predefinedAbapType</dtel:typeKind><dtel:typeName/><dtel:dataType>STRING</dtel:dataType><dtel:dataTypeLength>000000</dtel:dataTypeLength><dtel:dataTypeDecimals>000000</dtel:dataTypeDecimals><dtel:shortFieldLabel>String</dtel:shortFieldLabel><dtel:shortFieldLength>10</dtel:shortFieldLength><dtel:shortFieldMaxLength>10</dtel:shortFieldMaxLength><dtel:mediumFieldLabel>String</dtel:mediumFieldLabel><dtel:mediumFieldLength>20</dtel:mediumFieldLength><dtel:mediumFieldMaxLength>20</dtel:mediumFieldMaxLength><dtel:longFieldLabel>String</dtel:longFieldLabel><dtel:longFieldLength>40</dtel:longFieldLength><dtel:longFieldMaxLength>40</dtel:longFieldMaxLength><dtel:headingFieldLabel>String</dtel:headingFieldLabel><dtel:headingFieldLength>55</dtel:headingFieldLength><dtel:headingFieldMaxLength>55</dtel:headingFieldMaxLength><dtel:searchHelp/><dtel:searchHelpParameter/><dtel:setGetParameter/><dtel:defaultComponentName/><dtel:deactivateInputHistory>false</dtel:deactivateInputHistory><dtel:changeDocument>false</dtel:changeDocument><dtel:leftToRightDirection>true</dtel:leftToRightDirection><dtel:deactivateBIDIFiltering>true</dtel:deactivateBIDIFiltering></dtel:dataElement></blue:wbobj>'''
