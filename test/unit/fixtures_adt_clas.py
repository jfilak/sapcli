CREATE_CLASS_ADT_XML="""<?xml version="1.0" encoding="UTF-8"?>
<class:abapClass xmlns:class="http://www.sap.com/adt/oo/classes" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="CLAS/OC" adtcore:description="Say hello!" adtcore:language="EN" adtcore:name="ZCL_HELLO_WORLD" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:responsible="FILAK" class:final="true" class:visibility="public">
<adtcore:packageRef adtcore:name="$TEST"/>
<class:include adtcore:name="CLAS/OC" adtcore:type="CLAS/OC" class:includeType="testclasses"/>
<class:superClassRef/>
</class:abapClass>"""

GET_CLASS_ADT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<class:abapClass xmlns:class="http://www.sap.com/adt/oo/classes" xmlns:abapoo="http://www.sap.com/adt/oo" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:adtcore="http://www.sap.com/adt/core" class:final="true" class:abstract="false" class:visibility="public" class:category="generalObjectType" class:sharedMemoryEnabled="false" abapoo:modeled="false" abapsource:fixPointArithmetic="true" abapsource:activeUnicodeCheck="true" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:name="ZCL_HELLO_WORLD" adtcore:type="CLAS/OC" adtcore:changedAt="2019-03-07T20:22:01Z" adtcore:version="active" adtcore:createdAt="2019-02-02T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="You cannot stop me!" adtcore:descriptionTextLimit="60" adtcore:language="EN">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="objectstructure" rel="http://www.sap.com/adt/relations/objectstructure" type="application/vnd.sap.adt.objectstructure.v2+xml"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/vit/wb/object_type/clasocx/object_name/ZCL_HELLO_WORLD" rel="http://www.sap.com/adt/relations/sources/textelements" type="application/vnd.sap.sapgui" title="Text elements"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/oo/classes/zcl_hello_world/source/main?withAbapDocFromShortTexts=true" rel="http://www.sap.com/adt/relations/sources/withabapdocfromshorttexts" type="text/plain" title="Source with ABAP Doc"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/oo/classes/zcl_hello_world/transports" rel="http://www.sap.com/adt/relations/transport" type="application/vnd.sap.as+xml;charset=utf-8;dataname=com.sap.adt.lock.result2" title="Related Transport Requests"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/classifications?uri=/sap/bc/adt/oo/classes/zcl_hello_world" rel="http://www.sap.com/adt/categories/classifications" type="application/vnd.sap.adt.classifications+xml" title="Classifications"/>
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24iamtheking" adtcore:type="DEVC/K" adtcore:name="$IAMTHEKING"/>
  <abapsource:syntaxConfiguration>
    <abapsource:language>
      <abapsource:version>X</abapsource:version>
      <abapsource:description>Standard ABAP (Unicode)</abapsource:description>
      <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/abapsource/parsers/rnd/grammar" rel="http://www.sap.com/adt/relations/abapsource/parser" type="text/plain" title="Standard ABAP (Unicode)" etag="752"/>
    </abapsource:language>
  </abapsource:syntaxConfiguration>
  <class:include class:includeType="definitions" abapsource:sourceUri="includes/definitions" adtcore:name="" adtcore:type="CLAS/I" adtcore:changedAt="2019-03-07T20:22:01Z" adtcore:version="active" adtcore:createdAt="2019-02-02T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER">
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="includes/definitions/versions" rel="http://www.sap.com/adt/relations/versions"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="includes/definitions" rel="http://www.sap.com/adt/relations/source" type="text/plain" etag="201903072022010011"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="includes/definitions" rel="http://www.sap.com/adt/relations/source" type="text/html" etag="201903072022010011"/>
  </class:include>
  <class:include class:includeType="implementations" abapsource:sourceUri="includes/implementations" adtcore:name="" adtcore:type="CLAS/I" adtcore:changedAt="2019-03-07T20:22:01Z" adtcore:version="active" adtcore:createdAt="2019-02-02T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER">
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="includes/implementations/versions" rel="http://www.sap.com/adt/relations/versions"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="includes/implementations" rel="http://www.sap.com/adt/relations/source" type="text/plain" etag="201903072022010011"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="includes/implementations" rel="http://www.sap.com/adt/relations/source" type="text/html" etag="201903072022010011"/>
  </class:include>
  <class:include class:includeType="macros" abapsource:sourceUri="includes/macros" adtcore:name="" adtcore:type="CLAS/I" adtcore:changedAt="2019-02-02T13:01:06Z" adtcore:version="active" adtcore:createdAt="2019-02-02T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER">
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="includes/macros/versions" rel="http://www.sap.com/adt/relations/versions"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="includes/macros" rel="http://www.sap.com/adt/relations/source" type="text/plain" etag="201902021301060011"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="includes/macros" rel="http://www.sap.com/adt/relations/source" type="text/html" etag="201902021301060011"/>
  </class:include>
  <class:include class:includeType="testclasses" abapsource:sourceUri="includes/testclasses" adtcore:name="" adtcore:type="CLAS/I" adtcore:changedAt="2019-02-02T13:01:06Z" adtcore:version="active" adtcore:createdAt="2019-02-02T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER">
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="includes/testclasses/versions" rel="http://www.sap.com/adt/relations/versions"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="includes/testclasses" rel="http://www.sap.com/adt/relations/source" type="text/plain" etag="201902021301060011"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="includes/testclasses" rel="http://www.sap.com/adt/relations/source" type="text/html" etag="201902021301060011"/>
  </class:include>
  <class:include class:includeType="main" abapsource:sourceUri="source/main" adtcore:name="" adtcore:type="CLAS/I" adtcore:changedAt="2019-02-02T13:01:06Z" adtcore:version="active" adtcore:createdAt="2019-02-02T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER">
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="includes/main/versions" rel="http://www.sap.com/adt/relations/versions"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="source/main" rel="http://www.sap.com/adt/relations/source" type="text/plain" etag="20190202130106001000001"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="source/main" rel="http://www.sap.com/adt/relations/source" type="text/html" etag="20190202130106001000001"/>
  </class:include>
</class:abapClass>'''

WRITE_INCLUDE_ERROR_XML = '''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="com.sap.adt"/><type id="ExceptionResourceSaveFailure"/><message lang="EN">TEST=====CCAU does not have any inactive version</message></exc:exception>'''

GENERATE_INCLUDE_REQUEST_XML = '''<?xml version="1.0" encoding="UTF-8"?><class:abapClassInclude xmlns:class="http://www.sap.com/adt/oo/classes" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:name="dummy" class:includeType="testclasses"/>'''
