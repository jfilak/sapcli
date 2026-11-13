# The entity protected by the access control
DDLS_NAME = 'ZSAPCLI_CDS'

DCLS_NAME = 'ZSAPCLI_DCL'

DCLS_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DCLS" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DCLS>
    <DCLNAME>{DCLS_NAME}</DCLNAME>
    <DCLLANGUAGE>E</DCLLANGUAGE>
    <DDTEXT>Test access control</DDTEXT>
   </DCLS>
  </asx:values>
 </asx:abap>
</abapGit>
'''

# abapGit writes ABAP_LANGUAGE_VERSION depending on the repository settings
DCLS_ABAP_LANGUAGE_VERSION_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DCLS" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DCLS>
    <DCLNAME>{DCLS_NAME}</DCLNAME>
    <DCLLANGUAGE>E</DCLLANGUAGE>
    <DDTEXT>Test access control</DDTEXT>
    <ABAP_LANGUAGE_VERSION>5</ABAP_LANGUAGE_VERSION>
   </DCLS>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DCLS_SOURCE_CODE = f'''@EndUserText.label: 'Test access control'
@MappingRole: true
define role {DCLS_NAME} {{
  grant select on {DDLS_NAME}
    where ( object ) = aspect pfcg_auth( s_develop, objtype, actvt = '03' );
}}
'''

DCLS_ADT_NEW_OBJECT_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<dcl:dclSource xmlns:dcl="http://www.sap.com/adt/acm/dclsources" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DCLS/DL" adtcore:description="Test access control" adtcore:language="EN" adtcore:name="{DCLS_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
</dcl:dclSource>'''

DCLS_ADT_ALREADY_EXISTS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="com.sap.adt"/><type id="ExceptionResourceAlreadyExists"/><message lang="EN">Resource Access Control {DCLS_NAME} does already exist.</message><localizedMessage lang="EN">Resource Access Control {DCLS_NAME} does already exist.</localizedMessage><properties/></exc:exception>'''

DCLS_ADT_GET_RESPONSE_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<dcl:dclSource xmlns:dcl="http://www.sap.com/adt/acm/dclsources" abapsource:sourceUri="source/main" abapsource:fixPointArithmetic="false" abapsource:activeUnicodeCheck="false" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:abapLanguageVersion="standard" adtcore:name="{DCLS_NAME}" adtcore:type="DCLS/DL" adtcore:changedAt="2026-10-20T13:21:01Z" adtcore:version="active" adtcore:createdAt="2026-10-20T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="Test access control" adtcore:language="EN" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:packageName="$TMP" adtcore:description="Local objects"/>
</dcl:dclSource>
'''

CHECKOUT_DCLS_SOURCE_CODE = f'''@EndUserText.label: 'Test access control'
@MappingRole: true
define role {DCLS_NAME} {{
  grant select on {DDLS_NAME}
    where ( object ) = aspect pfcg_auth( s_develop, objtype, actvt = '03' );
}}'''

DCLS_ABAPGIT_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DCLS" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DCLS>
    <DCLNAME>{DCLS_NAME}</DCLNAME>
    <DCLLANGUAGE>E</DCLLANGUAGE>
    <DDTEXT>Test access control</DDTEXT>
   </DCLS>
  </asx:values>
 </asx:abap>
</abapGit>
'''
