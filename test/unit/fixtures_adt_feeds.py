"""ADT feeds fixtures"""

FEEDS_XML = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>ADT Feeds</title>
  <entry>
    <title>ABAP Runtime Errors</title>
    <id>/sap/bc/adt/runtime/dumps</id>
  </entry>
  <entry>
    <title>System Log</title>
    <id>/sap/bc/adt/runtime/syslog</id>
  </entry>
</feed>
"""

FEEDS_XML_EMPTY = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>ADT Feeds</title>
</feed>
"""
