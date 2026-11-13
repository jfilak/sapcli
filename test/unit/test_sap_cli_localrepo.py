#!/usr/bin/env python3

import unittest
from unittest.mock import patch

import sap.cli.localrepo
import sap.fileformat.abapgit
from sap.errors import SAPCliError
from sap.fileformat import HandlerRegistry, RepositoryLayout


class TestFormats(unittest.TestCase):

    def test_object_handlers(self):
        self.assertIsInstance(sap.cli.localrepo.OBJECT_HANDLERS, HandlerRegistry)
        self.assertIs(sap.cli.localrepo.OBJECT_HANDLERS.for_metadata_file('clas', 'xml'),
                      sap.fileformat.abapgit.HANDLERS[0])

    def test_repository_layout(self):
        self.assertIsInstance(sap.cli.localrepo.REPOSITORY_LAYOUT, RepositoryLayout)


class LocalRepositoryTestCase(unittest.TestCase):
    """Local repository with the class FOO and the program ZREPORT"""

    def setUp(self):
        super().setUp()

        from sap.fileformat import RepoObject, RepoPackage, Repository

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
