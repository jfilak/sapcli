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


SERVICE_BINDING_NAME = 'ZSAPCLI_TEST_BND'
SERVICE_BINDING_PACKAGE = '$TMP'

SERVICE_BINDING_ADT_POST_ODATA_V4_REQUEST_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<srvb:serviceBinding xmlns:srvb="http://www.sap.com/adt/ddic/ServiceBindings" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="SRVB/SVB" adtcore:description="Test service binding" adtcore:language="EN" adtcore:name="ZSAPCLI_TEST_BND" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
<srvb:services>
<srvb:content srvb:version="0001" srvb:releaseState="NOT_RELEASED">
<srvb:serviceDefinition adtcore:type="SRVD/SRV" adtcore:name="ZSAPCLI_TEST_SRV"/>
</srvb:content>
</srvb:services>
<srvb:binding srvb:type="ODATA" srvb:version="V4" srvb:category="0">
<srvb:implementation adtcore:name="ZSAPCLI_TEST_BND"/>
</srvb:binding>
</srvb:serviceBinding>'''


SERVICE_BINDING_ADT_GET_V4_XML = '''<?xml version="1.0" encoding="utf-8"?>
<srvb:serviceBinding xmlns:srvb="http://www.sap.com/adt/ddic/ServiceBindings" xmlns:adtcore="http://www.sap.com/adt/core" srvb:contract="C1" srvb:releaseSupported="true" srvb:published="false" srvb:bindingCreated="true" adtcore:name="ZSAPCLI_TEST_BND" adtcore:type="SRVB/SVB" adtcore:version="active" adtcore:description="Test service binding" adtcore:language="EN">
<adtcore:packageRef adtcore:name="$TMP" adtcore:type="DEVC/K"/>
<srvb:services srvb:name="ZSAPCLI_TEST_BND">
<srvb:content srvb:version="0001" srvb:releaseState="NOT_RELEASED">
<srvb:serviceDefinition adtcore:uri="/sap/bc/adt/ddic/srvd/sources/zsapcli_test_srv" adtcore:type="SRVD/SRV" adtcore:name="ZSAPCLI_TEST_SRV"/>
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
