#!/usr/bin/env python3

import errno
import os
import unittest
from unittest.mock import Mock, call, mock_open, patch

import sap.errors
import sap.platform.abap.abapgit.handlers
import sap.platform.abap.abapgit.layout as layout
import sap.platform.abap.abapgit
import sap.platform.abap.ddic
from sap.errors import SAPCliError
from sap.platform.abap.localrepository import HandlerRegistry, RepoObject, RepoPackage, Repository, RepositoryLayout
from sap.platform.abap.abapgit.layout import AbapGitLayout
from sap.platform.abap.abapgit import DOT_ABAP_GIT, FOLDER_LOGIC_FULL, FOLDER_LOGIC_PREFIX

from mock import PatcherTestCase, StringIOFile
from fixtures_abap import ABAP_GIT_DEFAULT_XML
from fixtures_sap_platform_abap_abapgit_layout import PACKAGE_DEVC_XML, PACKAGE_DEVC_LANGUAGE_XML, \
    PACKAGE_DEVC_UNKNOWN_XML

REGISTRY = HandlerRegistry(sap.platform.abap.abapgit.handlers.HANDLERS)


class DirContentBuilder:
    """Builds the results of os.walk"""

    def __init__(self, path):
        self._path = path
        self._files = ['package.devc.xml']
        self._dirs = []

    def files(self):
        return [os.path.join(self._path, filename) for filename in self._files]

    def add_dir(self, name):
        self._dirs.append(name)
        return DirContentBuilder(os.path.join(self._path, name))

    def add_file(self, name):
        self._files.append(name)
        return self

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

    def add_abap_function_group(self, name):
        self._files.append(f'{name}.fugr.xml')
        self._files.append(f'{name}.fugr.module.abap')
        self._files.append(f'{name}.fugr.include.xml')
        self._files.append(f'{name}.fugr.include.abap')
        return self

    def add_data_definition(self, name):
        self._files.append(f'{name}.ddls.asddls')
        self._files.append(f'{name}.ddls.baseinfo')
        self._files.append(f'{name}.ddls.xml')
        return self

    def walk_stand(self):
        return self._path, self._dirs, self._files


class LayoutTestCase(unittest.TestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def setUp(self):
        super().setUp()

        self.layout = AbapGitLayout()

    def tearDown(self):
        try:
            self.unpatch_all()
        finally:
            super().tearDown()


class TestAbapGitLayout(unittest.TestCase):

    def test_is_repository_layout(self):
        self.assertIsInstance(AbapGitLayout(), RepositoryLayout)


class TestLoadSettings(LayoutTestCase):

    def test_no_file(self):
        self.patch('sap.platform.abap.abapgit.layout.open', side_effect=OSError(errno.ENOENT, 'No such file'))

        settings = layout.load_settings('/backend/')

        self.assertEqual(settings, DOT_ABAP_GIT.for_new_repo(STARTING_FOLDER='/backend/'))

    def test_no_file_default_starting_folder(self):
        self.patch('sap.platform.abap.abapgit.layout.open', side_effect=OSError(errno.ENOENT, 'No such file'))

        settings = layout.load_settings(None)

        self.assertEqual(settings, DOT_ABAP_GIT.for_new_repo())

    def test_no_permissions(self):
        self.patch('sap.platform.abap.abapgit.layout.open', side_effect=OSError(errno.EPERM))

        with self.assertRaises(OSError):
            layout.load_settings('/backend/')


    def test_file_overwrites_starting_folder(self):
        fake_open = self.patch('sap.platform.abap.abapgit.layout.open', new=mock_open(read_data=ABAP_GIT_DEFAULT_XML))

        settings = layout.load_settings('/backend/')

        fake_open.assert_called_once_with('.abapgit.xml', 'r', encoding='utf-8')
        self.assertEqual(settings.STARTING_FOLDER, '/src/')
        self.assertEqual(settings.FOLDER_LOGIC, FOLDER_LOGIC_PREFIX)

    def test_file_with_the_same_starting_folder(self):
        self.patch('sap.platform.abap.abapgit.layout.open', new=mock_open(read_data=ABAP_GIT_DEFAULT_XML))

        settings = layout.load_settings('/src/')

        self.assertEqual(settings.STARTING_FOLDER, '/src/')


class TestLoadRepository(LayoutTestCase):

    def setUp(self):
        super().setUp()

        self.settings = DOT_ABAP_GIT.for_new_repo()
        self.fake_load_settings = self.patch('sap.platform.abap.abapgit.layout.load_settings',
                                             return_value=self.settings)

        root = DirContentBuilder('./src/').add_abap_program('run_report').add_abap_function_group('test_fugr')
        sub = root.add_dir('sub').add_abap_interface('if_strategy')
        grand = sub.add_dir('grand').add_abap_class('cl_implementor')
        self.set_directories(root, sub, grand)

        self.fake_walk = self.patch('sap.platform.abap.abapgit.layout.os.walk')
        self.fake_walk.side_effect = lambda path: iter(self.walk_stands)

        self.fake_is_file = self.patch('sap.platform.abap.abapgit.layout.os.path.isfile')
        self.fake_is_file.side_effect = lambda path: path in self.files

    def set_directories(self, *directories):
        self.walk_stands = [directory.walk_stand() for directory in directories]
        self.files = []
        for directory in directories:
            self.files += directory.files()

    def test_load_repository(self):
        repo = self.layout.load_repository(None, REGISTRY)

        self.assertIsInstance(repo, Repository)
        self.fake_load_settings.assert_called_once_with(None)
        self.fake_walk.assert_called_once_with('./src/')
        self.assertIs(repo.settings, self.settings)
        self.assertEqual(repo.starting_folder, '/src/')
        self.assertEqual(repo.files, self.files)

        root = RepoPackage('./src/', './src/package.devc.xml', None)
        sub = RepoPackage('./src/sub', './src/sub/package.devc.xml', root)
        grand = RepoPackage('./src/sub/grand', './src/sub/grand/package.devc.xml', sub)
        self.assertEqual(repo.packages, [root, sub, grand])

        self.assertEqual(repo.objects, [
            RepoObject('prog', 'run_report', './src/run_report.prog.xml', ['./src/run_report.prog.abap'], root,
                       REGISTRY.for_metadata_file('prog', 'xml')),
            RepoObject('fugr', 'test_fugr', './src/test_fugr.fugr.xml',
                       ['./src/test_fugr.fugr.module.abap', './src/test_fugr.fugr.include.abap'], root,
                       REGISTRY.for_metadata_file('fugr', 'xml')),
            RepoObject('intf', 'if_strategy', './src/sub/if_strategy.intf.xml', ['./src/sub/if_strategy.intf.abap'],
                       sub, REGISTRY.for_metadata_file('intf', 'xml')),
            RepoObject('clas', 'cl_implementor', './src/sub/grand/cl_implementor.clas.xml',
                       ['./src/sub/grand/cl_implementor.clas.abap'], grand,
                       REGISTRY.for_metadata_file('clas', 'xml')),
        ])

    def test_load_repository_starting_folder(self):
        self.settings.STARTING_FOLDER = '/backend/src/'
        root = DirContentBuilder('./backend/src/').add_abap_program('run_report')
        self.set_directories(root)

        repo = self.layout.load_repository('/backend/src/', REGISTRY)

        self.fake_load_settings.assert_called_once_with('/backend/src/')
        self.fake_walk.assert_called_once_with('./backend/src/')
        self.assertEqual([package.dir_path for package in repo.packages], ['./backend/src/'])
        self.assertEqual([obj.path for obj in repo.objects], ['./backend/src/run_report.prog.xml'])

    def test_load_repository_data_definition(self):
        self.set_directories(DirContentBuilder('./src/').add_data_definition('zcds'))

        repo = self.layout.load_repository(None, REGISTRY)

        self.assertEqual([(obj.code, obj.name, obj.path, obj.files) for obj in repo.objects],
                         [('ddls', 'zcds', './src/zcds.ddls.xml',
                           ['./src/zcds.ddls.asddls', './src/zcds.ddls.baseinfo'])])

    def test_load_repository_other_files_are_not_objects(self):
        root = DirContentBuilder('./src/').add_abap_program('run_report').add_file('README') \
            .add_file('zsearch_help.shlp.xml').add_file('run_report_2.prog.abap')
        self.set_directories(root)

        repo = self.layout.load_repository(None, REGISTRY)

        self.assertEqual([obj.name for obj in repo.objects], ['run_report'])
        self.assertEqual(repo.objects[0].files, ['./src/run_report.prog.abap'])
        self.assertEqual(repo.files, ['./src/package.devc.xml', './src/run_report.prog.abap',
                                      './src/run_report.prog.xml', './src/README', './src/zsearch_help.shlp.xml',
                                      './src/run_report_2.prog.abap'])

    def test_load_repository_registry_decides(self):
        handler = Mock(FILE_TYPE='prog', METADATA_EXT='xml', ADT_TYPES=('PROG/P',))

        repo = self.layout.load_repository(None, HandlerRegistry((handler,)))

        self.assertEqual([obj.name for obj in repo.objects], ['run_report'])
        self.assertIs(repo.objects[0].handler, handler)

    def test_load_repository_file_name_without_object_name(self):
        self.set_directories(DirContentBuilder('./src/').add_file('clas.xml'))

        with self.assertRaises(SAPCliError) as caught:
            self.layout.load_repository(None, REGISTRY)

        self.assertEqual(str(caught.exception), 'Invalid ABAP file name: clas.xml')

    def test_load_repository_file_name_with_too_many_parts(self):
        self.set_directories(DirContentBuilder('./src/').add_file('zcl.foo.clas.xml'))

        with self.assertRaises(SAPCliError) as caught:
            self.layout.load_repository(None, REGISTRY)

        self.assertEqual(str(caught.exception), 'Invalid ABAP file name: zcl.foo.clas.xml')

    def test_load_repository_not_a_package_dir(self):
        self.files = []

        with self.assertRaises(SAPCliError) as caught:
            self.layout.load_repository(None, REGISTRY)

        self.assertEqual(str(caught.exception), 'Not a package directory: ./src/')

    def test_load_repository_sub_dir_not_a_package_dir(self):
        self.files.remove('./src/sub/package.devc.xml')

        with self.assertRaises(SAPCliError) as caught:
            self.layout.load_repository(None, REGISTRY)

        self.assertEqual(str(caught.exception), 'Not a package directory: ./src/sub')

    def test_load_repository_wrong_starting_folder(self):
        self.settings.STARTING_FOLDER = './foo'

        with self.assertRaises(SAPCliError) as caught:
            self.layout.load_repository(None, REGISTRY)

        self.assertEqual(str(caught.exception), 'Package dirs must start with "./": ../foo')
        self.fake_walk.assert_not_called()


class TestPackageName(unittest.TestCase):

    def setUp(self):
        self.layout = AbapGitLayout()

    def package_name(self, dir_path, root_package_name='unittest', **settings):
        dot_abap_git = DOT_ABAP_GIT.for_new_repo(**settings)
        repository = Repository([], [], [], dot_abap_git, dot_abap_git.STARTING_FOLDER)
        package = RepoPackage(dir_path, os.path.join(dir_path, 'package.devc.xml'), None)

        return self.layout.package_name(repository, package, root_package_name)

    def test_root(self):
        self.assertEqual(self.package_name('./src/'), 'unittest')

    def test_root_without_trailing_slash(self):
        self.assertEqual(self.package_name('./src'), 'unittest')

    def test_root_in_deep_starting_folder(self):
        self.assertEqual(self.package_name('./src/backend/', STARTING_FOLDER='/src/backend/'), 'unittest')

    def test_full(self):
        self.assertEqual(self.package_name('./src/myapp/myapp_tests'), 'myapp_tests')

    def test_full_local_package(self):
        self.assertEqual(self.package_name('./src/myapp/myapp_tests', root_package_name='$unittest'),
                         '$myapp_tests')

    def test_full_local_package_dir_with_dollar(self):
        self.assertEqual(self.package_name('./src/$victory_tests', root_package_name='$victory'),
                         '$victory_tests')

    def test_full_dir_with_dollar_of_not_local_package(self):
        self.assertEqual(self.package_name('./src/$victory_tests', root_package_name='victory'),
                         '$victory_tests')

    def test_prefix(self):
        self.assertEqual(self.package_name('./src/full/package/name', FOLDER_LOGIC=FOLDER_LOGIC_PREFIX),
                         'unittest_full_package_name')

    def test_prefix_local_package(self):
        self.assertEqual(self.package_name('./src/sub', root_package_name='$unittest',
                                           FOLDER_LOGIC=FOLDER_LOGIC_PREFIX),
                         '$unittest_sub')

    def test_outside_starting_folder(self):
        with self.assertRaises(SAPCliError) as caught:
            self.package_name('./secret')

        self.assertEqual(str(caught.exception), 'Sub-package dir ./secret not in starting folder /src/')

    def test_above_deep_starting_folder(self):
        with self.assertRaises(SAPCliError) as caught:
            self.package_name('./src', STARTING_FOLDER='/src/backend/')

        self.assertEqual(str(caught.exception), 'Sub-package dir ./src not in starting folder /src/backend/')

    def test_unsupported_folder_logic(self):
        with self.assertRaises(SAPCliError) as caught:
            self.package_name('./src/sub', FOLDER_LOGIC='MIXED')

        self.assertEqual(str(caught.exception), 'Unsupported folder logic: MIXED')


class TestPreparePackage(LayoutTestCase):

    def setUp(self):
        super().setUp()

        self.fake_open = self.patch('sap.platform.abap.abapgit.layout.open')
        self.package = RepoPackage('./src/', './src/package.devc.xml', None)

    def test_prepare_package(self):
        self.fake_open.return_value = StringIOFile(PACKAGE_DEVC_XML)

        devc = self.layout.prepare_package(self.package)

        self.fake_open.assert_called_once_with('./src/package.devc.xml', encoding='utf-8')
        self.assertEqual(devc.CTEXT, 'Test Package')

    def test_prepare_package_with_language(self):
        self.fake_open.return_value = StringIOFile(PACKAGE_DEVC_LANGUAGE_XML)

        devc = self.layout.prepare_package(self.package)

        self.assertEqual(devc.CTEXT, 'Test Package')

    def test_file_cannot_be_opened(self):
        self.fake_open.side_effect = OSError()

        with self.assertRaises(OSError):
            self.layout.prepare_package(self.package)

    def test_file_has_invalid_format(self):
        self.fake_open.return_value = StringIOFile('Foo')

        with self.assertRaises(sap.errors.InputError) as caught:
            self.layout.prepare_package(self.package)

        self.assertRegex(str(caught.exception), 'Invalid XML for DEVC:.*')

    def test_file_has_unknown_member(self):
        self.fake_open.return_value = StringIOFile(PACKAGE_DEVC_UNKNOWN_XML)

        with self.assertRaises(SAPCliError) as caught:
            self.layout.prepare_package(self.package)

        self.assertEqual(str(caught.exception), 'DEVC does not have the member FUTURE_FIELD')


class TestInitRepository(LayoutTestCase):

    def test_init_repository(self):
        fake_open = self.patch('sap.platform.abap.abapgit.layout.open', new=mock_open())
        fake_to_xml = self.patch('sap.platform.abap.to_xml')

        self.layout.init_repository('/repo', 'backend/abap/src')

        fake_open.assert_called_once_with('/repo/.abapgit.xml', 'w', encoding='utf8')

        args, kwargs = fake_to_xml.call_args
        dot_abap = args[0]
        self.assertEqual(dot_abap.MASTER_LANGUAGE, 'E')
        self.assertEqual(dot_abap.FOLDER_LOGIC, FOLDER_LOGIC_FULL)
        self.assertEqual(dot_abap.STARTING_FOLDER, '/backend/abap/src/')
        self.assertEqual(list(dot_abap.IGNORE),
                         ['/.gitignore', '/LICENSE', '/README.md', '/package.json', '/.travis.yml'])
        self.assertEqual(kwargs, {'dest': fake_open.return_value, 'top_element': 'DATA'})


class TestCheckoutPackage(LayoutTestCase):

    def test_checkout_package(self):
        fake_dump = self.patch('sap.platform.abap.abapgit.layout.dump_attributes_to_file')
        fake_package = self.patch('sap.adt.Package')
        fake_package.return_value.description = 'Description $VICTORY'

        self.layout.checkout_package('connection', '$VICTORY', '/repo/src', 'observer')

        fake_package.assert_called_once_with('connection', '$VICTORY')
        fake_package.return_value.fetch.assert_called_once_with()
        self.assertEqual(fake_dump.call_args_list, [
            call('observer', 'package', (sap.platform.abap.ddic.DEVC(CTEXT='Description $VICTORY'),), '.devc',
                 'LCL_OBJECT_DEVC', destdir='/repo/src')])


if __name__ == '__main__':
    unittest.main()
