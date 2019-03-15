#!/usr/bin/env python3

import os
import sys
from argparse import ArgumentParser
import unittest
from unittest.mock import Mock, PropertyMock, patch, mock_open, call
from types import SimpleNamespace

import sap.cli.checkout

from mock import Connection


def parse_args(argv):
    parser = ArgumentParser()
    sap.cli.checkout.CommandGroup().install_parser(parser)
    return parser.parse_args(argv)


def assert_wrote_file(unit_test, fake_open, file_name, contents, fileno=1):
    start = (fileno - 1) * 4
    unit_test.assertEqual(fake_open.mock_calls[start + 0], call(file_name, 'w'))
    unit_test.assertEqual(fake_open.mock_calls[start + 1], call().__enter__())
    unit_test.assertEqual(fake_open.mock_calls[start + 2], call().write(contents))
    unit_test.assertEqual(fake_open.mock_calls[start + 3], call().__exit__(None, None, None))


class TestCheckoutCommandGroup(unittest.TestCase):

    def test_constructor(self):
        sap.cli.checkout.CommandGroup()


class TestCheckout(unittest.TestCase):

    @patch('sap.adt.Class.test_classes', new_callable=PropertyMock)
    @patch('sap.adt.Class.implementations', new_callable=PropertyMock)
    @patch('sap.adt.Class.definitions', new_callable=PropertyMock)
    @patch('sap.adt.Class.text', new_callable=PropertyMock)
    def test_checkout_class(self, fake_text, fake_defs, fake_impls, fake_tests):
        fake_text.return_value = 'class zcl_hello_world'

        fake_defs.return_value = Mock()
        fake_defs.return_value.text = '* definitions'

        fake_impls.return_value = Mock()
        fake_impls.return_value.text = '* implementations'

        fake_tests.return_value = Mock()
        fake_tests.return_value.text = '* tests'

        args = parse_args(['class', 'ZCL_HELLO_WORLD'])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open:
            args.execute(Connection(), args)

        assert_wrote_file(self, fake_open, 'zcl_hello_world.clas.abap', 'class zcl_hello_world', fileno=1)
        assert_wrote_file(self, fake_open, 'zcl_hello_world.clas.locals_def.abap', '* definitions', fileno=2)
        assert_wrote_file(self, fake_open, 'zcl_hello_world.clas.locals_imp.abap', '* implementations', fileno=3)
        assert_wrote_file(self, fake_open, 'zcl_hello_world.clas.testclasses.abap', '* tests', fileno=4)

    @patch('sap.adt.Interface.text', new_callable=PropertyMock)
    def test_checkout_interface(self, fake_text):
        fake_text.return_value = 'interface zif_hello_world'

        args = parse_args(['interface', 'ZIF_HELLO_WORLD'])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open:
            args.execute(Connection(), args)

        assert_wrote_file(self, fake_open, 'zif_hello_world.intf.abap', 'interface zif_hello_world')

    @patch('sap.adt.Program.text', new_callable=PropertyMock)
    def test_checkout_program(self, fake_text):
        fake_text.return_value = 'REPORT z_hello_world'

        args = parse_args(['program', 'Z_HELLO_WORLD'])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open:
            args.execute(Connection(), args)

        assert_wrote_file(self, fake_open, 'z_hello_world.prog.abap', 'REPORT z_hello_world')


class TestCheckoutPackage(unittest.TestCase):

    @patch('sap.cli.checkout.checkout_class')
    @patch('sap.cli.checkout.checkout_interface')
    @patch('sap.cli.checkout.checkout_program')
    @patch('sap.adt.package.walk')
    def test_checkout_package_recursive(self, fake_walk, fake_prog, fake_intf, fake_clas):
        conn = Connection([])

        package_name = '$VICTORY'
        sub_package_name = '$VICTORY_TESTS'
        fake_walk.return_value = iter(
            (([],
              [sub_package_name],
              [SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD'),
               SimpleNamespace(typ='CLAS/OC', name='ZCL_HELLO_WORLD'),
               SimpleNamespace(typ='PROG/P', name='Z_HELLO_WORLD'),
               SimpleNamespace(typ='7777/3', name='Magic Unicorn')]),
             ([sub_package_name],
              [],
              [SimpleNamespace(typ='CLAS/OC', name='ZCL_TESTS')]))
        )

        args = parse_args(['package', package_name, '--recursive'])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open, \
             patch('sap.cli.checkout.print') as fake_print, \
             patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = True
            fake_makedirs.side_effect = Exception('Should not be evaluated')
            args.execute(conn, args)

        exp_destdir = os.path.abspath(os.path.join(package_name, 'src'))
        exp_sub_destdir = os.path.abspath(os.path.join(package_name, 'src', sub_package_name.lower()))
        fake_prog.assert_called_once_with(conn, 'Z_HELLO_WORLD', exp_destdir)
        fake_intf.assert_called_once_with(conn, 'ZIF_HELLO_WORLD', exp_destdir)
        self.assertEqual(fake_clas.mock_calls, [call(conn, 'ZCL_HELLO_WORLD', exp_destdir),
                                                call(conn, 'ZCL_TESTS', exp_sub_destdir)])

        self.assertEqual(fake_print.mock_calls, [call('Unsupported object: 7777/3 Magic Unicorn', file=sys.stderr)])

    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_non_recursive(self, fake_walk, fake_checkout):
        conn = Connection([])

        exp_objects = [SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD')]
        fake_walk.return_value = iter((([], ['$TESTS'], exp_objects),
                                       (['$TESTS'], [], [])))

        package_name = '$ROOT'
        starting_folder = 'src'
        args = parse_args(['package', package_name])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open, \
             patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = True
            fake_makedirs.side_effect = Exception('Should not be evaluated')
            args.execute(conn, args)

        exp_destdir = os.path.abspath(os.path.join(package_name, starting_folder))
        fake_checkout.assert_called_once_with(conn, exp_objects, destdir=exp_destdir)

    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_starting_folder(self, fake_walk, fake_checkout):
        conn = Connection([])

        exp_objects = [SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD')]
        fake_walk.return_value = iter((([], [], exp_objects), ))

        package_name = '$VICTORY'
        starting_folder = os.path.join('backend', 'abap', 'src')
        args = parse_args(['package', package_name, '--starting-folder', starting_folder])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open, \
             patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = True
            fake_makedirs.side_effect = Exception('Should not be executed')
            args.execute(conn, args)

        exp_repodir = os.path.abspath(package_name)
        fake_isdir.assert_called_once_with(exp_repodir)

        exp_sourcedir = os.path.abspath(os.path.join(exp_repodir, starting_folder))
        fake_checkout.assert_called_once_with(conn, exp_objects, destdir=exp_sourcedir)

    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_create_repo(self, fake_walk, fake_checkout):
        conn = Connection([])
        fake_walk.return_value = iter((([], [], []), ))

        package_name = '$VICTORY'
        starting_folder = os.path.join('backend', 'abap', 'src')
        args = parse_args(['package', package_name, '--starting-folder', starting_folder])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open, \
             patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = False
            args.execute(conn, args)

        exp_repodir = os.path.abspath(package_name)
        fake_isdir.assert_called_once_with(exp_repodir)
        fake_makedirs.assert_called_once_with(exp_repodir)

        abapgit_file = os.path.join(exp_repodir, '.abapgit.xml')
        assert_wrote_file(self, fake_open, abapgit_file, '''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <DATA>
   <MASTER_LANGUAGE>E</MASTER_LANGUAGE>
   <STARTING_FOLDER>/backend/abap/src/</STARTING_FOLDER>
   <FOLDER_LOGIC>FULL</FOLDER_LOGIC>
   <IGNORE>
    <item>/.gitignore</item>
    <item>/LICENSE</item>
    <item>/README.md</item>
    <item>/package.json</item>
    <item>/.travis.yml</item>
   </IGNORE>
  </DATA>
 </asx:values>
</asx:abap>''')

    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_custom_repo_dir(self, fake_walk, fake_checkout):
        conn = Connection([])

        exp_objects = [SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD')]
        fake_walk.return_value = iter((([], [], exp_objects), ))

        package_name = '$VICTORY'
        starting_folder = os.path.join('backend', 'abap', 'src')
        repo_dir_name = 'valhalla'
        args = parse_args(['package', package_name, repo_dir_name, '--starting-folder', starting_folder])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open, \
             patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = True
            fake_makedirs.side_effect = Exception('Should not be evaluated')
            args.execute(conn, args)

        exp_repodir = os.path.abspath(repo_dir_name)
        fake_isdir.assert_called_once_with(exp_repodir)

        exp_sourcedir = os.path.join(exp_repodir, starting_folder)
        fake_checkout.assert_called_once_with(conn, exp_objects, destdir=exp_sourcedir)

    def test_checkout_objects_makedirs(self):
        conn = Connection([])

        starting_folder = os.path.join('backend', 'abap', 'src')
        with patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = False
            sap.cli.checkout.checkout_objects(conn, [], destdir=starting_folder)

        fake_isdir.assert_called_once_with(starting_folder)
        fake_makedirs.assert_called_once_with(starting_folder)


if __name__ == '__main__':
    unittest.main()
