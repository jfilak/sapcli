DTEL_XML = '''﻿<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DTEL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD04V>
    <ROLLNAME>ZAGT_TEST_DTEL</ROLLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <HEADLEN>55</HEADLEN>
    <SCRLEN1>10</SCRLEN1>
    <SCRLEN2>20</SCRLEN2>
    <SCRLEN3>40</SCRLEN3>
    <DDTEXT>testing</DDTEXT>
    <REPTEXT>testing</REPTEXT>
    <SCRTEXT_S>testing</SCRTEXT_S>
    <SCRTEXT_M>testing</SCRTEXT_M>
    <SCRTEXT_L>testing</SCRTEXT_L>
    <DTELMASTER>E</DTELMASTER>
    <DATATYPE>CHAR</DATATYPE>
    <LENG>000001</LENG>
    <OUTPUTLEN>000001</OUTPUTLEN>
   </DD04V>
  </asx:values>
 </asx:abap>
</abapGit>
'''


DTEL_DOMAIN_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DTEL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD04V>
    <ROLLNAME>ZAGT_TEST_DTEL</ROLLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DOMNAME>ZABAPGIT_UNIT_TEST</DOMNAME>
    <MEMORYID>ZSAPCLI</MEMORYID>
    <LOGFLAG>X</LOGFLAG>
    <HEADLEN>30</HEADLEN>
    <SCRLEN1>08</SCRLEN1>
    <SCRLEN2>15</SCRLEN2>
    <SCRLEN3>25</SCRLEN3>
    <DDTEXT>Domain &amp; labels</DDTEXT>
    <REPTEXT>Heading</REPTEXT>
    <SCRTEXT_S>Short</SCRTEXT_S>
    <SCRTEXT_M>Medium</SCRTEXT_M>
    <SCRTEXT_L>Long</SCRTEXT_L>
    <DTELMASTER>E</DTELMASTER>
    <SHLPNAME>ZSAPCLI_SHLP</SHLPNAME>
    <SHLPFIELD>VALUE</SHLPFIELD>
    <DEFFDNAME>DOMAIN_VALUE</DEFFDNAME>
    <REFKIND>D</REFKIND>
    <LTRFLDDIS>X</LTRFLDDIS>
    <BIDICTRLC>X</BIDICTRLC>
    <NOHISTORY>X</NOHISTORY>
   </DD04V>
   <DD04L_EXTRA>
    <ABAP_LANGUAGE_VERSION>X</ABAP_LANGUAGE_VERSION>
   </DD04L_EXTRA>
  </asx:values>
 </asx:abap>
</abapGit>
'''


DTEL_TRANSLATIONS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DTEL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD04V>
    <ROLLNAME>ZAGT_TEST_DTEL</ROLLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DDTEXT>testing</DDTEXT>
    <DATATYPE>CHAR</DATATYPE>
    <LENG>000001</LENG>
   </DD04V>
   <I18N_LANGS>
    <LANGU>D</LANGU>
   </I18N_LANGS>
  </asx:values>
 </asx:abap>
</abapGit>
'''


DTEL_REFERENCE_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DTEL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD04V>
    <ROLLNAME>ZAGT_TEST_DTEL</ROLLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DOMNAME>CL_ABAP_TYPEDESCR</DOMNAME>
    <DDTEXT>testing</DDTEXT>
    <REFKIND>R</REFKIND>
    <REFTYPE>C</REFTYPE>
   </DD04V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DTEL_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DTEL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD04V>
    <ROLLNAME>ZAGT_TEST_DTEL</ROLLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <HEADLEN>55</HEADLEN>
    <SCRLEN1>10</SCRLEN1>
    <SCRLEN2>20</SCRLEN2>
    <SCRLEN3>40</SCRLEN3>
    <DDTEXT>testing</DDTEXT>
    <REPTEXT>testing</REPTEXT>
    <SCRTEXT_S>testing</SCRTEXT_S>
    <SCRTEXT_M>testing</SCRTEXT_M>
    <SCRTEXT_L>testing</SCRTEXT_L>
    <DTELMASTER>E</DTELMASTER>
    <DATATYPE>CHAR</DATATYPE>
    <LENG>000001</LENG>
    <OUTPUTLEN>000001</OUTPUTLEN>
   </DD04V>
  </asx:values>
 </asx:abap>
</abapGit>
'''


DTEL_DOMAIN_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DTEL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD04V>
    <ROLLNAME>ZAGT_TEST_DTEL</ROLLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DOMNAME>SPRAS</DOMNAME>
    <MEMORYID>SPR</MEMORYID>
    <LOGFLAG>X</LOGFLAG>
    <HEADLEN>30</HEADLEN>
    <SCRLEN1>08</SCRLEN1>
    <SCRLEN2>15</SCRLEN2>
    <SCRLEN3>25</SCRLEN3>
    <DDTEXT>A &amp; B &lt;C&gt; &apos;D&apos; &quot;E&quot;</DDTEXT>
    <REPTEXT>Heading</REPTEXT>
    <SCRTEXT_S>Short</SCRTEXT_S>
    <SCRTEXT_M>Medium</SCRTEXT_M>
    <SCRTEXT_L>Long</SCRTEXT_L>
    <DTELMASTER>E</DTELMASTER>
    <SHLPNAME>H_T002</SHLPNAME>
    <SHLPFIELD>SPRAS</SHLPFIELD>
    <DEFFDNAME>DOMAIN_VALUE</DEFFDNAME>
    <REFKIND>D</REFKIND>
    <NOHISTORY>X</NOHISTORY>
   </DD04V>
  </asx:values>
 </asx:abap>
</abapGit>
'''


DTEL_STRING_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DTEL" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD04V>
    <ROLLNAME>ZAGT_TEST_DTEL</ROLLNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <HEADLEN>55</HEADLEN>
    <SCRLEN1>10</SCRLEN1>
    <SCRLEN2>20</SCRLEN2>
    <SCRLEN3>40</SCRLEN3>
    <DDTEXT>String</DDTEXT>
    <REPTEXT>String</REPTEXT>
    <SCRTEXT_S>String</SCRTEXT_S>
    <SCRTEXT_M>String</SCRTEXT_M>
    <SCRTEXT_L>String</SCRTEXT_L>
    <DTELMASTER>E</DTELMASTER>
    <DATATYPE>STRG</DATATYPE>
    <LTRFLDDIS>X</LTRFLDDIS>
    <BIDICTRLC>X</BIDICTRLC>
   </DD04V>
  </asx:values>
 </asx:abap>
</abapGit>
'''
