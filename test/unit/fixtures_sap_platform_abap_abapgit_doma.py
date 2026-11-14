DOMA_XML = '''﻿<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DOMA" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD01V>
    <DOMNAME>ZABAPGIT_UNIT_TEST</DOMNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DATATYPE>CHAR</DATATYPE>
    <LENG>000010</LENG>
    <OUTPUTLEN>000010</OUTPUTLEN>
    <DDTEXT>Testing</DDTEXT>
   </DD01V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DOMA_ALL_FIELDS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DOMA" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD01V>
    <DOMNAME>ZABAPGIT_UNIT_TEST</DOMNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DATATYPE>DEC</DATATYPE>
    <LENG>000011</LENG>
    <OUTPUTLEN>000015</OUTPUTLEN>
    <DECIMALS>000002</DECIMALS>
    <LOWERCASE>X</LOWERCASE>
    <SIGNFLAG>X</SIGNFLAG>
    <VALEXI>X</VALEXI>
    <ENTITYTAB>T000</ENTITYTAB>
    <CONVEXIT>ALPHA</CONVEXIT>
    <DDTEXT>All fields</DDTEXT>
    <DOMMASTER>E</DOMMASTER>
    <OUTPUTSTYLE>01</OUTPUTSTYLE>
    <AMPMFORMAT>X</AMPMFORMAT>
   </DD01V>
   <DD07V_TAB>
    <DD07V>
     <VALPOS>0007</VALPOS>
     <DDLANGUAGE>E</DDLANGUAGE>
     <DOMVALUE_L>A</DOMVALUE_L>
     <DDTEXT>Alpha</DDTEXT>
    </DD07V>
    <DD07V>
     <VALPOS>0009</VALPOS>
     <DDLANGUAGE>E</DDLANGUAGE>
     <DOMVALUE_L>B</DOMVALUE_L>
     <DOMVALUE_H>C</DOMVALUE_H>
     <DDTEXT>Range</DDTEXT>
    </DD07V>
   </DD07V_TAB>
   <DD01L_EXTRA>
    <ABAP_LANGUAGE_VERSION>X</ABAP_LANGUAGE_VERSION>
   </DD01L_EXTRA>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DOMA_TRANSLATIONS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DOMA" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD01V>
    <DOMNAME>ZABAPGIT_UNIT_TEST</DOMNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DATATYPE>CHAR</DATATYPE>
    <LENG>000010</LENG>
    <OUTPUTLEN>000010</OUTPUTLEN>
    <DDTEXT>Testing</DDTEXT>
   </DD01V>
   <I18N_LANGS>
    <LANGU>D</LANGU>
   </I18N_LANGS>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DOMA_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DOMA" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD01V>
    <DOMNAME>ZABAPGIT_UNIT_TEST</DOMNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DATATYPE>CHAR</DATATYPE>
    <LENG>000010</LENG>
    <OUTPUTLEN>000010</OUTPUTLEN>
    <DDTEXT>Testing</DDTEXT>
   </DD01V>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DOMA_ALL_FIELDS_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DOMA" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD01V>
    <DOMNAME>ZABAPGIT_UNIT_TEST</DOMNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DATATYPE>DEC</DATATYPE>
    <LENG>000011</LENG>
    <OUTPUTLEN>000015</OUTPUTLEN>
    <DECIMALS>000002</DECIMALS>
    <LOWERCASE>X</LOWERCASE>
    <SIGNFLAG>X</SIGNFLAG>
    <VALEXI>X</VALEXI>
    <ENTITYTAB>T000</ENTITYTAB>
    <CONVEXIT>ALPHA</CONVEXIT>
    <DDTEXT>All fields</DDTEXT>
    <OUTPUTSTYLE>01</OUTPUTSTYLE>
    <AMPMFORMAT>X</AMPMFORMAT>
   </DD01V>
   <DD07V_TAB>
    <DD07V>
     <VALPOS>0001</VALPOS>
     <DDLANGUAGE>E</DDLANGUAGE>
     <DOMVALUE_L>A</DOMVALUE_L>
     <DDTEXT>Alpha</DDTEXT>
    </DD07V>
    <DD07V>
     <VALPOS>0002</VALPOS>
     <DDLANGUAGE>E</DDLANGUAGE>
     <DOMVALUE_L>B</DOMVALUE_L>
     <DOMVALUE_H>C</DOMVALUE_H>
     <DDTEXT>Range</DDTEXT>
    </DD07V>
   </DD07V_TAB>
  </asx:values>
 </asx:abap>
</abapGit>
'''

DOMA_RAWSTRING_ABAPGIT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DOMA" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DD01V>
    <DOMNAME>ZABAPGIT_UNIT_TEST</DOMNAME>
    <DDLANGUAGE>E</DDLANGUAGE>
    <DATATYPE>RSTR</DATATYPE>
    <DDTEXT>Raw string</DDTEXT>
   </DD01V>
  </asx:values>
 </asx:abap>
</abapGit>
'''
