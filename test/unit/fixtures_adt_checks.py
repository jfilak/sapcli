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
