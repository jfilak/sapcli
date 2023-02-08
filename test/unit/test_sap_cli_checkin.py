#!/usr/bin/env python3

import os
import unittest
import fnmatch
import errno
from types import SimpleNamespace
from unittest.mock import mock_open, patch, Mock, MagicMock, call

import sap.cli.checkin
import sap.platform.abap.abapgit
from sap import get_logger
from sap.adt.wb import CheckMessage, CheckMessageList
from sap.errors import SAPCliError
from sap.adt.errors import ExceptionResourceAlreadyExists, ExceptionCheckinFailure, ExceptionResourceCreationFailure

from mock import PatcherTestCase, ConsoleOutputTestCase, StringIOFile

from fixtures_abap import ABAP_GIT_DEFAULT_XML
from fixtures_cli_checkin import PACKAGE_DEVC_XML, CLAS_XML, INTF_XML, PROG_XML, INCLUDE_XML, INVALID_TYPE_XML
from infra import generate_parse_args


parse_args = generate_parse_args(sap.cli.checkin.CommandGroup())


class ActivationMessageGenerator:

    def __init__(self):
        self.check_message_list = None

    def add_message(self, typ, obj_descr, short_text):
        if self.check_message_list is None:
            self.check_message_list = CheckMessageList()

        message = CheckMessage()
        message.typ = typ
        message.obj_descr = obj_descr
        message.short_text = short_text

        self.check_message_list.append(message)

        return self

    def add_error(self, obj_descr, short_text):
        return self.add_message(CheckMessage.Type.ERROR, obj_descr, short_text)

    def add_warning(self, obj_descr, short_text):
        return self.add_message(CheckMessage.Type.WARNING, obj_descr, short_text)


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
        return self._path, self._dirs, self._files


class TestRepository(unittest.TestCase):

    def setUp(self):
        self.config = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo()
        self.repo = sap.cli.checkin.Repository('unittest', self.config)
        self.root_package = sap.cli.checkin.RepoPackage('unittest', './src/package.devc.xml', './src', None)

    def test_init(self):
        self.assertEqual(self.repo.config, self.config)
        self.assertEqual(len(self.repo.packages), 0)
        self.assertEqual(len(self.repo.objects), 0)

        with self.assertRaises(KeyError):
            self.repo.find_package_by_path('./src')

    def test_repo_add_object_unsupported(self):
        with self.assertRaises(sap.errors.SAPCliError) as caught:
            self.repo.add_object('log.txt', None)

        self.assertEqual(str(caught.exception), 'Invalid ABAP file name: log.txt')

    @patch('sap.cli.checkin.glob.glob', return_value=['zreport.prog.abap', 'zreport.prog.bogus', 'zreport.prog.xml'])
    def test_repo_add_object_ok(self, fake_glob):
        obj = self.repo.add_object('zreport.prog.xml', self.root_package)

        self.assertEqual(obj, sap.cli.checkin.RepoObject('prog',
                                                         'zreport',
                                                         './src/zreport.prog.xml',
                                                         self.root_package,
                                                         ['zreport.prog.abap', 'zreport.prog.bogus']))

    @patch('sap.cli.checkin.os.path.isfile', return_value=False)
    def test_repo_not_a_packagedir(self, fake_isfile):
        with self.assertRaises(sap.errors.SAPCliError) as caught:
            self.repo.add_package_dir('./.git', None)

        self.assertEqual(str(caught.exception), 'Not a package directory: ./.git')

    @patch('sap.cli.checkin.os.path.isfile', return_value=True)
    def test_repo_package_add_root(self, fake_isfile):
        pkg = self.repo.add_package_dir('./src', None)
        self.assertEqual(pkg, self.root_package)

        pkg = self.repo.find_package_by_path('./src')
        self.assertEqual(pkg, self.root_package)

    @patch('sap.cli.checkin.os.path.isfile', return_value=True)
    def test_repo_package_dir_parent(self, fake_isfile):
        config = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo()
        config.STARTING_FOLDER = '/src/backend/'
        repo = sap.cli.checkin.Repository('unittest', config)

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            repo.add_package_dir('./secret', None)

        self.assertEqual(str(caught.exception), 'Sub-package dir ./secret not in starting folder /src/backend/')

    @patch('sap.cli.checkin.os.path.isfile', return_value=True)
    def test_repo_package_dir_outside(self, fake_isfile):
        with self.assertRaises(sap.errors.SAPCliError) as caught:
            self.repo.add_package_dir('./secret', None)

        self.assertEqual(str(caught.exception), 'Sub-package dir ./secret not in starting folder /src/')

    @patch('sap.cli.checkin.os.path.isfile', return_value=True)
    def test_repo_package_dir_wrong_name(self, fake_isfile):
        with self.assertRaises(sap.errors.SAPCliError) as caught:
            self.repo.add_package_dir('../foo', None)

        self.assertEqual(str(caught.exception), 'Package dirs must start with "./": ../foo')

    @patch('sap.cli.checkin.os.path.isfile', return_value=True)
    def test_repo_package_name_fulll(self, fake_isfile):
        pkg = self.repo.add_package_dir('./src/myapp/myapp_tests', None)
        self.assertEqual(pkg.name, 'myapp_tests')

    @patch('sap.cli.checkin.os.path.isfile', return_value=True)
    def test_repo_package_name_prefix(self, fake_isfile):
        config = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo()
        config.FOLDER_LOGIC = sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX
        repo = sap.cli.checkin.Repository('unittest', config)

        pkg = repo.add_package_dir('./src/full/package/name', None)
        self.assertEqual(pkg.name, 'unittest_full_package_name')


class TestGetConfig(ConsoleOutputTestCase):

    @patch('sap.cli.checkin.open', side_effect=OSError(errno.ENOENT, 'No such file'))
    def test_get_config_noent(self, fake_open):
        act = sap.cli.checkin._get_config('/backend/', self.console)
        exp = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(STARTING_FOLDER='/backend/')

        self.assertEqual(act, exp)
        self.assertEmptyConsole(self.console)

    @patch('sap.cli.checkin.open', side_effect=OSError(errno.ENOENT, 'No such file'))
    def test_get_config_noent_default(self, fake_open):
        act = sap.cli.checkin._get_config(None, self.console)
        exp = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo()

        self.assertEqual(act, exp)
        self.assertEmptyConsole(self.console)

    @patch('sap.cli.checkin.open', side_effect=OSError(errno.EPERM))
    def test_get_config_noperm(self, fake_open):
        with self.assertRaises(OSError):
            sap.cli.checkin._get_config('/backend/', self.console)

        self.assertEmptyConsole(self.console)

    def test_get_config_overwrites(self):
        with patch('sap.cli.checkin.open', mock_open(read_data=ABAP_GIT_DEFAULT_XML)):
            config = sap.cli.checkin._get_config('/backend/', self.console)
            self.assertEqual(config.STARTING_FOLDER, '/src/')

        self.assertConsoleContents(self.console, stdout='Using starting-folder from .abapgit.xml: /src/\n')

    def test_get_config_simple(self):
        with patch('sap.cli.checkin.open', mock_open(read_data=ABAP_GIT_DEFAULT_XML)):
            config = sap.cli.checkin._get_config('/src/', self.console)
            self.assertEqual(config.STARTING_FOLDER, '/src/')

        self.assertEmptyConsole(self.console)


class TestCheckinGroup(ConsoleOutputTestCase):

    def setUp(self):
        super(TestCheckinGroup, self).setUp()

        self.mock_object = sap.cli.checkin.RepoObject(code='bogu', name='bogus', path='./bogus.txt', package=None,
                                                      files=[])
        self.mock_object_group = [self.mock_object]

    def test_checkin_group_none_handler(self):
        sap.cli.checkin._checkin_dependency_group(None, self.mock_object_group, self.console, None)

        self.assertConsoleContents(self.console, stderr='Object not supported: ./bogus.txt\n')

    def test_checkin_group_none_resp(self):
        with patch('sap.cli.checkin.OBJECT_CHECKIN_HANDLERS') as fake_handler:
            fake_handler.get = Mock()
            fake_handler.get.return_value.side_effect = ExceptionCheckinFailure('Checkin of adt object failed')

            inactive = sap.cli.checkin._checkin_dependency_group(None, self.mock_object_group, self.console, None)

        self.assertConsoleContents(self.console, stdout='Object handled without activation: ./bogus.txt\n')
        self.assertEqual(inactive.references, [])

    def test_checkin_group_simple(self):
        adt_object = Mock()

        with patch('sap.cli.checkin.OBJECT_CHECKIN_HANDLERS') as fake_handler:
            fake_handler.get = Mock()
            fake_handler.get.return_value = lambda x, y, z: adt_object

            inactive = sap.cli.checkin._checkin_dependency_group(None, self.mock_object_group, self.console, None)

        self.assertEqual(len(inactive.references), 1)


class TestCheckIn(PatcherTestCase, ConsoleOutputTestCase):

    def walk(self, name):
        for stand in self.walk_stands:
            yield stand

    def is_file(self, path):
        return path in self.files

    def glob(self, pattern):
        return [name for name in self.files if fnmatch.fnmatch(name, pattern)]

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

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

    @patch('sap.cli.checkin._get_config')
    @patch('sap.cli.checkin.checkin_package')
    def test_do_checkin_sanity(self, fake_checkin, fake_config):
        fake_config.return_value = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(
            FOLDER_LOGIC=sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX
        )

        # open -> .abapgit.xml

        def mock_object_handler(connection, repo_obj, corrnr):
            return SimpleNamespace(full_adt_uri=repo_obj.path, name=repo_obj.name)

        args = parse_args('$foo')
        with patch('sap.cli.checkin.OBJECT_CHECKIN_HANDLERS') as fake_handler, \
             patch('sap.adt.wb.try_mass_activate') as fake_activate:
            fake_handler.get = Mock()
            fake_handler.get.return_value = mock_object_handler

            fake_activate.return_value = []

            args.execute(None, args)

        fake_config.assert_called_once_with(None, sap.cli.core.get_console())

    @patch('sap.cli.checkin.os.path.isdir')
    def test_do_checkin_starting_folder_not_folder(self, fake_os_isdir):
        fake_os_isdir.return_value = False

        args = parse_args('$foo', '--starting-folder', 'FILE')
        exit_code = args.execute(None, args)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='Cannot check-in ABAP objects from "./FILE": not a directory\n')

    @patch('sap.cli.checkin._get_config')
    @patch('sap.cli.checkin._load_objects')
    def test_do_checkin_error(self, fake_load_objects, fake_config):
        fake_load_objects.side_effect = sap.errors.SAPCliError('Load failed.')
        fake_config.return_value = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(
            FOLDER_LOGIC=sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX
        )

        args = parse_args('$foo')
        exit_code = args.execute(None, args)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='Checkin failed: Load failed.\n')

    def test_load_objects(self):
        config = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(FOLDER_LOGIC=sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX)
        repo = sap.cli.checkin.Repository('unittest', config)

        sap.cli.checkin._load_objects(repo)

        self.assertEqual([package.name for package in repo.packages],
                         ['unittest', 'unittest_sub', 'unittest_sub_grand'])

        self.assertEqual([(obj.package.name, obj.name) for obj in repo.objects],
                         [('unittest', 'run_report'), ('unittest_sub', 'if_strategy'), ('unittest_sub_grand', 'cl_implementor')])

    def test_resolve_dependencies(self):
        clas = sap.cli.checkin.RepoObject(code='clas', name='cl_ass', path='./cl_ass', package=None, files=[])
        intf = sap.cli.checkin.RepoObject(code='intf', name='if_ace', path='./if_ace', package=None, files=[])
        prog = sap.cli.checkin.RepoObject(code='prog', name='program', path='./program', package=None, files=[])
        fugr = sap.cli.checkin.RepoObject(code='fugr', name='function_group', path='./function_group', package=None, files=[])

        objects = [clas, prog, intf, fugr]

        deps = sap.cli.checkin._resolve_dependencies(objects)

        self.assertEqual(deps, [[clas, intf], [prog], [fugr]])


class TestActivate(ConsoleOutputTestCase, PatcherTestCase):

    def setUp(self):
        super(TestActivate, self).setUp()

        self.fake_activate = self.patch('sap.adt.wb.try_mass_activate')

        self.connection = Mock()
        self.inactive_list = Mock()

    def call_activate(self):
        ret = sap.cli.checkin._activate(self.connection, self.inactive_list, self.console)
        self.assertIsNone(ret)
        self.fake_activate.assert_called_once_with(self.connection, self.inactive_list)

    def test_activate_no_messages(self):
        self.fake_activate.return_value = []

        self.call_activate()

        self.assertEmptyConsole(self.console)

    def test_activate_no_error(self):
        self.fake_activate.return_value = ActivationMessageGenerator().add_warning('CLAS/A', 'One').add_warning('PROG/B', 'Two').check_message_list

        self.call_activate()

        self.assertConsoleContents(self.console, stdout='''* CLAS/A ::
| W: One
* PROG/B ::
| W: Two
''')

    def test_activate_error(self):
        self.fake_activate.return_value = ActivationMessageGenerator().add_error('CLAS/A', 'One').add_warning('PROG/B', 'Two').check_message_list

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            self.call_activate()

        self.assertEqual(str(caught.exception), 'Aborting because of activation errors')

        self.assertConsoleContents(self.console, stdout='''* CLAS/A ::
| E: One
* PROG/B ::
| W: Two
''')


class TestCheckInPackage(ConsoleOutputTestCase, PatcherTestCase):

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

        self.connection = Mock()
        self.config = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo()
        self.repo = sap.cli.checkin.Repository('checkin-test', self.config)
        self.fake_open = self.patch('sap.cli.checkin.open')
        self.fake_args = Mock(software_component='LOCAL', app_component=None, transport_layer=None, corrnr=None)

        with self.patch('sap.cli.checkin.os.path.isfile') as fake_is_file:
            fake_is_file.return_value = True
            self.repo.add_package_dir(f'.{self.config.STARTING_FOLDER}')

    def test_devc_file_cannot_be_opened(self):
        self.fake_open.side_effect = OSError()

        with self.assertRaises(OSError):
            sap.cli.checkin.checkin_package(self.connection, self.repo.packages[0], self.fake_args)

    def test_devc_file_has_invalid_format(self):
        self.fake_open.return_value = StringIOFile('Foo')

        with self.assertRaises(sap.errors.InputError) as caught:
            sap.cli.checkin.checkin_package(self.connection, self.repo.packages[0], self.fake_args)

        self.assertRegex(str(caught.exception), 'Invalid XML for DEVC:.*')

    @patch('sap.cli.checkin.mod_log')
    @patch('sap.adt.package.Package.create')
    def test_package_already_exists(self, fake_package_create, fake_mod_log):
        fake_package_create.side_effect = ExceptionResourceAlreadyExists(message='Package already exists.')
        mock_info = Mock()
        fake_mod_log.return_value.info = mock_info
        self.fake_open.return_value = StringIOFile(PACKAGE_DEVC_XML)

        sap.cli.checkin.checkin_package(self.connection, self.repo.packages[0], self.fake_args)

        mock_info.assert_called_once_with('Package already exists.')

    @patch('sap.adt.package.Package.create')
    def test_package_create_raises_error(self, fake_package_create):
        fake_package_create.side_effect = SAPCliError('Create error.')
        self.fake_open.return_value = StringIOFile(PACKAGE_DEVC_XML)

        with self.assertRaises(SAPCliError) as cm:
            sap.cli.checkin.checkin_package(self.connection, self.repo.packages[0], self.fake_args)

        self.assertEqual(str(cm.exception), 'Create error.')

    @patch('sap.adt.Package')
    @patch('sap.adt.ADTCoreData')
    def test_checkin_successful(self, fake_core_data, fake_package):
        self.fake_open.return_value = StringIOFile(PACKAGE_DEVC_XML)
        self.connection.user = 'fake_user'
        metadata = Mock()
        fake_core_data.return_value = metadata
        package = Mock()
        package.super_package.name = None
        fake_package.return_value = package

        sap.cli.checkin.checkin_package(self.connection, self.repo.packages[0], self.fake_args)

        self.assertConsoleContents(self.console,
                                   stdout=f'Creating Package: {self.repo.packages[0].name} Test Package\n')
        fake_core_data.assert_called_once_with(language='EN', master_language='EN', responsible='fake_user',
                                               description='Test Package')
        fake_package.assert_called_once_with(self.connection, self.repo.packages[0].name.upper(),
                                             metadata=metadata)
        package.set_package_type.assert_called_once_with('development')
        self.assertIsNone(package.super_package.name)
        package.set_software_component.assert_called_once_with('LOCAL')
        package.set_app_component.assert_not_called()
        package.set_transport_layer.assert_not_called()
        package.create.assert_called_once_with(None)

    @patch('sap.adt.Package')
    @patch('sap.adt.ADTCoreData')
    def test_checkin_successful_full(self, _, fake_package):
        self.fake_open.return_value = StringIOFile(PACKAGE_DEVC_XML)
        self.connection.user = 'fake_user'
        repo_package = self.repo.packages[0]
        fake_repo_package = Mock()
        fake_repo_package.__dict__.update(**{'parent': Mock(), 'name': repo_package.name, 'path': repo_package.path,
                                             'dir_path': repo_package.dir_path})
        package = Mock()
        package.super_package.name = None
        fake_package.return_value = package
        full_fake_args = Mock(software_component='LOCAL', app_component='app', transport_layer='trans', corrnr='corrnr')

        sap.cli.checkin.checkin_package(self.connection, fake_repo_package, full_fake_args)

        self.assertConsoleContents(self.console,
                                   stdout=f'Creating Package: {self.repo.packages[0].name} Test Package\n')
        self.assertEqual(package.super_package.name, fake_repo_package.parent.name.upper())
        package.set_software_component.assert_called_once_with('LOCAL')
        package.set_app_component.assert_called_once_with('APP')
        package.set_transport_layer.assert_called_once_with('TRANS')
        package.create.assert_called_once_with('corrnr')


class TestCheckInClass(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

        self.fake_open = self.patch('sap.cli.checkin.open')
        self.fake_core_data = self.patch('sap.adt.ADTCoreData')
        self.fake_class = self.patch('sap.adt.Class')

        self.metadata = Mock()
        self.fake_core_data.return_value = self.metadata

        self.clas_editor = MagicMock()
        self.clas_editor.__enter__.return_value = self.clas_editor

        self.clas = MagicMock()
        self.clas.open_editor.return_value = self.clas_editor
        self.clas.definitions.open_editor.return_value = self.clas_editor
        self.clas.implementations.open_editor.return_value = self.clas_editor
        self.clas.test_classes.open_editor.return_value = self.clas_editor
        self.fake_class.return_value = self.clas

        self.connection = Mock()
        self.connection.user = 'test_user'
        self.package = sap.cli.checkin.RepoPackage('test_package', '/src/package.devc.xml', '/src', None)
        self.clas_object = sap.cli.checkin.RepoObject('', 'test_clas', '/src/test_clas', self.package,
                                                      ['foo.clas.abap', 'foo.locals_def.abap', 'foo.locals_imp.abap',
                                                       'foo.testclasses.abap'])

    def assert_open_editor_calls(self, source_files_content, corrnr=None):
        self.clas.open_editor.assert_called_once_with(corrnr=corrnr)
        self.clas.definitions.open_editor.assert_called_once_with(corrnr=corrnr)
        self.clas.implementations.open_editor.assert_called_once_with(corrnr=corrnr)
        self.clas.test_classes.open_editor.assert_called_once_with(corrnr=corrnr)
        self.clas_editor.write.assert_has_calls([call(content) for content in source_files_content])

    def test_checkin_clas_no_files(self):
        clas_obj = sap.cli.checkin.RepoObject('', 'no_files_clas', '/src/test_clas', Mock(), [])

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            sap.cli.checkin.checkin_clas(self.connection, clas_obj)

        self.assertConsoleContents(self.console, stdout=f'Creating Class: {clas_obj.name}\n')
        self.assertEqual(str(cm.exception), f'No source file for class {clas_obj.name}')

    def test_checkin_clas(self):
        source_files_content = ['class_body', 'locals_def_body', 'locals_imp_body', 'test_body']
        self.fake_open.side_effect = [StringIOFile(content) for content in
                                      [CLAS_XML] + source_files_content]

        sap.cli.checkin.checkin_clas(self.connection, self.clas_object)

        self.fake_core_data.assert_called_once_with(language='EN', master_language='EN',
                                                    responsible=self.connection.user, description='Test description')
        self.fake_class.assert_called_once_with(self.connection, self.clas_object.name.upper(),
                                                package=self.package.name, metadata=self.metadata)
        self.clas.create.assert_called_once_with(None)
        self.assert_open_editor_calls(source_files_content)
        self.assertConsoleContents(self.console, stdout=f'''Creating Class: {self.clas_object.name}
Writing Clas: {self.clas_object.name} clas
Writing Clas: {self.clas_object.name} locals_def
Writing Clas: {self.clas_object.name} locals_imp
Writing Clas: {self.clas_object.name} testclasses
''')

    def test_checkin_clas_with_corrnr(self):
        self.fake_open.return_value = StringIOFile(CLAS_XML)

        sap.cli.checkin.checkin_clas(self.connection, self.clas_object, 'corrnr')

        self.clas.create.assert_called_once_with('corrnr')
        self.assert_open_editor_calls([], corrnr='corrnr')

    @patch('sap.cli.checkin.mod_log')
    def test_checkin_clas_create_error(self, fake_mod_log):
        self.fake_open.return_value = StringIOFile(CLAS_XML)
        self.clas.create.side_effect = ExceptionResourceAlreadyExists('Clas already created.')

        sap.cli.checkin.checkin_clas(self.connection, self.clas_object)

        fake_mod_log.return_value.info.assert_called_once_with('Clas already created.')
        self.assert_open_editor_calls([])

    def test_checkin_clas_source_file_wrong_suffix(self):
        self.fake_open.return_value = StringIOFile(CLAS_XML)
        self.clas_object.files.append('foo.wrong.prefix')

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            sap.cli.checkin.checkin_clas(self.connection, self.clas_object)

        self.clas.create.assert_called_once_with(None)
        self.assertEqual(str(cm.exception),
                         f'No .abap suffix of source file for class {self.clas_object.name}: foo.wrong.prefix')

    def test_checkin_clas_unknown_class_part(self):
        source_files_content = ['class_body', 'locals_def_body', 'locals_imp_body', 'test_body']
        self.fake_open.side_effect = [StringIOFile(content) for content in
                                      [CLAS_XML] + source_files_content]
        self.clas_object.files.append('foo.unknown.abap')

        sap.cli.checkin.checkin_clas(self.connection, self.clas_object)

        self.clas.create.assert_called_once_with(None)
        self.assert_open_editor_calls(source_files_content)
        self.assertConsoleContents(self.console, stderr='Unknown class part foo.unknown.abap\n',
                                   stdout=f'''Creating Class: {self.clas_object.name}
Writing Clas: {self.clas_object.name} clas
Writing Clas: {self.clas_object.name} locals_def
Writing Clas: {self.clas_object.name} locals_imp
Writing Clas: {self.clas_object.name} testclasses
''')


class TestCheckInInterface(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

        self.fake_open = self.patch('sap.cli.checkin.open')
        self.fake_open.side_effect = [StringIOFile(INTF_XML), StringIOFile('test_intf_body')]
        self.fake_core_data = self.patch('sap.adt.ADTCoreData')
        self.fake_interface = self.patch('sap.adt.Interface')

        self.metadata = Mock()
        self.fake_core_data.return_value = self.metadata

        self.interface_editor = MagicMock()
        self.interface_editor.__enter__.return_value = self.interface_editor

        self.interface = MagicMock()
        self.interface.open_editor.return_value = self.interface_editor
        self.fake_interface.return_value = self.interface

        self.connection = Mock()
        self.connection.user = 'test_user'
        self.package = sap.cli.checkin.RepoPackage('test_package', '/src/package.devc.xml', '/src', None)
        self.interface_object = sap.cli.checkin.RepoObject('', 'test_interface', '/src/test_interface', self.package,
                                                           ['foo.intf.abap'])

    def test_checkin_intf_no_file(self):
        interface_object = sap.cli.checkin.RepoObject('', 'test_intf', '/src/boo', Mock(), [])

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            sap.cli.checkin.checkin_intf(self.connection, interface_object)

        self.assertEqual(str(cm.exception), f'No source file for interface {interface_object.name}')
        self.assertConsoleContents(self.console, stdout=f'Creating Interface: {interface_object.name}\n')

    def test_checkin_intf_too_many_files(self):
        self.interface_object.files.append('too-many.intf.abap')

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            sap.cli.checkin.checkin_intf(self.connection, self.interface_object)

        self.assertEqual(str(cm.exception), f'Too many source files for interface {self.interface_object.name}: '
                                            f'foo.intf.abap,too-many.intf.abap')

    def test_checkin_intf_wrong_suffix(self):
        interface_object = sap.cli.checkin.RepoObject('', 'test_intf', '/src/boo', Mock(), ['random.file'])

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            sap.cli.checkin.checkin_intf(self.connection, interface_object)

        self.assertEqual(str(cm.exception), f'No .abap suffix of source file for interface {interface_object.name}')

    def test_checkin_intf(self):
        sap.cli.checkin.checkin_intf(self.connection, self.interface_object)

        self.fake_core_data.assert_called_once_with(language='EN', master_language='EN',
                                                    responsible=self.connection.user, description='Test intf descr')
        self.fake_interface.assert_called_once_with(self.connection, self.interface_object.name.upper(),
                                                    package=self.package.name, metadata=self.metadata)
        self.interface.create.assert_called_once_with(None)
        self.interface.open_editor.assert_called_once_with(corrnr=None)
        self.interface_editor.write.assert_called_once_with('test_intf_body')
        self.assertConsoleContents(self.console, stdout=f'Creating Interface: {self.interface_object.name}\n'
                                                        f'Writing Interface: {self.interface_object.name}\n')

    def test_checkin_intf_with_corrnr(self):
        sap.cli.checkin.checkin_intf(self.connection, self.interface_object, 'corrnr')

        self.interface.create.assert_called_once_with('corrnr')
        self.interface.open_editor.assert_called_once_with(corrnr='corrnr')

    @patch('sap.cli.checkin.mod_log')
    def test_checkin_intf_already_exists(self, fake_mod_log):
        self.interface.create.side_effect = ExceptionResourceAlreadyExists('Interface already exists.')

        sap.cli.checkin.checkin_intf(self.connection, self.interface_object)
        self.interface.create.assert_called_once_with(None)
        fake_mod_log.return_value.info.assert_called_once_with('Interface already exists.')
        self.interface.open_editor.assert_called_once_with(corrnr=None)


class TestCheckInProgram(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

        self.fake_open = self.patch('sap.cli.checkin.open')
        self.fake_core_data = self.patch('sap.adt.ADTCoreData')
        self.fake_program = self.patch('sap.adt.Program')
        self.fake_include = self.patch('sap.adt.Include')

        self.metadata = Mock()
        self.fake_core_data.return_value = self.metadata

        self.program_editor = MagicMock()
        self.program_editor.__enter__.return_value = self.program_editor

        self.program = MagicMock()
        self.program.open_editor.return_value = self.program_editor
        self.fake_program.return_value = self.program

        self.include_editor = MagicMock()
        self.include_editor.__enter__.return_value = self.include_editor

        self.include = MagicMock()
        self.include.open_editor.return_value = self.include_editor
        self.fake_include.return_value = self.include

        self.connection = Mock()
        self.connection.user = 'test_user'
        self.package = sap.cli.checkin.RepoPackage('test_package', '/src/package.devc.xml', '/src', None)
        self.prog_object = sap.cli.checkin.RepoObject('', 'test_prog', '/src/test_prog', self.package,
                                                      ['foo.prog.abap'])

    def test_checkin_prog_no_files(self):
        prog_object = sap.cli.checkin.RepoObject('', 'test_prog', '/src/test_prog', Mock(), [])

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            sap.cli.checkin.checkin_prog(self.connection, prog_object)

        self.assertConsoleContents(self.console, stdout=f'Creating Program: {prog_object.name}\n')
        self.assertEqual(str(cm.exception), f'No source file for program {prog_object.name}')

    def test_checkin_prog_too_many_files(self):
        self.prog_object.files.append('foo.many.files.abap')

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            sap.cli.checkin.checkin_prog(self.connection, self.prog_object)

        self.assertConsoleContents(self.console, stdout=f'Creating Program: {self.prog_object.name}\n')
        self.assertEqual(str(cm.exception), f'Too many source files for program {self.prog_object.name}:'
                                            f' foo.prog.abap,foo.many.files.abap')

    def test_checkin_prog_wrong_suffix(self):
        prog_object = sap.cli.checkin.RepoObject('', 'test_prog', '/src/test_prog', Mock(), ['foo.prog.wrong'])

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            sap.cli.checkin.checkin_prog(self.connection, prog_object)

        self.assertConsoleContents(self.console, stdout=f'Creating Program: {prog_object.name}\n')
        self.assertEqual(str(cm.exception), f'No .abap suffix of source file for program {prog_object.name}')

    def test_checkin_prog_invalid_type(self):
        self.fake_open.side_effect = [StringIOFile(INVALID_TYPE_XML)]

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            sap.cli.checkin.checkin_prog(self.connection, self.prog_object)

        self.assertEqual(str(cm.exception), 'Unknown program type X')
        self.fake_core_data.assert_called_once_with(language='EN', master_language='EN',
                                                    responsible=self.connection.user)
        self.fake_program.assert_not_called()
        self.fake_include.assert_not_called()

    def test_checkin_prog_program(self):
        self.fake_open.side_effect = [StringIOFile(PROG_XML), StringIOFile('test_prog_body')]

        sap.cli.checkin.checkin_prog(self.connection, self.prog_object)

        self.fake_core_data.assert_called_once_with(language='EN', master_language='EN',
                                                    responsible=self.connection.user)
        self.fake_program.assert_called_once_with(self.connection, self.prog_object.name, package=self.package.name,
                                                  metadata=self.metadata)
        self.assertEqual(self.program.description, 'Test program desc')
        self.program.create.assert_called_once_with(None)
        self.program.open_editor.assert_called_once_with(corrnr=None)
        self.program_editor.write.assert_called_once_with('test_prog_body')
        self.assertConsoleContents(self.console, stdout=f'''Creating Program: {self.prog_object.name}
Writing Program: {self.prog_object.name}
''')

    def test_checkin_prog_include(self):
        self.fake_open.side_effect = [StringIOFile(INCLUDE_XML), StringIOFile('test_include_body')]

        sap.cli.checkin.checkin_prog(self.connection, self.prog_object)

        self.fake_core_data.assert_called_once_with(language='EN', master_language='EN',
                                                    responsible=self.connection.user)
        self.fake_include.assert_called_once_with(self.connection, self.prog_object.name, package=self.package.name,
                                                  metadata=self.metadata)
        self.assertEqual(self.include.description, 'Test include desc')
        self.include.create.assert_called_once_with(None)
        self.include.open_editor.assert_called_once_with(corrnr=None)
        self.include_editor.write.assert_called_once_with('test_include_body')
        self.assertConsoleContents(self.console, stdout=f'''Creating Program: {self.prog_object.name}
Creating Include: {self.prog_object.name}
Writing Program: {self.prog_object.name}
''')

    def test_checkin_prog_with_corrnr(self):
        self.fake_open.side_effect = [StringIOFile(PROG_XML), StringIOFile('test_prog_body')]

        sap.cli.checkin.checkin_prog(self.connection, self.prog_object, 'corrnr')

        self.program.create.assert_called_once_with('corrnr')
        self.program.open_editor.assert_called_once_with(corrnr='corrnr')

    @patch('sap.cli.checkin.mod_log')
    def test_checkin_prog_already_exists(self, fake_mod_log):
        self.fake_open.side_effect = [StringIOFile(PROG_XML), StringIOFile('test_prog_body')]
        self.program.create.side_effect = ExceptionResourceCreationFailure(f'A program or include already exists with'
                                                                           f' the name {self.prog_object.name.upper()}')

        sap.cli.checkin.checkin_prog(self.connection, self.prog_object)

        fake_mod_log.return_value.info.assert_called_once_with(f'A program or include already exists with the name'
                                                               f' {self.prog_object.name.upper()}')
        self.program.open_editor.assert_called_once_with(corrnr=None)
        self.program_editor.write.assert_called_once_with('test_prog_body')

    def test_checkin_prog_creation_error(self):
        self.fake_open.side_effect = [StringIOFile(PROG_XML)]
        self.program.create.side_effect = ExceptionResourceCreationFailure('Failed to create program')

        with self.assertRaises(ExceptionResourceCreationFailure) as cm:
            sap.cli.checkin.checkin_prog(self.connection, self.prog_object)

        self.assertEqual(str(cm.exception), 'Failed to create program')
        self.program.open_editor.assert_not_called()


if __name__ == '__main__':
    unittest.main()

