DOMAIN_NAME = 'BEGRM'

DOMAIN_ADT_GET_RESPONSE_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<doma:domain xmlns:doma="http://www.sap.com/dictionary/domain" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="SAP" adtcore:abapLanguageVersion="standard" adtcore:name="BEGRM" adtcore:type="DOMA/DD" adtcore:changedAt="2015-06-05T08:49:19Z" adtcore:version="active" adtcore:changedBy="SAP" adtcore:createdBy="DEVELOPER" adtcore:description="Authorization group in the material master" adtcore:language="EN" xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Fdomains%2Fbegrm" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" type="application/vnd.sap.adt.nameditems.v1+xml" title="Allowed ABAP language versions"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/vit/wb/object_type/domadd/object_name/BEGRM" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP Gui"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/vit/docu/object_type/do/object_name/begrm?masterLanguage=E&amp;mode=edit" rel="http://www.sap.com/adt/relations/documentation" type="application/vnd.sap.sapgui" title="Documentation"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="./begrm" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Landing Page (HTML)"/>
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/mga" adtcore:type="DEVC/K" adtcore:name="MGA" adtcore:description="Application development R/3 material master from 3.0"/>
  <doma:content>
    <doma:typeInformation>
      <doma:datatype>CHAR</doma:datatype>
      <doma:length>000004</doma:length>
      <doma:decimals>000000</doma:decimals>
    </doma:typeInformation>
    <doma:outputInformation>
      <doma:length>000004</doma:length>
      <doma:style>00</doma:style>
      <doma:conversionExit/>
      <doma:signExists>false</doma:signExists>
      <doma:lowercase>false</doma:lowercase>
      <doma:ampmFormat>false</doma:ampmFormat>
    </doma:outputInformation>
    <doma:valueInformation>
      <doma:valueTableRef adtcore:uri="/sap/bc/adt/ddic/tables/tmbg" adtcore:type="TABL/DT" adtcore:name="TMBG"/>
      <doma:appendExists>false</doma:appendExists>
      <doma:fixValues>
        <doma:fixValue>
          <doma:position>0006</doma:position>
          <doma:low>H</doma:low>
          <doma:high/>
          <doma:text>History</doma:text>
        </doma:fixValue>
        <doma:fixValue>
          <doma:position>0007</doma:position>
          <doma:low>X</doma:low>
          <doma:high/>
          <doma:text>Xml</doma:text>
        </doma:fixValue>
      </doma:fixValues>
    </doma:valueInformation>
  </doma:content>
</doma:domain>'''

DOMAIN_NEW_NAME = 'ZABAPGIT_UNIT_TEST'

DOMAIN_ADT_NEW_OBJECT_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<doma:domain xmlns:doma="http://www.sap.com/dictionary/domain" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DOMA/DD" adtcore:description="Testing" adtcore:language="EN" adtcore:name="{DOMAIN_NEW_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
</doma:domain>'''

DOMAIN_ADT_ALREADY_EXISTS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="com.sap.adt"/><type id="ExceptionResourceAlreadyExists"/><message lang="EN">Resource Domain {DOMAIN_NEW_NAME} does already exist.</message><localizedMessage lang="EN">Resource Domain {DOMAIN_NEW_NAME} does already exist.</localizedMessage><properties/></exc:exception>'''

# Response to GET of a domain right after its creation
DOMAIN_ADT_GET_NEW_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<doma:domain adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:abapLanguageVersion="standard" adtcore:name="{DOMAIN_NEW_NAME}" adtcore:type="DOMA/DD" adtcore:changedAt="2026-11-02T14:55:15Z" adtcore:version="new" adtcore:createdAt="2026-11-02T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="Testing" adtcore:language="EN" xmlns:doma="http://www.sap.com/dictionary/domain" xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <atom:link href="./{DOMAIN_NEW_NAME.lower()}" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Landing Page (HTML)" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:description="Temporary Objects (never transported!)"/>
  <doma:content>
    <doma:typeInformation>
      <doma:datatype/>
      <doma:length>000000</doma:length>
      <doma:decimals>000000</doma:decimals>
    </doma:typeInformation>
    <doma:outputInformation>
      <doma:length>000000</doma:length>
      <doma:style>00</doma:style>
      <doma:conversionExit/>
      <doma:signExists>false</doma:signExists>
      <doma:lowercase>false</doma:lowercase>
      <doma:ampmFormat>false</doma:ampmFormat>
    </doma:outputInformation>
    <doma:valueInformation>
      <doma:valueTableRef/>
      <doma:appendExists>false</doma:appendExists>
      <doma:fixValues/>
    </doma:valueInformation>
  </doma:content>
</doma:domain>'''

# Response to GET of a domain having fixed values, value table and all flags
DOMAIN_ADT_GET_ALL_FIELDS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<doma:domain adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:abapLanguageVersion="standard" adtcore:name="{DOMAIN_NEW_NAME}" adtcore:type="DOMA/DD" adtcore:changedAt="2026-11-02T14:55:15Z" adtcore:version="active" adtcore:createdAt="2026-11-02T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="All fields" adtcore:language="EN" xmlns:doma="http://www.sap.com/dictionary/domain" xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:description="Temporary Objects (never transported!)"/>
  <doma:content>
    <doma:typeInformation>
      <doma:datatype>DEC</doma:datatype>
      <doma:length>000011</doma:length>
      <doma:decimals>000002</doma:decimals>
    </doma:typeInformation>
    <doma:outputInformation>
      <doma:length>000015</doma:length>
      <doma:style>01</doma:style>
      <doma:conversionExit>ALPHA</doma:conversionExit>
      <doma:signExists>true</doma:signExists>
      <doma:lowercase>true</doma:lowercase>
      <doma:ampmFormat>true</doma:ampmFormat>
    </doma:outputInformation>
    <doma:valueInformation>
      <doma:valueTableRef adtcore:uri="/sap/bc/adt/ddic/tables/t000" adtcore:type="TABL/DT" adtcore:name="T000"/>
      <doma:appendExists>false</doma:appendExists>
      <doma:fixValues>
        <doma:fixValue>
          <doma:position>0001</doma:position>
          <doma:low>A</doma:low>
          <doma:high/>
          <doma:text>Alpha</doma:text>
        </doma:fixValue>
        <doma:fixValue>
          <doma:position>0002</doma:position>
          <doma:low>B</doma:low>
          <doma:high>C</doma:high>
          <doma:text>Range</doma:text>
        </doma:fixValue>
      </doma:fixValues>
    </doma:valueInformation>
  </doma:content>
</doma:domain>'''

# Response to GET of a domain of a DDIC type which ADT names differently (taken from SWFXST_BASE64BINARY)
DOMAIN_ADT_GET_RAWSTRING_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<doma:domain adtcore:responsible="SAP" adtcore:masterLanguage="EN" adtcore:masterSystem="SAP" adtcore:abapLanguageVersion="standard" adtcore:name="{DOMAIN_NEW_NAME}" adtcore:type="DOMA/DD" adtcore:changedAt="2026-11-02T14:55:15Z" adtcore:version="active" adtcore:changedBy="SAP" adtcore:createdBy="SAP" adtcore:description="Raw string" adtcore:language="EN" xmlns:doma="http://www.sap.com/dictionary/domain" xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:description="Temporary Objects (never transported!)"/>
  <doma:content>
    <doma:typeInformation>
      <doma:datatype>RAWSTRING</doma:datatype>
      <doma:length>000000</doma:length>
      <doma:decimals>000000</doma:decimals>
    </doma:typeInformation>
    <doma:outputInformation>
      <doma:length>000000</doma:length>
      <doma:style>00</doma:style>
      <doma:conversionExit/>
      <doma:signExists>false</doma:signExists>
      <doma:lowercase>false</doma:lowercase>
      <doma:ampmFormat>false</doma:ampmFormat>
    </doma:outputInformation>
    <doma:valueInformation>
      <doma:valueTableRef/>
      <doma:appendExists>false</doma:appendExists>
      <doma:fixValues/>
    </doma:valueInformation>
  </doma:content>
</doma:domain>'''

DOMAIN_ADT_DEFINE_SAMPLE_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<doma:domain xmlns:doma="http://www.sap.com/dictionary/domain" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DOMA/DD" adtcore:description="Testing" adtcore:language="EN" adtcore:name="{DOMAIN_NEW_NAME}" adtcore:abapLanguageVersion="standard" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:responsible="DEVELOPER" adtcore:version="new">
<adtcore:packageRef adtcore:name="$TMP"/>
<doma:content>
<doma:typeInformation>
<doma:datatype>CHAR</doma:datatype>
<doma:length>000010</doma:length>
<doma:decimals>0</doma:decimals>
</doma:typeInformation>
<doma:outputInformation>
<doma:length>000010</doma:length>
<doma:style>00</doma:style>
<doma:conversionExit></doma:conversionExit>
<doma:signExists>false</doma:signExists>
<doma:lowercase>false</doma:lowercase>
<doma:ampmFormat>false</doma:ampmFormat>
</doma:outputInformation>
<doma:valueInformation>
<doma:valueTableRef/>
<doma:appendExists>false</doma:appendExists>
<doma:fixValues/>
</doma:valueInformation>
</doma:content>
</doma:domain>'''

DOMAIN_ADT_DEFINE_ALL_FIELDS_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<doma:domain xmlns:doma="http://www.sap.com/dictionary/domain" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DOMA/DD" adtcore:description="All fields" adtcore:language="EN" adtcore:name="{DOMAIN_NEW_NAME}" adtcore:abapLanguageVersion="standard" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:responsible="DEVELOPER" adtcore:version="new">
<adtcore:packageRef adtcore:name="$TMP"/>
<doma:content>
<doma:typeInformation>
<doma:datatype>DEC</doma:datatype>
<doma:length>000011</doma:length>
<doma:decimals>000002</doma:decimals>
</doma:typeInformation>
<doma:outputInformation>
<doma:length>000015</doma:length>
<doma:style>01</doma:style>
<doma:conversionExit>ALPHA</doma:conversionExit>
<doma:signExists>true</doma:signExists>
<doma:lowercase>true</doma:lowercase>
<doma:ampmFormat>true</doma:ampmFormat>
</doma:outputInformation>
<doma:valueInformation>
<doma:valueTableRef adtcore:name="T000"/>
<doma:appendExists>false</doma:appendExists>
<doma:fixValues>
<doma:fixValue>
<doma:position>0001</doma:position>
<doma:low>A</doma:low>
<doma:high></doma:high>
<doma:text>Alpha</doma:text>
</doma:fixValue>
<doma:fixValue>
<doma:position>0002</doma:position>
<doma:low>B</doma:low>
<doma:high>C</doma:high>
<doma:text>Range</doma:text>
</doma:fixValue>
</doma:fixValues>
</doma:valueInformation>
</doma:content>
</doma:domain>'''

# Response to GET of the activated domain ZABAPGIT_UNIT_TEST
DOMAIN_ADT_GET_SAMPLE_RESPONSE_XML = DOMAIN_ADT_GET_NEW_RESPONSE_XML \
    .replace('adtcore:version="new"', 'adtcore:version="active"') \
    .replace('<doma:datatype/>', '<doma:datatype>CHAR</doma:datatype>') \
    .replace('<doma:length>000000</doma:length>', '<doma:length>000010</doma:length>')
