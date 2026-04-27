TRANSACTION_NAME = 'ZABAPGIT'

TRANSACTION_DEFINITION_ADT_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue"
 abapsource:sourceUri="./zabapgit/source/main"
 abapsource:fixPointArithmetic="false"
 abapsource:activeUnicodeCheck="false"
 adtcore:responsible="DEVELOPER"
 adtcore:masterLanguage="EN"
 adtcore:masterSystem="C50"
 adtcore:abapLanguageVersion="standard"
 adtcore:name="{TRANSACTION_NAME}"
 adtcore:type="TRAN/T"
 adtcore:changedAt="2026-04-26T15:30:28Z"
 adtcore:createdAt="2026-04-26T15:30:28Z"
 adtcore:changedBy="DEVELOPER"
 adtcore:createdBy="DEVELOPER"
 adtcore:description="abapgit"
 adtcore:language="EN"
 xmlns:abapsource="http://www.sap.com/adt/abapsource"
 xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
   href="./zabapgit/source/main/versions"
   rel="http://www.sap.com/adt/relations/versions"
   title="Historic versions"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
   href="./zabapgit/source/main"
   rel="http://www.sap.com/adt/relations/source"
   type="application/json"
   title="Source Content"
   etag="20260426133029001application/json_YNQKQAjEkSb2pt9Yco1lyJhRcBs="/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
   href="./zabapgit/source/main"
   rel="http://www.sap.com/adt/relations/source"
   type="text/html"
   title="Source Content (HTML)"
   etag=""/>
  <adtcore:packageRef
   adtcore:uri="/sap/bc/adt/packages/%24tmp"
   adtcore:type="DEVC/K"
   adtcore:name="$TMP"
   adtcore:description="Temporary Objects (never transported!)"/>
</blue:blueSource>'''

CREATE_TRANSACTION_ADT_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="TRAN/T" adtcore:description="abapgit" adtcore:language="EN" adtcore:name="{TRANSACTION_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
</blue:blueSource>'''

REPORT_TRANSACTION_CREATION_JSON = '{' \
    '"abapLanguVersionText":"Standard ABAP",' \
    '"transactionType":"reportTransaction",' \
    '"reportName":"ZABAPGIT",' \
    '"reportDynnr":"1000",' \
    '"updateMode":"notSet",' \
    '"metadata":{' \
        '"name":"ZABAPGIT",' \
        '"description":"abapgit",' \
        '"package":"$TMP"' \
    '}' \
'}'

CREATE_TRANSACTION_WITH_CONTENT_ADT_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="TRAN/T" adtcore:description="abapgit" adtcore:language="EN" adtcore:name="{TRANSACTION_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
<blue:additionalCreationProperties>
<adtcore:content adtcore:encoding="base64" adtcore:type="application/vnd.sap.adt.serverdriven.content.v1+json">eyJhYmFwTGFuZ3VWZXJzaW9uVGV4dCI6IlN0YW5kYXJkIEFCQVAiLCJ0cmFuc2FjdGlvblR5cGUiOiJyZXBvcnRUcmFuc2FjdGlvbiIsInJlcG9ydE5hbWUiOiJaQUJBUEdJVCIsInJlcG9ydER5bm5yIjoiMTAwMCIsInVwZGF0ZU1vZGUiOiJub3RTZXQiLCJtZXRhZGF0YSI6eyJuYW1lIjoiWkFCQVBHSVQiLCJkZXNjcmlwdGlvbiI6ImFiYXBnaXQiLCJwYWNrYWdlIjoiJFRNUCJ9fQ==</adtcore:content>
</blue:additionalCreationProperties>
</blue:blueSource>'''

PARAMETER_TRANSACTION_NAME = 'ZJF_TEST_JAKUB'

# CLI fixtures use ANZEIGER as responsible (mock Connection default user)
CLI_CREATE_TRANSACTION_ADT_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="TRAN/T" adtcore:description="abapgit" adtcore:language="EN" adtcore:name="{TRANSACTION_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="ANZEIGER">
<adtcore:packageRef adtcore:name="$TMP"/>
</blue:blueSource>'''

CLI_CREATE_TRANSACTION_WITH_CONTENT_ADT_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="TRAN/T" adtcore:description="abapgit" adtcore:language="EN" adtcore:name="{TRANSACTION_NAME}" adtcore:masterLanguage="EN" adtcore:responsible="ANZEIGER">
<adtcore:packageRef adtcore:name="$TMP"/>
<blue:additionalCreationProperties>
<adtcore:content adtcore:encoding="base64" adtcore:type="application/vnd.sap.adt.serverdriven.content.v1+json">eyJhYmFwTGFuZ3VWZXJzaW9uVGV4dCI6IlN0YW5kYXJkIEFCQVAiLCJ0cmFuc2FjdGlvblR5cGUiOiJyZXBvcnRUcmFuc2FjdGlvbiIsInJlcG9ydE5hbWUiOiJaQUJBUEdJVCIsInJlcG9ydER5bm5yIjoiMTAwMCIsInVwZGF0ZU1vZGUiOiJub3RTZXQiLCJtZXRhZGF0YSI6eyJuYW1lIjoiWkFCQVBHSVQiLCJkZXNjcmlwdGlvbiI6ImFiYXBnaXQiLCJwYWNrYWdlIjoiJFRNUCJ9fQ==</adtcore:content>
</blue:additionalCreationProperties>
</blue:blueSource>'''

PARAMETER_TRANSACTION_CREATION_JSON = '{' \
    '"abapLanguVersionText":"Standard ABAP",' \
    '"transactionType":"parameterTransaction",' \
    '"parParentTransactionCode":"/AIF/28000003",' \
    '"updateMode":"notSet",' \
    '"metadata":{' \
        '"name":"ZJF_TEST_JAKUB",' \
        '"description":"test jakub",' \
        '"package":"$TMP"' \
    '}' \
'}'
