"""ABAP Unit Test Coverage framework ADT wrappers"""
import xml
from typing import NamedTuple, List
from xml.sax.handler import ContentHandler

from sap import get_logger
from sap.adt.annotations import XmlNodeProperty, XmlElementProperty, OrderedClassMembers
from sap.adt.marshalling import Marshal
from sap.adt.objects import XMLNamespace, ADTObjectType

XMLNS_COV = XMLNamespace('cov', 'http://www.sap.com/adt/cov')


def mod_log():
    """ADT Module logger"""

    return get_logger()


# pylint: disable=too-few-public-methods
class Query(metaclass=OrderedClassMembers):
    """ABAP Coverage Query
    """

    objtype = ADTObjectType(None,
                            'runtime/traces/coverage/measurements/{identifier}',
                            XMLNS_COV,
                            'application/xml',
                            None,
                            'query')

    objects = XmlNodeProperty(XmlElementProperty.NAME_FROM_OBJECT)

    def __init__(self, identifier, objects):
        self.objtype.basepath = self.objtype.basepath.format(identifier=identifier)
        self.objects = objects


# pylint: disable=too-few-public-methods
class ACoverage:
    """ABAP Coverage
    """

    def __init__(self, connection):
        self._connection = connection

    def execute(self, identifier, adt_object_sets):
        """Executes ABAP Coverage on the given ADT object set"""

        query = Query(identifier, adt_object_sets)
        coverage_config = Marshal().serialize(query)

        return self._connection.execute(
            'POST',
            query.objtype.basepath,
            content_type=query.objtype.mimetype,
            body=coverage_config
        )


# pylint: disable=too-few-public-methods
class Node(NamedTuple):
    """ABAP Unit Tests Framework Coverage ADT results Node node"""

    name: str
    type: str
    nodes: List
    coverages: List
    parent_node: object


# pylint: disable=too-few-public-methods
class CoverageNode(NamedTuple):
    """ABAP Unit Tests Framework Coverage ADT results Coverage node"""

    type: str
    total: int
    executed: int


# pylint: disable=too-many-instance-attributes
class CoverageResponseHandler(ContentHandler):
    """ABAP Unit Test Framework Coverage ADT results XML parser"""

    def __init__(self):
        super().__init__()

        self.root_node = None
        self._node = None
        self._nodes = []
        self._parent_node = None
        self._coverage = None

    def startElement(self, name, attrs):
        mod_log().debug('XML: %s', name)
        if name == 'cov:result':
            self.root_node = Node(
                name=attrs.get('name'),
                type=None,
                nodes=[],
                coverages=[],
                parent_node=self._parent_node
            )
            self._node = self.root_node
        elif name == 'adtcore:objectReference':
            self._parent_node = self._node
            self._node = Node(
                name=attrs.get('adtcore:name'),
                type=attrs.get('adtcore:type'),
                nodes=[],
                coverages=[],
                parent_node=self._parent_node
            )
            self._parent_node.nodes.append(self._node)
            mod_log().debug('XML: %s: %s', name, self._node.name)
        elif name == 'coverage':
            coverage = CoverageNode(
                type=attrs.get('type'),
                total=int(attrs.get('total')),
                executed=int(attrs.get('executed'))
            )
            self._node.coverages.append(coverage)
            mod_log().debug('XML: %s: %s', name, coverage.type)

    def endElement(self, name):
        mod_log().debug('XML: %s: CLOSING', name)
        if name == 'node':
            self._node = self._node.parent_node
            self._parent_node = self._node.parent_node


def parse_acoverage_response(coverage_results_xml):
    """Converts XML results into Python representation"""

    xml_handler = CoverageResponseHandler()
    xml.sax.parseString(coverage_results_xml, xml_handler)

    return xml_handler
