"""Test fixtures for the ADT CDS Metadata Extension (DDLX)"""

METADATA_EXTENSION_NAME = 'Z_TEST_MD_EXT_V0'

METADATA_EXTENSION_ADT_GET_EXISTING_RESPONSE_XML = '''<?xml version="1.0" encoding="UTF-8"?><ddlx:ddlxSource xmlns:ddlx="http://www.sap.com/adt/ddic/ddlxsources" abapsource:sourceUri="./z_test_md_ext_v0/source/main" abapsource:fixPointArithmetic="false" abapsource:activeUnicodeCheck="false" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="C50" adtcore:abapLanguageVersion="standard" adtcore:name="Z_TEST_MD_EXT_V0" adtcore:type="DDLX/EX" adtcore:changedAt="2026-07-14T21:33:07Z" adtcore:version="inactive" adtcore:createdAt="2026-07-14T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="dfadfa" adtcore:language="EN" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="./z_test_md_ext_v0/source/main/versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Fddlx%2Fsources%2Fz_test_md_ext_v0" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" type="application/vnd.sap.adt.nameditems.v1+xml" title="Allowed ABAP language versions"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="./z_test_md_ext_v0/source/main" rel="http://www.sap.com/adt/relations/source" type="text/plain" title="Source Content" etag="19710401000000000text/plain_qLXiffCDlHrWywTkZHRHUXK3Vgw="/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="./z_test_md_ext_v0/source/main" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Source Content (HTML)" etag=""/>
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:description="Temporary Objects (never transported!)"/>
</ddlx:ddlxSource>'''

# The captured POST request declared the namespace with the prefix
# "ddlxsources" while the GET response declares the same namespace URI with
# the prefix "ddlx". sapcli uses a single namespace declaration per object for
# both serialization and deserialization, so the "ddlx" prefix (the one used by
# the server in its responses, which sapcli must parse) is used consistently.
# XML namespace prefixes are arbitrary tokens bound to a URI, so the server
# accepts the POST regardless of the prefix.
METADATA_EXTENSION_ADT_NEW_OBJECT_REQUEST_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<ddlx:ddlxSource xmlns:ddlx="http://www.sap.com/adt/ddic/ddlxsources" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DDLX/EX" adtcore:description="dfadfa" adtcore:language="EN" adtcore:name="Z_TEST_MD_EXT_V0" adtcore:masterLanguage="EN" adtcore:masterSystem="C50" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
</ddlx:ddlxSource>'''

METADATA_EXTENSION_CODE = '''@Metadata.layer: #CORE
annotate view Z_TEST_MD_EXT_V0 with
{
}
'''

# GET response of an active object - used to verify the activation flow which
# fetches the object afterwards to check its activation status.
METADATA_EXTENSION_ADT_GET_ACTIVE_RESPONSE_XML = METADATA_EXTENSION_ADT_GET_EXISTING_RESPONSE_XML.replace(
    'adtcore:version="inactive"', 'adtcore:version="active"')
