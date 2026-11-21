CLAS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_CLAS" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <VSEOCLASS>
    <CLSNAME>TEST CLASS</CLSNAME>
    <LANGU>E</LANGU>
    <DESCRIPT>Test description</DESCRIPT>
    <STATE>1</STATE>
    <CLSCCINCL>X</CLSCCINCL>
    <FIXPT>X</FIXPT>
    <UNICODE>X</UNICODE>
    <WITH_UNIT_TESTS>X</WITH_UNIT_TESTS>
    <DURATION_TYPE>1</DURATION_TYPE>
    <RISK_LEVEL>2</RISK_LEVEL>
   </VSEOCLASS>
  </asx:values>
 </asx:abap>
</abapGit>'''

CLAS_WITH_DESCRIPTIONS_SUB_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_CLAS" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <VSEOCLASS>
    <CLSNAME>TEST CLASS</CLSNAME>
    <LANGU>E</LANGU>
    <DESCRIPT>Test description</DESCRIPT>
    <STATE>1</STATE>
    <CLSCCINCL>X</CLSCCINCL>
    <FIXPT>X</FIXPT>
    <UNICODE>X</UNICODE>
   </VSEOCLASS>
   <DESCRIPTIONS_SUB>
    <SEOSUBCOTX>
     <CMPNAME>EXPAND_FUGR_TADIR_TO_FUNC</CMPNAME>
     <SCONAME>ZCX_ABAPGIT_EXCEPTION</SCONAME>
     <LANGU>E</LANGU>
     <DESCRIPT>abapGit - Exception</DESCRIPT>
    </SEOSUBCOTX>
   </DESCRIPTIONS_SUB>
  </asx:values>
 </asx:abap>
</abapGit>'''

CLAS_WITH_TPOOL_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_CLAS" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <VSEOCLASS>
    <CLSNAME>TEST CLASS</CLSNAME>
    <LANGU>E</LANGU>
    <DESCRIPT>Test description</DESCRIPT>
    <STATE>1</STATE>
    <CLSCCINCL>X</CLSCCINCL>
    <FIXPT>X</FIXPT>
    <UNICODE>X</UNICODE>
   </VSEOCLASS>
   <TPOOL>
    <item>
     <ID>I</ID>
     <KEY>001</KEY>
     <ENTRY>Hello, world!</ENTRY>
     <LENGTH>20</LENGTH>
    </item>
    <item>
     <ID>I</ID>
     <KEY>002</KEY>
     <ENTRY>a=b</ENTRY>
     <LENGTH>10</LENGTH>
    </item>
   </TPOOL>
   <DESCRIPTIONS_SUB>
    <SEOSUBCOTX>
     <CMPNAME>EXPAND_FUGR_TADIR_TO_FUNC</CMPNAME>
     <SCONAME>ZCX_ABAPGIT_EXCEPTION</SCONAME>
     <LANGU>E</LANGU>
     <DESCRIPT>abapGit - Exception</DESCRIPT>
    </SEOSUBCOTX>
   </DESCRIPTIONS_SUB>
  </asx:values>
 </asx:abap>
</abapGit>'''

CLAS_WITHOUT_DESCRIPTION_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_CLAS" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <VSEOCLASS>
    <CLSNAME>TEST CLASS</CLSNAME>
    <LANGU>E</LANGU>
    <STATE>1</STATE>
    <CLSCCINCL>X</CLSCCINCL>
    <FIXPT>X</FIXPT>
    <UNICODE>X</UNICODE>
   </VSEOCLASS>
  </asx:values>
 </asx:abap>
</abapGit>'''
