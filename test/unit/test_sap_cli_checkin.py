#!/usr/bin/env python3

import os
import unittest
from unittest.mock import patch
from argparse import ArgumentParser

import sap.cli.checkin


from mock import PatcherTestCase, patch_get_print_console_with_buffer


class DirContentBuilder:

    def __init__(self, path, parent=None):
        self._path = path
        self._parent = parent
        self._files = ['package.devc']
        self._dirs = list()

    def add_dir(self, name):
        self._dirs.append(name)
        child = DirContentBuilder(os.path.join(self._path, name), parent=self)
        return child

    def add_abap_class(self, name):
        self._files.append(f'{name}.clas.abap')
        self._files.append(f'{name}.clas.xml')

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

    def setUp(self):
        simple_root = DirContentBuilder('.').add_abap_class('cl_foo')
        simple_sub = simple_root.add_dir('sub').add_abap_class('cl_bar')
        simple_grand = simple_sub.add_dir('grand').add_abap_class('cl_grc')

        self.walk_stands = [simple_root.walk_stand(),
                            simple_sub.walk_stand(),
                            simple_grand.walk_stand()]

        self.fake_walk = self.patch('sap.cli.checkin.os.walk')
        self.fake_walk.side_effect = self.walk

        self.fake_console = self.patch_console()

    @patch('sap.cli.checkin._get_config')
    def test_foo(self, fake_config):
        fake_config.return_value = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(FOLDER_LOGIC=sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX)

        args = parse_args('$foo')
        args.execute(None, args)

        self.assertEqual(self.fake_console.return_value.capout, '''$foo
$foo_sub
$foo_sub_grand
''')


if __name__ == '__main__':
    unittest.main()

