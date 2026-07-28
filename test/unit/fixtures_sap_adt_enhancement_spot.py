ENHANCEMENT_SPOT_NAME = 'SSAMPLE_ENHS'

FIXTURE_ADT_ENHANCEMENT_SPOT = '''<?xml version="1.0" encoding="UTF-8"?>
<enhs:objectData xmlns:enhs="http://www.sap.com/adt/enhancements/enhs" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:abapLanguageVersion="standard" adtcore:name="SSAMPLE_ENHS" adtcore:type="ENHS/XSB" adtcore:changedAt="2021-04-20T00:00:00Z" adtcore:version="active" adtcore:createdAt="2021-02-22T00:00:00Z" adtcore:changedBy="SAP" adtcore:createdBy="DEVELOPER" adtcore:description="Lovely Enhancement spot" adtcore:language="EN" xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fenhancements%2Fenhsxsb%2Fssample_enhs" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" type="application/vnd.sap.adt.nameditems.v1+xml" title="Allowed ABAP language versions"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/vit/wb/object_type/enhsxs/object_name/SSAMPLE_ENHS" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP GUI"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/enhancements/enhsxsb/ssample_enhs/enhancements/definitions" rel="http://www.sap.com/adt/relations/badiDefinitions" type="application/xml" title="BAdI Definitions"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="./ssample_enhs" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Landing Page (HTML)"/>
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/my_es" adtcore:type="DEVC/K" adtcore:name="MY_ES" adtcore:description="Home package"/>
  <enhs:contentCommon enhs:toolType="BADI_DEF" enhs:internal="false" enhs:internalFlagEditable="true">
    <enhs:usages>
      <enhcore:referencedObject xmlns:enhcore="http://www.sap.com/abapsource/enhancementscore" enhcore:program_id="R3TR" enhcore:element_usage="USEO" enhcore:upgrade="false" enhcore:automatic_transport="false">
        <enhcore:objectReference adtcore:uri="/sap/bc/adt/oo/interfaces/if_example_badi" adtcore:type="INTF/OI" adtcore:name="IF_SAMPLE_ENHS"/>
        <enhcore:mainObjectReference adtcore:uri="/sap/bc/adt/oo/interfaces/if_example_badi" adtcore:type="INTF/OI" adtcore:name="IF_SAMPLE_ENHS"/>
      </enhcore:referencedObject>
    </enhs:usages>
  </enhs:contentCommon>
  <enhs:contentSpecific>
    <enhs:badiTechnology>
      <enhs:badiDefinitions>
        <enhs:badiDefinition enhs:name="SAMPLE_ENHS" enhs:shorttext="BAdI for awesome" enhs:singleUse="false" enhs:useFallbackClass="false" enhs:filterLimitation="false" enhs:documentationId="SAMPLE_ENHS" enhs:contextMode="N" enhs:amdp="false" enhs:internalUse="true" enhs:customLogicRegistered="false">
          <enhs:interface adtcore:uri="/sap/bc/adt/oo/interfaces/if_example_badi" adtcore:type="INTF/OI" adtcore:name="IF_SAMPLE_ENHS"/>
          <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/enhancements/enhsxsb/ssample_enhs#type=enhs%2fxb;name=sample_impl" rel="http://www.sap.com/adt/relations/badiDefinition"/>
        </enhs:badiDefinition>
      </enhs:badiDefinitions>
    </enhs:badiTechnology>
  </enhs:contentSpecific>
</enhs:objectData>
'''

# The XML sapcli sends in the PUT request after the fetched Enhancement Spot
# got its contentCommon/internal flag switched to true.
FIXTURE_SAPCLI_ADT_ENHANCEMENT_SPOT = '''<?xml version="1.0" encoding="UTF-8"?>
<enhs:objectData xmlns:enhs="http://www.sap.com/adt/enhancements/enhs" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="ENHS/XSB" adtcore:description="Lovely Enhancement spot" adtcore:language="EN" adtcore:name="SSAMPLE_ENHS" adtcore:abapLanguageVersion="standard" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:responsible="DEVELOPER" adtcore:version="active">
<adtcore:packageRef adtcore:name="MY_ES"/>
<enhs:contentCommon enhs:toolType="BADI_DEF" enhs:internal="true" enhs:internalFlagEditable="true">
<enhs:usages>
<enhcore:referencedObject xmlns:enhcore="http://www.sap.com/abapsource/enhancementscore" enhcore:program_id="R3TR" enhcore:element_usage="USEO" enhcore:upgrade="false" enhcore:automatic_transport="false">
<enhcore:objectReference adtcore:uri="/sap/bc/adt/oo/interfaces/if_example_badi" adtcore:type="INTF/OI" adtcore:name="IF_SAMPLE_ENHS"/>
<enhcore:mainObjectReference adtcore:uri="/sap/bc/adt/oo/interfaces/if_example_badi" adtcore:type="INTF/OI" adtcore:name="IF_SAMPLE_ENHS"/>
</enhcore:referencedObject>
</enhs:usages>
</enhs:contentCommon>
<enhs:contentSpecific>
<enhs:badiTechnology>
<enhs:badiDefinitions>
<enhs:badiDefinition enhs:name="SAMPLE_ENHS" enhs:shorttext="BAdI for awesome" enhs:singleUse="false" enhs:useFallbackClass="false" enhs:filterLimitation="false" enhs:documentationId="SAMPLE_ENHS" enhs:contextMode="N" enhs:amdp="false" enhs:internalUse="true" enhs:customLogicRegistered="false">
<enhs:interface adtcore:uri="/sap/bc/adt/oo/interfaces/if_example_badi" adtcore:type="INTF/OI" adtcore:name="IF_SAMPLE_ENHS"/>
</enhs:badiDefinition>
</enhs:badiDefinitions>
</enhs:badiTechnology>
</enhs:contentSpecific>
</enhs:objectData>'''

FIXTURE_ADT_ENHS_REPOSITORY_ROOT = '''<?xml version="1.0" encoding="UTF-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
    <DATA>
      <TREE_CONTENT/>
      <CATEGORIES>
        <SEU_ADT_OBJECT_CATEGORY_INFO>
          <CATEGORY>enhancements</CATEGORY>
          <CATEGORY_LABEL>Enhancements</CATEGORY_LABEL>
        </SEU_ADT_OBJECT_CATEGORY_INFO>
      </CATEGORIES>
      <OBJECT_TYPES>
        <SEU_ADT_OBJECT_TYPE_INFO>
          <OBJECT_TYPE>ENHO/XHB</OBJECT_TYPE>
          <CATEGORY_TAG>enhancements</CATEGORY_TAG>
          <OBJECT_TYPE_LABEL>Enhancement Implementations</OBJECT_TYPE_LABEL>
          <NODE_ID>000004</NODE_ID>
        </SEU_ADT_OBJECT_TYPE_INFO>
        <SEU_ADT_OBJECT_TYPE_INFO>
          <OBJECT_TYPE>ENHS/XB</OBJECT_TYPE>
          <CATEGORY_TAG>enhancements</CATEGORY_TAG>
          <OBJECT_TYPE_LABEL>BAdI Definitions</OBJECT_TYPE_LABEL>
          <NODE_ID>000001</NODE_ID>
        </SEU_ADT_OBJECT_TYPE_INFO>
      </OBJECT_TYPES>
    </DATA>
  </asx:values>
</asx:abap>
'''

FIXTURE_ADT_ENHS_REPOSITORY_BADI_DEFINITIONS = '''<?xml version="1.0" encoding="UTF-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
    <DATA>
      <TREE_CONTENT>
        <SEU_ADT_REPOSITORY_OBJ_NODE>
          <OBJECT_TYPE>ENHS/XB</OBJECT_TYPE>
          <OBJECT_NAME>CTS_TRANSPORT_FLOW</OBJECT_NAME>
          <TECH_NAME>CTS_TRANSPORT_FLOW</TECH_NAME>
          <OBJECT_URI>/sap/bc/adt/enhancements/enhsxsb/ssample_enhs#type=enhs%2fxb;name=sample_impl</OBJECT_URI>
          <OBJECT_VIT_URI>/sap/bc/adt/vit/wb/object_type/enhsxb/object_name/SAMPLE_ENHS%20%20%20%20%20%20%20%20%20%20%20SAMPLE_IMPL</OBJECT_VIT_URI>
          <EXPANDABLE/>
          <IS_FINAL/>
          <IS_ABSTRACT/>
          <IS_FOR_TESTING/>
          <IS_EVENT_HANDLER/>
          <IS_CONSTRUCTOR/>
          <IS_REDEFINITION/>
          <IS_STATIC/>
          <IS_READ_ONLY/>
          <IS_CONSTANT/>
          <VISIBILITY>0</VISIBILITY>
          <NODE_ID/>
          <PARENT_NAME/>
          <DESCRIPTION>BAdI for awesome</DESCRIPTION>
          <DESCRIPTION_TYPE>XB</DESCRIPTION_TYPE>
          <VERSION/>
          <INACTIVE_TYPE/>
        </SEU_ADT_REPOSITORY_OBJ_NODE>
      </TREE_CONTENT>
      <CATEGORIES>
        <SEU_ADT_OBJECT_CATEGORY_INFO>
          <CATEGORY>enhancements</CATEGORY>
          <CATEGORY_LABEL>Enhancements</CATEGORY_LABEL>
        </SEU_ADT_OBJECT_CATEGORY_INFO>
      </CATEGORIES>
      <OBJECT_TYPES>
        <SEU_ADT_OBJECT_TYPE_INFO>
          <OBJECT_TYPE>ENHS/XB</OBJECT_TYPE>
          <CATEGORY_TAG>enhancements</CATEGORY_TAG>
          <OBJECT_TYPE_LABEL/>
          <NODE_ID>000002</NODE_ID>
        </SEU_ADT_OBJECT_TYPE_INFO>
      </OBJECT_TYPES>
    </DATA>
  </asx:values>
</asx:abap>
'''

FIXTURE_ADT_ENHS_REPOSITORY_EHNO = '''<?xml version="1.0" encoding="UTF-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
    <DATA>
      <TREE_CONTENT>
        <SEU_ADT_REPOSITORY_OBJ_NODE>
          <OBJECT_TYPE>ENHO/XHB</OBJECT_TYPE>
          <OBJECT_NAME>MY_FABULOUS_ENHS_ONE</OBJECT_NAME>
          <TECH_NAME>MY_FABULOUS_ENHS_ONE</TECH_NAME>
          <OBJECT_URI>/sap/bc/adt/enhancements/enhoxhb/my_fabulous_enhs_one</OBJECT_URI>
          <OBJECT_VIT_URI>/sap/bc/adt/vit/wb/object_type/enhoxh/object_name/MY_FABULOUS_ENHS_ONE</OBJECT_VIT_URI>
          <EXPANDABLE/>
          <IS_FINAL/>
          <IS_ABSTRACT/>
          <IS_FOR_TESTING/>
          <IS_EVENT_HANDLER/>
          <IS_CONSTRUCTOR/>
          <IS_REDEFINITION/>
          <IS_STATIC/>
          <IS_READ_ONLY/>
          <IS_CONSTANT/>
          <VISIBILITY>0</VISIBILITY>
          <NODE_ID/>
          <PARENT_NAME/>
          <DESCRIPTION/>
          <DESCRIPTION_TYPE>XHB</DESCRIPTION_TYPE>
          <VERSION/>
          <INACTIVE_TYPE/>
        </SEU_ADT_REPOSITORY_OBJ_NODE>
        <SEU_ADT_REPOSITORY_OBJ_NODE>
          <OBJECT_TYPE>ENHO/XHB</OBJECT_TYPE>
          <OBJECT_NAME>OPEN_SOURCE_IS_BEST</OBJECT_NAME>
          <TECH_NAME>OPEN_SOURCE_IS_BEST</TECH_NAME>
          <OBJECT_URI>/sap/bc/adt/enhancements/enhoxhb/open_source_is_best</OBJECT_URI>
          <OBJECT_VIT_URI>/sap/bc/adt/vit/wb/object_type/enhoxh/object_name/OPEN_SOURCE_IS_BEST</OBJECT_VIT_URI>
          <EXPANDABLE/>
          <IS_FINAL/>
          <IS_ABSTRACT/>
          <IS_FOR_TESTING/>
          <IS_EVENT_HANDLER/>
          <IS_CONSTRUCTOR/>
          <IS_REDEFINITION/>
          <IS_STATIC/>
          <IS_READ_ONLY/>
          <IS_CONSTANT/>
          <VISIBILITY>0</VISIBILITY>
          <NODE_ID/>
          <PARENT_NAME/>
          <DESCRIPTION/>
          <DESCRIPTION_TYPE>XHB</DESCRIPTION_TYPE>
          <VERSION/>
          <INACTIVE_TYPE/>
        </SEU_ADT_REPOSITORY_OBJ_NODE>
      </TREE_CONTENT>
      <CATEGORIES>
        <SEU_ADT_OBJECT_CATEGORY_INFO>
          <CATEGORY>enhancements</CATEGORY>
          <CATEGORY_LABEL>Enhancements</CATEGORY_LABEL>
        </SEU_ADT_OBJECT_CATEGORY_INFO>
      </CATEGORIES>
      <OBJECT_TYPES>
        <SEU_ADT_OBJECT_TYPE_INFO>
          <OBJECT_TYPE>ENHO/XHB</OBJECT_TYPE>
          <CATEGORY_TAG>enhancements</CATEGORY_TAG>
          <OBJECT_TYPE_LABEL/>
          <NODE_ID>000005</NODE_ID>
        </SEU_ADT_OBJECT_TYPE_INFO>
      </OBJECT_TYPES>
    </DATA>
  </asx:values>
</asx:abap>
'''
