GET_PACKAGE_ADT_XML='''<?xml version="1.0" encoding="utf-8"?>
<pak:package xmlns:pak="http://www.sap.com/adt/packages" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:masterLanguage="EN" adtcore:name="$IAMTHEKING" adtcore:type="DEVC/K" adtcore:changedAt="2019-01-29T23:00:00Z" adtcore:version="active" adtcore:createdAt="2019-01-29T23:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:description="This is a package" adtcore:descriptionTextLimit="60" adtcore:language="EN">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/vit/wb/object_type/devck/object_name/%24IAMTHEKING" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP Gui"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/packages/valuehelps/applicationcomponents" rel="applicationcomponents" type="application/vnd.sap.adt.nameditems.v1+xml" title="Application Components Value Help"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/packages/valuehelps/softwarecomponents" rel="softwarecomponents" type="application/vnd.sap.adt.nameditems.v1+xml" title="Software Components Value Help"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/packages/valuehelps/transportlayers" rel="transportlayers" type="application/vnd.sap.adt.nameditems.v1+xml" title="Transport Layers Value Help"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/packages/valuehelps/translationrelevances" rel="translationrelevances" type="application/vnd.sap.adt.nameditems.v1+xml" title="Transport Relevances Value Help"/>
  <pak:attributes pak:packageType="development" pak:isPackageTypeEditable="false" pak:isAddingObjectsAllowed="false" pak:isAddingObjectsAllowedEditable="true" pak:isEncapsulated="false" pak:isEncapsulationEditable="false" pak:recordChanges="false" pak:isRecordChangesEditable="false" pak:isSwitchVisible="false"/>
  <pak:superPackage/>
  <pak:applicationComponent pak:name="-" pak:description="No application component assigned" pak:isVisible="true" pak:isEditable="false"/>
  <pak:transport>
    <pak:softwareComponent pak:name="LOCAL" pak:description="" pak:isVisible="true" pak:isEditable="false"/>
    <pak:transportLayer pak:name="" pak:description="" pak:isVisible="false" pak:isEditable="false"/>
  </pak:transport>
  <pak:useAccesses pak:isVisible="false"/>
  <pak:packageInterfaces pak:isVisible="false"/>
  <pak:subPackages>
    <pak:packageRef adtcore:uri="/sap/bc/adt/packages/%24iamtheking_doc" adtcore:type="DEVC/K" adtcore:name="$IAMTHEKING_DOC" adtcore:description="Documentation stuff"/>
    <pak:packageRef adtcore:uri="/sap/bc/adt/packages/%24iamtheking_src" adtcore:type="DEVC/K" adtcore:name="$IAMTHEKING_SRC" adtcore:description="Production source codes"/>
    <pak:packageRef adtcore:uri="/sap/bc/adt/packages/%24iamtheking_tests" adtcore:type="DEVC/K" adtcore:name="$IAMTHEKING_TESTS" adtcore:description="Package with Tests"/>
  </pak:subPackages>
</pak:package>
'''

GET_PACKAGE_ADT_XML_NOT_FOUND='''<?xml version="1.0" encoding="utf-8"?>
<exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework">
  <namespace id="com.sap.adt"/>
  <type id="ExceptionResourceNotFound"/>
  <message lang="EN">Error while importing object PKG_NAME from the database.</message>
  <localizedMessage lang="EN">Error while importing object PKG_NAME from the database.</localizedMessage>
  <properties/>
</exc:exception>
'''.replace('\n', '').replace('\r', '')
