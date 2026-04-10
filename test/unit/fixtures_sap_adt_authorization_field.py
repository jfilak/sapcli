"""Test fixtures for Authorization Field"""

AUTHORIZATION_FIELD_NAME = 'BEGRU'

AUTHORIZATION_FIELD_ADT_GET_RESPONSE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<auth:auth xmlns:auth="http://www.sap.com/iam/auth" adtcore:responsible="KNOETIG" adtcore:masterLanguage="DE" adtcore:masterSystem="YI3" adtcore:abapLanguageVersion="standard" adtcore:name="BEGRU" adtcore:type="AUTH" adtcore:changedAt="1971-04-01T00:00:00Z" adtcore:createdBy="KNOETIG" adtcore:description="Authorization Group" adtcore:descriptionTextLimit="60" adtcore:language="EN" xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Faps%2Fiam%2Fauth%2Fbegru" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" type="application/vnd.sap.adt.nameditems.v1+xml" title="Allowed ABAP language versions"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/vit/wb/object_type/auth/object_name/BEGRU" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP GUI"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="./begru" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Landing Page (HTML)"/>
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/s_bupa_general" adtcore:type="DEVC/K" adtcore:name="S_BUPA_GENERAL" adtcore:description="SAP Business Partner: Basic Components"/>
  <auth:content>
    <auth:fieldName>BEGRU</auth:fieldName>
    <auth:rollName>BEGRU</auth:rollName>
    <auth:checkTable/>
    <auth:exitFB/>
    <auth:abap_language_version/>
    <auth:search>false</auth:search>
    <auth:objexit>false</auth:objexit>
    <auth:domname>BEGRU</auth:domname>
    <auth:outputlen>000004</auth:outputlen>
    <auth:convexit/>
    <auth:orglvlinfo>Field is not defined as Organizational level.</auth:orglvlinfo>
    <auth:col_searchhelp>false</auth:col_searchhelp>
    <auth:col_searchhelp_name/>
    <auth:col_searchhelp_descr/>
    <auth:objectVisibility>
      <auth:isSearchHelpTypeVisible>true</auth:isSearchHelpTypeVisible>
      <auth:isExitModuleVisible>true</auth:isExitModuleVisible>
      <auth:isCreateAuthObjectVisible>true</auth:isCreateAuthObjectVisible>
      <auth:isAssignToAuthObjectVisible>true</auth:isAssignToAuthObjectVisible>
      <auth:isCreateRestrictionFieldVisible>false</auth:isCreateRestrictionFieldVisible>
      <auth:isAbapDictionaryVisible>true</auth:isAbapDictionaryVisible>
      <auth:isAddSearchHelpVisible>true</auth:isAddSearchHelpVisible>
    </auth:objectVisibility>
  </auth:content>
</auth:auth>"""
