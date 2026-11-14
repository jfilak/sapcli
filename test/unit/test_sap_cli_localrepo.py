#!/usr/bin/env python3

import unittest
from unittest.mock import patch

import sap.cli.localrepo
import sap.platform.abap.abapgit.handlers
from sap.errors import SAPCliError
from sap.platform.abap.localrepository import HandlerRegistry, RepositoryLayout, RepositoryObserver

from mock import ConsoleOutputTestCase


class TestFormats(unittest.TestCase):

    def test_object_handlers(self):
        self.assertIsInstance(sap.cli.localrepo.OBJECT_HANDLERS, HandlerRegistry)
        self.assertIs(sap.cli.localrepo.OBJECT_HANDLERS.for_metadata_file('clas', 'xml'),
                      sap.platform.abap.abapgit.handlers.HANDLERS[0])

    def test_repository_layout(self):
        self.assertIsInstance(sap.cli.localrepo.REPOSITORY_LAYOUT, RepositoryLayout)


class TestConsoleObserver(ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()

        self.observer = sap.cli.localrepo.ConsoleObserver(self.console)

    def test_is_repository_observer(self):
        self.assertIsInstance(self.observer, RepositoryObserver)

    def test_checking_out(self):
        self.observer.checking_out('ZCL_FOO')

        self.assertConsoleContents(self.console, stdout='ZCL_FOO\n')

    def test_file_written(self):
        self.observer.file_written('/repo/src/zcl_foo.clas.xml')

        self.assertConsoleContents(self.console, stdout='- zcl_foo.clas.xml\n')

    def test_creating(self):
        self.observer.creating('Class', 'zcl_foo')

        self.assertConsoleContents(self.console, stdout='Creating Class: zcl_foo\n')

    def test_writing(self):
        self.observer.writing('Program', 'zreport')

        self.assertConsoleContents(self.console, stdout='Writing Program: zreport\n')

    def test_writing_part(self):
        self.observer.writing('Clas', 'zcl_foo', 'text elements')

        self.assertConsoleContents(self.console, stdout='Writing Clas: zcl_foo text elements\n')

    def test_warning(self):
        self.observer.warning('Skipping unsupported secondary keys of ZTT')

        self.assertConsoleContents(self.console, stderr='Skipping unsupported secondary keys of ZTT\n')


class LocalRepositoryTestCase(unittest.TestCase):
    """Local repository with the class FOO and the program ZREPORT"""

    def setUp(self):
        super().setUp()

        from sap.platform.abap.localrepository import RepoObject, RepoPackage, Repository

        clas_handler = sap.cli.localrepo.OBJECT_HANDLERS.for_adt_type('CLAS/OC')
        prog_handler = sap.cli.localrepo.OBJECT_HANDLERS.for_adt_type('PROG/P')

        package = RepoPackage('./src/', './src/package.devc.xml', None)
        self.clas = RepoObject('clas', 'foo', './src/foo.clas.xml',
                               ['./src/foo.clas.abap', './src/foo.clas.testclasses.abap'], package, clas_handler)
        self.prog = RepoObject('prog', 'zreport', './src/zreport.prog.xml', ['./src/zreport.prog.abap'], package,
                               prog_handler)
        self.repo = Repository([package], [self.clas, self.prog], [], None)
        self.local_objects = {('CLAS/OC', 'FOO'): self.clas, ('PROG/P', 'ZREPORT'): self.prog}


class TestLoadLocalObjects(LocalRepositoryTestCase):

    def test_repository(self):
        with patch('sap.cli.localrepo.REPOSITORY_LAYOUT') as fake_layout:
            fake_layout.load_repository.return_value = self.repo
            local_objects = sap.cli.localrepo.load_local_objects()

        fake_layout.load_repository.assert_called_once_with(None, sap.cli.localrepo.OBJECT_HANDLERS)
        self.assertEqual(local_objects, self.local_objects)

    def test_not_a_repository(self):
        with patch('sap.cli.localrepo.REPOSITORY_LAYOUT') as fake_layout:
            fake_layout.load_repository.side_effect = SAPCliError('Not a package directory: ./src/')
            local_objects = sap.cli.localrepo.load_local_objects()

        self.assertIsNone(local_objects)

    def test_unreadable_repository(self):
        with patch('sap.cli.localrepo.REPOSITORY_LAYOUT') as fake_layout:
            fake_layout.load_repository.side_effect = OSError('Permission denied')
            local_objects = sap.cli.localrepo.load_local_objects()

        self.assertIsNone(local_objects)


class TestLocateSource(LocalRepositoryTestCase):

    def test_class_main(self):
        self.assertEqual(sap.cli.localrepo.locate_source(self.local_objects, 'CLAS/OC', 'foo', 'source/main', 12),
                         ('src/foo.clas.abap', 12))

    def test_class_testclasses(self):
        self.assertEqual(
            sap.cli.localrepo.locate_source(self.local_objects, 'CLAS/OC', 'FOO', 'includes/testclasses', 3),
            ('src/foo.clas.testclasses.abap', 3))

    def test_program(self):
        self.assertEqual(sap.cli.localrepo.locate_source(self.local_objects, 'PROG/P', 'ZREPORT', 'source/main', 7),
                         ('src/zreport.prog.abap', 7))

    def test_no_repository(self):
        self.assertIsNone(sap.cli.localrepo.locate_source(None, 'CLAS/OC', 'FOO', 'source/main', 12))

    def test_unknown_object(self):
        self.assertIsNone(sap.cli.localrepo.locate_source(self.local_objects, 'CLAS/OC', 'BAR', 'source/main', 12))

    def test_unknown_type(self):
        self.assertIsNone(sap.cli.localrepo.locate_source(self.local_objects, None, 'FOO', 'source/main', 12))

    def test_no_file_of_part(self):
        self.assertIsNone(
            sap.cli.localrepo.locate_source(self.local_objects, 'CLAS/OC', 'FOO', 'includes/implementations', 12))


if __name__ == '__main__':
    unittest.main()
