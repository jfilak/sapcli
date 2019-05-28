CREATE_DCLS_ADT_REQ_XML='''<?xml version="1.0" encoding="UTF-8"?>
<dcl:dclSource xmlns:dcl="http://www.sap.com/adt/acm/dclsources" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DCLS/DL" adtcore:description="You cannot stop me!" adtcore:language="EN" adtcore:name="ZDCLS_HELLO_WORLD" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:responsible="FILAK">
<adtcore:packageRef adtcore:name="$TEST"/>
</dcl:dclSource>'''

# Content-Type: application/vnd.sap.adt.dclSource+xml; charset=utf-8
FETCH_DCLS_ADT_RESP_XML='''<?xml version="1.0" encoding="UTF-8"?>
<dcl:dclSource xmlns:dcl="http://www.sap.com/adt/acm/dclsources" abapsource:sourceUri="source/main" abapsource:fixPointArithmetic="false" abapsource:activeUnicodeCheck="false" adtcore:responsible="FILAK" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:name="ZDCLS_HELLO_WORLD" adtcore:type="DCLS/DL" adtcore:changedAt="2019-05-27T17:25:57Z" adtcore:version="inactive" adtcore:createdAt="2019-05-27T00:00:00Z" adtcore:changedBy="FILAK" adtcore:createdBy="FILAK" adtcore:description="You cannot stop me!" adtcore:language="EN" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="source/main" rel="http://www.sap.com/adt/relations/source" etag="201905271725570002"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="source/main" rel="http://www.sap.com/adt/relations/source" type="text/html" etag="201905271725570002"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="versions" rel="http://www.sap.com/adt/relations/versions"/>
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/$test" adtcore:type="DEVC/K" adtcore:name="$TEST" adtcore:packageName="$TEST" adtcore:description="Tests"/>
</dcl:dclSource>'''

PUT_DCLS_ADT_REQ_XML='''<?xml version="1.0" encoding="UTF-8"?>
<dcl:dclSource xmlns:dcl="http://www.sap.com/adt/acm/dclsources" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:adtcore="http://www.sap.com/adt/core" xmlns:atom="http://www.w3.org/2005/Atom" adtcore:changedAt="2019-05-27T17:38:05Z" adtcore:changedBy="FILAK" adtcore:createdAt="2019-05-27T00:00:00Z" adtcore:createdBy="FILAK" adtcore:description="Unstoppable" adtcore:language="EN" adtcore:name="DCLS_HELLO_WORLD" adtcore:type="DCLS/DL" adtcore:version="active" adtcore:masterLanguage="EN" adtcore:masterSystem="DC0" adtcore:responsible="FILAK" abapsource:activeUnicodeCheck="false" abapsource:fixPointArithmetic="false" abapsource:sourceUri="source/main">
<adtcore:packageRef adtcore:description="Tests" adtcore:name="$TEST" adtcore:packageName="$TEST" adtcore:type="DEVC/K" adtcore:uri="/sap/bc/adt/packages/$test"/>
</dcl:dclSource>'''

ACTIVATION_DCL_REQ_XML='''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/acm/dcl/sources/zdcls_hello_world" adtcore:name="ZDCLS_HELLO_WORLD"/>
</adtcore:objectReferences>'''
