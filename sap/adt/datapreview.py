"""ADT SQL Console wrappers"""

import xml.sax
from xml.sax.handler import ContentHandler

from sap import get_logger


def mod_log():
    """ADT Module logger"""

    return get_logger()


# pylint: disable=too-many-instance-attributes
class FreeStyleTableXMLHandler(ContentHandler):
    """ABAP Unit Test Framework ADT results XML parser"""

    def __init__(self, rows):
        super().__init__()

        self.table = None
        self._column = None
        self._known_columns = []
        self._row = None
        self._datahandler = lambda x: x
        self._iter = None
        self._cntr = 0
        self._total_rows = 0
        self._rows = rows

    def _initrows(self, content):
        self.table = []
        i = 0
        rows = min(self._rows, int(content))
        while i < rows:
            self.table.append({})
            i += 1

    def _assigncolumn(self, content):
        self._row[self._column] = content

    def startElement(self, name, attrs):
        mod_log().debug('XML: %s', name)
        if name == 'dataPreview:totalRows':
            self._datahandler = self._initrows
        elif name == 'dataPreview:columns':
            if self.table is None:
                self._initrows(self._rows)
        elif name == 'dataPreview:metadata':
            self._column = attrs.get('dataPreview:name')
            self._known_columns.append(self._column)
            self._iter = iter(self.table)
        elif name == 'dataPreview:data':
            self._cntr += 1
            self._datahandler = self._assigncolumn
            self._row = next(self._iter)

    def characters(self, content):
        mod_log().debug('XML: data: %s', content)
        self._datahandler(content)

    def endElement(self, name):
        mod_log().debug('XML: %s: CLOSING', name)
        if name == 'dataPreview:totalRows':
            self._datahandler = lambda x: x
        elif name == 'dataPreview:columns':
            self._column = None
            self._iter = None
        elif name == 'dataPreview:data':
            self._datahandler = lambda x: x
        elif name == 'dataPreview:dataSet':
            self._total_rows = max(self._total_rows, self._cntr)
            self._cntr = 0
        elif name == 'dataPreview:tableData':
            self.table = self.table[0:self._total_rows]
            for column in self._known_columns:
                for row in self.table:
                    if column not in row:
                        row[column] = ''


def parse_freestyle_table(freestyle_table_xml, rows):
    """Converts XML results into Python representation"""

    xml_handler = FreeStyleTableXMLHandler(rows)
    xml.sax.parseString(freestyle_table_xml, xml_handler)

    return xml_handler.table


def freestyle_table_params(rows, aging):
    """Returns parameters for OpenSQL freestyle request"""

    return {'rowNumber': str(rows), 'dataAging': str(aging).lower()}


class DataPreview:
    """SQL Console aka Data Preview functions"""

    def __init__(self, connection):
        self._connection = connection

    def execute(self, osql_query, rows=100, aging=True):
        """Executes Open SQL Statement"""

        response = self._connection.execute(
            'POST',
            'datapreview/freestyle',
            params=freestyle_table_params(rows, aging),
            headers={'Accept': 'application/xml, application/vnd.sap.adt.datapreview.table.v1+xml',
                     'Content-Type': 'text/plain'},
            body=osql_query)

        return parse_freestyle_table(response.text, rows=rows)
