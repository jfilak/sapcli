"""Fixtures for sap.adt.apirelease tests"""

OBJECT_URI = '/sap/bc/adt/ddic/ddl/sources/i_statisticalkeyfigurecat'

API_RELEASE_RESPONSE_XML = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<ars:apiRelease xmlns:ars="http://www.sap.com/adt/ars">' \
    '<ars:releasableObject xmlns:adtcore="http://www.sap.com/adt/core"' \
    ' adtcore:uri="/sap/bc/adt/ddic/ddl/sources/i_statisticalkeyfigurecat"' \
    ' adtcore:type="DDLS/DF"' \
    ' adtcore:name="I_STATISTICALKEYFIGURECAT"/>' \
    '<ars:behaviour ars:create="true" ars:commentEnabled="true">' \
    '<ars:c0Release ars:create="true" ars:read="false" ars:update="false" ars:delete="false"' \
    ' ars:useInKeyUserAppsDefault="false" ars:useInKeyUserAppsReadOnly="true"' \
    ' ars:useInSAPCloudPlatformDefault="true" ars:useInSAPCloudPlatformReadOnly="false"' \
    ' ars:authValuesEnabled="false"/>' \
    '<ars:c1Release ars:create="false" ars:read="true" ars:update="true" ars:delete="true"' \
    ' ars:useInKeyUserAppsDefault="false" ars:useInKeyUserAppsReadOnly="false"' \
    ' ars:useInSAPCloudPlatformDefault="false" ars:useInSAPCloudPlatformReadOnly="false"' \
    ' ars:authValuesEnabled="true"/>' \
    '</ars:behaviour>' \
    '<ars:c0Release xmlns:adtcore="http://www.sap.com/adt/core"' \
    ' ars:contract="C0" ars:useInKeyUserApps="false" ars:useInSAPCloudPlatform="false"' \
    ' ars:comment="" ars:featureToggle="" ars:createAuthValues="false"' \
    ' adtcore:name="sap_bc_adt_ddic_ddl_sources_i_statisticalkeyfigurecat_C0">' \
    '<ars:status ars:state="NOT_RELEASED" ars:stateDescription="Not Released"/>' \
    '<ars:stateTransitions>' \
    '<ars:status ars:state="NOT_RELEASED" ars:stateDescription="Not Released"/>' \
    '<ars:status ars:state="RELEASED" ars:stateDescription="Released"/>' \
    '</ars:stateTransitions>' \
    '<ars:transportObject' \
    ' adtcore:uri="/sap/bc/adt/apireleases/apis/I_STATISTICALKEYFIGURECAT%20%20%20%20%20%20%20%20%20%20%20DDLS"' \
    ' adtcore:type="APIS"' \
    ' adtcore:name="I_STATISTICALKEYFIGURECAT           DDLS"' \
    ' adtcore:packageName="FINS_STSTCL_KEY_FIGURE_VDM"/>' \
    '</ars:c0Release>' \
    '<ars:c1Release xmlns:adtcore="http://www.sap.com/adt/core"' \
    ' ars:contract="C1" ars:useInKeyUserApps="true" ars:useInSAPCloudPlatform="false"' \
    ' ars:comment="" ars:featureToggle="" ars:createAuthValues="false"' \
    ' adtcore:name="sap_bc_adt_ddic_ddl_sources_i_statisticalkeyfigurecat_C1"' \
    ' adtcore:changedAt="2018-01-25T23:00:00Z" adtcore:changedBy="LIYI2">' \
    '<ars:status ars:state="RELEASED" ars:stateDescription="Released"/>' \
    '<ars:stateTransitions>' \
    '<ars:status ars:state="RELEASED" ars:stateDescription="Released"/>' \
    '<ars:status ars:state="DEPRECATED" ars:stateDescription="Deprecated"/>' \
    '<ars:status ars:state="NOT_RELEASED" ars:stateDescription="Not Released"/>' \
    '</ars:stateTransitions>' \
    '<ars:transportObject' \
    ' adtcore:uri="/sap/bc/adt/apireleases/apis/I_STATISTICALKEYFIGURECAT%20%20%20%20%20%20%20%20%20%20%20DDLS"' \
    ' adtcore:type="APIS"' \
    ' adtcore:name="I_STATISTICALKEYFIGURECAT           DDLS"' \
    ' adtcore:packageName="FINS_STSTCL_KEY_FIGURE_VDM"/>' \
    '</ars:c1Release>' \
    '<ars:apiCatalogData ars:isAnyAssignmentPossible="true" ars:isAnyContractReleased="true">' \
    '<ars:ApiCatalogs/>' \
    '</ars:apiCatalogData>' \
    '</ars:apiRelease>'

VALIDATION_RESPONSE_INFO_XML = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<ars:apiRelease xmlns:ars="http://www.sap.com/adt/ars">' \
    '<ars:releasableObject xmlns:adtcore="http://www.sap.com/adt/core"' \
    ' adtcore:uri="/sap/bc/adt/ddic/ddl/sources/i_statisticalkeyfigurecat"' \
    ' adtcore:type="DDLS/DF"' \
    ' adtcore:name="I_STATISTICALKEYFIGURECAT"/>' \
    '<ars:validationMessages>' \
    '<ars:validationMessage type="I" text="Changes are valid."' \
    ' msgid="ARS_ADT" msgno="002" msgv1="" msgv2="" msgv3="" msgv4=""/>' \
    '</ars:validationMessages>' \
    '</ars:apiRelease>'

VALIDATION_RESPONSE_ERROR_XML = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<ars:apiRelease xmlns:ars="http://www.sap.com/adt/ars">' \
    '<ars:releasableObject xmlns:adtcore="http://www.sap.com/adt/core"' \
    ' adtcore:uri="/sap/bc/adt/ddic/ddl/sources/i_statisticalkeyfigurecat"' \
    ' adtcore:type="DDLS/DF"' \
    ' adtcore:name="I_STATISTICALKEYFIGURECAT"/>' \
    '<ars:validationMessages>' \
    '<ars:validationMessage type="E" text="Contract C1 cannot be released."' \
    ' msgid="ARS_ADT" msgno="010" msgv1="C1" msgv2="" msgv3="" msgv4=""/>' \
    '</ars:validationMessages>' \
    '</ars:apiRelease>'

VALIDATION_RESPONSE_WARNING_XML = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<ars:apiRelease xmlns:ars="http://www.sap.com/adt/ars">' \
    '<ars:releasableObject xmlns:adtcore="http://www.sap.com/adt/core"' \
    ' adtcore:uri="/sap/bc/adt/ddic/ddl/sources/i_statisticalkeyfigurecat"' \
    ' adtcore:type="DDLS/DF"' \
    ' adtcore:name="I_STATISTICALKEYFIGURECAT"/>' \
    '<ars:validationMessages>' \
    '<ars:validationMessage type="W" text="Object has open changes."' \
    ' msgid="ARS_ADT" msgno="005" msgv1="" msgv2="" msgv3="" msgv4=""/>' \
    '</ars:validationMessages>' \
    '</ars:apiRelease>'

VALIDATION_RESPONSE_MULTIPLE_MESSAGES_XML = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<ars:apiRelease xmlns:ars="http://www.sap.com/adt/ars">' \
    '<ars:releasableObject xmlns:adtcore="http://www.sap.com/adt/core"' \
    ' adtcore:uri="/sap/bc/adt/ddic/ddl/sources/i_statisticalkeyfigurecat"' \
    ' adtcore:type="DDLS/DF"' \
    ' adtcore:name="I_STATISTICALKEYFIGURECAT"/>' \
    '<ars:validationMessages>' \
    '<ars:validationMessage type="I" text="Changes are valid."' \
    ' msgid="ARS_ADT" msgno="002" msgv1="" msgv2="" msgv3="" msgv4=""/>' \
    '<ars:validationMessage type="W" text="Object has open changes."' \
    ' msgid="ARS_ADT" msgno="005" msgv1="" msgv2="" msgv3="" msgv4=""/>' \
    '</ars:validationMessages>' \
    '</ars:apiRelease>'

SET_API_RELEASE_RESPONSE_XML = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<ars:apiRelease xmlns:ars="http://www.sap.com/adt/ars">' \
    '<ars:releasableObject xmlns:adtcore="http://www.sap.com/adt/core"' \
    ' adtcore:uri="/sap/bc/adt/ddic/ddl/sources/i_statisticalkeyfigurecat"' \
    ' adtcore:type="DDLS/DF"' \
    ' adtcore:name="I_STATISTICALKEYFIGURECAT"/>' \
    '<ars:behaviour ars:create="true" ars:commentEnabled="true">' \
    '<ars:c0Release ars:create="true" ars:read="false" ars:update="false" ars:delete="false"' \
    ' ars:useInKeyUserAppsDefault="false" ars:useInKeyUserAppsReadOnly="true"' \
    ' ars:useInSAPCloudPlatformDefault="true" ars:useInSAPCloudPlatformReadOnly="false"' \
    ' ars:authValuesEnabled="false"/>' \
    '<ars:c1Release ars:create="false" ars:read="true" ars:update="true" ars:delete="true"' \
    ' ars:useInKeyUserAppsDefault="false" ars:useInKeyUserAppsReadOnly="false"' \
    ' ars:useInSAPCloudPlatformDefault="false" ars:useInSAPCloudPlatformReadOnly="false"' \
    ' ars:authValuesEnabled="true"/>' \
    '</ars:behaviour>' \
    '<ars:c1Release xmlns:adtcore="http://www.sap.com/adt/core"' \
    ' ars:contract="C1" ars:useInKeyUserApps="true" ars:useInSAPCloudPlatform="true"' \
    ' ars:comment="This is a comment" ars:featureToggle="" ars:createAuthValues="true"' \
    ' adtcore:name="sap_bc_adt_ddic_ddl_sources_i_statisticalkeyfigurecat_C1"' \
    ' adtcore:changedAt="2026-04-20T00:00:00Z" adtcore:changedBy="DEVELOPER">' \
    '<ars:status ars:state="RELEASED" ars:stateDescription="Released"/>' \
    '<ars:useConceptAsSuccessor>false</ars:useConceptAsSuccessor>' \
    '<ars:successors/>' \
    '<ars:successorConceptName/>' \
    '<ars:stateTransitions>' \
    '<ars:status ars:state="RELEASED" ars:stateDescription="Released"/>' \
    '<ars:status ars:state="DEPRECATED" ars:stateDescription="Deprecated"/>' \
    '<ars:status ars:state="NOT_RELEASED" ars:stateDescription="Not Released"/>' \
    '</ars:stateTransitions>' \
    '<ars:transportObject' \
    ' adtcore:uri="/sap/bc/adt/apireleases/apis/I_STATISTICALKEYFIGURECAT%20%20%20%20%20%20%20%20%20%20%20DDLS"' \
    ' adtcore:type="APIS"' \
    ' adtcore:name="I_STATISTICALKEYFIGURECAT           DDLS"' \
    ' adtcore:packageName="FINS_STSTCL_KEY_FIGURE_VDM"/>' \
    '</ars:c1Release>' \
    '<ars:apiCatalogData ars:isAnyAssignmentPossible="true" ars:isAnyContractReleased="true">' \
    '<ars:ApiCatalogs/>' \
    '</ars:apiCatalogData>' \
    '</ars:apiRelease>'

VALIDATE_POST_BODY_XML = '<?xml version="1.0" encoding="UTF-8"?>\n' \
    '<ars:apiRelease xmlns:ars="http://www.sap.com/adt/ars">\n' \
    '<ars:c1Release ars:contract="C1" ars:useInKeyUserApps="true"' \
    ' ars:useInSAPCloudPlatform="false" ars:comment=""' \
    ' ars:featureToggle="" ars:createAuthValues="false">\n' \
    '<ars:status ars:state="RELEASED"/>\n' \
    '<ars:useConceptAsSuccessor>false</ars:useConceptAsSuccessor>\n' \
    '<ars:successors/>\n' \
    '<ars:successorConceptName/>\n' \
    '</ars:c1Release>\n' \
    '<ars:apiCatalogData ars:isAnyAssignmentPossible="true"' \
    ' ars:isAnyContractReleased="true">\n' \
    '<ars:ApiCatalogs></ars:ApiCatalogs>\n' \
    '</ars:apiCatalogData>\n' \
    '</ars:apiRelease>'
