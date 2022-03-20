#!/usr/bin/env python3

import unittest
from unittest.mock import Mock

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
