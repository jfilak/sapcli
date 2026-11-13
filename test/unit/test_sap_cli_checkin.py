#!/usr/bin/env python3

import os
import unittest
import fnmatch
import errno
from types import SimpleNamespace
from unittest.mock import mock_open, patch, Mock, MagicMock, PropertyMock, call, ANY

import sap.adt.checks
import sap.cli.checkin
import sap.platform.abap.abapgit
from sap import get_logger
from sap.adt.wb import CheckMessage, CheckMessageList
from sap.errors import SAPCliError
from sap.adt.errors import ExceptionResourceAlreadyExists, ExceptionCheckinFailure, ExceptionResourceCreationFailure

from mock import PatcherTestCase, ConsoleOutputTestCase, StringIOFile

FIXTURE_TEXT_SYMBOLS = '@MaxLength:20\r\n001=Hello, world!\r\n@MaxLength:10\r\n002=a=b\r\n'

from mock import Connection, Response
from fixtures_abap import ABAP_GIT_DEFAULT_XML
from fixtures_cli_checkin import PACKAGE_DEVC_UNKNOWN_XML, PACKAGE_DEVC_LANGUAGE_XML, PACKAGE_DEVC_XML
from infra import generate_parse_args
from sap.fileformat import HandlerRegistry, CheckinContext

# The tests of the objects not migrated to sap.fileformat yet replace the
# registry with the empty one to use only the tested dictionaries.
NO_HANDLERS = HandlerRegistry(())


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

    def test_repo_unused_files_tracking(self):
        self.repo.add_file('./src/a.abap')
        self.repo.add_file('./src/b.abap')
        self.assertEqual(self.repo.unused_files, ['./src/a.abap', './src/b.abap'])

        self.repo.mark_file_used('./src/a.abap')
        self.assertEqual(self.repo.unused_files, ['./src/b.abap'])

    def test_repo_mark_file_used_unrecorded(self):
        self.repo.mark_file_used('./src/ghost.abap')

        self.assertEqual(self.repo.unused_files, [])

    @patch('sap.cli.checkin.glob.glob', return_value=['./src/zreport.prog.abap', './src/zreport.prog.xml'])
    def test_repo_add_object_marks_xml_used(self, fake_glob):
        self.repo.add_file('./src/zreport.prog.xml')
        self.repo.add_file('./src/zreport.prog.abap')

        self.repo.add_object('zreport.prog.xml', self.root_package)

        self.assertEqual(self.repo.unused_files, ['./src/zreport.prog.abap'])

    @patch('sap.cli.checkin.os.path.isfile', return_value=True)
    def test_repo_add_package_dir_marks_devc_used(self, fake_isfile):
        self.repo.add_file('./src/package.devc.xml')

        self.repo.add_package_dir('./src', None)

        self.assertEqual(self.repo.unused_files, [])

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
        self.repo = Mock()

    def test_checkin_group_none_handler(self):
        sap.cli.checkin._checkin_dependency_group(None, self.repo, self.mock_object_group, self.console, None)

        self.assertConsoleContents(self.console, stderr='Object not supported: ./bogus.txt\n')
        self.repo.mark_file_used.assert_not_called()

    def test_checkin_group_failure_stops_checkin(self):
        with patch('sap.cli.checkin.OBJECT_CHECKIN_HANDLERS') as fake_handler:
            fake_handler.get = Mock()
            fake_handler.get.return_value.side_effect = ExceptionCheckinFailure('Checkin of adt object failed')

            with self.assertRaises(ExceptionCheckinFailure) as caught:
                sap.cli.checkin._checkin_dependency_group(None, self.repo, self.mock_object_group, self.console, None)

        self.assertEqual(str(caught.exception), 'Checkin of adt object failed')
        self.assertEmptyConsole(self.console)
        self.repo.mark_file_used.assert_not_called()

    def test_checkin_group_passes_prepared_data(self):
        handler = Mock(return_value=sap.fileformat.ObjectCheckinResult([], []))

        with patch('sap.cli.checkin.OBJECT_CHECKIN_HANDLERS') as fake_handler:
            fake_handler.get = Mock(return_value=handler)

            sap.cli.checkin._checkin_dependency_group('connection', self.repo, self.mock_object_group, self.console,
                                                      '420', check_before_save=True,
                                                      prepared={'./bogus.txt': 'prepared bogus'})

        handler.assert_called_once_with('connection', self.mock_object, '420', check_before_save=True,
                                        prepared='prepared bogus')

    def test_checkin_group_prefers_registered_handler(self):
        adt_object = Mock()
        handler = Mock(FILE_TYPE='bogu', METADATA_EXT='xml', ADT_TYPES=('BOGU/S',))
        handler.checkin.return_value = sap.fileformat.ObjectCheckinResult([adt_object], ['./src/used.abap'])

        package = sap.cli.checkin.RepoPackage('$bogus', './package.devc.xml', '.', None)
        repo_obj = sap.cli.checkin.RepoObject(code='bogu', name='bogus', path='./bogus.bogu.xml', package=package,
                                              files=[])

        with patch('sap.cli.checkin.OBJECT_HANDLERS', HandlerRegistry((handler,))), \
             patch('sap.cli.checkin.OBJECT_CHECKIN_HANDLERS') as fake_handler:
            inactive = sap.cli.checkin._checkin_dependency_group(
                'connection', self.repo, [repo_obj], self.console, '420', check_before_save=True,
                prepared={'./bogus.bogu.xml': 'prepared bogus'})

        handler.checkin.assert_called_once_with(CheckinContext('connection', '$bogus', '420', True), repo_obj,
                                                'prepared bogus')
        fake_handler.get.assert_not_called()
        self.assertEqual(len(inactive.references), 1)
        self.repo.mark_file_used.assert_called_once_with('./src/used.abap')
        self.assertEmptyConsole(self.console)

    def test_checkin_group_simple(self):
        adt_object = Mock()

        with patch('sap.cli.checkin.OBJECT_CHECKIN_HANDLERS') as fake_handler:
            fake_handler.get = Mock()
            fake_handler.get.return_value = lambda *_args, **_kwargs: sap.fileformat.ObjectCheckinResult(
                [adt_object], ['./src/used.abap'])

            inactive = sap.cli.checkin._checkin_dependency_group(None, self.repo, self.mock_object_group, self.console, None)

        self.assertEqual(len(inactive.references), 1)
        self.repo.mark_file_used.assert_called_once_with('./src/used.abap')


class TestPrepareRepository(ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()

        self.package = sap.cli.checkin.RepoPackage('$TMP', './src/package.devc.xml', './src', None)
        self.intf = sap.cli.checkin.RepoObject('intf', 'zif_good', './src/zif_good.intf.xml', self.package, [])
        self.clas = sap.cli.checkin.RepoObject('clas', 'zcl_bad', './src/zcl_bad.clas.xml', self.package, [])
        self.tabl = sap.cli.checkin.RepoObject('tabl', 'zbad', './src/zbad.tabl.xml', self.package, [])
        self.repo = Mock(packages=[self.package], objects=[self.intf, self.clas, self.tabl])

    def test_prepare_repository(self):
        preparers = {
            'intf': Mock(return_value='prepared intf'),
            'clas': Mock(return_value='prepared clas'),
            'tabl': Mock(return_value='prepared tabl'),
        }

        with patch('sap.cli.checkin.prepare_package', return_value='prepared package') as fake_prepare_package, \
             patch('sap.cli.checkin.OBJECT_HANDLERS', NO_HANDLERS), \
             patch.dict('sap.cli.checkin.OBJECT_CHECKIN_PREPARERS', preparers):
            prepared = sap.cli.checkin._prepare_repository(self.repo, self.console)

        fake_prepare_package.assert_called_once_with(self.package)
        preparers['intf'].assert_called_once_with(self.intf)
        self.assertEqual(prepared, {
            './src/package.devc.xml': 'prepared package',
            './src/zif_good.intf.xml': 'prepared intf',
            './src/zcl_bad.clas.xml': 'prepared clas',
            './src/zbad.tabl.xml': 'prepared tabl',
        })
        self.assertEmptyConsole(self.console)

    def test_prepare_repository_prefers_registered_handler(self):
        handler = Mock(FILE_TYPE='clas', METADATA_EXT='xml', ADT_TYPES=('CLAS/OC',))
        handler.prepare.return_value = 'prepared by handler'

        preparers = {
            'intf': Mock(return_value='prepared intf'),
            'clas': Mock(return_value='prepared clas'),
            'tabl': Mock(return_value='prepared tabl'),
        }

        with patch('sap.cli.checkin.prepare_package', return_value='prepared package'), \
             patch('sap.cli.checkin.OBJECT_HANDLERS', HandlerRegistry((handler,))), \
             patch.dict('sap.cli.checkin.OBJECT_CHECKIN_PREPARERS', preparers):
            prepared = sap.cli.checkin._prepare_repository(self.repo, self.console)

        handler.prepare.assert_called_once_with(self.clas)
        preparers['clas'].assert_not_called()
        self.assertEqual(prepared['./src/zcl_bad.clas.xml'], 'prepared by handler')
        self.assertEqual(prepared['./src/zif_good.intf.xml'], 'prepared intf')

    def test_prepare_repository_reports_all_problems(self):
        preparers = {
            'intf': Mock(return_value='prepared intf'),
            'clas': Mock(side_effect=ExceptionCheckinFailure('No source file for class zcl_bad')),
            'tabl': Mock(side_effect=sap.errors.InputError('Invalid XML for DD02V: syntax error')),
        }

        with patch('sap.cli.checkin.prepare_package', side_effect=SAPCliError('DEVC does not have the member FOO')), \
             patch('sap.cli.checkin.OBJECT_HANDLERS', NO_HANDLERS), \
             patch.dict('sap.cli.checkin.OBJECT_CHECKIN_PREPARERS', preparers), \
             self.assertRaises(SAPCliError) as caught:
            sap.cli.checkin._prepare_repository(self.repo, self.console)

        self.assertEqual(str(caught.exception), 'Cannot check in 3 files - nothing has been changed')
        self.assertConsoleContents(self.console, stderr='''./src/package.devc.xml: DEVC does not have the member FOO
./src/zcl_bad.clas.xml: No source file for class zcl_bad
./src/zbad.tabl.xml: Invalid XML for DD02V: syntax error
''')


class TestCheckIn(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def walk(self, name):
        for stand in self.walk_stands:
            yield stand

    def is_file(self, path):
        return path in self.files

    def glob(self, pattern):
        return [name for name in self.files if fnmatch.fnmatch(name, pattern)]

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

        simple_root = DirContentBuilder('./src/').add_abap_program('run_report').add_abap_function_group('test_fugr')
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

    @patch('sap.cli.checkin._prepare_repository', return_value={})
    @patch('sap.cli.checkin._get_config')
    @patch('sap.cli.checkin.checkin_package')
    def test_do_checkin_sanity(self, fake_checkin, fake_config, _):
        fake_config.return_value = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(
            FOLDER_LOGIC=sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX
        )

        # open -> .abapgit.xml

        def mock_object_handler(connection, repo_obj, corrnr, **_):
            return sap.fileformat.ObjectCheckinResult(
                [SimpleNamespace(full_adt_uri=repo_obj.path, name=repo_obj.name)],
                list(repo_obj.files))

        args = parse_args('package', '$foo')
        with patch('sap.cli.checkin.OBJECT_CHECKIN_HANDLERS') as fake_handler, \
             patch('sap.cli.checkin.OBJECT_HANDLERS', NO_HANDLERS), \
             patch('sap.adt.wb.try_mass_activate') as fake_activate:
            fake_handler.get = Mock()
            fake_handler.get.return_value = mock_object_handler

            fake_activate.return_value = []

            args.execute(None, args)

        fake_config.assert_called_once_with(None, sap.cli.core.get_console())

    @patch('sap.cli.checkin.os.path.isdir')
    def test_do_checkin_starting_folder_not_folder(self, fake_os_isdir):
        fake_os_isdir.return_value = False

        args = parse_args('package', '$foo', '--starting-folder', 'FILE')
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

        args = parse_args('package', '$foo')
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
                         [('unittest', 'run_report'), ('unittest', 'test_fugr'), ('unittest_sub', 'if_strategy'),
                          ('unittest_sub_grand', 'cl_implementor')])

    def test_load_objects_tracks_files(self):
        config = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(FOLDER_LOGIC=sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX)
        repo = sap.cli.checkin.Repository('unittest', config)

        sap.cli.checkin._load_objects(repo)

        self.assertEqual(repo.unused_files,
                         ['./src/run_report.prog.abap',
                          './src/sub/grand/cl_implementor.clas.abap',
                          './src/sub/if_strategy.intf.abap',
                          './src/test_fugr.fugr.include.abap',
                          './src/test_fugr.fugr.include.xml',
                          './src/test_fugr.fugr.module.abap'])

    def test_load_objects_data_definition(self):
        root = DirContentBuilder('./src/').add_data_definition('zcds')
        self.walk_stands = [root.walk_stand()]
        self.files = root.files()

        config = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(FOLDER_LOGIC=sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX)
        repo = sap.cli.checkin.Repository('unittest', config)

        sap.cli.checkin._load_objects(repo)

        self.assertEqual([(obj.code, obj.name, obj.path, obj.files) for obj in repo.objects],
                         [('ddls', 'zcds', './src/zcds.ddls.xml', ['./src/zcds.ddls.asddls', './src/zcds.ddls.baseinfo'])])

    def test_load_objects_ignores_files_without_dot(self):
        root = DirContentBuilder('./src/').add_abap_program('run_report').add_file('README').add_file('zsearch_help.shlp.xml')
        self.walk_stands = [root.walk_stand()]
        self.files = root.files()

        config = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(FOLDER_LOGIC=sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX)
        repo = sap.cli.checkin.Repository('unittest', config)

        sap.cli.checkin._load_objects(repo)

        self.assertEqual([obj.name for obj in repo.objects], ['run_report'])
        self.assertEqual(repo.unused_files,
                         ['./src/README',
                          './src/run_report.prog.abap',
                          './src/zsearch_help.shlp.xml'])

    @patch('sap.cli.checkin._prepare_repository', return_value={})
    @patch('sap.cli.checkin._get_config')
    @patch('sap.cli.checkin.checkin_package')
    def test_do_checkin_reports_unused_files(self, fake_checkin, fake_config, _):
        fake_config.return_value = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(
            FOLDER_LOGIC=sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX
        )

        def mock_object_handler(connection, repo_obj, corrnr, **_):
            return sap.fileformat.ObjectCheckinResult(
                [SimpleNamespace(full_adt_uri=repo_obj.path, name=repo_obj.name)],
                list(repo_obj.files))

        handlers = {'intf': mock_object_handler,
                    'clas': mock_object_handler,
                    'prog': mock_object_handler,
                    'fugr': mock_object_handler}

        args = parse_args('package', '$foo')
        with patch.dict('sap.cli.checkin.OBJECT_CHECKIN_HANDLERS', handlers, clear=True), \
             patch('sap.cli.checkin.OBJECT_HANDLERS', NO_HANDLERS), \
             patch('sap.adt.wb.try_mass_activate') as fake_activate:
            fake_activate.return_value = []

            exit_code = args.execute(None, args)

        self.assertEqual(exit_code, 0)
        self.assertConsoleContents(self.console,
                                   stdout='''Checking files ...
Creating packages ...
Creating objects ...
Creating objects ...
Activating objects ...
Creating objects ...
Activating objects ...
Creating objects ...
Activating objects ...
''',
                                   stderr='Unused file: ./src/test_fugr.fugr.include.xml\n')

    def test_resolve_dependencies(self):
        clas = sap.cli.checkin.RepoObject(code='clas', name='cl_ass', path='./cl_ass', package=None, files=[])
        intf = sap.cli.checkin.RepoObject(code='intf', name='if_ace', path='./if_ace', package=None, files=[])
        prog = sap.cli.checkin.RepoObject(code='prog', name='program', path='./program', package=None, files=[])
        fugr = sap.cli.checkin.RepoObject(code='fugr', name='function_group', path='./function_group', package=None, files=[])
        ttyp = sap.cli.checkin.RepoObject(code='ttyp', name='table_type', path='./table_type', package=None, files=[])
        ddls = sap.cli.checkin.RepoObject(code='ddls', name='cds_view', path='./cds_view', package=None, files=[])
        dcls = sap.cli.checkin.RepoObject(code='dcls', name='cds_role', path='./cds_role', package=None, files=[])
        ddlx = sap.cli.checkin.RepoObject(code='ddlx', name='cds_ext', path='./cds_ext', package=None, files=[])
        bdef = sap.cli.checkin.RepoObject(code='bdef', name='cds_bo', path='./cds_bo', package=None, files=[])

        tabl = sap.cli.checkin.RepoObject(code='tabl', name='structure', path='./structure', package=None, files=[])
        doma = sap.cli.checkin.RepoObject(code='doma', name='domain', path='./domain', package=None, files=[])
        dtel = sap.cli.checkin.RepoObject(code='dtel', name='data_element', path='./data_element', package=None,
                                          files=[])

        objects = [clas, dcls, ddls, ddlx, prog, intf, fugr, ttyp, bdef, tabl, dtel, doma]

        deps = sap.cli.checkin._resolve_dependencies(objects)

        self.assertEqual(deps, [[doma, dtel, tabl, ddls, ttyp], [bdef, clas, intf], [prog], [dcls, ddlx, fugr]])

    @patch('sap.cli.checkin._checkin_dependency_group')
    @patch('sap.cli.checkin._resolve_dependencies')
    @patch('sap.cli.checkin._get_config')
    @patch('sap.cli.checkin._load_objects')
    def _do_checkin(self, _, fake_config, fake_resolve_dependencies, fake_checkin_dependency_group, fake_activate, inactive_objects):
        fake_checkin_dependency_group.return_value = inactive_objects
        fake_resolve_dependencies.return_value = [Mock()]
        fake_config.return_value = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(
            FOLDER_LOGIC=sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX
        )

        args = parse_args('package', '$foo')
        exit_code = args.execute(None, args)

        self.assertEqual(exit_code, 0)

    @patch('sap.cli.checkin._activate')
    def test_do_checkin_nothing_to_activate(self, fake_activate):
        self._do_checkin(fake_activate=fake_activate, inactive_objects=Mock(references=[]))
        fake_activate.assert_not_called()

    @patch('sap.cli.checkin._activate')
    def test_do_checkin_with_activate(self, fake_activate):
        inactive_objects = Mock(references=[Mock()])
        self._do_checkin(fake_activate=fake_activate, inactive_objects=inactive_objects)
        self.assertConsoleContents(self.console, stdout='''Checking files ...
Creating packages ...
Creating objects ...
Activating objects ...
''')
        fake_activate.assert_called_once_with(None, inactive_objects, self.console)

    @patch('sap.cli.checkin.checkin_package')
    @patch('sap.cli.checkin._prepare_repository')
    @patch('sap.cli.checkin._get_config')
    @patch('sap.cli.checkin._load_objects')
    def test_do_checkin_preparation_fails(self, _, fake_config, fake_prepare_repository, fake_checkin_package):
        fake_prepare_repository.side_effect = SAPCliError('Cannot check in 1 files - nothing has been changed')
        fake_config.return_value = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(
            FOLDER_LOGIC=sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX
        )

        args = parse_args('package', '$foo')
        exit_code = args.execute(None, args)

        self.assertEqual(exit_code, 1)
        fake_checkin_package.assert_not_called()
        self.assertConsoleContents(self.console, stdout='Checking files ...\n',
                                   stderr='Checkin failed: Cannot check in 1 files - nothing has been changed\n')

    @patch('sap.cli.checkin._checkin_dependency_group')
    @patch('sap.cli.checkin._resolve_dependencies')
    @patch('sap.cli.checkin.checkin_package')
    @patch('sap.cli.checkin._prepare_repository')
    @patch('sap.cli.checkin._get_config')
    @patch('sap.cli.checkin._load_objects')
    def test_do_checkin_uses_prepared_data(self, _, fake_config, fake_prepare_repository, fake_checkin_package,
                                           fake_resolve_dependencies, fake_checkin_dependency_group):
        package = sap.cli.checkin.RepoPackage('$FOO', './package.devc.xml', '.', None)
        group = [Mock()]
        prepared = {'./package.devc.xml': 'prepared package'}
        fake_prepare_repository.return_value = prepared
        fake_resolve_dependencies.return_value = [group]
        fake_checkin_dependency_group.return_value = Mock(references=[])
        fake_config.return_value = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(
            FOLDER_LOGIC=sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX
        )

        args = parse_args('package', '$foo')
        with patch('sap.cli.checkin.Repository.packages', new_callable=PropertyMock, return_value=[package]):
            exit_code = args.execute('connection', args)

        self.assertEqual(exit_code, 0)
        fake_checkin_package.assert_called_once_with('connection', package, args, prepared='prepared package')
        fake_checkin_dependency_group.assert_called_once_with('connection', ANY, group, self.console, None,
                                                              check_before_save=False, prepared=prepared)

    def _resolved_check_before_save(self, *cli_args, env_value=None):
        """Run do_checkin_directory with the given CLI args and return
        the ``check_before_save`` value passed to _checkin_dependency_group.
        """

        captured = {}

        def fake_group(connection, repo, group, console, corrnr, check_before_save=False, prepared=None):
            captured['value'] = check_before_save
            return Mock(references=[])

        env = {} if env_value is None else {'SAPCLI_CHECK_BEFORE_SAVE': env_value}

        with patch('sap.cli.checkin._load_objects'), \
             patch('sap.cli.checkin._resolve_dependencies', return_value=[Mock()]), \
             patch('sap.cli.checkin._get_config') as fake_cfg, \
             patch('sap.cli.checkin._checkin_dependency_group', side_effect=fake_group), \
             patch('os.environ', env):
            fake_cfg.return_value = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(
                FOLDER_LOGIC=sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX
            )

            args = parse_args('package', '$foo', *cli_args)
            args.execute(None, args)

        return captured['value']

    def test_do_checkin_default_disables_pre_check(self):
        self.assertFalse(self._resolved_check_before_save())

    def test_do_checkin_check_flag_enables_pre_check(self):
        self.assertTrue(self._resolved_check_before_save('--check'))

    def test_do_checkin_no_check_flag_overrides_env_true(self):
        self.assertFalse(self._resolved_check_before_save('--no-check', env_value='true'))

    def test_do_checkin_env_true_enables_pre_check(self):
        self.assertTrue(self._resolved_check_before_save(env_value='true'))


class TestActivate(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

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

    def test_devc_file_has_unknown_member(self):
        self.fake_open.return_value = StringIOFile(PACKAGE_DEVC_UNKNOWN_XML)

        with self.assertRaises(SAPCliError) as caught:
            sap.cli.checkin.checkin_package(self.connection, self.repo.packages[0], self.fake_args)

        self.assertEqual(str(caught.exception), 'DEVC does not have the member FUTURE_FIELD')

    @patch('sap.adt.Package')
    @patch('sap.adt.ADTCoreData')
    def test_checkin_package_with_language(self, fake_core_data, fake_package):
        self.fake_open.return_value = StringIOFile(PACKAGE_DEVC_LANGUAGE_XML)
        self.connection.user = 'fake_user'
        package = Mock()
        package.super_package.name = None
        fake_package.return_value = package

        sap.cli.checkin.checkin_package(self.connection, self.repo.packages[0], self.fake_args)

        fake_core_data.assert_called_once_with(language='EN', master_language='EN', responsible='FAKE_USER',
                                               description='Test Package')
        package.create.assert_called_once()

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
        fake_core_data.assert_called_once_with(language='EN', master_language='EN', responsible='FAKE_USER',
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


if __name__ == '__main__':
    unittest.main()

