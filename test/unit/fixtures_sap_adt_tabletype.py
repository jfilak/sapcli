TABLE_TYPE_NAME = 'ZSAPCLI_TT_DATA'

FAKE_LOCK_HANDLE = 'lock_handle'

TABLE_TYPE_ADT_VALUE_HELPS_XML = '''<ttyp:valueHelps>
    <ttyp:typeKindValues>
      <ttyp:valueHelp ttyp:key="dictionaryType" ttyp:value="Dictionary Type" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="predefinedAbapType" ttyp:value="Predefined Type" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="refToPredefinedAbapType" ttyp:value="Reference to Predefined Type" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="refToDictionaryType" ttyp:value="Reference to Dictionary Type" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="refToClassOrInterfaceType" ttyp:value="Reference to Class/Interface" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="rangeTypeOnPredefinedType" ttyp:value="Range Table on Predefined Type" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="rangeTypeOnDataelement" ttyp:value="Range Table on Data Element" ttyp:description=""/>
    </ttyp:typeKindValues>
    <ttyp:keyDefinitionValues>
      <ttyp:valueHelp ttyp:key="standard" ttyp:value="Standard Key" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="rowType" ttyp:value="Row Type" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="keyComponents" ttyp:value="Key Components" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="empty" ttyp:value="Empty Key" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="notSpecified" ttyp:value="Not Specified" ttyp:description=""/>
    </ttyp:keyDefinitionValues>
    <ttyp:keyKindValues>
      <ttyp:valueHelp ttyp:key="unique" ttyp:value="Unique" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="nonUnique" ttyp:value="Non-Unique" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="notSpecified" ttyp:value="Not Specified" ttyp:description=""/>
    </ttyp:keyKindValues>
    <ttyp:accessTypeValues>
      <ttyp:valueHelp ttyp:key="standard" ttyp:value="Standard Table" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="sorted" ttyp:value="Sorted Table" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="hashed" ttyp:value="Hashed Table" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="index" ttyp:value="Index Table" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="notSpecified" ttyp:value="Not Specified" ttyp:description=""/>
    </ttyp:accessTypeValues>
    <ttyp:secKeyAccessValues>
      <ttyp:valueHelp ttyp:key="uniqueHashed" ttyp:value="Unique Hashed" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="uniqueSorted" ttyp:value="Unique Sorted" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="nonUniqueSorted" ttyp:value="Non-Unique Sorted" ttyp:description=""/>
    </ttyp:secKeyAccessValues>
    <ttyp:secKeyDefinitionValues>
      <ttyp:valueHelp ttyp:key="rowType" ttyp:value="Row Type" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="keyComponents" ttyp:value="Key Components" ttyp:description=""/>
    </ttyp:secKeyDefinitionValues>
    <ttyp:secKeyAllowedValues>
      <ttyp:valueHelp ttyp:key="allowed" ttyp:value="Allowed" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="notAllowed" ttyp:value="Not Allowed" ttyp:description=""/>
      <ttyp:valueHelp ttyp:key="notSpecified" ttyp:value="Not Specified" ttyp:description=""/>
    </ttyp:secKeyAllowedValues>
  </ttyp:valueHelps>'''

# Response to GET of a just created table type - ADT fills in the defaults
TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<ttyp:tableType adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:abapLanguageVersion="standard" adtcore:name="{TABLE_TYPE_NAME}" adtcore:type="TTYP/DA" adtcore:changedAt="2026-10-17T18:18:02Z" adtcore:version="new" adtcore:createdAt="2026-10-17T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="Test table type" adtcore:descriptionTextLimit="60" adtcore:language="EN" xmlns:ttyp="http://www.sap.com/dictionary/tabletype" xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <atom:link href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Ftabletypes%2F{TABLE_TYPE_NAME.lower()}" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" type="application/vnd.sap.adt.nameditems.v1+xml" title="Allowed ABAP language versions" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <atom:link href="/sap/bc/adt/vit/wb/object_type/ttypda/object_name/" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP Gui" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <atom:link href="./{TABLE_TYPE_NAME.lower()}" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Landing Page (HTML)" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:description="Temporary Objects (never transported!)"/>
  <ttyp:rowType>
    <ttyp:typeKind>predefinedAbapType</ttyp:typeKind>
    <ttyp:typeName/>
    <ttyp:builtInType>
      <ttyp:dataType>CHAR</ttyp:dataType>
      <ttyp:length>000001</ttyp:length>
      <ttyp:decimals>000000</ttyp:decimals>
    </ttyp:builtInType>
    <ttyp:rangeType/>
  </ttyp:rowType>
  <ttyp:initialRowCount>00000</ttyp:initialRowCount>
  <ttyp:accessType>standard</ttyp:accessType>
  <ttyp:primaryKey ttyp:isVisible="true" ttyp:isEditable="true">
    <ttyp:definition>standard</ttyp:definition>
    <ttyp:kind>nonUnique</ttyp:kind>
    <ttyp:components ttyp:isVisible="false"/>
    <ttyp:alias/>
  </ttyp:primaryKey>
  <ttyp:secondaryKeys ttyp:isVisible="true" ttyp:isEditable="true">
    <ttyp:allowed>notSpecified</ttyp:allowed>
  </ttyp:secondaryKeys>
  {TABLE_TYPE_ADT_VALUE_HELPS_XML}
</ttyp:tableType>'''

# Response to GET of a sorted table type of a structure with a unique key
TABLE_TYPE_ADT_GET_KEY_COMPONENTS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<ttyp:tableType adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:abapLanguageVersion="standard" adtcore:name="{TABLE_TYPE_NAME}" adtcore:type="TTYP/DA" adtcore:changedAt="2026-10-17T18:18:13Z" adtcore:version="active" adtcore:createdAt="2026-10-17T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="Test table type" adtcore:descriptionTextLimit="60" adtcore:language="EN" xmlns:ttyp="http://www.sap.com/dictionary/tabletype" xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <atom:link href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Ftabletypes%2F{TABLE_TYPE_NAME.lower()}" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" type="application/vnd.sap.adt.nameditems.v1+xml" title="Allowed ABAP language versions" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <atom:link href="/sap/bc/adt/vit/wb/object_type/ttypda/object_name/" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP Gui" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <atom:link href="./{TABLE_TYPE_NAME.lower()}" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Landing Page (HTML)" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:description="Temporary Objects (never transported!)"/>
  <ttyp:rowType>
    <ttyp:typeKind>dictionaryType</ttyp:typeKind>
    <ttyp:typeName>BAPIRET2</ttyp:typeName>
    <ttyp:builtInType>
      <ttyp:dataType>STRU</ttyp:dataType>
      <ttyp:length>000000</ttyp:length>
      <ttyp:decimals>000000</ttyp:decimals>
    </ttyp:builtInType>
    <ttyp:rangeType/>
  </ttyp:rowType>
  <ttyp:initialRowCount>00000</ttyp:initialRowCount>
  <ttyp:accessType>sorted</ttyp:accessType>
  <ttyp:primaryKey ttyp:isVisible="true" ttyp:isEditable="true">
    <ttyp:definition>keyComponents</ttyp:definition>
    <ttyp:kind>unique</ttyp:kind>
    <ttyp:components ttyp:isVisible="true">
      <ttyp:component ttyp:name="TYPE"/>
      <ttyp:component ttyp:name="ID"/>
    </ttyp:components>
    <ttyp:alias/>
  </ttyp:primaryKey>
  <ttyp:secondaryKeys ttyp:isVisible="true" ttyp:isEditable="true">
    <ttyp:allowed>notSpecified</ttyp:allowed>
  </ttyp:secondaryKeys>
  {TABLE_TYPE_ADT_VALUE_HELPS_XML}
</ttyp:tableType>'''

# Response to GET of a table type with a secondary key (taken from /AIF/CDATA_T)
TABLE_TYPE_ADT_GET_SECONDARY_KEYS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<ttyp:tableType adtcore:responsible="SAP" adtcore:masterLanguage="EN" adtcore:masterSystem="SAP" adtcore:abapLanguageVersion="standard" adtcore:name="{TABLE_TYPE_NAME}" adtcore:type="TTYP/DA" adtcore:changedAt="2024-02-02T15:36:35Z" adtcore:version="active" adtcore:changedBy="SAP" adtcore:createdBy="SAP" adtcore:description="Table for changed data (fields)" adtcore:descriptionTextLimit="60" adtcore:language="EN" xmlns:ttyp="http://www.sap.com/dictionary/tabletype" xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link href="versions" rel="http://www.sap.com/adt/relations/versions" title="Historic versions" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <atom:link href="/sap/bc/adt/repository/informationsystem/abaplanguageversions?uri=%2Fsap%2Fbc%2Fadt%2Fddic%2Ftabletypes%2F{TABLE_TYPE_NAME.lower()}" rel="http://www.sap.com/adt/relations/informationsystem/abaplanguageversions" type="application/vnd.sap.adt.nameditems.v1+xml" title="Allowed ABAP language versions" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <atom:link href="/sap/bc/adt/vit/wb/object_type/ttypda/object_name/" rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP Gui" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <atom:link href="./{TABLE_TYPE_NAME.lower()}" rel="http://www.sap.com/adt/relations/source" type="text/html" title="Landing Page (HTML)" xmlns:atom="http://www.w3.org/2005/Atom"/>
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%2faif%2fchange_log_db" adtcore:type="DEVC/K" adtcore:name="/AIF/CHANGE_LOG_DB" adtcore:description="AIF Change Log DB"/>
  <ttyp:rowType>
    <ttyp:typeKind>dictionaryType</ttyp:typeKind>
    <ttyp:typeName>/AIF/CDATA_S</ttyp:typeName>
    <ttyp:builtInType>
      <ttyp:dataType>STRU</ttyp:dataType>
      <ttyp:length>000000</ttyp:length>
      <ttyp:decimals>000000</ttyp:decimals>
    </ttyp:builtInType>
    <ttyp:rangeType/>
  </ttyp:rowType>
  <ttyp:initialRowCount>00000</ttyp:initialRowCount>
  <ttyp:accessType>standard</ttyp:accessType>
  <ttyp:primaryKey ttyp:isVisible="true" ttyp:isEditable="true">
    <ttyp:definition>standard</ttyp:definition>
    <ttyp:kind>nonUnique</ttyp:kind>
    <ttyp:components ttyp:isVisible="false"/>
    <ttyp:alias/>
  </ttyp:primaryKey>
  <ttyp:secondaryKeys ttyp:isVisible="true" ttyp:isEditable="true">
    <ttyp:allowed>notSpecified</ttyp:allowed>
    <ttyp:secondaryKey ttyp:identifier="PATH_LINE" ttyp:description="key for field path and line number" ttyp:language="E" ttyp:access="nonUniqueSorted" ttyp:definition="keyComponents">
      <ttyp:components ttyp:isVisible="true">
        <ttyp:component ttyp:name="FIELD_PATH"/>
        <ttyp:component ttyp:name="LINE_NR"/>
      </ttyp:components>
    </ttyp:secondaryKey>
  </ttyp:secondaryKeys>
  {TABLE_TYPE_ADT_VALUE_HELPS_XML}
</ttyp:tableType>'''

# Response to GET of a range table type (taken from /AIF/NRT_MSGGUID_RANGE_T)
TABLE_TYPE_ADT_GET_RANGE_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<ttyp:tableType adtcore:responsible="SAP" adtcore:masterLanguage="EN" adtcore:masterSystem="SAP" adtcore:abapLanguageVersion="standard" adtcore:name="{TABLE_TYPE_NAME}" adtcore:type="TTYP/DA" adtcore:changedAt="2024-02-02T15:36:35Z" adtcore:version="active" adtcore:changedBy="SAP" adtcore:createdBy="SAP" adtcore:description="Range table" adtcore:descriptionTextLimit="60" adtcore:language="EN" xmlns:ttyp="http://www.sap.com/dictionary/tabletype" xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP" adtcore:description="Temporary Objects (never transported!)"/>
  <ttyp:rowType>
    <ttyp:typeKind>rangeTypeOnDataelement</ttyp:typeKind>
    <ttyp:typeName>/AIF/NRT_MSGGUID_E</ttyp:typeName>
    <ttyp:builtInType>
      <ttyp:dataType>RAW</ttyp:dataType>
      <ttyp:length>000016</ttyp:length>
      <ttyp:decimals>000000</ttyp:decimals>
    </ttyp:builtInType>
    <ttyp:rangeType>/AIF/NRT_MSGGUID_RANGE_S</ttyp:rangeType>
  </ttyp:rowType>
  <ttyp:initialRowCount>00000</ttyp:initialRowCount>
  <ttyp:accessType>standard</ttyp:accessType>
  <ttyp:primaryKey ttyp:isVisible="true" ttyp:isEditable="true">
    <ttyp:definition>standard</ttyp:definition>
    <ttyp:kind>nonUnique</ttyp:kind>
    <ttyp:components ttyp:isVisible="false"/>
    <ttyp:alias/>
  </ttyp:primaryKey>
  <ttyp:secondaryKeys ttyp:isVisible="true" ttyp:isEditable="true">
    <ttyp:allowed>notSpecified</ttyp:allowed>
  </ttyp:secondaryKeys>
  {TABLE_TYPE_ADT_VALUE_HELPS_XML}
</ttyp:tableType>'''

# Request body of POST creating a new table type - ADT wants only the header
TABLE_TYPE_ADT_NEW_OBJECT_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<ttyp:tableType xmlns:ttyp="http://www.sap.com/dictionary/tabletype" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="TTYP/DA" adtcore:description="Test table type" adtcore:language="EN" adtcore:name="{TABLE_TYPE_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
</ttyp:tableType>'''

TABLE_TYPE_ADT_SERIALIZED_VALUE_HELPS_XML = '''<ttyp:valueHelps>
<ttyp:typeKindValues>
<ttyp:valueHelp ttyp:key="dictionaryType" ttyp:value="Dictionary Type" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="predefinedAbapType" ttyp:value="Predefined Type" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="refToPredefinedAbapType" ttyp:value="Reference to Predefined Type" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="refToDictionaryType" ttyp:value="Reference to Dictionary Type" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="refToClassOrInterfaceType" ttyp:value="Reference to Class/Interface" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="rangeTypeOnPredefinedType" ttyp:value="Range Table on Predefined Type" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="rangeTypeOnDataelement" ttyp:value="Range Table on Data Element" ttyp:description=""/>
</ttyp:typeKindValues>
<ttyp:keyDefinitionValues>
<ttyp:valueHelp ttyp:key="standard" ttyp:value="Standard Key" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="rowType" ttyp:value="Row Type" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="keyComponents" ttyp:value="Key Components" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="empty" ttyp:value="Empty Key" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="notSpecified" ttyp:value="Not Specified" ttyp:description=""/>
</ttyp:keyDefinitionValues>
<ttyp:keyKindValues>
<ttyp:valueHelp ttyp:key="unique" ttyp:value="Unique" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="nonUnique" ttyp:value="Non-Unique" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="notSpecified" ttyp:value="Not Specified" ttyp:description=""/>
</ttyp:keyKindValues>
<ttyp:accessTypeValues>
<ttyp:valueHelp ttyp:key="standard" ttyp:value="Standard Table" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="sorted" ttyp:value="Sorted Table" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="hashed" ttyp:value="Hashed Table" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="index" ttyp:value="Index Table" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="notSpecified" ttyp:value="Not Specified" ttyp:description=""/>
</ttyp:accessTypeValues>
<ttyp:secKeyAccessValues>
<ttyp:valueHelp ttyp:key="uniqueHashed" ttyp:value="Unique Hashed" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="uniqueSorted" ttyp:value="Unique Sorted" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="nonUniqueSorted" ttyp:value="Non-Unique Sorted" ttyp:description=""/>
</ttyp:secKeyAccessValues>
<ttyp:secKeyDefinitionValues>
<ttyp:valueHelp ttyp:key="rowType" ttyp:value="Row Type" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="keyComponents" ttyp:value="Key Components" ttyp:description=""/>
</ttyp:secKeyDefinitionValues>
<ttyp:secKeyAllowedValues>
<ttyp:valueHelp ttyp:key="allowed" ttyp:value="Allowed" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="notAllowed" ttyp:value="Not Allowed" ttyp:description=""/>
<ttyp:valueHelp ttyp:key="notSpecified" ttyp:value="Not Specified" ttyp:description=""/>
</ttyp:secKeyAllowedValues>
</ttyp:valueHelps>'''

# Request body of PUT defining the new table type as a standard table of a structure
TABLE_TYPE_ADT_DEFINE_STANDARD_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<ttyp:tableType xmlns:ttyp="http://www.sap.com/dictionary/tabletype" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="TTYP/DA" adtcore:description="Test table type" adtcore:language="EN" adtcore:name="{TABLE_TYPE_NAME}" adtcore:abapLanguageVersion="standard" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:responsible="DEVELOPER" adtcore:version="new">
<adtcore:packageRef adtcore:name="$TMP"/>
<ttyp:rowType>
<ttyp:typeKind>dictionaryType</ttyp:typeKind>
<ttyp:typeName>BAPIRET2</ttyp:typeName>
<ttyp:builtInType>
<ttyp:dataType></ttyp:dataType>
<ttyp:length>0</ttyp:length>
<ttyp:decimals>0</ttyp:decimals>
</ttyp:builtInType>
<ttyp:rangeType></ttyp:rangeType>
</ttyp:rowType>
<ttyp:initialRowCount>00000</ttyp:initialRowCount>
<ttyp:accessType>standard</ttyp:accessType>
<ttyp:primaryKey ttyp:isVisible="true" ttyp:isEditable="true">
<ttyp:definition>standard</ttyp:definition>
<ttyp:kind>nonUnique</ttyp:kind>
<ttyp:components ttyp:isVisible="false"/>
<ttyp:alias></ttyp:alias>
</ttyp:primaryKey>
<ttyp:secondaryKeys ttyp:isVisible="true" ttyp:isEditable="true">
<ttyp:allowed>notSpecified</ttyp:allowed>
</ttyp:secondaryKeys>
{TABLE_TYPE_ADT_SERIALIZED_VALUE_HELPS_XML}
</ttyp:tableType>'''

# Request body of PUT defining the new table type as a sorted table of a structure with a unique key
TABLE_TYPE_ADT_DEFINE_SORTED_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<ttyp:tableType xmlns:ttyp="http://www.sap.com/dictionary/tabletype" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="TTYP/DA" adtcore:description="Test table type" adtcore:language="EN" adtcore:name="{TABLE_TYPE_NAME}" adtcore:abapLanguageVersion="standard" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:responsible="DEVELOPER" adtcore:version="new">
<adtcore:packageRef adtcore:name="$TMP"/>
<ttyp:rowType>
<ttyp:typeKind>dictionaryType</ttyp:typeKind>
<ttyp:typeName>BAPIRET2</ttyp:typeName>
<ttyp:builtInType>
<ttyp:dataType></ttyp:dataType>
<ttyp:length>0</ttyp:length>
<ttyp:decimals>0</ttyp:decimals>
</ttyp:builtInType>
<ttyp:rangeType></ttyp:rangeType>
</ttyp:rowType>
<ttyp:initialRowCount>00000</ttyp:initialRowCount>
<ttyp:accessType>sorted</ttyp:accessType>
<ttyp:primaryKey ttyp:isVisible="true" ttyp:isEditable="true">
<ttyp:definition>keyComponents</ttyp:definition>
<ttyp:kind>unique</ttyp:kind>
<ttyp:components ttyp:isVisible="true">
<ttyp:component ttyp:name="TYPE"/>
<ttyp:component ttyp:name="ID"/>
</ttyp:components>
<ttyp:alias></ttyp:alias>
</ttyp:primaryKey>
<ttyp:secondaryKeys ttyp:isVisible="true" ttyp:isEditable="true">
<ttyp:allowed>notSpecified</ttyp:allowed>
</ttyp:secondaryKeys>
{TABLE_TYPE_ADT_SERIALIZED_VALUE_HELPS_XML}
</ttyp:tableType>'''

# Request body of PUT with a secondary key - serialized from TABLE_TYPE_ADT_GET_SECONDARY_KEYS_RESPONSE_XML
TABLE_TYPE_ADT_SECONDARY_KEYS_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<ttyp:tableType xmlns:ttyp="http://www.sap.com/dictionary/tabletype" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="TTYP/DA" adtcore:description="Table for changed data (fields)" adtcore:language="EN" adtcore:name="{TABLE_TYPE_NAME}" adtcore:abapLanguageVersion="standard" adtcore:masterLanguage="EN" adtcore:masterSystem="SAP" adtcore:responsible="SAP" adtcore:version="active">
<adtcore:packageRef adtcore:name="/AIF/CHANGE_LOG_DB"/>
<ttyp:rowType>
<ttyp:typeKind>dictionaryType</ttyp:typeKind>
<ttyp:typeName>/AIF/CDATA_S</ttyp:typeName>
<ttyp:builtInType>
<ttyp:dataType>STRU</ttyp:dataType>
<ttyp:length>000000</ttyp:length>
<ttyp:decimals>000000</ttyp:decimals>
</ttyp:builtInType>
<ttyp:rangeType></ttyp:rangeType>
</ttyp:rowType>
<ttyp:initialRowCount>00000</ttyp:initialRowCount>
<ttyp:accessType>standard</ttyp:accessType>
<ttyp:primaryKey ttyp:isVisible="true" ttyp:isEditable="true">
<ttyp:definition>standard</ttyp:definition>
<ttyp:kind>nonUnique</ttyp:kind>
<ttyp:components ttyp:isVisible="false"/>
<ttyp:alias></ttyp:alias>
</ttyp:primaryKey>
<ttyp:secondaryKeys ttyp:isVisible="true" ttyp:isEditable="true">
<ttyp:allowed>notSpecified</ttyp:allowed>
<ttyp:secondaryKey ttyp:identifier="PATH_LINE" ttyp:description="key for field path and line number" ttyp:language="E" ttyp:access="nonUniqueSorted" ttyp:definition="keyComponents">
<ttyp:components ttyp:isVisible="true">
<ttyp:component ttyp:name="FIELD_PATH"/>
<ttyp:component ttyp:name="LINE_NR"/>
</ttyp:components>
</ttyp:secondaryKey>
</ttyp:secondaryKeys>
{TABLE_TYPE_ADT_SERIALIZED_VALUE_HELPS_XML}
</ttyp:tableType>'''

TABLE_TYPE_ADT_ACTIVATE_REQUEST_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/ddic/tabletypes/{TABLE_TYPE_NAME.lower()}" adtcore:name="{TABLE_TYPE_NAME}"/>
</adtcore:objectReferences>'''

TABLE_TYPE_ADT_ALREADY_EXISTS_RESPONSE_XML = f'''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="com.sap.adt"/><type id="ExceptionResourceAlreadyExists"/><message lang="EN">Resource Table Type {TABLE_TYPE_NAME} does already exist.</message><localizedMessage lang="EN">Resource Table Type {TABLE_TYPE_NAME} does already exist.</localizedMessage><properties/></exc:exception>'''
