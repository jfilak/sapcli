#!/usr/bin/env python3

import os
import sys
from argparse import ArgumentParser
import unittest
from unittest.mock import Mock, PropertyMock, patch, mock_open, call
from types import SimpleNamespace
from io import StringIO

import sap.cli.checkout
import sap.platform.abap
import sap.platform.abap.abapgit

from mock import ConnectionViaHTTP as Connection


def parse_args(argv):
    parser = ArgumentParser()
    sap.cli.checkout.CommandGroup().install_parser(parser)
    return parser.parse_args(argv)


def assert_wrote_file(unit_test, fake_open, file_name, contents, fileno=1):
    start = (fileno - 1) * 4
    unit_test.assertEqual(fake_open.mock_calls[start + 0], call(file_name, 'w', encoding='utf8'))
    unit_test.assertEqual(fake_open.mock_calls[start + 1], call().__enter__())
    unit_test.assertEqual(fake_open.mock_calls[start + 2], call().write(contents))
    unit_test.assertEqual(fake_open.mock_calls[start + 3], call().__exit__(None, None, None))


class TestCheckoutCommandGroup(unittest.TestCase):

    def test_constructor(self):
        sap.cli.checkout.CommandGroup()


class TestCheckout(unittest.TestCase):

    @patch('sap.cli.checkout.checkout_class')
    def test_checkout_uppercase_name_clas(self, fake_clas):
        conn = Connection()

        args = parse_args(['class', 'zcl_lowercase'])
        args.execute(conn, args)

        args = parse_args(['class', 'ZCL_UPPERCASE'])
        args.execute(conn, args)

        self.assertEquals(fake_clas.mock_calls, [call(conn, 'ZCL_LOWERCASE'), call(conn, 'ZCL_UPPERCASE')])

    @patch('sap.cli.checkout.checkout_interface')
    def test_checkout_uppercase_name_intf(self, fake_intf):
        conn = Connection()

        args = parse_args(['interface', 'zif_lowercase'])
        args.execute(conn, args)

        args = parse_args(['interface', 'ZIF_UPPERCASE'])
        args.execute(conn, args)

        self.assertEqual(fake_intf.mock_calls, [call(conn, 'ZIF_LOWERCASE'), call(conn, 'ZIF_UPPERCASE')])

    @patch('sap.cli.checkout.checkout_program')
    def test_checkout_uppercase_name_prog(self, fake_prog):
        conn = Connection()

        args = parse_args(['program', 'zlowercase'])
        args.execute(conn, args)

        args = parse_args(['program', 'ZUPPERCASE'])
        args.execute(conn, args)

        self.assertEqual(fake_prog.mock_calls, [call(conn, 'ZLOWERCASE'), call(conn, 'ZUPPERCASE')])

    @patch('sap.cli.checkout.XMLWriter')
    @patch('sap.adt.Class')
    def test_checkout_class(self, fake_clas, fake_writer):
        fake_inst = Mock()
        fake_inst.name = 'ZCL_HELLO_WORLD'
        fake_inst.description = 'Cowabunga'
        fake_inst.master_language = 'EN'
        fake_inst.active = 'active'
        fake_inst.modeled = False
        fake_inst.fix_point_arithmetic = True
        fake_inst.text = 'class zcl_hello_world'

        fake_inst.definitions = Mock()
        fake_inst.definitions.text = '* definitions'

        fake_inst.implementations = Mock()
        fake_inst.implementations.text = '* implementations'

        fake_inst.test_classes = Mock()
        fake_inst.test_classes.text = '* tests'

        fake_clas.return_value = fake_inst

        fake_inst = Mock()
        fake_inst.add = Mock()
        fake_inst.close = Mock()
        fake_writer.return_value = fake_inst

        args = parse_args(['class', 'ZCL_HELLO_WORLD'])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open:
            args.execute(Connection(), args)

        assert_wrote_file(self, fake_open, 'zcl_hello_world.clas.abap', 'class zcl_hello_world', fileno=1)
        assert_wrote_file(self, fake_open, 'zcl_hello_world.clas.locals_def.abap', '* definitions', fileno=2)
        assert_wrote_file(self, fake_open, 'zcl_hello_world.clas.locals_imp.abap', '* implementations', fileno=3)
        assert_wrote_file(self, fake_open, 'zcl_hello_world.clas.testclasses.abap', '* tests', fileno=4)
        self.assertEqual(fake_open.mock_calls[16], call('zcl_hello_world.clas.xml', 'w', encoding='utf8'))

        args, kwargs = fake_writer.call_args
        ag_serializer = args[0]
        self.assertEqual(ag_serializer, 'LCL_OBJECT_CLAS')

        args, kwargs = fake_writer.return_value.add.call_args
        vseoclass = args[0]
        self.assertEqual(vseoclass.CLSNAME, 'ZCL_HELLO_WORLD')
        self.assertEqual(vseoclass.VERSION, '1')
        self.assertEqual(vseoclass.LANGU, 'E')
        self.assertEqual(vseoclass.DESCRIPT, 'Cowabunga')
        self.assertEqual(vseoclass.STATE, '1')
        self.assertEqual(vseoclass.CLSCCINCL, 'X')
        self.assertEqual(vseoclass.FIXPT, 'X')
        self.assertEqual(vseoclass.UNICODE, 'X')

    @patch('sap.cli.checkout.XMLWriter')
    @patch('sap.adt.Interface.fetch')
    @patch('sap.adt.Interface.text', new_callable=PropertyMock)
    def test_checkout_interface(self, fake_text, fake_fetch, fake_writer):
        fake_writer.return_value = fake_writer
        fake_writer.add = Mock()

        fake_conn = Connection()

        fake_inst = sap.adt.Interface(fake_conn, 'ZIF_HELLO_WORLD')
        fake_inst.description = 'This is an interface'
        fake_inst.master_language = 'EN'
        fake_inst.active = 'active'
        fake_inst.modeled = 'false'

        fake_text.return_value = 'interface zif_hello_world'

        args = parse_args(['interface', 'ZIF_HELLO_WORLD'])
        with patch('sap.adt.Interface') as fake_intf, \
             patch('sap.cli.checkout.open', mock_open()) as fake_open:
            fake_intf.return_value = fake_inst
            args.execute(fake_conn, args)

        assert_wrote_file(self, fake_open, 'zif_hello_world.intf.abap', 'interface zif_hello_world')

        args, kwargs = fake_writer.call_args
        ag_serializer = args[0]
        self.assertEqual(ag_serializer, 'LCL_OBJECT_INTF')

        args, kwargs = fake_writer.add.call_args
        vseointerf = args[0]
        self.assertEqual(vseointerf.CLSNAME, 'ZIF_HELLO_WORLD')
        self.assertEqual(vseointerf.VERSION, '1')
        self.assertEqual(vseointerf.LANGU, 'E')
        self.assertEqual(vseointerf.DESCRIPT, 'This is an interface')
        self.assertEqual(vseointerf.EXPOSURE, '2')
        self.assertEqual(vseointerf.STATE, '1')
        self.assertEqual(vseointerf.UNICODE, 'X')

    @patch('sap.cli.checkout.XMLWriter')
    @patch('sap.adt.Program')
    def test_checkout_program(self, fake_program, fake_writer):
        fake_inst = Mock()
        fake_inst.name = 'Z_HELLO_WORLD'
        fake_inst.description = 'Cowabunga'
        fake_inst.text = 'REPORT z_hello_world'
        fake_inst.active = 'active'
        fake_inst.application_database = 'S'
        fake_inst.program_type = '1'
        fake_inst.fix_point_arithmetic = True
        fake_inst.logical_database = Mock()
        fake_inst.logical_database.reference = Mock()
        fake_inst.logical_database.reference.name = 'D$S'

        fake_inst.fetch = Mock()

        fake_program.return_value = fake_inst

        added = list()
        def collect_abap(abap):
            added.append(abap)

        fake_inst = Mock()
        fake_inst.add = Mock()
        fake_inst.add.side_effect = collect_abap
        fake_inst.close = Mock()

        fake_writer.return_value = fake_inst

        conn = Connection()
        args = parse_args(['program', 'Z_HELLO_WORLD'])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open:
            args.execute(conn, args)

        assert_wrote_file(self, fake_open, 'z_hello_world.prog.abap', 'REPORT z_hello_world')

        fake_program.assert_called_once_with(conn, 'Z_HELLO_WORLD')
        fake_program.return_value.fetch.assert_called_once_with()

        args, kwargs = fake_writer.call_args
        ag_serializer = args[0]
        self.assertEqual(ag_serializer, 'LCL_OBJECT_PROG')

        progdir = added[0]
        tpool = added[1]

        self.assertEqual(progdir.NAME, 'Z_HELLO_WORLD')
        self.assertEqual(progdir.STATE, 'A')
        self.assertEqual(progdir.VARCL, 'X')
        self.assertEqual(progdir.DBAPL, 'S')
        self.assertEqual(progdir.SUBC, '1')
        self.assertEqual(progdir.FIXPT, 'X')
        self.assertEqual(progdir.LDBNAME, 'D$S')
        self.assertEqual(progdir.UCCHECK, 'X')

        self.assertEqual(len(tpool), 1)
        item = tpool[0]
        self.assertEqual(item.ID, 'R')
        self.assertEqual(item.ENTRY, 'Cowabunga')
        self.assertEqual(item.LENGTH, len('Cowabunga'))


class TestCheckoutClass(unittest.TestCase):

    @patch('sap.adt.Class')
    def test_build_class_attributes(self, fake_class):
        fake_inst = Mock()
        fake_inst.name = 'ZCL_HELLO_WORLD'
        fake_inst.description = 'Cowabunga'
        fake_inst.master_language = 'EN'
        fake_inst.active = 'inactive'
        fake_inst.modeled = True
        fake_inst.fix_point_arithmetic = False

        vseoclass = sap.cli.checkout.build_class_abap_attributes(fake_inst)

        self.assertEqual(vseoclass.CLSNAME, 'ZCL_HELLO_WORLD')
        self.assertEqual(vseoclass.VERSION, '0')
        self.assertEqual(vseoclass.LANGU, 'E')
        self.assertEqual(vseoclass.DESCRIPT, 'Cowabunga')
        self.assertEqual(vseoclass.STATE, '0')
        self.assertEqual(vseoclass.CLSCCINCL, 'X')
        self.assertEqual(vseoclass.FIXPT, ' ')
        self.assertEqual(vseoclass.UNICODE, 'X')


class TestCheckoutInterface(unittest.TestCase):

    def test_build_interface_attributes(self):
        fake_conn = Mock()
        intf = sap.adt.Interface(fake_conn, 'ZIF_HELLO_WORLD')

        fake_inst = sap.adt.Interface(fake_conn, 'ZIF_HELLO_WORLD')
        fake_inst.description = 'This is an interface'
        fake_inst.master_language = 'EN'
        fake_inst.active = 'inactive'
        fake_inst.modeled = 'true'

        vseointerf = sap.cli.checkout.build_interface_abap_attributes(fake_inst)

        self.assertEqual(vseointerf.CLSNAME, 'ZIF_HELLO_WORLD')
        self.assertEqual(vseointerf.DESCRIPT, 'This is an interface')
        self.assertEqual(vseointerf.LANGU, 'E')
        self.assertEqual(vseointerf.EXPOSURE, '2')
        self.assertEqual(vseointerf.VERSION, '0')
        self.assertEqual(vseointerf.STATE, '0')
        self.assertEqual(vseointerf.UNICODE, 'X')


class TestCheckoutProgram(unittest.TestCase):

    def test_build_program_attributes(self):
        fake_conn = Mock()
        prog = sap.adt.Program(fake_conn, 'ZHELLO_WORLD')
        prog.description = 'Say hello!'
        prog.active = 'inactive'
        prog.fix_point_arithmetic = False
        prog.logical_database.reference.name = 'HANA'
        prog.program_type = 'executableProgram'

        progdir, tpool = sap.cli.checkout.build_program_abap_attributes(prog)

        self.assertEqual(progdir.NAME, 'ZHELLO_WORLD')
        self.assertEqual(progdir.STATE, 'S')
        self.assertEqual(progdir.DBAPL, 'S')
        self.assertEqual(progdir.VARCL, 'X')
        self.assertEqual(progdir.SUBC, '1')
        self.assertEqual(progdir.LDBNAME, 'HANA')
        self.assertEqual(progdir.UCCHECK, 'X')

        self.assertEqual(['DBNA', 'RLOAD', 'RSTAT'], sorted([attr for attr, value in progdir.__dict__.items() if not attr.startswith('_') and value is None]))

        self.assertEqual(len(tpool), 1)
        descr = tpool[0]
        self.assertEqual(descr.ID, 'R')
        self.assertEqual(descr.ENTRY, 'Say hello!')
        self.assertEqual(descr.LENGTH, len('Say hello!'))


class TestCheckoutPackage(unittest.TestCase):

    @patch('sap.adt.Package.fetch')
    @patch('sap.cli.checkout.dump_attributes_to_file')
    @patch('sap.cli.checkout.checkout_class')
    @patch('sap.cli.checkout.checkout_interface')
    @patch('sap.cli.checkout.checkout_program')
    @patch('sap.adt.package.walk')
    def test_checkout_package_recursive(self, fake_walk, fake_prog, fake_intf, fake_clas, fake_dump, fake_fetch):
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

        package_factory = sap.adt.Package
        def new_package(connection, name):
            package = package_factory(connection, name)
            package.description = f'Description {name}'
            return package

        args = parse_args(['package', package_name, '--recursive'])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open, \
             patch('sap.cli.checkout.print') as fake_print, \
             patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs, \
             patch('sap.adt.Package') as fake_package:

            fake_package.side_effect = new_package

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

        self.assertEqual(fake_fetch.mock_calls, [call(), call()])
        self.assertEqual(fake_dump.mock_calls, [call('package',
                                                     (sap.platform.abap.ddic.DEVC(CTEXT='Description $VICTORY'),),
                                                     '.devc',
                                                     'LCL_OBJECT_DEVC',
                                                     destdir=exp_destdir),
                                                call('package',
                                                     (sap.platform.abap.ddic.DEVC(CTEXT='Description $VICTORY_TESTS'),),
                                                     '.devc',
                                                     'LCL_OBJECT_DEVC',
                                                     destdir=exp_sub_destdir)
                                                ])

    @patch('sap.cli.checkout.checkout_package')
    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_non_recursive(self, fake_walk, fake_checkout, fake_package):
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

    @patch('sap.cli.checkout.checkout_package')
    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_starting_folder(self, fake_walk, fake_checkout, fake_package):
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

    @patch('sap.platform.abap.to_xml')
    @patch('sap.cli.checkout.checkout_package')
    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_create_repo(self, fake_walk, fake_checkout, fake_package, fake_to_xml):
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
        args, kwargs = fake_to_xml.call_args
        dot_abap = args[0]

        self.assertEqual(dot_abap.MASTER_LANGUAGE, 'E')
        self.assertEqual(dot_abap.FOLDER_LOGIC, sap.platform.abap.abapgit.FOLDER_LOGIC_FULL)
        self.assertEqual(dot_abap.STARTING_FOLDER, f'/{starting_folder}/')
        self.assertEqual([ignore for ignore in dot_abap.IGNORE], ['/.gitignore', '/LICENSE', '/README.md', '/package.json', '/.travis.yml'])
        self.assertEqual(kwargs['top_element'], 'DATA')

    @patch('sap.cli.checkout.checkout_package')
    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_custom_repo_dir(self, fake_walk, fake_checkout, fake_package):
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


class TestDOT_ABAP_GIT(unittest.TestCase):

    def test_for_empty_repo(self):
        dot_abap = sap.cli.checkout.DOT_ABAP_GIT.for_new_repo(STARTING_FOLDER='foo')
        dest = StringIO()
        sap.platform.abap.to_xml(dot_abap, dest=dest)
        self.maxDiff = None
        self.assertEqual(dest.getvalue(), '''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <DOT_ABAP_GIT>
   <MASTER_LANGUAGE>E</MASTER_LANGUAGE>
   <STARTING_FOLDER>foo</STARTING_FOLDER>
   <FOLDER_LOGIC>FULL</FOLDER_LOGIC>
   <IGNORE>
    <item>/.gitignore</item>
    <item>/LICENSE</item>
    <item>/README.md</item>
    <item>/package.json</item>
    <item>/.travis.yml</item>
   </IGNORE>
  </DOT_ABAP_GIT>
 </asx:values>
</asx:abap>
''')


if __name__ == '__main__':
    unittest.main()
