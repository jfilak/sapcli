#!/usr/bin/env python3

import unittest
from unittest.mock import Mock

import sap.adt
import sap.adt.programs
import sap.adt.function
from sap.errors import SAPCliError
from sap.adt.object_factory import (
    ADTObjectFactory,
    human_names_factory
)



class TestgADTObjectFactory(unittest.TestCase):

    def setUp(self):
        self.mock_conn = Mock()

    def test_factory_init_default(self):
        factory = ADTObjectFactory(self.mock_conn)

        self.assertEqual(factory._connection, self.mock_conn)
        self.assertEqual(list(factory.get_supported_names()), [])

    def test_factory_init_with_builders(self):
        exp_builders = {'fabulous': 'awesome'}
        factory = ADTObjectFactory(self.mock_conn, builders=exp_builders)

        self.assertEqual(factory._connection, self.mock_conn)
        self.assertEqual(list(factory.get_supported_names()), ['fabulous'])

    def test_factory_register_new(self):
        exp_producer = Mock()

        factory = ADTObjectFactory(self.mock_conn)
        factory.register('fabulous', exp_producer)
        product = factory.make('fabulous', 'awesome')

        self.assertEqual(product, exp_producer.return_value)
        exp_producer.assert_called_once_with(self.mock_conn, 'awesome')

    def test_factory_register_existing_raise(self):
        exp_producer = Mock()

        factory = ADTObjectFactory(self.mock_conn, builders={'fabulous': exp_producer})
        with self.assertRaises(SAPCliError) as caught:
            factory.register('fabulous', exp_producer)

        self.assertEqual(str(caught.exception), 'Object type builder was already registered: fabulous')

    def test_factory_register_existing_overwrote(self):
        def_producer = Mock()
        def_producer.side_effect = Exception

        exp_another_producer = Mock()

        factory = ADTObjectFactory(self.mock_conn, builders={'fabulous': def_producer})
        factory.register('fabulous', exp_another_producer, overwrite=True)
        product = factory.make('fabulous', 'awesome')

        self.assertEqual(product, exp_another_producer.return_value)
        exp_another_producer.assert_called_once_with(self.mock_conn, 'awesome')

    def test_factory_make_unknown(self):
        exp_builders = {'fabulous': 'awesome'}
        factory = ADTObjectFactory(self.mock_conn, builders=exp_builders)

        with self.assertRaises(SAPCliError) as caught:
            product = factory.make('gorgeous', 'success')

        self.assertEqual(str(caught.exception), 'Unknown ADT object type: gorgeous')

    def test_factory_make_known(self):
        mock_producer = Mock()
        exp_builders = {'fabulous': mock_producer}
        factory = ADTObjectFactory(self.mock_conn, builders=exp_builders)

        product = factory.make('fabulous', 'success')

        self.assertEqual(product, mock_producer.return_value)
        mock_producer.assert_called_once_with(self.mock_conn, 'success')


class TestHumanNamesFactory(unittest.TestCase):
    """Tests covering the catalogue produced by human_names_factory.

    The catalogue must expose every human readable ADT object kind
    historically defined either by sap.adt.object_factory or by
    sap.cli.activation, plus the corresponding ABAP-style 4-char
    aliases.
    """

    def setUp(self):
        self.mock_conn = Mock()
        self.factory = human_names_factory(self.mock_conn)

    # ------------------------------------------------------------------
    # canonical human readable names
    # ------------------------------------------------------------------
    def test_program(self):
        obj = self.factory.make('program', 'ZMYREP')
        self.assertIsInstance(obj, sap.adt.Program)
        self.assertEqual(obj.name, 'ZMYREP')

    def test_include(self):
        obj = self.factory.make('include', 'ZMYREP_C01')
        self.assertIsInstance(obj, sap.adt.Include)
        self.assertEqual(obj.name, 'ZMYREP_C01')

    def test_program_include_keeps_dedicated_builder(self):
        # The '\\' syntax exercises the parsing branch of
        # make_program_include_object (no remote fetch), which proves the
        # dedicated builder is still wired up rather than the bare
        # Include constructor.
        obj = self.factory.make('program-include', 'ZMYREP\\ZMYREP_C01')
        self.assertIsInstance(obj, sap.adt.Include)
        self.assertEqual(obj.name, 'ZMYREP_C01')
        self.assertEqual(obj.master, 'ZMYREP')

    def test_class(self):
        obj = self.factory.make('class', 'CL_FOO')
        self.assertIsInstance(obj, sap.adt.Class)
        self.assertEqual(obj.name, 'CL_FOO')

    def test_interface(self):
        obj = self.factory.make('interface', 'IF_FOO')
        self.assertIsInstance(obj, sap.adt.Interface)
        self.assertEqual(obj.name, 'IF_FOO')

    def test_function_group(self):
        obj = self.factory.make('function-group', 'ZFG')
        self.assertIsInstance(obj, sap.adt.FunctionGroup)
        self.assertEqual(obj.name, 'ZFG')

    def test_function_module_is_registered(self):
        # The 'function-module' kind uses the dedicated builder
        # make_function_module_object which accepts the
        # 'GROUP\\FUNCTION' input and turns it into a proper
        # FunctionModule instance carrying the function group name
        # required by its constructor.
        obj = self.factory.make('function-module', 'ZFG_HELLO_WORLD\\Z_FN_HELLO_WORLD')
        self.assertIsInstance(obj, sap.adt.FunctionModule)
        self.assertEqual(obj.name, 'Z_FN_HELLO_WORLD')
        self.assertEqual(obj._function_group_name, 'ZFG_HELLO_WORLD')

    def test_function_include_is_registered(self):
        # The 'function-include' kind uses the dedicated builder
        # make_function_include_object which enforces the
        # 'GROUP\\INCLUDE' input because function include names are
        # not unique across function groups and cannot be looked up.
        obj = self.factory.make('function-include', 'ZFG_HELLO_WORLD\\ZFI_HELLO_WORLD')
        self.assertIsInstance(obj, sap.adt.FunctionInclude)
        self.assertEqual(obj.name, 'ZFI_HELLO_WORLD')
        self.assertEqual(obj._function_group_name, 'ZFG_HELLO_WORLD')

    def test_data_element(self):
        obj = self.factory.make('data-element', 'ZDTEL')
        self.assertIsInstance(obj, sap.adt.DataElement)
        self.assertEqual(obj.name, 'ZDTEL')

    def test_domain(self):
        obj = self.factory.make('domain', 'ZDOMA')
        self.assertIsInstance(obj, sap.adt.Domain)
        self.assertEqual(obj.name, 'ZDOMA')

    def test_table(self):
        obj = self.factory.make('table', 'ZTAB')
        self.assertIsInstance(obj, sap.adt.Table)
        self.assertEqual(obj.name, 'ZTAB')

    def test_structure(self):
        obj = self.factory.make('structure', 'ZSTRU')
        self.assertIsInstance(obj, sap.adt.Structure)
        self.assertEqual(obj.name, 'ZSTRU')

    def test_behavior_definition(self):
        obj = self.factory.make('behavior-definition', 'ZBDEF')
        self.assertIsInstance(obj, sap.adt.BehaviorDefinition)
        self.assertEqual(obj.name, 'ZBDEF')

    def test_message_class(self):
        obj = self.factory.make('message-class', 'ZMSG')
        self.assertIsInstance(obj, sap.adt.MessageClass)
        self.assertEqual(obj.name, 'ZMSG')

    def test_transaction(self):
        obj = self.factory.make('transaction', 'ZTRN')
        self.assertIsInstance(obj, sap.adt.Transaction)
        self.assertEqual(obj.name, 'ZTRN')

    def test_package(self):
        obj = self.factory.make('package', '$ZPKG')
        self.assertIsInstance(obj, sap.adt.Package)
        self.assertEqual(obj.name, '$ZPKG')

    # ------------------------------------------------------------------
    # ABAP-style 4-char aliases share the builder of the canonical name
    # ------------------------------------------------------------------
    def test_alias_prog_resolves_to_program(self):
        obj = self.factory.make('prog', 'ZMYREP')
        self.assertIsInstance(obj, sap.adt.Program)

    def test_alias_incl_resolves_to_include(self):
        obj = self.factory.make('incl', 'ZMYREP_C01')
        self.assertIsInstance(obj, sap.adt.Include)

    def test_alias_clas_resolves_to_class(self):
        obj = self.factory.make('clas', 'CL_FOO')
        self.assertIsInstance(obj, sap.adt.Class)

    def test_alias_intf_resolves_to_interface(self):
        obj = self.factory.make('intf', 'IF_FOO')
        self.assertIsInstance(obj, sap.adt.Interface)

    def test_alias_fugr_resolves_to_function_group(self):
        obj = self.factory.make('fugr', 'ZFG')
        self.assertIsInstance(obj, sap.adt.FunctionGroup)

    def test_alias_fm_is_registered(self):
        # See test_function_module_is_registered for the rationale.
        self.assertIn('fm', self.factory.get_supported_names())

    def test_alias_dtel_resolves_to_data_element(self):
        obj = self.factory.make('dtel', 'ZDTEL')
        self.assertIsInstance(obj, sap.adt.DataElement)

    def test_alias_doma_resolves_to_domain(self):
        obj = self.factory.make('doma', 'ZDOMA')
        self.assertIsInstance(obj, sap.adt.Domain)

    def test_alias_tabl_resolves_to_table(self):
        obj = self.factory.make('tabl', 'ZTAB')
        self.assertIsInstance(obj, sap.adt.Table)

    def test_alias_stru_resolves_to_structure(self):
        obj = self.factory.make('stru', 'ZSTRU')
        self.assertIsInstance(obj, sap.adt.Structure)

    def test_alias_bdef_resolves_to_behavior_definition(self):
        obj = self.factory.make('bdef', 'ZBDEF')
        self.assertIsInstance(obj, sap.adt.BehaviorDefinition)

    def test_alias_msag_resolves_to_message_class(self):
        obj = self.factory.make('msag', 'ZMSG')
        self.assertIsInstance(obj, sap.adt.MessageClass)

    def test_alias_tran_resolves_to_transaction(self):
        obj = self.factory.make('tran', 'ZTRN')
        self.assertIsInstance(obj, sap.adt.Transaction)

    # ------------------------------------------------------------------
    # discoverability
    # ------------------------------------------------------------------
    def test_get_supported_names_lists_canonical_and_aliases(self):
        names = list(self.factory.get_supported_names())

        # spot-check that both forms are present
        self.assertIn('program', names)
        self.assertIn('prog', names)
        self.assertIn('class', names)
        self.assertIn('clas', names)
        self.assertIn('program-include', names)


if __name__ == '__main__':
    unittest.main()
