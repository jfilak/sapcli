"""System Information ADT fixtures"""

from mock import Response

SYSTEM_INFORMATION_XML = '''<?xml version="1.0" encoding="utf-8"?>
<atom:feed xmlns:atom="http://www.w3.org/2005/Atom">
<atom:author>
    <atom:name>SAP SE</atom:name>
</atom:author>
<atom:title>System Information</atom:title>
<atom:updated>2026-03-23T13:43:39Z</atom:updated>
<atom:entry>
    <atom:id>ApplicationServerName</atom:id>
    <atom:title>C50_ddci</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>DBLibrary</atom:id>
    <atom:title>SQLDBC 2.27.024.1772569942</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>DBName</atom:id>
    <atom:title>C50/02</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>DBRelease</atom:id>
    <atom:title>2.00.089.01.1769502981</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>DBSchema</atom:id>
    <atom:title>SAPHANADB</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>DBServer</atom:id>
    <atom:title>saphost</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>DBSystem</atom:id>
    <atom:title>HDB</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>IPAddress</atom:id>
    <atom:title>172.27.4.5</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>KernelCompilationDate</atom:id>
    <atom:title>Linux GNU SLES-15 x86_64  cc10.3.0 use-pr260304 Mar 09 2026 11:05:09</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>KernelKind</atom:id>
    <atom:title>opt</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>KernelPatchLevel</atom:id>
    <atom:title>0</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>KernelRelease</atom:id>
    <atom:title>920</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>MachineType</atom:id>
    <atom:title>x86_64</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>NodeName</atom:id>
    <atom:title>saphost</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>NotAuthorizedDB</atom:id>
    <atom:title>false</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>NotAuthorizedHost</atom:id>
    <atom:title>false</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>NotAuthorizedKernel</atom:id>
    <atom:title>false</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>NotAuthorizedSystem</atom:id>
    <atom:title>false</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>NotAuthorizedUser</atom:id>
    <atom:title>false</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>OSName</atom:id>
    <atom:title>Linux</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>OSVersion</atom:id>
    <atom:title>6.4.0-150600.23.60-default</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>SAPSystemID</atom:id>
    <atom:title>390</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>SAPSystemNumber</atom:id>
    <atom:title>000000000000000001</atom:title>
</atom:entry>
<atom:entry>
    <atom:id>UnicodeSystem</atom:id>
    <atom:title>True</atom:title>
</atom:entry>
</atom:feed>'''

RESPONSE_SYSTEM_INFORMATION = Response(
    text=SYSTEM_INFORMATION_XML,
    status_code=200,
    headers={'Content-Type': 'application/atom+xml;type=feed'}
)

JSON_SYSTEM_INFORMATION = {
    'systemID': 'C50',
    'userName': 'DEVELOPER',
    'userFullName': '',
    'client': '100',
    'language': 'EN',
}

RESPONSE_JSON_SYSTEM_INFORMATION = Response(
    status_code=200,
    json=JSON_SYSTEM_INFORMATION,
    headers={'Content-Type': 'application/vnd.sap.adt.core.http.systeminformation.v1+json'}
)
