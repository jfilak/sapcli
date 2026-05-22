MESSAGE_CLASS_NAME = 'ZST_MY_MESSAGES'

MESSAGE_CLASS_ADT_GET_RESPONSE_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<mc:messageClass xmlns:mc="http://www.sap.com/adt/MessageClass" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:name="ZST_MY_MESSAGES" adtcore:type="MSAG/N" adtcore:changedAt="2026-05-20T16:28:18Z" adtcore:version="active" adtcore:createdAt="2026-05-19T22:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="Testing messages" adtcore:language="EN" xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/messageclass/zst_my_messages" rel="self" type="text/html" title="Message Class HTTP Request"/>
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP"/>
  <mc:messages mc:msgno="000" mc:msgtext="&amp;" mc:selfexplainatory="true" mc:documented="false" mc:lastchangedby="DEVELOPER" mc:lastmodified="2026-05-20" adtcore:name="">
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/vit/docu/object_type/NA/object_name/ZST_MY_MESSAGES000" rel="http://www.sap.com/adt/relations/longtext"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/messageclass/zst_my_messages/messages/000" rel="http://www.sap.com/adt/relations/messageclasses/messages"/>
  </mc:messages>
  <mc:messages mc:msgno="001" mc:msgtext="Repository not found" mc:selfexplainatory="true" mc:documented="false" mc:lastchangedby="DEVELOPER" mc:lastmodified="2026-05-20" adtcore:name="">
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/vit/docu/object_type/NA/object_name/ZST_MY_MESSAGES001" rel="http://www.sap.com/adt/relations/longtext"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/messageclass/zst_my_messages/messages/001" rel="http://www.sap.com/adt/relations/messageclasses/messages"/>
  </mc:messages>
</mc:messageClass>'''

MESSAGE_CLASS_ADT_GET_RESPONSE_EMPTY_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<mc:messageClass xmlns:mc="http://www.sap.com/adt/MessageClass" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:name="ZST_MY_MESSAGES" adtcore:type="MSAG/N" adtcore:changedAt="2026-05-20T16:28:18Z" adtcore:version="active" adtcore:createdAt="2026-05-19T22:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="Testing messages" adtcore:language="EN" xmlns:adtcore="http://www.sap.com/adt/core">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/messageclass/zst_my_messages" rel="self" type="text/html" title="Message Class HTTP Request"/>
  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP"/>
</mc:messageClass>'''

MESSAGE_CLASS_ADT_POST_REQUEST_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<mc:messageClass xmlns:mc="http://www.sap.com/adt/MessageClass" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="MSAG/N" adtcore:description="Testing messages" adtcore:language="EN" adtcore:name="ZST_MY_MESSAGES" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">
<adtcore:packageRef adtcore:name="$TMP"/>
</mc:messageClass>'''

MESSAGE_CLASS_ADT_PUT_REQUEST_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<mc:messageClass xmlns:mc="http://www.sap.com/adt/MessageClass" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="MSAG/N" adtcore:description="Testing messages" adtcore:language="EN" adtcore:name="ZST_MY_MESSAGES" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:responsible="DEVELOPER" adtcore:version="active">
<adtcore:packageRef adtcore:name="$TMP"/>
<mc:messages mc:msgno="000" mc:msgtext="&amp;" mc:selfexplainatory="true" mc:lockhandle="LOCK1"/>
<mc:messages mc:msgno="001" mc:msgtext="Repository not found" mc:selfexplainatory="true" mc:lockhandle="LOCK2"/>
</mc:messageClass>'''

MESSAGE_CLASS_ADT_PUT_WITH_DELETED_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<mc:messageClass xmlns:mc="http://www.sap.com/adt/MessageClass" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="MSAG/N" adtcore:description="Testing messages" adtcore:language="EN" adtcore:name="ZST_MY_MESSAGES" adtcore:masterLanguage="EN" adtcore:masterSystem="A4H" adtcore:responsible="DEVELOPER" adtcore:version="active">
<adtcore:packageRef adtcore:name="$TMP"/>
<mc:messages mc:msgno="001" mc:msgtext="Repository not found" mc:selfexplainatory="true" mc:lockhandle="LOCK2"/>
<mc:deletedmessages mc:msgno="000" mc:msgtext="&amp;" mc:selfexplainatory="true" mc:lockhandle="LOCK_DEL"/>
</mc:messageClass>'''

LOCK_RESPONSE_XML = '''<?xml version="1.0" encoding="UTF-8"?><asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
    <DATA>
      <LOCK_HANDLE>LOCK_HANDLE_123</LOCK_HANDLE>
      <CORRNR/>
      <CORRUSER/>
      <CORRTEXT/>
      <IS_LOCAL/>
      <IS_LINK_UP/>
      <MODIFICATION_SUPPORT/>
      <SCOPE_MESSAGES/>
    </DATA>
  </asx:values>
</asx:abap>'''
