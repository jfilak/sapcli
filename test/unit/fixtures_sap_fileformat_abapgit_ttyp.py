TTYP_STANDARD_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <ROWTYPE>BAPIRET2</ROWTYPE>
    <ROWKIND>S</ROWKIND>
    <DATATYPE>STRU</DATATYPE>
    <ACCESSMODE>T</ACCESSMODE>
    <KEYDEF>D</KEYDEF>
    <KEYKIND>N</KEYKIND>
    <DDTEXT>Test table type</DDTEXT>
   </DD40V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_SORTED_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <ROWTYPE>BAPIRET2</ROWTYPE>
    <ROWKIND>S</ROWKIND>
    <DATATYPE>STRU</DATATYPE>
    <ACCESSMODE>S</ACCESSMODE>
    <KEYDEF>K</KEYDEF>
    <KEYKIND>U</KEYKIND>
    <KEYFDCOUNT>0002</KEYFDCOUNT>
    <DDTEXT>Test table type</DDTEXT>
   </DD40V>
   <DD42V>
    <DD42V>
     <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
     <KEYFDPOS>0001</KEYFDPOS>
     <ROWTYPEPOS>0001</ROWTYPEPOS>
     <KEYFIELD>TYPE</KEYFIELD>
    </DD42V>
    <DD42V>
     <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
     <KEYFDPOS>0002</KEYFDPOS>
     <ROWTYPEPOS>0002</ROWTYPEPOS>
     <KEYFIELD>ID</KEYFIELD>
    </DD42V>
   </DD42V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_PREDEFINED_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DATATYPE>STRG</DATATYPE>
    <ACCESSMODE>T</ACCESSMODE>
    <KEYDEF>D</KEYDEF>
    <KEYKIND>N</KEYKIND>
    <DDTEXT>Test table type</DDTEXT>
    <TYPELEN>000008</TYPELEN>
   </DD40V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_SECONDARY_KEYS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <ROWTYPE>BAPIRET2</ROWTYPE>
    <ROWKIND>S</ROWKIND>
    <DATATYPE>STRU</DATATYPE>
    <ACCESSMODE>T</ACCESSMODE>
    <KEYDEF>D</KEYDEF>
    <KEYKIND>N</KEYKIND>
    <KEYFDCOUNT>0001</KEYFDCOUNT>
    <DDTEXT>Test table type</DDTEXT>
   </DD40V>
   <DD42V>
    <DD42V>
     <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
     <SECKEYNAME>BY_ID</SECKEYNAME>
     <KEYFDPOS>0001</KEYFDPOS>
     <ROWTYPEPOS>0002</ROWTYPEPOS>
     <KEYFIELD>ID</KEYFIELD>
    </DD42V>
   </DD42V>
   <DD43V>
    <DD43V>
     <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
     <SECKEYNAME>BY_ID</SECKEYNAME>
     <DDLANGUAGE>E</DDLANGUAGE>
     <ACCESSMODE>S</ACCESSMODE>
     <KIND>K</KIND>
     <KEYDESCRIPTION>Messages by ID</KEYDESCRIPTION>
    </DD43V>
   </DD43V>
   <DD40L_EXTRA>
    <ABAP_LANGUAGE_VERSION>X</ABAP_LANGUAGE_VERSION>
   </DD40L_EXTRA>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_RANGE_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <ROWTYPE>/AIF/NRT_MSGGUID_RANGE_S</ROWTYPE>
    <ROWKIND>S</ROWKIND>
    <DATATYPE>STRU</DATATYPE>
    <ACCESSMODE>T</ACCESSMODE>
    <KEYDEF>D</KEYDEF>
    <KEYKIND>N</KEYKIND>
    <DDTEXT>Range table for /aif/nrt_msgguid_e</DDTEXT>
    <TTYPKIND>R</TTYPKIND>
    <RANGE_CTYP>/AIF/NRT_MSGGUID_E</RANGE_CTYP>
    <CTDATATYPE>RAW</CTDATATYPE>
    <CTLENG>000016</CTLENG>
   </DD40V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_SORTED_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <ROWTYPE>BAPIRET2</ROWTYPE>
    <ROWKIND>S</ROWKIND>
    <DATATYPE>STRU</DATATYPE>
    <ACCESSMODE>S</ACCESSMODE>
    <KEYDEF>K</KEYDEF>
    <KEYKIND>U</KEYKIND>
    <KEYFDCOUNT>0002</KEYFDCOUNT>
    <DDTEXT>Test table type</DDTEXT>
   </DD40V>
   <DD42V>
    <DD42V>
     <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
     <KEYFDPOS>0001</KEYFDPOS>
     <KEYFIELD>TYPE</KEYFIELD>
    </DD42V>
    <DD42V>
     <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
     <KEYFDPOS>0002</KEYFDPOS>
     <KEYFIELD>ID</KEYFIELD>
    </DD42V>
   </DD42V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_PREDEFINED_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DATATYPE>CHAR</DATATYPE>
    <LENG>000001</LENG>
    <ACCESSMODE>T</ACCESSMODE>
    <KEYDEF>D</KEYDEF>
    <KEYKIND>N</KEYKIND>
    <DDTEXT>Test table type</DDTEXT>
   </DD40V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_STRING_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>D</DDLANGUAGE>
    <DATATYPE>STRG</DATATYPE>
    <ACCESSMODE>T</ACCESSMODE>
    <KEYDEF>D</KEYDEF>
    <KEYKIND>N</KEYKIND>
    <DDTEXT>Tabelle von Strings</DDTEXT>
   </DD40V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

TTYP_SECONDARY_KEYS_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_TTYP" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD40V>
    <TYPENAME>ZSAPCLI_TT_DATA</TYPENAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <ROWTYPE>/AIF/CDATA_S</ROWTYPE>
    <ROWKIND>S</ROWKIND>
    <DATATYPE>STRU</DATATYPE>
    <ACCESSMODE>T</ACCESSMODE>
    <KEYDEF>D</KEYDEF>
    <KEYKIND>N</KEYKIND>
    <DDTEXT>Table for changed data (fields)</DDTEXT>
   </DD40V>
  </asx:values>
 </asx:abap>
</abapGit>
'''
