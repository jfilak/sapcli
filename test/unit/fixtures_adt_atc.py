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

# << Content-Type: application/xml; charset=utf-8
ADT_XML_ATC_RUN_RESPONSE_WITH_FINDINGS='''<?xml version="1.0" encoding="utf-8"?>
<atcworklist:worklist xmlns:atcworklist="http://www.sap.com/adt/atc/worklist" atcworklist:id="CB763CE23E611EDDB38C172F2E7607EB" atcworklist:timestamp="2023-03-27T05:32:22Z" atcworklist:usedObjectSet="00000000000000000000000000000000" atcworklist:objectSetIsComplete="false">
    <atcworklist:objectSets>
        <atcworklist:objectSet atcworklist:name="00000000000000000000000000000000" atcworklist:title="All Objects" atcworklist:kind="ALL"/>
    </atcworklist:objectSets>
    <atcworklist:objects>
        <atcobject:object xmlns:atcobject="http://www.sap.com/adt/atc/object" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/atc/objects/R3TR/APIS/OBJ1" adtcore:type="APIS" adtcore:name="OBJ1" adtcore:packageName="$TMP" atcobject:author="DEVELOPER">
            <atcobject:findings>
                <atcfinding:finding xmlns:atcfinding="http://www.sap.com/adt/atc/finding" adtcore:uri="/sap/bc/adt/atc/findings/itemid/A32FC0C4E8521EDDB1F11923DA6F0C5A/index/9" atcfinding:location="/sap/bc/adt/vit/atc/runs/CB763CE23E611EDDB38C172F2E7607EB/verdict/OBJ1/APIS/005056AB5B8D1ED4BFDA1CA5D9EBA6C4/0898/974362469" atcfinding:processor="DEVELOPER" atcfinding:lastChangedBy="" atcfinding:priority="1" atcfinding:checkId="005056AB5B8D1ED4BFDA1CA5D9EBA6C4" atcfinding:checkTitle="Test Environment (CHK_ZDM)" atcfinding:messageId="0898" atcfinding:messageTitle="Exception occurred (see details)" atcfinding:exemptionApproval="" atcfinding:exemptionKind="" atcfinding:checksum="974362469">
                    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/documentation/atc/documents/itemid/A32FC0C4E8521EDDB1F11923DA6F0C5A/index/9" rel="http://www.sap.com/adt/relations/documentation" type="text/html"/>
                    <atcfinding:quickfixes atcfinding:manual="false" atcfinding:automatic="false" atcfinding:pseudo="false"/>
                </atcfinding:finding>
                <atcfinding:finding xmlns:atcfinding="http://www.sap.com/adt/atc/finding" adtcore:uri="/sap/bc/adt/atc/findings/itemid/A32FC0C4E8521EDDB1F11923DA6F0C5A/index/9" atcfinding:location="/sap/bc/adt/vit/atc/runs/CB763CE23E611EDDB38C172F2E7607EB/verdict/OBJ1/APIS/005056AB5B8D1ED4BFDA1CA5D9EBA6C4/0898/974362469" atcfinding:processor="DEVELOPER" atcfinding:lastChangedBy="" atcfinding:priority="one" atcfinding:checkId="005056AB5B8D1ED4BFDA1CA5D9EBA6C4" atcfinding:checkTitle="Test Environment (CHK_ZDM)" atcfinding:messageId="0898" atcfinding:messageTitle="Exception occurred (see details)" atcfinding:exemptionApproval="" atcfinding:exemptionKind="" atcfinding:checksum="974362469">
                    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/documentation/atc/documents/itemid/A32FC0C4E8521EDDB1F11923DA6F0C5A/index/9" rel="http://www.sap.com/adt/relations/documentation" type="text/html"/>
                    <atcfinding:quickfixes atcfinding:manual="false" atcfinding:automatic="false" atcfinding:pseudo="false"/>
                </atcfinding:finding>
            </atcobject:findings>
        </atcobject:object>
        <atcobject:object xmlns:atcobject="http://www.sap.com/adt/atc/object" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/atc/objects/R3TR/TABL/TBL1" adtcore:type="TABL" adtcore:name="TBL1" adtcore:packageName="$TMP" atcobject:author="DEVELOPER">
            <atcobject:findings/>
        </atcobject:object>
    </atcworklist:objects>
    <atcworklist:infos/>
 </atcworklist:worklist>'''

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

# POST /sap/bc/adt/datapreview/freestyle?sap-client=500&saml2=disabled&rowNumber=99999&dataAging=true
ADT_XML_PROFILES_TABLE='''<?xml version="1.0" encoding="utf-8"?>
<dataPreview:tableData xmlns:dataPreview="http://www.sap.com/adt/dataPreview">
	<dataPreview:totalRows>23</dataPreview:totalRows>
	<dataPreview:isHanaAnalyticalView>false</dataPreview:isHanaAnalyticalView>
	<dataPreview:executedQueryString>SELECT CHKPRFID, CRETSTAMP, CREUSER, CHGTSTAMP, CHGUSER FROM CRMCHKPRFH   INTO     TABLE @DATA(LT_RESULT)   UP TO 99999  ROWS   .</dataPreview:executedQueryString>
	<dataPreview:queryExecutionTime>13.7210000</dataPreview:queryExecutionTime>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="CHKPRFID" dataPreview:type="C" dataPreview:description="CHKPRFID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>PROFILE1</dataPreview:data>
			<dataPreview:data>PROFILE2</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="CRETSTAMP" dataPreview:type="N" dataPreview:description="CRETSTAMP" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>20010309180000</dataPreview:data>
			<dataPreview:data>20010328100000</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="CREUSER" dataPreview:type="C" dataPreview:description="CREUSER" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>CREUSER1</dataPreview:data>
			<dataPreview:data>CREUSER2</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="CHGTSTAMP" dataPreview:type="N" dataPreview:description="CHGTSTAMP" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>20080415161735</dataPreview:data>
			<dataPreview:data>00000000000000</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="CHGUSER" dataPreview:type="C" dataPreview:description="CHGUSER" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>CHGUSER1</dataPreview:data>
			<dataPreview:data />
		</dataPreview:dataSet>
	</dataPreview:columns>
</dataPreview:tableData>
'''

# POST /sap/bc/adt/datapreview/freestyle?sap-client=500&saml2=disabled&rowNumber=99999&dataAging=true
ADT_XML_PROFILES_TRAN_TABLE='''<?xml version="1.0" encoding="utf-8"?>
<dataPreview:tableData xmlns:dataPreview="http://www.sap.com/adt/dataPreview">
	<dataPreview:totalRows>134</dataPreview:totalRows>
	<dataPreview:isHanaAnalyticalView>false</dataPreview:isHanaAnalyticalView>
	<dataPreview:executedQueryString>SELECT LANGU, CHKPRFID, TXTCHKPRF FROM CRMCHKPRFT   INTO     TABLE @DATA(LT_RESULT)   UP TO 99999  ROWS   .</dataPreview:executedQueryString>
	<dataPreview:queryExecutionTime>5.6360000</dataPreview:queryExecutionTime>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="LANGU" dataPreview:type="C" dataPreview:description="LANGU" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>E</dataPreview:data>
			<dataPreview:data>E</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="CHKPRFID" dataPreview:type="C" dataPreview:description="CHKPRFID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>PROFILE1</dataPreview:data>
			<dataPreview:data>PROFILE2</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="TXTCHKPRF" dataPreview:type="C" dataPreview:description="TXTCHKPRF" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>Standard Check Profile1 CheckMan 6.20</dataPreview:data>
			<dataPreview:data>Standard Check Profile2 CheckMan 6.20</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
</dataPreview:tableData>'''


# POST /sap/bc/adt/datapreview/freestyle?sap-client=500&saml2=disabled&rowNumber=99999&dataAging=true
ADT_XML_PROFILES_CHECKS_TABLE='''<?xml version="1.0" encoding="utf-8"?>
<dataPreview:tableData xmlns:dataPreview="http://www.sap.com/adt/dataPreview">
	<dataPreview:totalRows>928</dataPreview:totalRows>
	<dataPreview:isHanaAnalyticalView>false</dataPreview:isHanaAnalyticalView>
	<dataPreview:executedQueryString>SELECT CHKPRFID, CHKID, SEQNBR, SINCE, NOTE FROM CRMCHKPRF   INTO     TABLE @DATA(LT_RESULT)   UP TO 99999  ROWS   .</dataPreview:executedQueryString>
	<dataPreview:queryExecutionTime>7.3740000</dataPreview:queryExecutionTime>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="CHKPRFID" dataPreview:type="C" dataPreview:description="CHKPRFID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>PROFILE1</dataPreview:data>
			<dataPreview:data>PROFILE1</dataPreview:data>
			<dataPreview:data>PROFILE2</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="CHKID" dataPreview:type="C" dataPreview:description="CHKID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>CHECK1_1</dataPreview:data>
			<dataPreview:data>CHECK1_2</dataPreview:data>
			<dataPreview:data>CHECK2_1</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="SEQNBR" dataPreview:type="N" dataPreview:description="SEQNBR" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>00000001</dataPreview:data>
			<dataPreview:data>00000002</dataPreview:data>
			<dataPreview:data>00000003</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
    <dataPreview:metadata dataPreview:name="SINCE" dataPreview:type="D" dataPreview:description="SINCE" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
		<dataPreview:dataSet>
			<dataPreview:data>00000091</dataPreview:data>
			<dataPreview:data>00000092</dataPreview:data>
			<dataPreview:data>00000093</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="NOTE" dataPreview:type="C" dataPreview:description="NOTE" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>Note PRF1 CHK1</dataPreview:data>
			<dataPreview:data>Note PRF1 CHK2</dataPreview:data>
			<dataPreview:data>Note PRF2 CHK1</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
</dataPreview:tableData>'''

# POST /sap/bc/adt/datapreview/freestyle?sap-client=500&saml2=disabled&rowNumber=99999&dataAging=true
ADT_XML_PROFILES_CHKMSG_LOCAL_TABLE='''<?xml version="1.0" encoding="utf-8"?>
<dataPreview:tableData xmlns:dataPreview="http://www.sap.com/adt/dataPreview">
	<dataPreview:totalRows>624</dataPreview:totalRows>
	<dataPreview:isHanaAnalyticalView>false</dataPreview:isHanaAnalyticalView>
	<dataPreview:executedQueryString>SELECT CHKID, CHKVIEW, CHKMSGID, LOCAL_PRIO, DEACTIVATED, VALID_TO, VALID_ID FROM  CRMCHKMSG_LOCAL   INTO     TABLE @DATA(LT_RESULT)   UP TO 99999  ROWS   .</dataPreview:executedQueryString>
	<dataPreview:queryExecutionTime>31.6760000</dataPreview:queryExecutionTime>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="CHKID" dataPreview:type="C" dataPreview:description="CHKID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>CHECK1_1</dataPreview:data>
			<dataPreview:data>CHECK1_2</dataPreview:data>
			<dataPreview:data>CHECK2_1</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="CHKVIEW" dataPreview:type="C" dataPreview:description="CHKVIEW" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data />
			<dataPreview:data />
			<dataPreview:data />
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="CHKMSGID" dataPreview:type="C" dataPreview:description="CHKMSGID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>0001</dataPreview:data>
			<dataPreview:data>EHPW</dataPreview:data>
			<dataPreview:data>NEXO</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="LOCAL_PRIO" dataPreview:type="N" dataPreview:description="LOCAL_PRIO" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>2</dataPreview:data>
			<dataPreview:data>4</dataPreview:data>
			<dataPreview:data>1</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="DEACTIVATED" dataPreview:type="C" dataPreview:description="DEACTIVATED" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data />
			<dataPreview:data>X</dataPreview:data>
			<dataPreview:data />
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="VALID_TO" dataPreview:type="D" dataPreview:description="VALID_TO" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data>20250802</dataPreview:data>
			<dataPreview:data>20250802</dataPreview:data>
			<dataPreview:data>20250802</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
	<dataPreview:columns>
		<dataPreview:metadata dataPreview:name="VALID_ID" dataPreview:type="C" dataPreview:description="VALID_ID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false" />
		<dataPreview:dataSet>
			<dataPreview:data />
			<dataPreview:data>Requested by Bob and Alice</dataPreview:data>
			<dataPreview:data>Added 16/01/2020</dataPreview:data>
		</dataPreview:dataSet>
	</dataPreview:columns>
</dataPreview:tableData>'''

ADT_XML_CRMCHK_TABLE='''<?xml version="1.0" encoding="UTF-8"?><dataPreview:tableData xmlns:dataPreview="http://www.sap.com/adt/dataPreview">
  <dataPreview:totalRows>187</dataPreview:totalRows>
  <dataPreview:isHanaAnalyticalView>false</dataPreview:isHanaAnalyticalView>
  <dataPreview:executedQueryString>SELECT CHKID, CLCHK FROM CRMCHK   INTO     TABLE @DATA(LT_RESULT)   UP TO 100  ROWS   .</dataPreview:executedQueryString>
  <dataPreview:queryExecutionTime>0.1930000</dataPreview:queryExecutionTime>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="CHKID" dataPreview:type="C" dataPreview:description="CHKID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>CHECK1_1</dataPreview:data>
      <dataPreview:data>CHECK1_2</dataPreview:data>
      <dataPreview:data>CHECK2_1</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="CLCHK" dataPreview:type="C" dataPreview:description="CLCHK" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>CL_CHK_1_1</dataPreview:data>
      <dataPreview:data>CL_CHK_1_2</dataPreview:data>
      <dataPreview:data>CL_CHK_2_1</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
</dataPreview:tableData>
'''

ADT_XML_CRMCHKT_TABLE='''<?xml version="1.0" encoding="UTF-8"?><dataPreview:tableData xmlns:dataPreview="http://www.sap.com/adt/dataPreview">
  <dataPreview:totalRows>182</dataPreview:totalRows>
  <dataPreview:isHanaAnalyticalView>false</dataPreview:isHanaAnalyticalView>
  <dataPreview:executedQueryString>SELECT CHKID, TXTCHK FROM CRMCHKT WHERE LANGU = 'E'   INTO     TABLE @DATA(LT_RESULT)   UP TO 100  ROWS   .</dataPreview:executedQueryString>
  <dataPreview:queryExecutionTime>1.8110000</dataPreview:queryExecutionTime>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="CHKID" dataPreview:type="C" dataPreview:description="CHKID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>CHECK1_1</dataPreview:data>
      <dataPreview:data>CHECK1_2</dataPreview:data>
      <dataPreview:data>CHECK2_1</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="TXTCHK" dataPreview:type="C" dataPreview:description="TXTCHK" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>Description for check 1_1</dataPreview:data>
      <dataPreview:data>Description for check 1_2</dataPreview:data>
      <dataPreview:data>Description for check 2_1</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
</dataPreview:tableData>
'''

ADT_XML_CRMCHKMSG_TABLE='''<?xml version="1.0" encoding="UTF-8"?><dataPreview:tableData xmlns:dataPreview="http://www.sap.com/adt/dataPreview">
  <dataPreview:totalRows>2229</dataPreview:totalRows>
  <dataPreview:isHanaAnalyticalView>false</dataPreview:isHanaAnalyticalView>
  <dataPreview:executedQueryString>SELECT CHKID, CHKVIEW, CHKMSGID, DEFAULTMSGPRIO, CHKMSGPRIO FROM CRMCHKMSG   INTO     TABLE @DATA(LT_RESULT)   UP TO 100  ROWS   .</dataPreview:executedQueryString>
  <dataPreview:queryExecutionTime>8.8280000</dataPreview:queryExecutionTime>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="CHKID" dataPreview:type="C" dataPreview:description="CHKID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>CHECK1_1</dataPreview:data>
      <dataPreview:data>CHECK1_2</dataPreview:data>
      <dataPreview:data>CHECK2_1</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="CHKVIEW" dataPreview:type="C" dataPreview:description="CHKVIEW" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data/>
      <dataPreview:data/>
      <dataPreview:data/>
    </dataPreview:dataSet>
  </dataPreview:columns>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="CHKMSGID" dataPreview:type="C" dataPreview:description="CHKMSGID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>MSG1_1_1</dataPreview:data>
      <dataPreview:data>MSG1_1_2</dataPreview:data>
      <dataPreview:data>MSG1_1_3</dataPreview:data>
      <dataPreview:data>MSG1_2_1</dataPreview:data>
      <dataPreview:data>MSG2_1_1</dataPreview:data>
      <dataPreview:data>MSG2_1_2</dataPreview:data>
      <dataPreview:data>MSG2_1_3</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="DEFAULTMSGPRIO" dataPreview:type="N" dataPreview:description="DEFAULTMSGPRIO" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>1</dataPreview:data>
      <dataPreview:data>2</dataPreview:data>
      <dataPreview:data>3</dataPreview:data>
      <dataPreview:data>4</dataPreview:data>
      <dataPreview:data>5</dataPreview:data>
      <dataPreview:data>6</dataPreview:data>
      <dataPreview:data>7</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="CHKMSGPRIO" dataPreview:type="N" dataPreview:description="CHKMSGPRIO" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>11</dataPreview:data>
      <dataPreview:data>12</dataPreview:data>
      <dataPreview:data>13</dataPreview:data>
      <dataPreview:data>14</dataPreview:data>
      <dataPreview:data>15</dataPreview:data>
      <dataPreview:data>16</dataPreview:data>
      <dataPreview:data>17</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
</dataPreview:tableData>
'''

ADT_XML_CRMCHKMSGT_TABLE='''<?xml version="1.0" encoding="UTF-8"?><dataPreview:tableData xmlns:dataPreview="http://www.sap.com/adt/dataPreview">
  <dataPreview:totalRows>2201</dataPreview:totalRows>
  <dataPreview:isHanaAnalyticalView>false</dataPreview:isHanaAnalyticalView>
  <dataPreview:executedQueryString>SELECT CHKID, CHKMSGID, TXTCHKMSG FROM CRMCHKMSGT WHERE LANGU = 'E'   INTO     TABLE @DATA(LT_RESULT)   UP TO 100  ROWS   .</dataPreview:executedQueryString>
  <dataPreview:queryExecutionTime>2.0250000</dataPreview:queryExecutionTime>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="CHKID" dataPreview:type="C" dataPreview:description="CHKID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>CHECK1_1</dataPreview:data>
      <dataPreview:data>CHECK1_1</dataPreview:data>
      <dataPreview:data>CHECK1_1</dataPreview:data>
      <dataPreview:data>CHECK1_2</dataPreview:data>
      <dataPreview:data>CHECK2_1</dataPreview:data>
      <dataPreview:data>CHECK2_1</dataPreview:data>
      <dataPreview:data>CHECK2_1</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="CHKMSGID" dataPreview:type="C" dataPreview:description="CHKMSGID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>MSG1_1_1</dataPreview:data>
      <dataPreview:data>MSG1_1_2</dataPreview:data>
      <dataPreview:data>MSG1_1_3</dataPreview:data>
      <dataPreview:data>MSG1_2_1</dataPreview:data>
      <dataPreview:data>MSG2_1_1</dataPreview:data>
      <dataPreview:data>MSG2_1_2</dataPreview:data>
      <dataPreview:data>MSG2_1_3</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="TXTCHKMSG" dataPreview:type="C" dataPreview:description="TXTCHKMSG" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>Description for message MSG1_1_1 of check 1_1</dataPreview:data>
      <dataPreview:data>Description for message MSG1_1_2 of check 1_1</dataPreview:data>
      <dataPreview:data>Description for message MSG1_1_3 of check 1_1</dataPreview:data>
      <dataPreview:data>Description for message MSG1_2_1 of check 1_2</dataPreview:data>
      <dataPreview:data>Description for message MSG2_1_1 of check 2_1</dataPreview:data>
      <dataPreview:data>Description for message MSG2_1_2 of check 2_1</dataPreview:data>
      <dataPreview:data>Description for message MSG2_1_3 of check 2_1</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
</dataPreview:tableData>
'''

ADT_XML_CRM_CHECK_RULE_VIEW='''<?xml version="1.0" encoding="UTF-8"?><dataPreview:tableData xmlns:dataPreview="http://www.sap.com/adt/dataPreview">
  <dataPreview:totalRows>2200</dataPreview:totalRows>
  <dataPreview:isHanaAnalyticalView>false</dataPreview:isHanaAnalyticalView>
  <dataPreview:executedQueryString>SELECT CHKID, CHKMSGID, DEFAULTMSGPRIO, CHKMSGPRIO FROM CRM_CHECK_RULE   INTO     TABLE @DATA(LT_RESULT)   UP TO 100  ROWS   .</dataPreview:executedQueryString>
  <dataPreview:queryExecutionTime>2.8910000</dataPreview:queryExecutionTime>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="CHKID" dataPreview:type="C" dataPreview:description="CHKID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>CHECK1_1</dataPreview:data>
      <dataPreview:data>CHECK1_1</dataPreview:data>
      <dataPreview:data>CHECK1_1</dataPreview:data>
      <dataPreview:data>CHECK1_2</dataPreview:data>
      <dataPreview:data>CHECK2_1</dataPreview:data>
      <dataPreview:data>CHECK2_1</dataPreview:data>
      <dataPreview:data>CHECK2_1</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="CHKMSGID" dataPreview:type="C" dataPreview:description="CHKMSGID" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>MSG1_1_1</dataPreview:data>
      <dataPreview:data>MSG1_1_2</dataPreview:data>
      <dataPreview:data>MSG1_1_3</dataPreview:data>
      <dataPreview:data>MSG1_2_1</dataPreview:data>
      <dataPreview:data>MSG2_1_1</dataPreview:data>
      <dataPreview:data>MSG2_1_2</dataPreview:data>
      <dataPreview:data>MSG2_1_3</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="DEFAULTMSGPRIO" dataPreview:type="N" dataPreview:description="DEFAULTMSGPRIO" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>1</dataPreview:data>
      <dataPreview:data>2</dataPreview:data>
      <dataPreview:data>3</dataPreview:data>
      <dataPreview:data>4</dataPreview:data>
      <dataPreview:data>5</dataPreview:data>
      <dataPreview:data>6</dataPreview:data>
      <dataPreview:data>7</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
  <dataPreview:columns>
    <dataPreview:metadata dataPreview:name="CHKMSGPRIO" dataPreview:type="N" dataPreview:description="CHKMSGPRIO" dataPreview:keyAttribute="false" dataPreview:colType="" dataPreview:isKeyFigure="false"/>
    <dataPreview:dataSet>
      <dataPreview:data>11</dataPreview:data>
      <dataPreview:data>12</dataPreview:data>
      <dataPreview:data>13</dataPreview:data>
      <dataPreview:data>14</dataPreview:data>
      <dataPreview:data>15</dataPreview:data>
      <dataPreview:data>16</dataPreview:data>
      <dataPreview:data>17</dataPreview:data>
    </dataPreview:dataSet>
  </dataPreview:columns>
</dataPreview:tableData>
'''

