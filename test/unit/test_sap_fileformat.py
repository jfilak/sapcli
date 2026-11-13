#!/usr/bin/env python3

import unittest

import sap.errors
import sap.fileformat
from sap.fileformat import (
    ObjectHandler,
    RepositoryLayout,
    HandlerRegistry,
    RepoPackage,
    RepoObject,
    Repository,
    CheckinContext,
    ObjectCheckinResult,
)


class CompleteHandler(ObjectHandler):
    """Handler implementing everything"""

    FILE_TYPE = 'clas'
    METADATA_EXT = 'xml'
    ADT_TYPES = ('CLAS/OC',)

    def checkout(self, connection, adt_type, name, destdir):
        return 'checkout'

    def prepare(self, repo_obj):
        return 'prepare'

    def checkin(self, context, repo_obj, prepared):
        return 'checkin'

    def locate(self, repo_obj, part, line):
        return None


class JsonClassHandler(CompleteHandler):
    """The same object type in another serialization"""

    METADATA_EXT = 'json'


class TableHandler(CompleteHandler):
    """Handler of several ADT types"""

    FILE_TYPE = 'tabl'
    ADT_TYPES = ('TABL/DT', 'TABL/DS')


class TestObjectHandler(unittest.TestCase):

    def test_complete_handler_can_be_instantiated(self):
        handler = CompleteHandler()

        self.assertEqual(handler.FILE_TYPE, 'clas')
        self.assertEqual(handler.METADATA_EXT, 'xml')
        self.assertEqual(handler.ADT_TYPES, ('CLAS/OC',))

    def test_missing_checkout(self):
        class Handler(CompleteHandler):
            checkout = ObjectHandler.checkout

        with self.assertRaises(TypeError) as caught:
            Handler()

        self.assertIn('checkout', str(caught.exception))

    def test_missing_prepare(self):
        class Handler(CompleteHandler):
            prepare = ObjectHandler.prepare

        with self.assertRaises(TypeError) as caught:
            Handler()

        self.assertIn('prepare', str(caught.exception))

    def test_missing_checkin(self):
        class Handler(CompleteHandler):
            checkin = ObjectHandler.checkin

        with self.assertRaises(TypeError) as caught:
            Handler()

        self.assertIn('checkin', str(caught.exception))

    def test_missing_locate(self):
        class Handler(CompleteHandler):
            locate = ObjectHandler.locate

        with self.assertRaises(TypeError) as caught:
            Handler()

        self.assertIn('locate', str(caught.exception))

    def test_missing_file_type(self):
        class Handler(CompleteHandler):
            FILE_TYPE = None

        with self.assertRaises(TypeError) as caught:
            Handler()

        self.assertEqual(str(caught.exception), 'Handler does not define FILE_TYPE')

    def test_missing_metadata_ext(self):
        class Handler(CompleteHandler):
            METADATA_EXT = None

        with self.assertRaises(TypeError) as caught:
            Handler()

        self.assertEqual(str(caught.exception), 'Handler does not define METADATA_EXT')

    def test_missing_adt_types(self):
        class Handler(CompleteHandler):
            ADT_TYPES = ()

        with self.assertRaises(TypeError) as caught:
            Handler()

        self.assertEqual(str(caught.exception), 'Handler does not define ADT_TYPES')

    def test_attributes_not_defined_at_all(self):
        class Handler(ObjectHandler):

            def checkout(self, connection, adt_type, name, destdir):
                pass

            def prepare(self, repo_obj):
                pass

            def checkin(self, context, repo_obj, prepared):
                pass

            def locate(self, repo_obj, part, line):
                pass

        with self.assertRaises(TypeError) as caught:
            Handler()

        self.assertEqual(str(caught.exception), 'Handler does not define FILE_TYPE')


class CompleteLayout(RepositoryLayout):
    """Layout implementing everything"""

    def load_repository(self, starting_folder, registry):
        return 'repository'

    def package_name(self, repository, repo_package, root_package_name):
        return 'package name'

    def prepare_package(self, repo_package):
        return 'prepared'

    def init_repository(self, repo_dir, starting_folder):
        return 'init'

    def checkout_package(self, connection, name, destdir):
        return 'checkout'


class TestRepositoryLayout(unittest.TestCase):

    def test_complete_layout_can_be_instantiated(self):
        layout = CompleteLayout()

        self.assertEqual(layout.load_repository('/src/', None), 'repository')

    def test_missing_load_repository(self):
        class Layout(CompleteLayout):
            load_repository = RepositoryLayout.load_repository

        with self.assertRaises(TypeError) as caught:
            Layout()

        self.assertIn('load_repository', str(caught.exception))

    def test_missing_package_name(self):
        class Layout(CompleteLayout):
            package_name = RepositoryLayout.package_name

        with self.assertRaises(TypeError) as caught:
            Layout()

        self.assertIn('package_name', str(caught.exception))

    def test_missing_prepare_package(self):
        class Layout(CompleteLayout):
            prepare_package = RepositoryLayout.prepare_package

        with self.assertRaises(TypeError) as caught:
            Layout()

        self.assertIn('prepare_package', str(caught.exception))

    def test_missing_init_repository(self):
        class Layout(CompleteLayout):
            init_repository = RepositoryLayout.init_repository

        with self.assertRaises(TypeError) as caught:
            Layout()

        self.assertIn('init_repository', str(caught.exception))

    def test_missing_checkout_package(self):
        class Layout(CompleteLayout):
            checkout_package = RepositoryLayout.checkout_package

        with self.assertRaises(TypeError) as caught:
            Layout()

        self.assertIn('checkout_package', str(caught.exception))


class TestHandlerRegistry(unittest.TestCase):

    def setUp(self):
        self.xml_class = CompleteHandler()
        self.json_class = JsonClassHandler()
        self.table = TableHandler()

        self.registry = HandlerRegistry((self.json_class, self.xml_class, self.table))

    def test_for_metadata_file_xml(self):
        self.assertIs(self.registry.for_metadata_file('clas', 'xml'), self.xml_class)

    def test_for_metadata_file_json(self):
        self.assertIs(self.registry.for_metadata_file('clas', 'json'), self.json_class)

    def test_for_metadata_file_unknown_type(self):
        self.assertIsNone(self.registry.for_metadata_file('prog', 'xml'))

    def test_for_metadata_file_unknown_ext(self):
        self.assertIsNone(self.registry.for_metadata_file('tabl', 'json'))

    def test_for_adt_type_first_wins(self):
        self.assertIs(self.registry.for_adt_type('CLAS/OC'), self.json_class)

    def test_for_adt_type_reversed_priority(self):
        registry = HandlerRegistry((self.xml_class, self.json_class))

        self.assertIs(registry.for_adt_type('CLAS/OC'), self.xml_class)

    def test_for_adt_type_all_codes_of_handler(self):
        self.assertIs(self.registry.for_adt_type('TABL/DT'), self.table)
        self.assertIs(self.registry.for_adt_type('TABL/DS'), self.table)

    def test_for_adt_type_unknown(self):
        self.assertIsNone(self.registry.for_adt_type('PROG/P'))

    def test_empty_registry(self):
        registry = HandlerRegistry(())

        self.assertIsNone(registry.for_metadata_file('clas', 'xml'))
        self.assertIsNone(registry.for_adt_type('CLAS/OC'))

    def test_duplicate_metadata_file(self):
        with self.assertRaises(sap.errors.SAPCliError) as caught:
            HandlerRegistry((self.xml_class, self.table, CompleteHandler()))

        self.assertEqual(str(caught.exception),
                         'Duplicate object handlers of the files *.clas.xml: CompleteHandler and CompleteHandler')


class TestData(unittest.TestCase):

    def test_repo_package(self):
        root = RepoPackage(dir_path='./src', path='./src/package.devc.xml', parent=None)
        sub = RepoPackage('./src/sub', './src/sub/package.devc.xml', root)

        self.assertEqual(root.dir_path, './src')
        self.assertEqual(root.path, './src/package.devc.xml')
        self.assertIsNone(root.parent)
        self.assertIs(sub.parent, root)

    def test_repo_object(self):
        package = RepoPackage('./src', './src/package.devc.xml', None)
        handler = CompleteHandler()

        obj = RepoObject(code='clas', name='zcl_foo', path='./src/zcl_foo.clas.xml',
                         files=['./src/zcl_foo.clas.xml', './src/zcl_foo.clas.abap'],
                         package=package, handler=handler)

        self.assertEqual(obj.code, 'clas')
        self.assertEqual(obj.name, 'zcl_foo')
        self.assertEqual(obj.path, './src/zcl_foo.clas.xml')
        self.assertEqual(obj.files, ['./src/zcl_foo.clas.xml', './src/zcl_foo.clas.abap'])
        self.assertIs(obj.package, package)
        self.assertIs(obj.handler, handler)

    def test_repository(self):
        repo = Repository(packages=['package'], objects=['object'], files=['file'], settings='settings')

        self.assertEqual(repo.packages, ['package'])
        self.assertEqual(repo.objects, ['object'])
        self.assertEqual(repo.files, ['file'])
        self.assertEqual(repo.settings, 'settings')

    def test_checkin_context(self):
        context = CheckinContext(connection='connection', package_name='ZPKG', corrnr='K900001',
                                 check_before_save=True)

        self.assertEqual(context.connection, 'connection')
        self.assertEqual(context.package_name, 'ZPKG')
        self.assertEqual(context.corrnr, 'K900001')
        self.assertTrue(context.check_before_save)

    def test_object_checkin_result(self):
        result = ObjectCheckinResult(abap_objects=['object'], used_files=['file'])

        self.assertEqual(result.abap_objects, ['object'])
        self.assertEqual(result.used_files, ['file'])


if __name__ == '__main__':
    unittest.main()
