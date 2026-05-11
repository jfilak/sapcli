#!/usr/bin/env python3

import unittest

import sap.adt
import sap.adt.wb
from sap.adt.behaviordefinition import BehaviorDefinition
from sap.adt.common_types import ADTTemplate, ADTTemplateProperty

from mock import Connection, Response

from fixtures_adt import GET_BDEF_ADT_XML, LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK


FIXTURE_ACTIVATION_REQUEST_XML='''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/bo/behaviordefinitions/zmybdef" adtcore:name="ZMYBDEF"/>
</adtcore:objectReferences>'''

FIXTURE_BDEF_CODE='''projection;
strict ( 2 );
use draft;

define behavior for ZMyEntity alias MyEntity
{
  use create;
  use update;
  use delete;
}
'''


class TestADTBehaviorDefinition(unittest.TestCase):

    def test_adt_bdef_init(self):
        metadata = sap.adt.ADTCoreData()

        bdef = sap.adt.BehaviorDefinition('CONNECTION', name='ZMYBDEF', package='PACKAGE', metadata=metadata)
        self.assertEqual(bdef.name, 'ZMYBDEF')
        self.assertEqual(bdef.reference.name, 'PACKAGE')
        self.assertEqual(bdef.coredata, metadata)

    def test_adt_bdef_objtype(self):
        bdef = sap.adt.BehaviorDefinition('CONNECTION', name='ZMYBDEF')
        self.assertEqual(bdef.objtype.code, 'BDEF/BDO')
        self.assertEqual(bdef.objtype.basepath, 'bo/behaviordefinitions')
        self.assertEqual(bdef.objtype.mimetype, 'application/vnd.sap.adt.blues.v1+xml')
        self.assertEqual(bdef.objtype.xmlname, 'blueSource')

    def test_adt_bdef_uri(self):
        bdef = sap.adt.BehaviorDefinition('CONNECTION', name='ZMYBDEF')
        self.assertEqual(bdef.uri, 'bo/behaviordefinitions/zmybdef')

    def test_adt_bdef_read(self):
        conn = Connection([Response(text=FIXTURE_BDEF_CODE,
                                 status_code=200,
                                 headers={'Content-Type': 'text/plain; charset=utf-8'})])

        bdef = sap.adt.BehaviorDefinition(conn, name='ZMYBDEF')
        code = bdef.text

        self.assertEqual(conn.mock_methods(), [('GET', '/sap/bc/adt/bo/behaviordefinitions/zmybdef/source/main')])

        get_request = conn.execs[0]
        self.assertEqual(sorted(get_request.headers), ['Accept'])
        self.assertEqual(get_request.headers['Accept'], 'text/plain')

        self.assertIsNone(get_request.params)
        self.assertIsNone(get_request.body)

        self.maxDiff = None
        self.assertEqual(code, FIXTURE_BDEF_CODE)

    def test_adt_bdef_activate(self):
        conn = Connection([
            EMPTY_RESPONSE_OK,
            Response(text=GET_BDEF_ADT_XML,
                status_code=200,
                headers={'Content-Type': 'application/xml; charset=utf-8'})
            ])

        bdef = sap.adt.BehaviorDefinition(conn, name='ZMYBDEF')
        sap.adt.wb.activate(bdef)

        self.assertEqual(conn.mock_methods(), [
            ('POST', '/sap/bc/adt/activation'),
            ('GET', '/sap/bc/adt/bo/behaviordefinitions/zmybdef')
        ])

        # two requests - activation + fetch
        self.assertEqual(len(conn.execs), 2)

        get_request = conn.execs[0]
        self.assertEqual(sorted(get_request.headers), ['Accept', 'Content-Type'])
        self.assertEqual(get_request.headers['Accept'], 'application/xml')
        self.assertEqual(get_request.headers['Content-Type'], 'application/xml')

        self.assertEqual(sorted(get_request.params), ['method', 'preauditRequested'])
        self.assertEqual(get_request.params['method'], 'activate')
        self.assertEqual(get_request.params['preauditRequested'], 'true')

        self.assertEqual(get_request.body, FIXTURE_ACTIVATION_REQUEST_XML)


FIXTURE_LIST_INTERFACES_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<nameditem:namedItemList xmlns:nameditem="http://www.sap.com/adt/nameditem">
  <nameditem:totalItemCount>1</nameditem:totalItemCount>
  <nameditem:namedItem>
    <nameditem:name>I_PRODUCTTP_2</nameditem:name>
    <nameditem:description/>
    <nameditem:data/>
  </nameditem:namedItem>
</nameditem:namedItemList>'''

FIXTURE_LIST_INTERFACES_EMPTY_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<nameditem:namedItemList xmlns:nameditem="http://www.sap.com/adt/nameditem">
  <nameditem:totalItemCount>0</nameditem:totalItemCount>
</nameditem:namedItemList>'''


class TestBehaviorDefinitionListInterfaces(unittest.TestCase):

    def test_list_interfaces(self):
        conn = Connection([Response(text=FIXTURE_LIST_INTERFACES_XML,
                                    status_code=200,
                                    headers={'Content-Type': 'application/vnd.sap.adt.nameditems.v1+xml; charset=utf-8'})])

        result = BehaviorDefinition.list_interfaces(conn, 'r_producttp')

        self.assertEqual(conn.mock_methods(), [
            ('GET', '/sap/bc/adt/bo/behaviordefinitions/interfaces')
        ])

        get_request = conn.execs[0]
        self.assertEqual(get_request.params, {'name': 'R_PRODUCTTP'})
        self.assertEqual(get_request.headers['Accept'],
                         'application/vnd.sap.adt.nameditems.v1+xml, application/xml')

        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0].name, 'I_PRODUCTTP_2')

    def test_list_interfaces_empty(self):
        conn = Connection([Response(text=FIXTURE_LIST_INTERFACES_EMPTY_XML,
                                    status_code=200,
                                    headers={'Content-Type': 'application/vnd.sap.adt.nameditems.v1+xml; charset=utf-8'})])

        result = BehaviorDefinition.list_interfaces(conn, 'R_PRODUCTTP')

        self.assertEqual(len(result.items), 0)


class TestBehaviorDefinitionWithTemplate(unittest.TestCase):

    def test_bdef_template_default_none(self):
        bdef = sap.adt.BehaviorDefinition('CONNECTION', name='ZMYBDEF')
        self.assertIsNone(bdef.template)

    def test_bdef_set_template(self):
        bdef = sap.adt.BehaviorDefinition('CONNECTION', name='ZMYBDEF')
        template = ADTTemplate([
            ADTTemplateProperty('base_bdef', 'R_PRODUCTTP'),
            ADTTemplateProperty('interface_bdef'),
        ])
        bdef.template = template
        self.assertEqual(bdef.template, template)

    def test_bdef_create_without_template(self):
        conn = Connection([Response(text='', status_code=201)])
        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN',
                                        package='MYPACKAGE', responsible='DEVELOPER')
        bdef = sap.adt.BehaviorDefinition(conn, name='R_PRODUCTTP_EXT',
                                           package='MYPACKAGE', metadata=metadata)
        bdef.description = 'test ext'
        bdef.create()

        body = conn.execs[0].body.decode('utf-8')
        self.assertNotIn('adtcore:adtTemplate', body)

    def test_bdef_create_with_template_no_interface(self):
        conn = Connection([Response(text='', status_code=201)])
        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN',
                                        package='MYPACKAGE', responsible='DEVELOPER')
        bdef = sap.adt.BehaviorDefinition(conn, name='R_PRODUCTTP_EXT',
                                           package='MYPACKAGE', metadata=metadata)
        bdef.description = 'test ext'
        bdef.template = ADTTemplate([
            ADTTemplateProperty('base_bdef', 'R_PRODUCTTP'),
            ADTTemplateProperty('interface_bdef'),
        ])
        bdef.create(corrnr='C50K000066')

        self.assertEqual(conn.execs[0].method, 'POST')
        self.assertEqual(conn.execs[0].adt_uri, '/sap/bc/adt/bo/behaviordefinitions')
        self.assertEqual(conn.execs[0].params, {'corrNr': 'C50K000066'})

        body = conn.execs[0].body.decode('utf-8')
        self.assertIn('<adtcore:adtTemplate>', body)
        self.assertIn('<adtcore:adtProperty adtcore:key="base_bdef">R_PRODUCTTP</adtcore:adtProperty>', body)
        self.assertIn('<adtcore:adtProperty adtcore:key="interface_bdef"/>', body)

    def test_bdef_create_with_template_with_interface(self):
        conn = Connection([Response(text='', status_code=201)])
        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN',
                                        package='MYPACKAGE', responsible='DEVELOPER')
        bdef = sap.adt.BehaviorDefinition(conn, name='R_PRODUCTTP_EXT',
                                           package='MYPACKAGE', metadata=metadata)
        bdef.description = 'test ext'
        bdef.template = ADTTemplate([
            ADTTemplateProperty('base_bdef', 'R_PRODUCTTP'),
            ADTTemplateProperty('interface_bdef', 'I_PRODUCTTP_2'),
        ])
        bdef.create()

        body = conn.execs[0].body.decode('utf-8')
        self.assertIn('<adtcore:adtProperty adtcore:key="interface_bdef">I_PRODUCTTP_2</adtcore:adtProperty>', body)


FIXTURE_BDEF_CREATE_WITH_TEMPLATE_XML = '<?xml version="1.0" encoding="UTF-8"?>\n' \
    '<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue" xmlns:adtcore="http://www.sap.com/adt/core"' \
    ' adtcore:type="BDEF/BDO" adtcore:description="test ext" adtcore:language="EN"' \
    ' adtcore:name="R_PRODUCTTP_EXT" adtcore:masterLanguage="EN" adtcore:responsible="DEVELOPER">\n' \
    '<adtcore:adtTemplate>\n' \
    '<adtcore:adtProperty adtcore:key="base_bdef">R_PRODUCTTP</adtcore:adtProperty>\n' \
    '<adtcore:adtProperty adtcore:key="interface_bdef"/>\n' \
    '</adtcore:adtTemplate>\n' \
    '<adtcore:packageRef adtcore:name="MYPACKAGE"/>\n' \
    '</blue:blueSource>'


class TestBehaviorDefinitionSerialization(unittest.TestCase):

    def test_bdef_serialize_with_template(self):
        conn = Connection([Response(text='', status_code=201)])
        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN',
                                        package='MYPACKAGE', responsible='DEVELOPER')
        bdef = sap.adt.BehaviorDefinition(conn, name='R_PRODUCTTP_EXT',
                                           package='MYPACKAGE', metadata=metadata)
        bdef.description = 'test ext'
        bdef.template = ADTTemplate([
            ADTTemplateProperty('base_bdef', 'R_PRODUCTTP'),
            ADTTemplateProperty('interface_bdef'),
        ])
        bdef.create()

        body = conn.execs[0].body.decode('utf-8')
        self.maxDiff = None
        self.assertEqual(body, FIXTURE_BDEF_CREATE_WITH_TEMPLATE_XML)


class TestBehaviorDefinitionExtend(unittest.TestCase):

    def test_extend_without_interface(self):
        bdef = BehaviorDefinition.extend(
            'CONNECTION', 'R_PRODUCTTP_EXT', base_bdef='R_PRODUCTTP',
            package='MYPACKAGE', description="jakub's extension"
        )

        self.assertIsInstance(bdef, BehaviorDefinition)
        self.assertEqual(bdef.name, 'R_PRODUCTTP_EXT')
        self.assertEqual(bdef.reference.name, 'MYPACKAGE')
        self.assertEqual(bdef.description, "jakub's extension")
        self.assertIsNotNone(bdef.template)
        self.assertEqual(len(bdef.template.properties), 2)
        self.assertEqual(bdef.template.properties[0].key, 'base_bdef')
        self.assertEqual(bdef.template.properties[0].value, 'R_PRODUCTTP')
        self.assertEqual(bdef.template.properties[1].key, 'interface_bdef')
        self.assertIsNone(bdef.template.properties[1].value)

    def test_extend_with_interface(self):
        bdef = BehaviorDefinition.extend(
            'CONNECTION', 'R_PRODUCTTP_EXT', base_bdef='R_PRODUCTTP',
            package='MYPACKAGE', description='test ext',
            interface_bdef='I_PRODUCTTP_2'
        )

        self.assertEqual(bdef.template.properties[1].key, 'interface_bdef')
        self.assertEqual(bdef.template.properties[1].value, 'I_PRODUCTTP_2')

    def test_extend_without_optional_params(self):
        bdef = BehaviorDefinition.extend(
            'CONNECTION', 'R_PRODUCTTP_EXT', base_bdef='R_PRODUCTTP'
        )

        self.assertIsNone(bdef.reference.name)
        self.assertIsNone(bdef.description)
        self.assertIsNotNone(bdef.template)


if __name__ == '__main__':
    unittest.main()
