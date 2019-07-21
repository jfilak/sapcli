# Content-Type: application/xml; charset=utf-8
ADT_XML_ATC_CUSTOMIZING='''<?xml version="1.0" encoding="utf-8"?>
<atc:customizing xmlns:atc="http://www.sap.com/adt/atc">
  <properties>
    <property name="ciCheckFlavour" value="false"/>
    <property name="systemCheckVariant" value="STANDARD"/>
    <property name="afterActivationCheckVariant" value="ACTIVATION"/>
  </properties>
</atc:customizing>
'''

# Content-Type: application/vnd.sap.atc.customizing-v1+xml; charset=utf-8
ADT_XML_ATC_CUSTOMIZING_ATTRIBUTES='''<?xml version="1.0" encoding="UTF-8"?>
<atc:customizing xmlns:atc="http://www.sap.com/adt/atc">
  <properties>
    <property name="additionalProjectInfoLabel" value=" (Checkman)"/>
    <property name="ciCheckFlavour" value="false"/>
    <property name="systemCheckVariant" value="OPENABAPCHECKS"/>
    <property name="afterActivationCheckVariant" value="ACTIVATION"/>
  </properties>
  <scaAttributes>
    <scaAttribute labelL="Component ID" labelM="Applicatn Component" labelS="Component" label="false" attributeName="APPLICATION_COMPONENT"/>
    <scaAttribute labelL="SAP Note Number" labelM="SAP Note Number" labelS="Note" label="false" attributeName="NOTE"/>
    <scaAttribute labelL="Short Text" labelM="Short Text" labelS="Short Text" label="true" refAttributeName="NOTE" attributeName="NOTE_TEXT"/>
    <scaAttribute labelL="Referenced Object" labelM="Ref. Object" labelS="Ref. Obj." label="false" attributeName="REF_OBJ_NAME"/>
    <scaAttribute labelL="Referenced Object Type" labelM="Ref. Object Type" labelS="RefObjType" label="false" attributeName="REF_OBJ_TYPE"/>
    <scaAttribute labelL="Simplification Item Category" labelM="Category" labelS="Category" label="false" attributeName="SITEM_STATE"/>
  </scaAttributes>
</atc:customizing>'''

# POST /sap/bc/adt/atc/worklists?checkVariant=STANDARD HTTP/1.1
# >> Accept    : text/plain
# << Content-Type: text/plain; charset=utf-8
# << Location    : /atc/worklists/worklistId/0242AC1100021EE9AAE43D24739F1C3A
# 0242AC1100021EE9AAE43D24739F1C3A

#POST /sap/bc/adt/atc/runs?worklistId=0242AC1100021EE9AAE43D24739F1C3A HTTP/1.1

# >> Accept      : application/xml
# >> Content-Type: application/xml
# !!! BEWARE - adtcore:name is not sent by Eclipse ADT
ADT_XML_ATC_RUN_REQUEST_PACKAGE='''<?xml version="1.0" encoding="UTF-8"?>
<atc:run xmlns:atc="http://www.sap.com/adt/atc" maximumVerdicts="69">
<objectSets xmlns:adtcore="http://www.sap.com/adt/core">
<objectSet kind="inclusive">
<adtcore:objectReferences>
<adtcore:objectReference adtcore:uri="/sap/bc/adt/packages/%24iamtheking" adtcore:name="$IAMTHEKING"/>
</adtcore:objectReferences>
</objectSet>
</objectSets>
</atc:run>'''

# << Content-Type: application/xml; charset=utf-8
ADT_XML_ATC_RUN_RESPONSE_NO_OBJECTS='''<?xml version="1.0" encoding="utf-8"?>
<atcworklist:worklistRun xmlns:atcworklist="http://www.sap.com/adt/atc/worklist">
    <atcworklist:worklistId>0242AC1100021EE9AAE43D24739F1C3A</atcworklist:worklistId>
    <atcworklist:worklistTimestamp>2019-07-20T19:09:34Z</atcworklist:worklistTimestamp>
    <atcworklist:infos>
        <atcinfo:info xmlns:atcinfo="http://www.sap.com/adt/atc/info">
            <atcinfo:type>NO_OBJS</atcinfo:type>
            <atcinfo:description>Selection does not contain objects which can be checked by ATC</atcinfo:description>
        </atcinfo:info>
    </atcworklist:infos>
</atcworklist:worklistRun>'''

# >> Accept      : application/xml
# >> Content-Type: application/xml
# !!! BEWARE - adtcore:name is not sent by Eclipse ADT
ADT_XML_ATC_RUN_REQUEST_CLASS='''<?xml version="1.0" encoding="UTF-8"?>
<atc:run xmlns:atc="http://www.sap.com/adt/atc" maximumVerdicts="100">
<objectSets xmlns:adtcore="http://www.sap.com/adt/core">
<objectSet kind="inclusive">
<adtcore:objectReferences>
<adtcore:objectReference adtcore:uri="/sap/bc/adt/oo/classes/zcl_z001_dpc" adtcore:name="ZCL_Z001_DPC"/>
</adtcore:objectReferences>
</objectSet>
</objectSets>
</atc:run>'''

# << Content-Type: application/xml; charset=utf-8
ADT_XML_ATC_RUN_RESPONSE_FAILURES='''<?xml version="1.0" encoding="UTF-8"?>
<atcworklist:worklistRun xmlns:atcworklist="http://www.sap.com/adt/atc/worklist">
  <atcworklist:worklistId>0242AC1100021EE9AAE43D24739F1C3A</atcworklist:worklistId>
  <atcworklist:worklistTimestamp>2019-07-20T19:18:57Z</atcworklist:worklistTimestamp>
  <atcworklist:infos>
    <atcinfo:info xmlns:atcinfo="http://www.sap.com/adt/atc/info">
      <atcinfo:type>TOOL_FAILURE</atcinfo:type>
      <atcinfo:description>ATC check run aborted, due to missing prerequisites</atcinfo:description>
    </atcinfo:info>
    <atcinfo:info xmlns:atcinfo="http://www.sap.com/adt/atc/info">
      <atcinfo:type>TOOL_FAILURE</atcinfo:type>
      <atcinfo:description>ATC check run aborted, due to missing prerequisites</atcinfo:description>
    </atcinfo:info>
    <atcinfo:info xmlns:atcinfo="http://www.sap.com/adt/atc/info">
      <atcinfo:type>TOOL_FAILURE</atcinfo:type>
      <atcinfo:description>ATC check run aborted, due to missing prerequisites</atcinfo:description>
    </atcinfo:info>
    <atcinfo:info xmlns:atcinfo="http://www.sap.com/adt/atc/info">
      <atcinfo:type>TOOL_FAILURE</atcinfo:type>
      <atcinfo:description>ATC check run aborted, due to missing prerequisites</atcinfo:description>
    </atcinfo:info>
    <atcinfo:info xmlns:atcinfo="http://www.sap.com/adt/atc/info">
      <atcinfo:type>FINDING_STATS</atcinfo:type>
      <atcinfo:description>0,0,1</atcinfo:description>
    </atcinfo:info>
  </atcworklist:infos>
</atcworklist:worklistRun>'''

# GET /sap/bc/adt/atc/worklists/0242AC1100021EE9AAE43D24739F1C3A?includeExemptedFindings=false HTTP/1.1
# >> Accept    : application/atc.worklist.v1+xml
# << Content-Type: application/atc.worklist.v1+xml; charset=utf-8
ADT_XML_ATC_WORKLIST_EMPTY='''<?xml version="1.0" encoding="UTF-8"?>
<atcworklist:worklist xmlns:atcworklist="http://www.sap.com/adt/atc/worklist" atcworklist:id="0242AC1100021EE9AAE43D24739F1C3A" atcworklist:timestamp="2019-07-20T19:09:34Z" atcworklist:usedObjectSet="99999999999999999999999999999999" atcworklist:objectSetIsComplete="true">
  <atcworklist:objectSets>
    <atcworklist:objectSet atcworklist:name="00000000000000000000000000000000" atcworklist:title="All Objects" atcworklist:kind="ALL"/>
  </atcworklist:objectSets>
  <atcworklist:objects/>
</atcworklist:worklist>'''

# GET /sap/bc/adt/atc/worklists/0242AC1100021EE9AAE43D24739F1C3A?timestamp=1563649774&includeExemptedFindings=false HTTP/1.1
# >> Accept    : application/atc.worklist.v1+xml
# << Content-Type: application/atc.worklist.v1+xml; charset=utf-8
ADT_XML_ATC_WORKLIST_CLASS='''<?xml version="1.0" encoding="UTF-8"?>
<atcworklist:worklist xmlns:atcworklist="http://www.sap.com/adt/atc/worklist" atcworklist:id="0242AC1100021EE9AAE43D24739F1C3A" atcworklist:timestamp="2019-07-20T19:18:57Z" atcworklist:usedObjectSet="99999999999999999999999999999999" atcworklist:objectSetIsComplete="true">
  <atcworklist:objectSets>
    <atcworklist:objectSet atcworklist:name="00000000000000000000000000000000" atcworklist:title="All Objects" atcworklist:kind="ALL"/>
    <atcworklist:objectSet atcworklist:name="99999999999999999999999999999999" atcworklist:title="Last Check Run" atcworklist:kind="LAST_RUN"/>
  </atcworklist:objectSets>
  <atcworklist:objects>
    <atcobject:object xmlns:atcobject="http://www.sap.com/adt/atc/object" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/atc/objects/R3TR/CLAS/ZCL_Z001_DPC" adtcore:type="CLAS" adtcore:name="ZCL_Z001_DPC" adtcore:packageName="$TMP" atcobject:author="DEVELOPER" atcobject:objectTypeId="CLAS/OC">
      <atcobject:findings>
        <atcfinding:finding xmlns:atcfinding="http://www.sap.com/adt/atc/finding" adtcore:uri="/sap/bc/adt/atc/worklists/0242AC1100021EE9AAE43D24739F1C3A/findings/ZCL_Z001_DPC/CLAS/001321AF52A31DDBA7E0EE95D633EA22/0028/-1" atcfinding:location="/sap/bc/adt/oo/classes/zcl_z001_dpc#start=1,0" atcfinding:priority="3" atcfinding:checkId="001321AF52A31DDBA7E0EE95D633EA22" atcfinding:checkTitle="Test Environment  (SLIN_UMFLD)" atcfinding:messageId="0028" atcfinding:messageTitle="Inconsistency in the SAP configuration of time zones (0028)" atcfinding:exemptionApproval="-" atcfinding:exemptionKind="">
          <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/documentation/atc/documents/0242AC1100021EE9AAE43D24739F1C3A/findings/ZCL_Z001_DPC/CLAS/001321AF52A31DDBA7E0EE95D633EA22/0028/-1" rel="http://www.sap.com/adt/relations/documentation" type="text/html"/>
        </atcfinding:finding>
      </atcobject:findings>
    </atcobject:object>
  </atcworklist:objects>
</atcworklist:worklist>'''
