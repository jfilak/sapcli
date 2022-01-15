"""ABAP Unit Test Coverage framework code highlighting wrappers"""
import xml
from typing import NamedTuple, List
from xml.sax.handler import ContentHandler

from sap import get_logger
from sap.adt.annotations import OrderedClassMembers, xml_attribute, xml_element
from sap.adt.marshalling import Marshal
from sap.adt.objects import XMLNamespace, ADTObjectType

XMLNS_COV = XMLNamespace('cov', 'http://www.sap.com/adt/cov')


def mod_log():
    """ACoverage Statements Module logger"""

    return get_logger()


# pylint: disable=too-few-public-methods
class StatementRequest(metaclass=OrderedClassMembers):
    """ABAP StatementRequest """

    def __init__(self, get):
        self._get = get

    @xml_attribute('get')
    def get(self):
        """Returns statements request's GET"""

        return self._get

    @get.setter
    def get(self, value):
        """Sets statements request's GET"""

        self._get = value


# pylint: disable=too-few-public-methods
class StatementsBulkRequest(metaclass=OrderedClassMembers):
    """ABAP StatementsBulkRequest
    """

    objtype = ADTObjectType(None,
                            'runtime/traces/coverage/results/{identifier}/statements',
                            XMLNS_COV,
                            'application/xml',
                            None,
                            'statementsBulkRequest')

    def __init__(self, identifier, statement_requests=None):
        self.objtype.basepath = self.objtype.basepath.format(identifier=identifier)
        self._statement_requests = statement_requests or []

    @xml_element('statementsRequest')
    def statement_requests(self):
        """Get statement requests

           :rtype: A list of :class:`StatementRequest`
        """

        return self._statement_requests

    def add_statement_request(self, statement_request):
        """Adds the given statement request. """

        self._statement_requests.append(statement_request)

        return statement_request


# pylint: disable=too-few-public-methods
class ACoverageStatements:
    """ABAP Coverage Statements
    """

    def __init__(self, connection):
        self._connection = connection

    def execute(self, statements_bulk_request):
        """Executes ABAP Coverage Statements on the given statement bulk request"""

        request_config = Marshal().serialize(statements_bulk_request)

        return self._connection.execute(
            'POST',
            statements_bulk_request.objtype.basepath,
            content_type=statements_bulk_request.objtype.mimetype,
            body=request_config
        )


# pylint: disable=too-few-public-methods
class Statement(NamedTuple):
    """ABAP Coverage Statements results XML parser Statement node"""

    executed: str
    uri: str


# pylint: disable=too-few-public-methods
class StatementResponse(NamedTuple):
    """ABAP Coverage Statements results XML parser StatementResponse node"""

    name: str
    statements: List


# pylint: disable=too-many-instance-attributes
class CoverageStatementsResponseHandler(ContentHandler):
    """ABAP Coverage Statements results XML parser"""

    def __init__(self):
        super().__init__()

        self.statement_responses = []
        self._current_statement_response = None
        self._current_statement_executed = None

    def startElement(self, name, attrs):
        mod_log().debug('XML: %s', name)
        if name == 'cov:statementsResponse':
            self._current_statement_response = StatementResponse(
                name=attrs.get('name'),
                statements=[]
            )
            self.statement_responses.append(self._current_statement_response)
            mod_log().debug('XML: %s: %s', name, self._current_statement_response.name)
        elif name == 'statement':
            self._current_statement_executed = attrs.get('executed')
        elif name == 'adtcore:objectReference' and self._current_statement_executed:
            statement = Statement(
                executed=self._current_statement_executed,
                uri=attrs.get('adtcore:uri')
            )
            self._current_statement_response.statements.append(statement)
            mod_log().debug('XML: %s: %s', name, attrs.get('adtcore:uri'))
            self._current_statement_executed = None

    def endElement(self, name):
        mod_log().debug('XML: %s: CLOSING', name)
        if name == 'statement':
            self._current_statement_executed = None
        elif name == 'cov:statementsResponse':
            self._current_statement_response = None


def parse_statements_response(coverage_statements_results_xml):
    """Converts XML results into Python representation"""

    xml_handler = CoverageStatementsResponseHandler()
    xml.sax.parseString(coverage_statements_results_xml, xml_handler)

    return xml_handler
