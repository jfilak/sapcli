"""Test fixtures for Where-Used ADT module"""

WHEREUSED_SCOPE_REQUEST_XML = \
'''<?xml version="1.0" encoding="UTF-8"?>
<usagereferences:usageScopeRequest xmlns:usagereferences="http://www.sap.com/adt/ris/usageReferences">
<usagereferences:affectedObjects/>
</usagereferences:usageScopeRequest>'''

WHEREUSED_SCOPE_RESPONSE_XML = \
'''<?xml version="1.0" encoding="UTF-8"?>
<usagereferences:usageScopeResult xmlns:usagereferences="http://www.sap.com/adt/ris/usageReferences" localUsage="false">
  <usagereferences:objectIdentifier displayName="Z_TEST_REPORT_XYZ (Program)" globalType="PROG/P"/>
  <usagereferences:grade definitions="false" elements="false" indirectReferences="true"/>
  <usagereferences:objectTypes>
    <usagereferences:type name="CLAS/OC" isSelected="true" isDefault="true"/>
    <usagereferences:type name="INTF/OI" isSelected="true" isDefault="true"/>
    <usagereferences:type name="PROG/P" isSelected="true" isDefault="true"/>
  </usagereferences:objectTypes>
  <usagereferences:payload>dGVzdHBheWxvYWRiYXNlNjQ=</usagereferences:payload>
</usagereferences:usageScopeResult>'''

WHEREUSED_SEARCH_REQUEST_XML = \
'''<?xml version="1.0" encoding="UTF-8"?>
<usagereferences:usageReferenceRequest xmlns:usagereferences="http://www.sap.com/adt/ris/usageReferences">
<usagereferences:affectedObjects/>
<usagereferences:scope localUsage="false">
<usagereferences:objectIdentifier displayName="Z_TEST_REPORT_XYZ (Program)" globalType="PROG/P"/>
<usagereferences:grade definitions="false" elements="false" indirectReferences="true"/>
<usagereferences:objectTypes>
<usagereferences:type name="CLAS/OC" isSelected="true" isDefault="true"/>
<usagereferences:type name="INTF/OI" isSelected="true" isDefault="true"/>
<usagereferences:type name="PROG/P" isSelected="true" isDefault="true"/>
</usagereferences:objectTypes>
<usagereferences:payload>dGVzdHBheWxvYWRiYXNlNjQ=</usagereferences:payload>
</usagereferences:scope>
</usagereferences:usageReferenceRequest>'''

WHEREUSED_SEARCH_RESPONSE_ZERO_RESULTS_XML = \
'''<?xml version="1.0" encoding="UTF-8"?>
<usagereferences:usageReferenceResult xmlns:usagereferences="http://www.sap.com/adt/ris/usageReferences" numberOfResults="0" resultDescription="[A4H] Where-Used List: Z_TEST_REPORT_XYZ (Program)" referencedObjectIdentifier="">
  <usagereferences:scope>
    <usagereferences:objectIdentifier displayName="Z_TEST_REPORT_XYZ (Unknown Type)" globalType="PROG"/>
    <usagereferences:grade definitions="false" elements="false" indirectReferences="true"/>
    <usagereferences:objectTypes>
      <usagereferences:type name="CLAS/OC" isSelected="true" isDefault="true"/>
      <usagereferences:type name="INTF/OI" isSelected="true" isDefault="true"/>
      <usagereferences:type name="PROG/P" isSelected="true" isDefault="true"/>
    </usagereferences:objectTypes>
    <usagereferences:payload>dGVzdHBheWxvYWRiYXNlNjQ=</usagereferences:payload>
  </usagereferences:scope>
  <usagereferences:referencedObjects/>
</usagereferences:usageReferenceResult>'''

WHEREUSED_SEARCH_RESPONSE_WITH_RESULTS_XML = \
'''<?xml version="1.0" encoding="UTF-8"?>
<usagereferences:usageReferenceResult xmlns:usagereferences="http://www.sap.com/adt/ris/usageReferences" numberOfResults="2" resultDescription="[A4H] Where-Used List: Z_TEST_REPORT_XYZ (Program)" referencedObjectIdentifier="">
  <usagereferences:scope>
    <usagereferences:objectIdentifier displayName="Z_TEST_REPORT_XYZ (Unknown Type)" globalType="PROG"/>
    <usagereferences:grade definitions="false" elements="false" indirectReferences="true"/>
    <usagereferences:objectTypes>
      <usagereferences:type name="CLAS/OC" isSelected="true" isDefault="true"/>
      <usagereferences:type name="INTF/OI" isSelected="true" isDefault="true"/>
      <usagereferences:type name="PROG/P" isSelected="true" isDefault="true"/>
    </usagereferences:objectTypes>
    <usagereferences:payload>dGVzdHBheWxvYWRiYXNlNjQ=</usagereferences:payload>
  </usagereferences:scope>
  <usagereferences:referencedObjects>
    <usagereferences:referencedObject uri="/sap/bc/adt/oo/classes/zcl_abapgit_abap_language_vers" parentUri="/sap/bc/adt/packages/%24abapgit_env" isResult="false" canHaveChildren="false">
      <usagereferences:adtObject xmlns:adtcore="http://www.sap.com/adt/core" adtcore:responsible="DEVELOPER" adtcore:name="ZCL_ABAPGIT_ABAP_LANGUAGE_VERS" adtcore:type="CLAS/OC">
        <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24abapgit_env" adtcore:type="DEVC/K" adtcore:name="$ABAPGIT_ENV"/>
      </usagereferences:adtObject>
    </usagereferences:referencedObject>
    <usagereferences:referencedObject uri="/sap/bc/adt/oo/classes/zcl_abapgit_abap_language_vers/includes/testclasses" parentUri="/sap/bc/adt/oo/classes/zcl_abapgit_abap_language_vers" isResult="false" canHaveChildren="true" usageInformation="gradeDirect,includeTest">
      <usagereferences:adtObject xmlns:adtcore="http://www.sap.com/adt/core" adtcore:name="Local Test Classes">
        <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24abapgit_env" adtcore:type="DEVC/K" adtcore:name="$ABAPGIT_ENV"/>
      </usagereferences:adtObject>
      <objectIdentifier>ABAPFullName;ZCL_ABAPGIT_ABAP_LANGUAGE_VERSCP;ZCL_ABAPGIT_ABAP_LANGUAGE_VERSCCAU;\TY:ZCL_ABAPGIT_FACTORY</objectIdentifier>
    </usagereferences:referencedObject>
  </usagereferences:referencedObjects>
</usagereferences:usageReferenceResult>'''
