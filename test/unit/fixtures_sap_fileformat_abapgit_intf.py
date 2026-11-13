INTF_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_INTF" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <VSEOINTERF>
    <CLSNAME>TEST_INTF</CLSNAME>
    <LANGU>E</LANGU>
    <DESCRIPT>Test intf descr</DESCRIPT>
    <EXPOSURE>2</EXPOSURE>
    <STATE>1</STATE>
    <UNICODE>X</UNICODE>
   </VSEOINTERF>
  </asx:values>
 </asx:abap>
</abapGit>'''

INTF_WITH_DESCRIPTIONS_SUB_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_INTF" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <VSEOINTERF>
    <CLSNAME>TEST_INTF</CLSNAME>
    <LANGU>E</LANGU>
    <DESCRIPT>Test intf descr</DESCRIPT>
    <EXPOSURE>2</EXPOSURE>
    <STATE>1</STATE>
    <UNICODE>X</UNICODE>
   </VSEOINTERF>
   <DESCRIPTIONS_SUB>
    <SEOSUBCOTX>
     <CMPNAME>GET_USED_OBJECTS</CMPNAME>
     <SCONAME>IV_OBJECT_NAME</SCONAME>
     <LANGU>E</LANGU>
     <DESCRIPT>Object Name</DESCRIPT>
    </SEOSUBCOTX>
   </DESCRIPTIONS_SUB>
  </asx:values>
 </asx:abap>
</abapGit>'''
