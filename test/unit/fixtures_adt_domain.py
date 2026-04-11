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
