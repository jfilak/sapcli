# The entity annotated by the metadata extension
DDLS_NAME = 'ZSAPCLI_CDS'

DDLX_NAME = 'ZSAPCLI_DDLX'

DDLX_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DDLX" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DDLX>
    <METADATA>
     <NAME>{DDLX_NAME}</NAME>
     <DESCRIPTION>Test metadata extension</DESCRIPTION>
     <MASTER_LANGUAGE>EN</MASTER_LANGUAGE>
    </METADATA>
   </DDLX>
  </asx:values>
 </asx:abap>
</abapGit>
'''

# abapGit reads ABAP_LANGU_VERSION of the workbench object metadata
DDLX_ABAP_LANGUAGE_VERSION_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DDLX" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DDLX>
    <METADATA>
     <NAME>{DDLX_NAME}</NAME>
     <DESCRIPTION>Test metadata extension</DESCRIPTION>
     <MASTER_LANGUAGE>EN</MASTER_LANGUAGE>
     <ABAP_LANGU_VERSION>5</ABAP_LANGU_VERSION>
    </METADATA>
   </DDLX>
  </asx:values>
 </asx:abap>
</abapGit>
'''

# abapGit writes the source code as it is - without the trailing new line
DDLX_SOURCE_CODE = f'''@Metadata.layer: #CORE
annotate entity {DDLS_NAME} with
{{
  @UI.lineItem: [{{ position: 10 }}]
  pgmid;
}}'''

DDLX_ADT_NEW_OBJECT_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<ddlx:ddlxSource xmlns:ddlx="http://www.sap.com/adt/ddic/ddlxsources" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DDLX/EX" adtcore:description="Test metadata extension" adtcore:language="EN" adtcore:name="{DDLX_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
</ddlx:ddlxSource>'''

DDLX_ADT_ALREADY_EXISTS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="com.sap.adt"/><type id="ExceptionResourceAlreadyExists"/><message lang="EN">Resource Metadata Extension {DDLX_NAME} does already exist.</message><localizedMessage lang="EN">Resource Metadata Extension {DDLX_NAME} does already exist.</localizedMessage><properties/></exc:exception>'''

DDLX_ADT_GET_RESPONSE_XML = f'''<?xml version="1.0" encoding="UTF-8"?><ddlx:ddlxSource xmlns:ddlx="http://www.sap.com/adt/ddic/ddlxsources" abapsource:sourceUri="./{DDLX_NAME.lower()}/source/main" abapsource:fixPointArithmetic="false" abapsource:activeUnicodeCheck="false" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:abapLanguageVersion="standard" adtcore:name="{DDLX_NAME}" adtcore:type="DDLX/EX" adtcore:changedAt="2026-10-20T21:33:07Z" adtcore:version="active" adtcore:createdAt="2026-10-20T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="Test metadata extension" adtcore:language="EN" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:packageName="$TMP" adtcore:description="Local objects"/>
</ddlx:ddlxSource>'''

DDLX_ABAPGIT_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DDLX" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DDLX>
    <METADATA>
     <NAME>{DDLX_NAME}</NAME>
     <DESCRIPTION>Test metadata extension</DESCRIPTION>
     <MASTER_LANGUAGE>EN</MASTER_LANGUAGE>
    </METADATA>
   </DDLX>
  </asx:values>
 </asx:abap>
</abapGit>
'''
