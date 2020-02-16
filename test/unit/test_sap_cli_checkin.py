#!/usr/bin/env python3

import os
import unittest
import fnmatch
from types import SimpleNamespace
from unittest.mock import patch, Mock
from argparse import ArgumentParser

import sap.cli.checkin
from sap import get_logger

from mock import PatcherTestCase, patch_get_print_console_with_buffer


class DirContentBuilder:

    def __init__(self, path, parent=None):
        self._path = path
        self._parent = parent
        self._files = ['package.devc.xml']
        self._dirs = list()

    def files(self):
        return [os.path.join(self._path, filename) for filename in self._files]

    def add_dir(self, name):
        self._dirs.append(name)
        child = DirContentBuilder(os.path.join(self._path, name), parent=self)
        return child

    def add_abap_class(self, name):
        self._files.append(f'{name}.clas.abap')
        self._files.append(f'{name}.clas.xml')

        return self

    def add_abap_interface(self, name):
        self._files.append(f'{name}.intf.abap')
        self._files.append(f'{name}.intf.xml')

        return self

    def add_abap_program(self, name):
        self._files.append(f'{name}.prog.abap')
        self._files.append(f'{name}.prog.xml')

        return self

    def walk_stand(self):
        return (self._path, self._dirs, self._files)


def parse_args(*argv):
    parser = ArgumentParser()
    sap.cli.checkin.CommandGroup().install_parser(parser)
    return parser.parse_args(argv)


class TestCheckIn(unittest.TestCase, PatcherTestCase):

    def walk(self, name):
        for stand in self.walk_stands:
            yield stand

    def is_file(self, path):
        return path in self.files

    def glob(self, pattern):
        return [name for name in self.files if fnmatch.fnmatch(name, pattern)]

    def setUp(self):
        simple_root = DirContentBuilder('./src/').add_abap_program('run_report')
        simple_sub = simple_root.add_dir('sub').add_abap_interface('if_strategy')
        simple_grand = simple_sub.add_dir('grand').add_abap_class('cl_implementor')

        self.walk_stands = [simple_root.walk_stand(),
                            simple_sub.walk_stand(),
                            simple_grand.walk_stand()]

        self.fake_walk = self.patch('sap.cli.checkin.os.walk')
        self.fake_walk.side_effect = self.walk

        self.files = simple_root.files() + simple_sub.files() + simple_grand.files()

        self.fake_is_file = self.patch('sap.cli.checkin.os.path.isfile')
        self.fake_is_file.side_effect = self.is_file

        self.fake_glob = self.patch('sap.cli.checkin.glob.glob')
        self.fake_glob.side_effect = self.glob

        get_logger().debug('Test files: %s', ','.join(self.files))

        self.fake_console = self.patch_console()

    @patch('sap.cli.checkin._get_config')
    @patch('sap.cli.checkin.checkin_package')
    def test_do_checkin_sanity(self, fake_checkin, fake_config):
        fake_config.return_value = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(FOLDER_LOGIC=sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX)

        # open -> .abapgit.xml

        def mock_object_handler(connection, repo_obj):
            return SimpleNamespace(full_adt_uri=repo_obj.path, name=repo_obj.name)

        args = parse_args('$foo')
        with patch('sap.cli.checkin.OBJECT_CHECKIN_HANDLERS') as fake_handler, \
             patch('sap.adt.wb.try_mass_activate') as fake_activate:
            fake_handler.get = Mock()
            fake_handler.get.return_value = mock_object_handler

            fake_activate.return_value = []

            args.execute(None, args)

        #TODO: _get_config asserts

    def test_repo_add_object_unsupported(self):
        repo = sap.cli.checkin.Repository('unittest', sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo())

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            repo.add_object('log.txt', None)

        self.assertEqual(str(caught.exception), 'Invalid ABAP file name: log.txt')

    def test_repo_package_dir_outside(self):

        pass

    def test_repo_package_dir_wrong_name(self):

        pass

    def test_load_objects(self):

        pass

    def test_get_config_noent(self):

        pass

    def test_get_config_noperm(self):

        pass

    def test_get_config_overwrites(self):

        pass

    def test_get_config_simple(self):

        pass

    def test_resolve_dependencies(self):

        pass

    def test_checkin_group_none_handler(self):

        pass

    def test_checkin_group_none_resp(self):

        pass

    def test_checkin_group_simple(self):

        pass

    def test_activate_no_messages(self):

        pass

    def test_activate_no_error(self):

        pass

    def test_activate_error(self):

        pass


class TestCheckInPackage(unittest.TestCase, PatcherTestCase):

    pass


class TestCheckInClass(unittest.TestCase, PatcherTestCase):

    pass


class TestCheckInInterface(unittest.TestCase, PatcherTestCase):

    pass


class TestCheckInProgram(unittest.TestCase, PatcherTestCase):

    pass


class TestCheckInFunctionGroup(unittest.TestCase, PatcherTestCase):

    pass


if __name__ == '__main__':
    unittest.main()

