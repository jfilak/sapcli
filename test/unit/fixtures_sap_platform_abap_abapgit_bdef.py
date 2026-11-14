# The entity the behavior is defined for
DDLS_NAME = 'ZSAPCLI_CDS'

BDEF_NAME = 'ZSAPCLI_BDEF'

# abapGit stores the workbench object metadata as returned by ADT
BDEF_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_BDEF" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <BDEF>
    <NAME>{BDEF_NAME}</NAME>
    <TYPE>BDEF/BDO</TYPE>
    <DESCRIPTION>Test behavior definition</DESCRIPTION>
    <DESCRIPTION_TEXT_LIMIT>60</DESCRIPTION_TEXT_LIMIT>
    <LANGUAGE>EN</LANGUAGE>
    <LINKS>
     <item>
      <HREF>./{BDEF_NAME.lower()}/source/main/versions</HREF>
      <REL>http://www.sap.com/adt/relations/versions</REL>
      <TITLE>Historic versions</TITLE>
     </item>
     <item>
      <HREF>./{BDEF_NAME.lower()}/source/main</HREF>
      <REL>http://www.sap.com/adt/relations/source</REL>
      <TYPE>text/plain</TYPE>
      <TITLE>Source Content</TITLE>
     </item>
    </LINKS>
    <MASTER_LANGUAGE>EN</MASTER_LANGUAGE>
    <ABAP_LANGU_VERSION>X</ABAP_LANGU_VERSION>
    <SOURCE_URI>./{BDEF_NAME.lower()}/source/main</SOURCE_URI>
    <SOURCE_TYPE>ABAP_SOURCE</SOURCE_TYPE>
    <SOURCE_FIXED_POINT_ARITHMETIC>true</SOURCE_FIXED_POINT_ARITHMETIC>
    <SOURCE_UNICODE_CHECKS_ACTIVE>true</SOURCE_UNICODE_CHECKS_ACTIVE>
   </BDEF>
  </asx:values>
 </asx:abap>
</abapGit>
'''

BDEF_SOURCE_CODE = f'''managed implementation in class zbp_sapcli_bdef unique;
strict ( 2 );

define behavior for {DDLS_NAME} alias Root
persistent table tadir
lock master
authorization master ( instance )
{{
  create;
  update;
  delete;
}}'''

BDEF_ADT_NEW_OBJECT_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="BDEF/BDO" adtcore:description="Test behavior definition" adtcore:language="EN" adtcore:name="{BDEF_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
</blue:blueSource>'''

BDEF_ADT_ALREADY_EXISTS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="com.sap.adt"/><type id="ExceptionResourceAlreadyExists"/><message lang="EN">Resource Behavior Definition {BDEF_NAME} does already exist.</message><localizedMessage lang="EN">Resource Behavior Definition {BDEF_NAME} does already exist.</localizedMessage><properties/></exc:exception>'''

# The file zroot_cds.bdef.xml of the repository abapGit-tests/BDEF with replaced name and description
BDEF_ABAPGIT_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_BDEF" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <BDEF>
    <NAME>{BDEF_NAME}</NAME>
    <TYPE>BDEF/BDO</TYPE>
    <DESCRIPTION>Test behavior definition</DESCRIPTION>
    <DESCRIPTION_TEXT_LIMIT>60</DESCRIPTION_TEXT_LIMIT>
    <LANGUAGE>EN</LANGUAGE>
    <LINKS>
     <item>
      <HREF>./{BDEF_NAME.lower()}/source/main/versions</HREF>
      <REL>http://www.sap.com/adt/relations/versions</REL>
      <TITLE>Historic versions</TITLE>
     </item>
     <item>
      <HREF>/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fbo%2Fbehaviordefinitions%2F{BDEF_NAME.lower()}</HREF>
      <REL>http://www.sap.com/adt/relations/informationsystem/abaplanguageversions</REL>
      <TYPE>application/vnd.sap.adt.nameditems.v1+xml</TYPE>
      <TITLE>Allowed ABAP language versions</TITLE>
     </item>
     <item>
      <HREF>./{BDEF_NAME.lower()}/source/main</HREF>
      <REL>http://www.sap.com/adt/relations/source</REL>
      <TYPE>text/plain</TYPE>
      <TITLE>Source Content</TITLE>
     </item>
     <item>
      <HREF>./{BDEF_NAME.lower()}/source/main</HREF>
      <REL>http://www.sap.com/adt/relations/source</REL>
      <TYPE>text/html</TYPE>
      <TITLE>Source Content (HTML)</TITLE>
     </item>
    </LINKS>
    <MASTER_LANGUAGE>EN</MASTER_LANGUAGE>
    <ABAP_LANGU_VERSION>X</ABAP_LANGU_VERSION>
    <SOURCE_URI>./{BDEF_NAME.lower()}/source/main</SOURCE_URI>
    <SOURCE_TYPE>ABAP_SOURCE</SOURCE_TYPE>
    <SOURCE_FIXED_POINT_ARITHMETIC>true</SOURCE_FIXED_POINT_ARITHMETIC>
    <SOURCE_UNICODE_CHECKS_ACTIVE>true</SOURCE_UNICODE_CHECKS_ACTIVE>
   </BDEF>
  </asx:values>
 </asx:abap>
</abapGit>
'''

