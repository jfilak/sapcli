#!/usr/bin/env python3

import unittest

import sap.adt
from sap.adt.errors import InvalidURIError
from sap.adt.objectstructure import get_object_structure, parse_object_structure
from sap.adt.uri import StatementPosition

from mock import Connection, Response, Request
from fixtures_adt_objectstructure import (
    OBJECT_STRUCTURE_CLASS_XML,
    OBJECT_STRUCTURE_OTHER_TYPES_XML,
    OBJECT_STRUCTURE_INVALID_RANGE_XML,
    OBJECT_STRUCTURE_WITHOUT_BASE_XML,
    OBJECT_STRUCTURE_PROGRAM_XML,
    OBJECT_STRUCTURE_FUNCTION_GROUP_XML,
)


OBJECT_STRUCTURE_MIME_TYPE = 'application/vnd.sap.adt.objectstructure.v2+xml'

PROBE = 'zcl_sapcli_ostruct_probe'


class TestParseObjectStructureRoot(unittest.TestCase):

    def setUp(self):
        self.root = parse_object_structure(OBJECT_STRUCTURE_CLASS_XML)

    def test_root_attributes(self):
        self.assertEqual(self.root.adt_type, 'CLAS/OC')
        self.assertEqual(self.root.name, 'ZCL_SAPCLI_OSTRUCT_PROBE')
        self.assertEqual(self.root.visibility, 'public')
        self.assertTrue(self.root.abstract)
        self.assertEqual(self.root.xml_base,
                         '/sap/bc/adt/oo/classes/zcl_sapcli_ostruct_probe/objectstructure?saml2=disabled&sap-client=001')

    def test_root_definition_identifier(self):
        self.assertEqual(self.root.definition_identifier,
                         StatementPosition(PROBE, 'source/main', 3, 6, 3, 30, 'CLAS/OC'))

    def test_root_definition_block(self):
        self.assertEqual(self.root.definition_block,
                         StatementPosition(PROBE, 'source/main', 3, 0, 36, 8, 'CLAS/OC'))

    def test_root_implementation_identifier(self):
        self.assertEqual(self.root.implementation_identifier,
                         StatementPosition(PROBE, 'source/main', 40, 6, 40, 30, 'CLAS/OC'))

    def test_root_implementation_block(self):
        self.assertEqual(self.root.implementation_block,
                         StatementPosition(PROBE, 'source/main', 40, 0, 68, 8, 'CLAS/OC'))

    def test_root_children(self):
        self.assertEqual([(child.adt_type, child.name) for child in self.root.children],
                         [('CLAS/OR', 'IF_OO_ADT_CLASSRUN'),
                          ('CLAS/OB', 'RUN'),
                          ('CLAS/OT', 'TY_COUNT'),
                          ('CLAS/OT', 'TY_PAIR'),
                          ('CLAS/OA', 'CO_ANSWER'),
                          ('CLAS/OA', 'COUNTER'),
                          ('CLAS/OA', 'INSTANCES'),
                          ('CLAS/OE', 'CHANGED'),
                          ('CLAS/OE', 'CREATED'),
                          ('CLAS/OM', 'CONSTRUCTOR'),
                          ('CLAS/OM', 'INCREMENT'),
                          ('CLAS/OM', 'CALCULATE'),
                          ('CLAS/OM', 'CREATE'),
                          ('CLAS/OM', 'ON_CHANGED'),
                          ('CLAS/OA', 'HELPER'),
                          ('CLAS/OM', 'GREET'),
                          ('CLAS/OM', 'IF_OO_ADT_CLASSRUN~MAIN'),
                          ('CLAS/OCL', 'LCL_HELPER'),
                          ('CLAS/OCL', 'LTCL_PROBE'),
                          ('CLAS/ON', 'LIF_GREETER'),
                          ('CLAS/OCX', 'ZCL_SAPCLI_OSTRUCT_PROBE')])


class TestParseObjectStructureMembers(unittest.TestCase):

    def setUp(self):
        self.root = parse_object_structure(OBJECT_STRUCTURE_CLASS_XML)

    def test_constructor_attributes(self):
        constructor = self.root.children[9]

        self.assertEqual(constructor.name, 'CONSTRUCTOR')
        self.assertEqual(constructor.level, 'instance')
        self.assertEqual(constructor.clif_name, 'ZCL_SAPCLI_OSTRUCT_PROBE')
        self.assertEqual(constructor.visibility, 'public')
        self.assertTrue(constructor.constructor)

    def test_method_implementation_block(self):
        greet = self.root.children[15]

        self.assertEqual(greet.name, 'GREET')
        self.assertEqual(greet.implementation_block,
                         StatementPosition(PROBE, 'source/main', 42, 2, 44, 11, 'CLAS/OC'))

    def test_abstract_method_without_implementation(self):
        calculate = self.root.children[11]

        self.assertEqual(calculate.name, 'CALCULATE')
        self.assertTrue(calculate.abstract)
        self.assertIsNone(calculate.implementation_identifier)
        self.assertIsNone(calculate.implementation_block)

    def test_interface_method_without_definition_block(self):
        main = self.root.children[16]

        self.assertEqual(main.name, 'IF_OO_ADT_CLASSRUN~MAIN')
        self.assertIsNone(main.definition_block)
        self.assertEqual(main.implementation_block,
                         StatementPosition(PROBE, 'source/main', 64, 2, 66, 11, 'CLAS/OC'))

    def test_final_method(self):
        increment = self.root.children[10]

        self.assertEqual(increment.name, 'INCREMENT')
        self.assertTrue(increment.final)

    def test_event_handler_method(self):
        on_changed = self.root.children[13]

        self.assertEqual(on_changed.name, 'ON_CHANGED')
        self.assertEqual(on_changed.visibility, 'protected')
        self.assertTrue(on_changed.event_handler_method)

    def test_constant(self):
        co_answer = self.root.children[4]

        self.assertEqual(co_answer.name, 'CO_ANSWER')
        self.assertEqual(co_answer.level, 'static')
        self.assertTrue(co_answer.constant)
        self.assertTrue(co_answer.read_only)

    def test_read_only_attribute(self):
        counter = self.root.children[5]

        self.assertEqual(counter.name, 'COUNTER')
        self.assertTrue(counter.read_only)
        self.assertFalse(counter.constant)

    def test_flags_false_when_missing(self):
        greet = self.root.children[15]

        self.assertEqual(greet.name, 'GREET')
        self.assertIs(greet.abstract, False)
        self.assertIs(greet.final, False)
        self.assertIs(greet.constant, False)
        self.assertIs(greet.read_only, False)
        self.assertIs(greet.constructor, False)
        self.assertIs(greet.redefinition, False)
        self.assertIs(greet.event_handler_method, False)
        self.assertIs(greet.test_class, False)
        self.assertIs(greet.test_method, False)
        self.assertIs(greet.is_external_ref, False)

    def test_link_type(self):
        interface = self.root.children[0]

        self.assertEqual(interface.name, 'IF_OO_ADT_CLASSRUN')
        self.assertEqual(interface.links[1].rel, 'http://www.sap.com/adt/relations/source/implementationIdentifier')
        self.assertEqual(interface.links[1].typ, 'CLAS/OM')

    def test_leaf_without_children(self):
        alias = self.root.children[1]

        self.assertEqual(alias.name, 'RUN')
        self.assertEqual(alias.children, [])

    def test_text_elements(self):
        text_elements = self.root.children[20]

        self.assertEqual(text_elements.adt_type, 'CLAS/OCX')
        self.assertTrue(text_elements.is_external_ref)
        self.assertEqual(text_elements.description, 'Text Elements')
        self.assertIsNone(text_elements.definition_identifier)
        self.assertEqual(text_elements.links[0].href, '/sap/bc/adt/textelements/classes/zcl_sapcli_ostruct_probe')


class TestParseObjectStructureLocalTypes(unittest.TestCase):

    def setUp(self):
        self.root = parse_object_structure(OBJECT_STRUCTURE_CLASS_XML)

    def test_local_class_children(self):
        helper = self.root.children[17]

        self.assertEqual(helper.name, 'LCL_HELPER')
        self.assertEqual([(child.adt_type, child.name) for child in helper.children],
                         [('CLAS/OLN', 'LIF_GREETER'),
                          ('CLAS/OLT', 'TY_NAME'),
                          ('CLAS/OLA', 'CO_DEFAULT'),
                          ('CLAS/OLA', 'NAME'),
                          ('CLAS/OLD', 'CONSTRUCTOR'),
                          ('CLAS/OLD', 'LIF_GREETER~GREET')])

    def test_local_class_definition_block(self):
        helper = self.root.children[17]

        self.assertEqual(helper.name, 'LCL_HELPER')
        self.assertEqual(helper.definition_block,
                         StatementPosition(PROBE, 'includes/definitions', 5, 0, 12, 8, 'CLAS/OC'))

    def test_local_class_implementation_block(self):
        helper = self.root.children[17]

        self.assertEqual(helper.name, 'LCL_HELPER')
        self.assertEqual(helper.implementation_block,
                         StatementPosition(PROBE, 'includes/implementations', 1, 0, 9, 8, 'CLAS/OC'))

    def test_local_method_implementation_block(self):
        constructor = self.root.children[17].children[4]

        self.assertEqual(constructor.name, 'CONSTRUCTOR')
        self.assertEqual(constructor.clif_name, 'LCL_HELPER')
        self.assertEqual(constructor.implementation_block,
                         StatementPosition(PROBE, 'includes/implementations', 2, 2, 4, 11, 'CLAS/OC'))

    def test_test_class(self):
        test_class = self.root.children[18]

        self.assertEqual(test_class.name, 'LTCL_PROBE')
        self.assertTrue(test_class.test_class)
        self.assertTrue(test_class.final)
        self.assertEqual(test_class.definition_block,
                         StatementPosition(PROBE, 'includes/testclasses', 1, 0, 7, 8, 'CLAS/OC'))

    def test_test_method(self):
        test_method = self.root.children[18].children[0]

        self.assertEqual(test_method.name, 'FIRST_TEST')
        self.assertEqual(test_method.visibility, 'private')
        self.assertTrue(test_method.test_method)
        self.assertEqual(test_method.implementation_block,
                         StatementPosition(PROBE, 'includes/testclasses', 10, 2, 11, 11, 'CLAS/OC'))

    def test_local_interface_method(self):
        method = self.root.children[19].children[0]

        self.assertEqual(method.adt_type, 'CLAS/OND')
        self.assertEqual(method.name, 'GREET')
        self.assertEqual(method.definition_block,
                         StatementPosition(PROBE, 'includes/definitions', 2, 2, 2, 51, 'CLAS/OC'))


class TestParseObjectStructureOtherTypes(unittest.TestCase):

    def setUp(self):
        self.root = parse_object_structure(OBJECT_STRUCTURE_OTHER_TYPES_XML)

    def test_children(self):
        self.assertEqual([(child.adt_type, child.name) for child in self.root.children],
                         [('CLAS/OF', 'CL_APC_WSP_CLIENT'),
                          ('CLAS/OQ', 'SET_OAUTH_TOKEN_SEAM'),
                          ('CLAS/I', 'PERFINTERVAL'),
                          ('CLAS/OLF', 'LCL_HTTP_CLIENT_TEST'),
                          ('CLAS/OK', 'ASSERT_WRONG_STATE'),
                          ('CLAS/OM', 'DELETE')])

    def test_unknown_attribute(self):
        friend = self.root.children[0]

        self.assertEqual(friend.name, 'CL_APC_WSP_CLIENT')
        self.assertEqual(friend.definition_identifier,
                         StatementPosition('cl_http_client', 'source/main', 5, 17, 5, 34, 'CLAS/OC'))

    def test_include_in_macros(self):
        include = self.root.children[2]

        self.assertEqual(include.name, 'PERFINTERVAL')
        self.assertEqual(include.definition_block,
                         StatementPosition('cl_http_client', 'includes/macros', 6, 0, 6, 21, 'CLAS/OC'))

    def test_redefinition(self):
        delete = self.root.children[5]

        self.assertEqual(delete.name, 'DELETE')
        self.assertTrue(delete.redefinition)


class TestParseObjectStructureRanges(unittest.TestCase):

    def test_invalid_range(self):
        root = parse_object_structure(OBJECT_STRUCTURE_INVALID_RANGE_XML)

        with self.assertRaises(InvalidURIError):
            root.definition_block

    def test_without_base(self):
        root = parse_object_structure(OBJECT_STRUCTURE_WITHOUT_BASE_XML)

        self.assertIsNone(root.xml_base)
        self.assertEqual(root.definition_block,
                         StatementPosition('.', 'source/main', 3, 0, 36, 8, None))


class TestParseObjectStructureProgram(unittest.TestCase):

    def setUp(self):
        self.root = parse_object_structure(OBJECT_STRUCTURE_PROGRAM_XML)

    def test_root(self):
        self.assertEqual(self.root.adt_type, 'PROG/P')
        self.assertEqual(self.root.name, 'DEMO_CLASSICAL_REPORTING')
        self.assertEqual(self.root.xml_base, '/sap/bc/adt/programs/programs/demo_classical_reporting/source/main')
        self.assertIsNone(self.root.definition_identifier)

    def test_children(self):
        self.assertEqual([(child.adt_type, child.name) for child in self.root.children],
                         [('PROG/PL', 'DEMO'),
                          ('PROG/PD', 'CARRID'),
                          ('PROG/PD', 'URL'),
                          ('PROG/PE', 'AT LINE-SELECTION'),
                          ('PROG/PE', 'START-OF-SELECTION'),
                          ('PROG/PX', 'DEMO_CLASSICAL_REPORTING')])

    def test_local_class(self):
        local_class = self.root.children[0]

        self.assertEqual(local_class.name, 'DEMO')
        self.assertEqual(local_class.include, 'DEMO_CLASSICAL_REPORTING')
        self.assertIsNone(local_class.definition_identifier)
        self.assertEqual(local_class.links[0].href,
                         '/sap/bc/adt/programs/programs/demo_classical_reporting/source/main#type=PROG%2FPL;name=DEMO')

    def test_local_class_method(self):
        method = self.root.children[0].children[0]

        self.assertEqual(method.adt_type, 'PROG/PLM')
        self.assertEqual(method.name, 'BROWSER')
        self.assertEqual(method.clif_name, 'DEMO')
        self.assertEqual(method.visibility, 'public')
        self.assertEqual(method.level, 'static')
        self.assertIsNone(method.definition_identifier)
        self.assertIsNone(method.implementation_identifier)

    def test_event(self):
        event = self.root.children[3]

        self.assertEqual(event.name, 'AT LINE-SELECTION')
        self.assertIsNone(event.definition_identifier)


class TestParseObjectStructureFunctionGroup(unittest.TestCase):

    def setUp(self):
        self.root = parse_object_structure(OBJECT_STRUCTURE_FUNCTION_GROUP_XML)

    def test_children(self):
        self.assertEqual([(child.adt_type, child.name) for child in self.root.children],
                         [('FUGR/FF', 'RFC_PING'),
                          ('FUGR/PD', 'ADMIN'),
                          ('FUGR/PZ', '001'),
                          ('FUGR/I', 'LSRFCI01'),
                          ('FUGR/PX', 'SAPLSRFC')])

    def test_function_module(self):
        function_module = self.root.children[0]

        self.assertEqual(function_module.name, 'RFC_PING')
        self.assertIsNone(function_module.type_description)
        self.assertIsNone(function_module.definition_identifier)
        self.assertEqual(function_module.links[0].href, '/sap/bc/adt/functions/groups/srfc/fmodules/rfc_ping/source/main')

    def test_data_object(self):
        data_object = self.root.children[1]

        self.assertEqual(data_object.name, 'ADMIN')
        self.assertIsNone(data_object.definition_identifier)

    def test_type_description(self):
        gui_titles = self.root.children[2]

        self.assertEqual(gui_titles.name, '001')
        self.assertEqual(gui_titles.type_description, 'GUI Titles')


class TestGetObjectStructure(unittest.TestCase):

    def test_default_version(self):
        connection = Connection([
            (Response(text=OBJECT_STRUCTURE_CLASS_XML, status_code=200, content_type=OBJECT_STRUCTURE_MIME_TYPE),
             Request.get(adt_uri='oo/classes/zcl_sapcli_ostruct_probe/objectstructure',
                         accept=OBJECT_STRUCTURE_MIME_TYPE))
        ], asserter=self)

        root = get_object_structure(sap.adt.Class(connection, 'ZCL_SAPCLI_OSTRUCT_PROBE'))

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(root.name, 'ZCL_SAPCLI_OSTRUCT_PROBE')
        self.assertEqual(root.children[17].definition_block,
                         StatementPosition(PROBE, 'includes/definitions', 5, 0, 12, 8, 'CLAS/OC'))

    def test_active_version(self):
        connection = Connection([
            (Response(text=OBJECT_STRUCTURE_CLASS_XML, status_code=200, content_type=OBJECT_STRUCTURE_MIME_TYPE),
             Request.get(adt_uri='oo/classes/zcl_sapcli_ostruct_probe/objectstructure',
                         accept=OBJECT_STRUCTURE_MIME_TYPE,
                         params={'version': 'active'}))
        ], asserter=self)

        root = get_object_structure(sap.adt.Class(connection, 'ZCL_SAPCLI_OSTRUCT_PROBE'), version='active')

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(root.name, 'ZCL_SAPCLI_OSTRUCT_PROBE')


if __name__ == '__main__':
    unittest.main()
