SERVICE_DEFINITION_NAME = 'ZSAPCLI_TEST_SRV'
SERVICE_DEFINITION_PACKAGE = '$TMP'

SERVICE_DEFINITION_SOURCE_TEXT = '''@EndUserText.label: 'Test service definition'
define service ZSAPCLI_TEST_SRV {
  expose ZSAPCLI_TEST_VIEW as Travel;
}
'''

SERVICE_DEFINITION_ADT_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<srvd:srvdSource xmlns:srvd="http://www.sap.com/adt/ddic/srvdsources"
 srvd:sourceOrigin="0"
 srvd:sourceOriginDescription="ABAP Development Tools"
 srvd:srvdSourceType="S"
 srvd:srvdSourceTypeDescription="Service Definition"
 abapsource:sourceUri="./example_config_srv/source/main"
 abapsource:fixPointArithmetic="false"
 abapsource:activeUnicodeCheck="false"
 adtcore:responsible="DEVELOPER"
 adtcore:masterLanguage="EN"
 adtcore:masterSystem="M62"
 adtcore:name="EXAMPLE_CONFIG_SRV"
 adtcore:type="SRVD/SRV"
 adtcore:changedAt="1971-04-01T00:00:00Z"
 adtcore:version="active"
 adtcore:createdAt="2021-03-26T00:00:00Z"
 adtcore:createdBy="DEVELOPER"
 adtcore:description="Example Configuration"
 adtcore:language="EN"
 xmlns:abapsource="http://www.sap.com/adt/abapsource"
 xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
   href="./example_config_srv/source/main"
   rel="http://www.sap.com/adt/relations/source"
   type="text/plain"
   title="Source Content"
   etag="19710401000000001text/plain_h1L0yDw6awd+pjz7ZFAq756mm4I="/>
  <atom:link
   xmlns:atom="http://www.w3.org/2005/Atom"
   href="./example_config_srv/source/main"
   rel="http://www.sap.com/adt/relations/source"
   type="text/html"
   title="Source Content (HTML)"
   etag=""/>
  <atom:link
   xmlns:atom="http://www.w3.org/2005/Atom"
   href="./example_config_srv/source/main/versions"
   rel="http://www.sap.com/adt/relations/versions"
   title="Historic versions"/>
  <adtcore:packageRef
   adtcore:uri="/sap/bc/adt/packages/example_config"
   adtcore:type="DEVC/K"
   adtcore:name="EXAMPLE_CONFIG"
   adtcore:description="Config App"/>
</srvd:srvdSource>'''


SERVICE_DEFINITION_ADT_POST_REQUEST_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<srvd:srvdSource xmlns:srvd="http://www.sap.com/adt/ddic/srvdsources" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="SRVD/SRV" adtcore:description="Test service definition" adtcore:language="EN" adtcore:name="ZSAPCLI_TEST_SRV" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER" srvd:srvdSourceType="S">
<adtcore:packageRef adtcore:name="$TMP"/>
</srvd:srvdSource>'''


SERVICE_DEFINITION_ADT_POST_REQUEST_XML_EXTENSION = '''<?xml version="1.0" encoding="UTF-8"?>
<srvd:srvdSource xmlns:srvd="http://www.sap.com/adt/ddic/srvdsources" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="SRVD/SRV" adtcore:description="Test service definition" adtcore:language="EN" adtcore:name="ZSAPCLI_TEST_SRV" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER" srvd:srvdSourceType="X">
<adtcore:packageRef adtcore:name="$TMP"/>
</srvd:srvdSource>'''


SERVICE_BINDING_NAME = 'ZSAPCLI_TEST_BND'
SERVICE_BINDING_PACKAGE = '$TMP'

SERVICE_BINDING_ADT_POST_ODATA_V4_REQUEST_XML_UI = '''<?xml version="1.0" encoding="UTF-8"?>
<srvb:serviceBinding xmlns:srvb="http://www.sap.com/adt/ddic/ServiceBindings" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="SRVB/SVB" adtcore:description="Test service binding" adtcore:language="EN" adtcore:name="ZSAPCLI_TEST_BND" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
<srvb:services srvb:name="ZSAPCLI_TEST_BND">
<srvb:content srvb:version="0001" srvb:releaseState="NOT_RELEASED">
<srvb:serviceDefinition adtcore:type="SRVD/SRV" adtcore:name="ZSAPCLI_TEST_SRV"/>
</srvb:content>
</srvb:services>
<srvb:binding srvb:type="ODATA" srvb:version="V4" srvb:category="0">
<srvb:implementation adtcore:name=""/>
</srvb:binding>
</srvb:serviceBinding>'''


SERVICE_BINDING_ADT_POST_ODATA_V4_REQUEST_XML_API = '''<?xml version="1.0" encoding="UTF-8"?>
<srvb:serviceBinding xmlns:srvb="http://www.sap.com/adt/ddic/ServiceBindings" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="SRVB/SVB" adtcore:description="Test service binding" adtcore:language="EN" adtcore:name="ZSAPCLI_TEST_BND" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
<srvb:services srvb:name="ZSAPCLI_TEST_BND">
<srvb:content srvb:version="0001" srvb:releaseState="NOT_RELEASED">
<srvb:serviceDefinition adtcore:type="SRVD/SRV" adtcore:name="ZSAPCLI_TEST_SRV"/>
</srvb:content>
</srvb:services>
<srvb:binding srvb:type="ODATA" srvb:version="V4" srvb:category="1">
<srvb:implementation adtcore:name=""/>
</srvb:binding>
</srvb:serviceBinding>'''


SERVICE_BINDING_ADT_GET_V4_XML = '''<?xml version="1.0" encoding="utf-8"?>
<srvb:serviceBinding xmlns:srvb="http://www.sap.com/adt/ddic/ServiceBindings" xmlns:adtcore="http://www.sap.com/adt/core" srvb:contract="C1" srvb:releaseSupported="true" srvb:published="false" srvb:bindingCreated="true" srvb:allowedAction="PUBLISH" adtcore:name="ZSAPCLI_TEST_BND" adtcore:type="SRVB/SVB" adtcore:version="active" adtcore:description="Test service binding" adtcore:language="EN">
<adtcore:packageRef adtcore:name="$TMP" adtcore:type="DEVC/K"/>
<srvb:services srvb:name="ZSAPCLI_TEST_BND">
<srvb:content srvb:version="0001" srvb:minorVersion="0" srvb:patchVersion="0" srvb:buildVersion="" srvb:releaseState="NOT_RELEASED">
<srvb:serviceDefinition adtcore:uri="/sap/bc/adt/ddic/srvd/sources/zsapcli_test_srv" adtcore:type="SRVD/SRV" adtcore:name="ZSAPCLI_TEST_SRV"/>
<srvb:bindingTypeData>
<adtcore:content adtcore:encoding="base64"/>
</srvb:bindingTypeData>
</srvb:content>
</srvb:services>
<srvb:binding srvb:type="ODATA" srvb:version="V4" srvb:category="0">
<srvb:implementation adtcore:name="ZSAPCLI_TEST_BND"/>
</srvb:binding>
</srvb:serviceBinding>'''


SERVICE_BINDING_PUBLISH_OK_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
    <DATA>
      <SEVERITY>OK</SEVERITY>
      <SHORT_TEXT>Service published successfully</SHORT_TEXT>
      <LONG_TEXT/>
    </DATA>
  </asx:values>
</asx:abap>
'''


SERVICE_BINDING_PUBLISH_FAIL_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
    <DATA>
      <SEVERITY>ERROR</SEVERITY>
      <SHORT_TEXT>Local Publish of ZSAPCLI_TEST_SRV failed</SHORT_TEXT>
      <LONG_TEXT>Service Binding ZSAPCLI_TEST_BND does not exist.</LONG_TEXT>
    </DATA>
  </asx:values>
</asx:abap>
'''

SERVICE_GROUP_ODATAV4_GET_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<odatav4:serviceGroup xmlns:odatav4="http://www.sap.com/categories/odatav4" odatav4:published="true" odatav4:serviceUrlPrefix="/sap/opu/odata4/sap/zscli_svcdemo_c/srvd/" adtcore:name="ZSCLI_SVCDEMO_C" xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" rel="http://www.sap.com/categories/ui5app" type="application/vnd.sap.adt.businessservices.ui5app.v1+xml" title="Launch UI5 App"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/businessservices/odatav4/publishjobs" rel="http://www.sap.com/categories/odatav4" title="ODATAV4PUBLISH"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/businessservices/odatav4/unpublishjobs" rel="http://www.sap.com/categories/odatav4" title="ODATAV4UNPUBLISH"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" xmlns:n0="SUSH" href="/sap/bc/adt/aps/iam/sush/a41813b73fa2e7ec5a71a92aed3107ht" rel="http://www.sap.com/iam/sush" title="SU22 Object Reference" n0:name="A41813B73FA2E7EC5A71A92AED3107HT"/>
  <odatav4:services odatav4:repositoryId="SRVD" odatav4:serviceId="ZSCLI_SVCDEMO_C" odatav4:serviceVersion="0001" odatav4:serviceUrl="/sap/opu/odata4/sap/zscli_svcdemo_c/srvd/sap/zscli_svcdemo_c/0001/" odatav4:annotationUrl="" odatav4:created="true">
    <serviceInfo:serviceInformation xmlns:serviceInfo="http://www.sap.com/categories/serviceinformation" serviceInfo:name="ZSCLI_SVCDEMO_C" serviceInfo:version="0001">
      <serviceInfo:collection serviceInfo:name="Demo" serviceInfo:isLeading="false" serviceInfo:isRoot="false"/>
      <serviceInfo:collection serviceInfo:name="FourthDemo" serviceInfo:isLeading="false" serviceInfo:isRoot="false"/>
    </serviceInfo:serviceInformation>
    <odatav4:applicationDetails odatav4:applicationState="NOT_DEPLOYED" odatav4:applicationDescription="Not deployed" odatav4:applicationId=""/>
  </odatav4:services>
</odatav4:serviceGroup>
'''

SERVICE_GROUP_ODATAV2_GET_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<odatav2:serviceList xmlns:odatav2="http://www.sap.com/categories/odatav2">
  <odatav2:services odatav2:repositoryId="" odatav2:serviceId="ZSCLI_DM_B_V2" odatav2:serviceVersion="0001" odatav2:serviceUrl="/sap/opu/odata/sap/ZSCLI_DM_B_V2" odatav2:annotationUrl="" odatav2:published="true" odatav2:created="true" odatav2:allowedAction="UNPUBLISH">
    <serviceInfo:serviceInformation xmlns:serviceInfo="http://www.sap.com/categories/serviceinformation" serviceInfo:name="ZSCLI_DM_B_V2" serviceInfo:version="0007">
      <serviceInfo:collection serviceInfo:name="Demo" serviceInfo:isLeading="false" serviceInfo:isRoot="true"/>
      <serviceInfo:collection serviceInfo:name="SecondDemo" serviceInfo:isLeading="true" serviceInfo:isRoot="false"/>
    </serviceInfo:serviceInformation>
    <odatav2:applicationDetails odatav2:applicationState="NOT_DEPLOYED" odatav2:applicationDescription="Not deployed" odatav2:applicationId=""/>
  </odatav2:services>
</odatav2:serviceList>
'''


# The following fixtures pair together to exercise `sapcli srvb preview html`.
# The ENCODEDPATHPARAMS constant is the exact output of the encoding recipe
# documented in `sap/cli/srvb.py::_encode_feap_path_params` applied to the
# components extracted from the two XML fixtures below and the entity set
# named `StatA`.
SERVICE_BINDING_UITEST_NAME = 'ZSCLI_UITEST_B'
SERVICE_GROUP_UITEST_ENTITY_SET = 'StatA'

SERVICE_BINDING_ADT_GET_V4_UITEST_XML = '''<?xml version="1.0" encoding="utf-8"?>
<srvb:serviceBinding xmlns:srvb="http://www.sap.com/adt/ddic/ServiceBindings" xmlns:adtcore="http://www.sap.com/adt/core" srvb:contract="C1" srvb:releaseSupported="true" srvb:published="false" srvb:bindingCreated="true" srvb:allowedAction="PUBLISH" adtcore:name="ZSCLI_UITEST_B" adtcore:type="SRVB/SVB" adtcore:version="active" adtcore:description="UI Test binding" adtcore:language="EN">
<adtcore:packageRef adtcore:name="$TMP" adtcore:type="DEVC/K"/>
<srvb:services srvb:name="ZSCLI_UITEST_B">
<srvb:content srvb:version="0001" srvb:releaseState="NOT_RELEASED">
<srvb:serviceDefinition adtcore:uri="/sap/bc/adt/ddic/srvd/sources/zscli_uitest_b" adtcore:type="SRVD/SRV" adtcore:name="ZSCLI_UITEST_B"/>
</srvb:content>
</srvb:services>
<srvb:binding srvb:type="ODATA" srvb:version="V4" srvb:category="0">
<srvb:implementation adtcore:name="ZSCLI_UITEST_B"/>
</srvb:binding>
</srvb:serviceBinding>'''


SERVICE_GROUP_ODATAV4_UITEST_GET_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<odatav4:serviceGroup xmlns:odatav4="http://www.sap.com/categories/odatav4" odatav4:published="false" odatav4:serviceUrlPrefix="/sap/opu/odata4/sap/zscli_uitest_b/srvd/" adtcore:name="ZSCLI_UITEST_B" xmlns:adtcore="http://www.sap.com/adt/core">
  <odatav4:services odatav4:repositoryId="SRVD" odatav4:serviceId="ZSCLI_UITEST_B" odatav4:serviceVersion="0001" odatav4:serviceUrl="/sap/opu/odata4/sap/zscli_uitest_b/srvd/sap/zscli_uitest_b/0001/" odatav4:annotationUrl="" odatav4:created="true">
    <serviceInfo:serviceInformation xmlns:serviceInfo="http://www.sap.com/categories/serviceinformation" serviceInfo:name="ZSCLI_UITEST_B" serviceInfo:version="0001">
      <serviceInfo:collection serviceInfo:name="StatA" serviceInfo:isLeading="false" serviceInfo:isRoot="false"/>
    </serviceInfo:serviceInformation>
    <odatav4:applicationDetails odatav4:applicationState="NOT_DEPLOYED" odatav4:applicationDescription="Not deployed" odatav4:applicationId=""/>
  </odatav4:services>
</odatav4:serviceGroup>
'''


SERVICE_GROUP_UITEST_ENCODEDPATHPARAMS = (
    'C%C2%87u%C2%84C%C2%83%C2%84%C2%89C%C2%83xu%C2%88uHC%C2%87u%C2%84C%C2%8E%C2%87w%C2%80%7D'
    's%C2%89%7D%C2%88y%C2%87%C2%88svC%C2%87%C2%86%C2%8AxC%C2%87u%C2%84C%C2%8E%C2%87w%C2%80'
    '%7Ds%C2%89%7D%C2%88y%C2%87%C2%88svCDDDEC77g%C2%88u%C2%88U777777ngW%60%5Dsi%5DhYghsV77'
    'DDDE77ngW%60%5Dsi%5DhYghsV'
)
