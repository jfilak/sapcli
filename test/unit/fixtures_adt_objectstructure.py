"""Test fixtures for the ADT object structure module"""

# The response of GET /sap/bc/adt/oo/classes/zcl_sapcli_ostruct_probe/objectstructure
# recorded on 2026-11-27, pretty-printed (ADT sends it in one line without the XML declaration)
OBJECT_STRUCTURE_CLASS_XML = \
'''<abapsource:objectStructureElement xmlns:adtcore="http://www.sap.com/adt/core" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:atom="http://www.w3.org/2005/Atom" xml:base="/sap/bc/adt/oo/classes/zcl_sapcli_ostruct_probe/objectstructure?saml2=disabled&amp;sap-client=001" adtcore:name="ZCL_SAPCLI_OSTRUCT_PROBE" visibility="public" abstract="true" adtcore:type="CLAS/OC">
  <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=3,6;end=3,30"/>
  <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./source/main#start=40,6;end=40,30"/>
  <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=3,0;end=36,8"/>
  <atom:link rel="http://www.sap.com/adt/relations/source/implementationBlock" href="./source/main#start=40,0;end=68,8"/>
  <abapsource:objectStructureElement adtcore:type="CLAS/OR" adtcore:name="IF_OO_ADT_CLASSRUN">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=9,15;end=9,33"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./source/main#start=64,9;end=64,32" type="CLAS/OM"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=9,4;end=9,33"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OB" adtcore:name="RUN" visibility="public">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=10,12;end=10,15"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=10,4;end=10,43"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OT" adtcore:name="TY_COUNT" visibility="public">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=12,10;end=12,18"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=12,4;end=12,25"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OT" adtcore:name="TY_PAIR" visibility="public">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=14,15;end=14,22"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=13,4;end=17,20"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OA" constant="true" adtcore:name="CO_ANSWER" level="static" readOnly="true" visibility="public">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=19,14;end=19,23"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=19,4;end=19,39"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OA" adtcore:name="COUNTER" level="instance" readOnly="true" visibility="public">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=20,9;end=20,16"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=20,4;end=20,40"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OA" adtcore:name="INSTANCES" level="static" visibility="public">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=21,15;end=21,24"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=21,4;end=21,31"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OE" adtcore:name="CHANGED" level="instance" visibility="public" clif_name="ZCL_SAPCLI_OSTRUCT_PROBE">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=23,11;end=23,18"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=23,4;end=23,52"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OE" adtcore:name="CREATED" level="static" visibility="public" clif_name="ZCL_SAPCLI_OSTRUCT_PROBE">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=24,17;end=24,24"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=24,4;end=24,24"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OM" adtcore:name="CONSTRUCTOR" level="instance" constructor="true" clif_name="ZCL_SAPCLI_OSTRUCT_PROBE" visibility="public">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=27,12;end=27,23" type="CLAS/OM"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./source/main#start=46,9;end=46,20"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=27,4;end=27,23"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationBlock" href="./source/main#start=46,2;end=49,11"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OM" adtcore:name="INCREMENT" level="instance" final="true" clif_name="ZCL_SAPCLI_OSTRUCT_PROBE" visibility="public">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=28,12;end=28,21" type="CLAS/OM"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./source/main#start=51,9;end=51,18"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=28,4;end=28,58"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationBlock" href="./source/main#start=51,2;end=55,11"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OM" adtcore:name="CALCULATE" level="instance" abstract="true" clif_name="ZCL_SAPCLI_OSTRUCT_PROBE" visibility="public">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=29,12;end=29,21" type="CLAS/OM"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=29,4;end=29,53"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OM" adtcore:name="CREATE" level="static" clif_name="ZCL_SAPCLI_OSTRUCT_PROBE" visibility="public">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=30,18;end=30,24" type="CLAS/OM"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./source/main#start=57,9;end=57,15"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=30,4;end=30,85"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationBlock" href="./source/main#start=57,2;end=59,11"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OM" adtcore:name="ON_CHANGED" eventhandlermethod="true" level="instance" clif_name="ZCL_SAPCLI_OSTRUCT_PROBE" visibility="protected">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=32,12;end=32,22" type="CLAS/OM"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./source/main#start=61,9;end=61,19"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=32,4;end=32,88"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationBlock" href="./source/main#start=61,2;end=62,11"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OA" adtcore:name="HELPER" level="instance" visibility="private">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=34,9;end=34,15"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=34,4;end=34,38"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OM" adtcore:name="GREET" level="instance" clif_name="ZCL_SAPCLI_OSTRUCT_PROBE" visibility="private">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=35,12;end=35,17" type="CLAS/OM"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./source/main#start=42,9;end=42,14"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=35,4;end=35,53"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationBlock" href="./source/main#start=42,2;end=44,11"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement clif_name="ZCL_SAPCLI_OSTRUCT_PROBE" adtcore:type="CLAS/OM" adtcore:name="IF_OO_ADT_CLASSRUN~MAIN" level="instance" visibility="public">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=9,15;end=9,33" type="CLAS/OR"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./source/main#start=64,9;end=64,32" type="CLAS/OM"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationBlock" href="./source/main#start=64,2;end=66,11"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:name="LCL_HELPER" adtcore:type="CLAS/OCL">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./includes/definitions#start=5,6;end=5,16"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./includes/implementations#start=1,6;end=1,16"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./includes/definitions#start=5,0;end=12,8"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationBlock" href="./includes/implementations#start=1,0;end=9,8"/>
    <abapsource:objectStructureElement adtcore:type="CLAS/OLN" adtcore:name="LIF_GREETER">
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./includes/definitions#start=7,15;end=7,26"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./includes/implementations#start=6,9;end=6,26" type="CLAS/OLD"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./includes/definitions#start=7,4;end=7,26"/>
    </abapsource:objectStructureElement>
    <abapsource:objectStructureElement adtcore:type="CLAS/OLT" adtcore:name="TY_NAME" visibility="public">
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./includes/definitions#start=8,10;end=8,17"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./includes/definitions#start=8,4;end=8,29"/>
    </abapsource:objectStructureElement>
    <abapsource:objectStructureElement adtcore:type="CLAS/OLA" constant="true" adtcore:name="CO_DEFAULT" level="static" readOnly="true" visibility="public">
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./includes/definitions#start=9,14;end=9,24"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./includes/definitions#start=9,4;end=9,51"/>
    </abapsource:objectStructureElement>
    <abapsource:objectStructureElement adtcore:type="CLAS/OLA" adtcore:name="NAME" level="instance" visibility="public">
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./includes/definitions#start=10,9;end=10,13"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./includes/definitions#start=10,4;end=10,26"/>
    </abapsource:objectStructureElement>
    <abapsource:objectStructureElement adtcore:type="CLAS/OLD" adtcore:name="CONSTRUCTOR" level="instance" constructor="true" clif_name="LCL_HELPER" visibility="public">
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./includes/definitions#start=11,12;end=11,23" type="CLAS/OLD"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./includes/implementations#start=2,9;end=2,20" type="CLAS/OLD"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./includes/definitions#start=11,4;end=11,60"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/implementationBlock" href="./includes/implementations#start=2,2;end=4,11"/>
    </abapsource:objectStructureElement>
    <abapsource:objectStructureElement clif_name="LCL_HELPER" adtcore:type="CLAS/OLD" adtcore:name="LIF_GREETER~GREET" level="instance" visibility="public">
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./includes/definitions#start=7,15;end=7,26" type="CLAS/OLN"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./includes/implementations#start=6,9;end=6,26" type="CLAS/OLD"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/implementationBlock" href="./includes/implementations#start=6,2;end=8,11"/>
    </abapsource:objectStructureElement>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:name="LTCL_PROBE" final="true" testclass="true" adtcore:type="CLAS/OCL">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./includes/testclasses#start=1,6;end=1,16"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./includes/testclasses#start=9,6;end=9,16"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./includes/testclasses#start=1,0;end=7,8"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationBlock" href="./includes/testclasses#start=9,0;end=12,8"/>
    <abapsource:objectStructureElement adtcore:type="CLAS/OLD" adtcore:name="FIRST_TEST" testmethod="true" level="instance" clif_name="LTCL_PROBE" visibility="private">
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./includes/testclasses#start=6,12;end=6,22" type="CLAS/OLD"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./includes/testclasses#start=10,9;end=10,19" type="CLAS/OLD"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./includes/testclasses#start=6,4;end=6,34"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/implementationBlock" href="./includes/testclasses#start=10,2;end=11,11"/>
    </abapsource:objectStructureElement>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:name="LIF_GREETER" adtcore:type="CLAS/ON">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./includes/definitions#start=1,10;end=1,21"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./includes/definitions#start=1,0;end=3,12"/>
    <abapsource:objectStructureElement adtcore:type="CLAS/OND" adtcore:name="GREET" level="instance" clif_name="LIF_GREETER" visibility="public">
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./includes/definitions#start=2,10;end=2,15" type="CLAS/OND"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./includes/definitions#start=2,2;end=2,51"/>
    </abapsource:objectStructureElement>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OCX" adtcore:name="ZCL_SAPCLI_OSTRUCT_PROBE" isExternalRef="true" description="Text Elements">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/textelements/classes/zcl_sapcli_ostruct_probe"/>
  </abapsource:objectStructureElement>
</abapsource:objectStructureElement>'''

# Recorded elements the probe class does not have, under the recorded root of CL_HTTP_CLIENT:
# CLAS/OF, CLAS/OQ, CLAS/I and CLAS/OLF of CL_HTTP_CLIENT, CLAS/OK of CL_ABAP_UNIT_ASSERT and
# a redefined method of CL_OO_ADT_RES_CLASS. The attribute futureFlag is not in any response;
# it stands for attributes the model does not know.
OBJECT_STRUCTURE_OTHER_TYPES_XML = \
'''<abapsource:objectStructureElement xml:base="/sap/bc/adt/oo/classes/cl_http_client/objectstructure?saml2=disabled&amp;sap-client=001" adtcore:name="CL_HTTP_CLIENT" visibility="private" adtcore:type="CLAS/OC" xmlns:adtcore="http://www.sap.com/adt/core" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:atom="http://www.w3.org/2005/Atom">
  <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=1,6;end=1,20"/>
  <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./source/main#start=505,6;end=505,20"/>
  <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=1,0;end=501,8"/>
  <atom:link rel="http://www.sap.com/adt/relations/source/implementationBlock" href="./source/main#start=505,0;end=7562,8"/>
  <abapsource:objectStructureElement adtcore:type="CLAS/OF" adtcore:name="CL_APC_WSP_CLIENT" futureFlag="true">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=5,17;end=5,34"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OQ" adtcore:name="SET_OAUTH_TOKEN_SEAM">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=7362,18;end=7362,38"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/I" adtcore:name="PERFINTERVAL">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./includes/macros#start=6,9;end=6,21"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./includes/macros#start=6,0;end=6,21"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OLF" adtcore:name="LCL_HTTP_CLIENT_TEST">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./includes/testclasses#start=9,46;end=9,66"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OK" adtcore:name="ASSERT_WRONG_STATE">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./includes/macros#start=3,7;end=3,25"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:type="CLAS/OM" adtcore:name="DELETE" level="instance" redefinition="true" visibility="public" clif_name="CL_OO_ADT_RES_CLASS">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="./source/main#start=54,12;end=54,18"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="./source/main#start=2022,9;end=2022,15"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=54,4;end=55,21"/>
    <atom:link rel="http://www.sap.com/adt/relations/source/implementationBlock" href="./source/main#start=2022,2;end=2160,11"/>
  </abapsource:objectStructureElement>
</abapsource:objectStructureElement>'''

# Not recorded: a definition block with a line that is not a number
OBJECT_STRUCTURE_INVALID_RANGE_XML = \
'''<abapsource:objectStructureElement xml:base="/sap/bc/adt/oo/classes/zcl_foo/objectstructure?saml2=disabled&amp;sap-client=001" adtcore:name="ZCL_FOO" visibility="public" adtcore:type="CLAS/OC" xmlns:adtcore="http://www.sap.com/adt/core" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:atom="http://www.w3.org/2005/Atom">
  <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=three,0;end=36,8"/>
</abapsource:objectStructureElement>'''

# Not recorded: a root without xml:base
OBJECT_STRUCTURE_WITHOUT_BASE_XML = \
'''<abapsource:objectStructureElement adtcore:name="ZCL_FOO" visibility="public" adtcore:type="CLAS/OC" xmlns:adtcore="http://www.sap.com/adt/core" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:atom="http://www.w3.org/2005/Atom">
  <atom:link rel="http://www.sap.com/adt/relations/source/definitionBlock" href="./source/main#start=3,0;end=36,8"/>
</abapsource:objectStructureElement>'''

# The response of GET /sap/bc/adt/programs/programs/demo_classical_reporting/objectstructure
# recorded on 2026-11-27, pretty-printed: absolute hrefs and object references instead of
# source ranges, also for the local class DEMO and its methods
OBJECT_STRUCTURE_PROGRAM_XML = \
'''<abapsource:objectStructureElement xmlns:adtcore="http://www.sap.com/adt/core" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:atom="http://www.w3.org/2005/Atom" xml:base="/sap/bc/adt/programs/programs/demo_classical_reporting/source/main" adtcore:name="DEMO_CLASSICAL_REPORTING" adtcore:type="PROG/P">
  <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/programs/programs/demo_classical_reporting"/>
  <abapsource:objectStructureElement adtcore:name="DEMO" include="DEMO_CLASSICAL_REPORTING" adtcore:type="PROG/PL">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/programs/programs/demo_classical_reporting/source/main#type=PROG%2FPL;name=DEMO"/>
    <abapsource:objectStructureElement adtcore:name="BROWSER" clif_name="DEMO" adtcore:type="PROG/PLM" visibility="public" level="static">
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/programs/programs/demo_classical_reporting/source/main#type=PROG%2FPLM;name=DEMO%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20BROWSER"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="/sap/bc/adt/programs/programs/demo_classical_reporting/source/main#type=PROG%2FPLM;name=DEMO%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20BROWSER"/>
    </abapsource:objectStructureElement>
    <abapsource:objectStructureElement adtcore:name="DETAIL" clif_name="DEMO" adtcore:type="PROG/PLM" visibility="public" level="static">
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/programs/programs/demo_classical_reporting/source/main#type=PROG%2FPLM;name=DEMO%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DETAIL"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="/sap/bc/adt/programs/programs/demo_classical_reporting/source/main#type=PROG%2FPLM;name=DEMO%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DETAIL"/>
    </abapsource:objectStructureElement>
    <abapsource:objectStructureElement adtcore:name="MAIN" clif_name="DEMO" adtcore:type="PROG/PLM" visibility="public" level="static">
      <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/programs/programs/demo_classical_reporting/source/main#type=PROG%2FPLM;name=DEMO%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20MAIN"/>
      <atom:link rel="http://www.sap.com/adt/relations/source/implementationIdentifier" href="/sap/bc/adt/programs/programs/demo_classical_reporting/source/main#type=PROG%2FPLM;name=DEMO%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20MAIN"/>
    </abapsource:objectStructureElement>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:name="CARRID" adtcore:type="PROG/PD">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/programs/programs/demo_classical_reporting/source/main#type=PROG%2FPD;name=CARRID"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:name="URL" adtcore:type="PROG/PD">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/programs/programs/demo_classical_reporting/source/main#type=PROG%2FPD;name=URL"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:name="AT LINE-SELECTION" adtcore:type="PROG/PE">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/programs/programs/demo_classical_reporting/source/main#type=PROG%2FPE;name=AT%20LINE-SELECTION"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:name="START-OF-SELECTION" adtcore:type="PROG/PE">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/programs/programs/demo_classical_reporting/source/main#type=PROG%2FPE;name=START-OF-SELECTION"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:name="DEMO_CLASSICAL_REPORTING" adtcore:type="PROG/PX">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/textelements/programs/demo_classical_reporting/source/symbols"/>
  </abapsource:objectStructureElement>
</abapsource:objectStructureElement>'''

# Recorded elements of the response of GET /sap/bc/adt/functions/groups/srfc/objectstructure
# (2026-11-27): a function module, a global data object, GUI titles with typeDescription,
# an include and the text elements
OBJECT_STRUCTURE_FUNCTION_GROUP_XML = \
'''<abapsource:objectStructureElement xml:base="/sap/bc/adt/functions/groups/srfc/source/main" adtcore:name="SRFC" adtcore:type="FUGR/F" xmlns:adtcore="http://www.sap.com/adt/core" xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:atom="http://www.w3.org/2005/Atom">
  <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/functions/groups/srfc/source/main"/>
  <abapsource:objectStructureElement adtcore:name="RFC_PING" adtcore:type="FUGR/FF">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/functions/groups/srfc/fmodules/rfc_ping/source/main"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:name="ADMIN" adtcore:type="FUGR/PD">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/functions/groups/srfc/includes/lsrfctop/source/main#type=FUGR%2FPD;name=ADMIN"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:name="001" typeDescription="GUI Titles" adtcore:type="FUGR/PZ">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/vit/wb/object_type/fugrpz/object_name/SAPLSRFC%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20001"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:name="LSRFCI01" adtcore:type="FUGR/I">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/functions/groups/srfc/includes/lsrfci01/source/main"/>
  </abapsource:objectStructureElement>
  <abapsource:objectStructureElement adtcore:name="SAPLSRFC" adtcore:type="FUGR/PX">
    <atom:link rel="http://www.sap.com/adt/relations/source/definitionIdentifier" href="/sap/bc/adt/textelements/functiongroups/srfc/source/symbols"/>
  </abapsource:objectStructureElement>
</abapsource:objectStructureElement>'''
