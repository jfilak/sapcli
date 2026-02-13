"""ADT Repository wrappers"""

from types import SimpleNamespace
import xml.sax
from xml.sax.handler import ContentHandler

from sap import get_logger


def mod_log():
    """ADT Module logger"""

    return get_logger()


class NodeStructureXMLHandler(ContentHandler):
    """Node Structure XML parser"""

    def __init__(self):
        super().__init__()

        self.tree_content = []
        self.categories = []
        self.object_types = []

        self._lists = {
            'SEU_ADT_REPOSITORY_OBJ_NODE': self.tree_content,
            'SEU_ADT_OBJECT_CATEGORY_INFO': self.categories,
            'SEU_ADT_OBJECT_TYPE_INFO': self.object_types}

        self._object = None
        self._property = None

    def startElement(self, name, attrs):
        mod_log().debug('XML: start: %s', name)

        if name in ['asx:abap', 'asx:values', 'DATA', 'TREE_CONTENT', 'CATEGORIES', 'OBJECT_TYPES']:
            return

        if name in self._lists:
            mod_log().debug('XML: new object: %s', name)
            self._object = SimpleNamespace()
        else:
            mod_log().debug('XML: object property: %s', name)
            self._property = name

    def characters(self, content):
        if self._property is None:
            return

        try:
            text = getattr(self._object, self._property)
        except AttributeError:
            text = content
        else:
            text += content

        mod_log().debug('XML: object property value: %s', text)
        setattr(self._object, self._property, text)

    def endElement(self, name):
        if name != self._property:
            try:
                self._lists[name].append(self._object)
                mod_log().debug('XML: complete object: %s', name)
                self._object = None
            except KeyError:
                pass
        else:
            if not hasattr(self._object, self._property):
                mod_log().debug('XML: object property value: <empty>')
                setattr(self._object, self._property, '')

            self._property = None

        mod_log().debug('XML: end: %s', name)


def nodekeys_list_table(nodekeys):
    """Converts List of nodekeys to XML ABAP internal table"""

    body = '\n'.join(map(lambda key: f'<TV_NODEKEY>{key}</TV_NODEKEY>', nodekeys))
    return f'<DATA>\n{body}\n</DATA>'


class Repository:
    """Repository proxy"""

    def __init__(self, connection):
        self._connection = connection

    def read_node(self, adt_object, withdescr=False, nodekeys=None):
        """Returns node structure iterator"""

        if nodekeys is None:
            keys = nodekeys_list_table(('000000',))
        else:
            nodekeys = set(nodekeys)  # remove duplicates
            keys = nodekeys_list_table(nodekeys)

        resp = self._connection.execute(
            'POST',
            'repository/nodestructure',
            params={
                'parent_name': adt_object.name,
                'parent_tech_name': adt_object.name,
                'parent_type': adt_object.objtype.code,
                'withShortDescriptions': str(withdescr).lower()},
            headers={
                'Accept': 'application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.RepositoryObjectTreeContent',
                'Content-Type': 'application/vnd.sap.as+xml; charset=UTF-8; dataname=null'},
            body=f'''<?xml version="1.0" encoding="UTF-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
<asx:values>
{keys}
</asx:values>
</asx:abap>''')

        if not resp.text:
            return SimpleNamespace(objects=[], types=[], categories=[])

        parser = NodeStructureXMLHandler()
        xml.sax.parseString(resp.text, parser)

        return SimpleNamespace(objects=parser.tree_content, types=parser.object_types, categories=parser.categories)

    def walk_step(self, adt_object, withdescr=False):
        """Returns list of intermediate subpackages and objects"""

        root_node = self.read_node(adt_object, withdescr=withdescr)
        subpackages = [subpkg.OBJECT_NAME for subpkg in root_node.objects]

        nodekeys = [objtyp.NODE_ID for objtyp in root_node.types if objtyp.OBJECT_TYPE != 'DEVC/K']
        if nodekeys:
            objects_node = self.read_node(adt_object, withdescr=withdescr, nodekeys=nodekeys)
            objects = [SimpleNamespace(typ=obj.OBJECT_TYPE,
                                       name=obj.OBJECT_NAME,
                                       uri=obj.OBJECT_URI,
                                       description=getattr(obj, 'DESCRIPTION', ''))
                       for obj in objects_node.objects]
        else:
            objects = []

        return subpackages, objects
