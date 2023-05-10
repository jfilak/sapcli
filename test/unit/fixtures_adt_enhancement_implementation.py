# Content-Type: application/vnd.sap.adt.enh.enhoxhb.v4+xml; charset=utf-8
ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4='''<?xml version="1.0" encoding="UTF-8"?>
<enho:objectData xmlns:enho="http://www.sap.com/adt/enhancements/enho" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="XYZ" adtcore:abapLanguageVersion="standard" adtcore:name="SAPCLI_ENH_IMPL" adtcore:type="ENHO/XHB" adtcore:changedAt="2021-05-07T08:51:15Z" adtcore:version="active" adtcore:createdAt="2021-05-07T08:51:15Z" adtcore:changedBy="SAP" adtcore:createdBy="DEVELOPER" adtcore:description="sapcli Test" adtcore:language="EN" xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/sapcli_tests" adtcore:type="DEVC/K" adtcore:name="SAPCLI_TESTS" adtcore:description="sapcli tests"/>
  <enho:contentCommon enho:toolType="BADI_IMPL" enho:adjustmentStatus="adjusted" enho:upgradeFlag="false" enho:switchSupported="true">
    <enho:usages>
      <enhcore:referencedObject xmlns:enhcore="http://www.sap.com/abapsource/enhancementscore" enhcore:program_id="R3TR" enhcore:element_usage="USEO" enhcore:upgrade="false" enhcore:automatic_transport="false">
        <enhcore:objectReference adtcore:uri="/sap/bc/adt/oo/classes/zcl_sapcli_badi_impl" adtcore:type="CLAS/OC" adtcore:name="ZCL_SAPCLI_BADI_IMPL"/>
        <enhcore:mainObjectReference adtcore:uri="/sap/bc/adt/oo/classes/cl_zcl_sapcli_badi_impl" adtcore:type="CLAS/OC" adtcore:name="ZCL_SAPCLI_BADI_IMPL"/>
      </enhcore:referencedObject>
      <enhcore:referencedObject xmlns:enhcore="http://www.sap.com/abapsource/enhancementscore" enhcore:program_id="R3TR" enhcore:element_usage="EXTO" enhcore:upgrade="false" enhcore:automatic_transport="false">
        <enhcore:objectReference adtcore:uri="/sap/bc/adt/enhancements/enhsxsb/sapcli_enh_spot" adtcore:type="ENHS/XSB" adtcore:name="SAPCLI_ENH_SPOT"/>
        <enhcore:mainObjectReference adtcore:uri="/sap/bc/adt/enhancements/enhsxsb/sapcli_enh_spot" adtcore:type="ENHS/XSB" adtcore:name="SAPCLI_ENH_SPOT"/>
      </enhcore:referencedObject>
    </enho:usages>
  </enho:contentCommon>
  <enho:contentSpecific>
    <enho:badiTechnology>
      <enho:badiImplementations>
        <enho:badiImplementation enho:name="SAPCLI_BADI_IMPL" enho:shortText="SAPCLI badi" enho:example="false" enho:default="false" enho:active="true" enho:customizingLock="" enho:runtimeBehaviorShorttext="The implementation will be called">
          <enho:enhancementSpot adtcore:uri="/sap/bc/adt/enhancements/enhsxsb/sapcli_enh_spot" adtcore:type="ENHS/XSB" adtcore:name="SAPCLI_ENH_SPOT"/>
          <enho:badiDefinition adtcore:uri="/sap/bc/adt/enhancements/enhsxsb/sapcli_enh_spot#type=enhs%2fxb;name=sapcli_badi_def" adtcore:type="ENHS/XB" adtcore:name="SAPCLI_BADI_DEF"/>
          <enho:implementingClass adtcore:uri="/sap/bc/adt/oo/classes/zcl_sapcli_badi_impl" adtcore:type="CLAS/OC" adtcore:name="ZCL_SAPCLI_BADI_IMPL"/>
        </enho:badiImplementation>
      </enho:badiImplementations>
    </enho:badiTechnology>
  </enho:contentSpecific>
</enho:objectData>
'''
