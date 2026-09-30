"""ABAP runtime short dumps fixtures"""

DUMPS_FEED_XML = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>ABAP Runtime Errors</title>
  <entry>
    <author><name>DEVELOPER</name></author>
    <title>CX_SY_ZERODIVIDE
Division by zero</title>
    <updated>2024-01-15T10:30:00Z</updated>
    <id>https://host/sap/bc/adt/runtime/dump/ABC123</id>
  </entry>
  <entry>
    <author><name>TESTER</name></author>
    <title>CX_SY_ITAB_LINE_NOT_FOUND</title>
    <updated>2024-01-16T11:00:00Z</updated>
    <id>https://host/sap/bc/adt/runtime/dump/DEF456</id>
  </entry>
</feed>
"""

DUMPS_FEED_XML_NO_AUTHOR = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>ABAP Runtime Errors</title>
  <entry>
    <title>CX_SY_ZERODIVIDE</title>
    <updated>2024-01-15T10:30:00Z</updated>
    <id>https://host/sap/bc/adt/runtime/dump/ABC123</id>
  </entry>
</feed>
"""

DUMP_FORMATTED = """<html><body>Formatted short dump ABC123</body></html>"""
