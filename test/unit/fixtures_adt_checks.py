ADT_XML_CHECK_REPORTERS = '''<?xml version="1.0" encoding="UTF-8"?>
<chkrun:checkReporters xmlns:chkrun="http://www.sap.com/adt/checkrun">
  <chkrun:reporter chkrun:name="abapCheckRun">
    <chkrun:supportedType>WDYN*</chkrun:supportedType>
    <chkrun:supportedType>CLAS*</chkrun:supportedType>
    <chkrun:supportedType>WGRP</chkrun:supportedType>
  </chkrun:reporter>
  <chkrun:reporter chkrun:name="abapPackageCheck">
    <chkrun:supportedType>PROG*</chkrun:supportedType>
    <chkrun:supportedType>INTF*</chkrun:supportedType>
    <chkrun:supportedType>HTTP</chkrun:supportedType>
  </chkrun:reporter>
  <chkrun:reporter chkrun:name="tableStatusCheck">
    <chkrun:supportedType>TABL/DT</chkrun:supportedType>
  </chkrun:reporter>
</chkrun:checkReporters>'''

ADT_XML_RUN_CHECK_2_REPORTERS = '''<?xml version="1.0" encoding="UTF-8"?>
<chkrun:checkRunReports xmlns:chkrun="http://www.sap.com/adt/checkrun">
  <chkrun:checkReport chkrun:reporter="abapCheckRun" chkrun:triggeringUri="/sap/bc/adt/ddic/tables/zexample" chkrun:status="processed" chkrun:statusText="Object zexample has been checked">
    <chkrun:checkMessageList>
      <chkrun:checkMessage chkrun:uri="/sap/bc/adt/ddic/tables/zexample/source/main#start=1" chkrun:type="E" chkrun:shortText="First" chkrun:category="Check1">
        <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/messageclass/DT/messages/242/longtext?language=E&amp;msgv1=CREATETIME" rel="http://www.sap.com/adt/relations/longtext" type="text/html"/>
        <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="art.syntax:DT242" rel="http://www.sap.com/adt/categories/quickfixes"/>
        <chkrun:t100Key chkrun:msgid="DT" chkrun:msgno="242" chkrun:msgv1="CREATETIME" chkrun:msgv2="" chkrun:msgv3="" chkrun:msgv4=""/>
      </chkrun:checkMessage>
      <chkrun:checkMessage chkrun:uri="/sap/bc/adt/ddic/tables/zexample/source/main#start=2" chkrun:type="E" chkrun:shortText="Second" chkrun:category="Check2">
        <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/messageclass/DT/messages/242/longtext?language=E&amp;msgv1=DESCRIPTION" rel="http://www.sap.com/adt/relations/longtext" type="text/html"/>
        <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="art.syntax:DT242" rel="http://www.sap.com/adt/categories/quickfixes"/>
        <chkrun:t100Key chkrun:msgid="DT" chkrun:msgno="242" chkrun:msgv1="DESCRIPTION" chkrun:msgv2="" chkrun:msgv3="" chkrun:msgv4=""/>
      </chkrun:checkMessage>
    </chkrun:checkMessageList>
  </chkrun:checkReport>
  <chkrun:checkReport chkrun:reporter="tableStatusCheck" chkrun:triggeringUri="/sap/bc/adt/ddic/tables/zexample" chkrun:status="processed" chkrun:statusText="Object zexample has been checked">
    <chkrun:checkMessageList>
      <chkrun:checkMessage chkrun:uri="/sap/bc/adt/ddic/tables/zexample/source/main#start=3" chkrun:type="W" chkrun:shortText="Third" chkrun:category="Check3">
        <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/messageclass/DT/messages/242/longtext?language=E&amp;msgv1=CREATETIME" rel="http://www.sap.com/adt/relations/longtext" type="text/html"/>
        <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="art.syntax:DT242" rel="http://www.sap.com/adt/categories/quickfixes"/>
        <chkrun:t100Key chkrun:msgid="DT" chkrun:msgno="242" chkrun:msgv1="CREATETIME" chkrun:msgv2="" chkrun:msgv3="" chkrun:msgv4=""/>
      </chkrun:checkMessage>
      <chkrun:checkMessage chkrun:uri="/sap/bc/adt/ddic/tables/zexample/source/main#start=4" chkrun:type="W" chkrun:shortText="Fourth" chkrun:category="Check4">
        <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/messageclass/DT/messages/242/longtext?language=E&amp;msgv1=DESCRIPTION" rel="http://www.sap.com/adt/relations/longtext" type="text/html"/>
        <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="art.syntax:DT242" rel="http://www.sap.com/adt/categories/quickfixes"/>
        <chkrun:t100Key chkrun:msgid="DT" chkrun:msgno="242" chkrun:msgv1="DESCRIPTION" chkrun:msgv2="" chkrun:msgv3="" chkrun:msgv4=""/>
      </chkrun:checkMessage>
    </chkrun:checkMessageList>
  </chkrun:checkReport>
</chkrun:checkRunReports>'''
