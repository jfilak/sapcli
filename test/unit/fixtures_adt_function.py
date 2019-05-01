"""Function Group/Module Fixtures"""

CREATE_FUNCTION_GROUP_ADT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<group:abapFunctionGroup xmlns:group="http://www.sap.com/adt/functions/groups" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="FUGR/F" adtcore:description="Hello FUGR!" adtcore:language="EN" adtcore:name="ZFG_HELLO_WORLD" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:responsible="FILAK">
<adtcore:packageRef adtcore:name="$TEST"/>
</group:abapFunctionGroup>"""

CLI_CREATE_FUNCTION_GROUP_ADT_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<group:abapFunctionGroup xmlns:group="http://www.sap.com/adt/functions/groups" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="FUGR/F" adtcore:description="Hello FUGR!" adtcore:language="EN" adtcore:name="ZFG_HELLO_WORLD" adtcore:masterLanguage="EN" adtcore:responsible="FILAK">
<adtcore:packageRef adtcore:name="$TEST"/>
</group:abapFunctionGroup>'''

CREATE_FUNCTION_MODULE_ADT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<fmodule:abapFunctionModule xmlns:fmodule="http://www.sap.com/adt/functions/fmodules" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="FUGR/FF" adtcore:description="Hello Function!" adtcore:name="Z_FN_HELLO_WORLD">
<adtcore:containerRef adtcore:name="ZFG_HELLO_WORLD" adtcore:type="FUGR/F" adtcore:uri="/sap/bc/adt/functions/groups/zfg_hello_world"/>
</fmodule:abapFunctionModule>"""

GET_FUNCTION_GROUP_ADT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<group:abapFunctionGroup xmlns:group="http://www.sap.com/adt/functions/groups" group:lockedByEditor="false" abapsource:sourceUri="source/main" abapsource:fixPointArithmetic="true" abapsource:activeUnicodeCheck="true" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:name="ZFG_HELLO_WORLD" adtcore:type="FUGR/F" adtcore:changedAt="2019-04-24T18:14:01Z" adtcore:version="active" adtcore:createdAt="2019-04-24T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="You cannot stop me!" adtcore:descriptionTextLimit="40" adtcore:language="EN" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="source/main/versions" rel="http://www.sap.com/adt/relations/versions"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="source/main" rel="http://www.sap.com/adt/relations/source" type="text/plain" etag="201904241814010011"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="source/main" rel="http://www.sap.com/adt/relations/source" type="text/html" etag="201904241814010011"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/vit/wb/object_type/progpx/object_name/SAPLZFG_HELLO_WORLD" rel="http://www.sap.com/adt/relations/sources/textelements" type="application/vnd.sap.sapgui" title="Text elements"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="./zfg_hello_world/objectstructure" rel="http://www.sap.com/adt/relations/objectstructure" type="application/vnd.sap.adt.objectstructure.v2+xml"/>
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24test" adtcore:type="DEVC/K" adtcore:name="$TEST"/>
  <abapsource:syntaxConfiguration>
    <abapsource:language>
      <abapsource:version>X</abapsource:version>
      <abapsource:description>Standard ABAP (Unicode)</abapsource:description>
      <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/abapsource/parsers/rnd/grammar" rel="http://www.sap.com/adt/relations/abapsource/parser" type="text/plain" title="Standard ABAP (Unicode)" etag="752"/>
    </abapsource:language>
  </abapsource:syntaxConfiguration>
</group:abapFunctionGroup>
"""

GET_FUNCTION_MODULE_ADT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<fmodule:abapFunctionModule xmlns:fmodule="http://www.sap.com/adt/functions/fmodules" fmodule:releaseState="notReleased" fmodule:processingType="normal" abapsource:sourceUri="source/main" adtcore:name="Z_FN_HELLO_WORLD" adtcore:type="FUGR/FF" adtcore:changedAt="2019-04-24T18:19:16Z" adtcore:version="inactive" adtcore:createdAt="2019-04-24T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:description="You cannot stop me!" adtcore:descriptionTextLimit="74" adtcore:language="EN" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:containerRef adtcore:uri="/sap/bc/adt/functions/groups/zfg_hello_world" adtcore:type="FUGR/F" adtcore:name="ZFG_HELLO_WORLD" adtcore:packageName="$TEST"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="source/main/versions" rel="http://www.sap.com/adt/relations/versions"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="source/main" rel="http://www.sap.com/adt/relations/source" type="text/plain" etag="201904241819160001"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="source/main" rel="http://www.sap.com/adt/relations/source" type="text/html" etag="201904241819160001"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/vit/wb/object_type/progpx/object_name/SAPLZFG_HELLO_WORLD" rel="http://www.sap.com/adt/relations/sources/textelements" type="application/vnd.sap.sapgui" title="Text elements"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/functions/groups/zfg_hello_world/fmodules/z_fn_hello_world/source/main?version=active" rel="http://www.sap.com/adt/relations/objectstates" title="Reference to active or inactive version"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/classifications?uri=/sap/bc/adt/functions/groups/zfg_hello_world/fmodules/z_fn_hello_world/source/main" rel="http://www.sap.com/adt/categories/classifications" type="application/vnd.sap.adt.classifications+xml" title="Classifications"/>
</fmodule:abapFunctionModule>
"""

PUT_FUNCITON_MODULE_ADT_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<fmodule:abapFunctionModule xmlns:fmodule="http://www.sap.com/adt/functions/fmodules" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="FUGR/FF" adtcore:description="You cannot stop me!" adtcore:name="Z_FN_HELLO_WORLD" adtcore:version="inactive" fmodule:processingType="rfc" fmodule:releaseState="notReleased">
<adtcore:containerRef adtcore:name="ZFG_HELLO_WORLD" adtcore:type="FUGR/F" adtcore:uri="/sap/bc/adt/functions/groups/zfg_hello_world" adtcore:packageName="$TEST"/>
</fmodule:abapFunctionModule>'''
