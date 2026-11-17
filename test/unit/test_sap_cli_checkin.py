#!/usr/bin/env python3

import unittest
from types import SimpleNamespace
from unittest.mock import patch, Mock, call

import sap.adt.checks
import sap.cli.checkin
import sap.errors
import sap.platform.abap.abapgit.handlers
from sap.adt.wb import CheckMessage, CheckMessageList
from sap.errors import SAPCliError
from sap.adt.errors import ExceptionResourceAlreadyExists, ExceptionCheckinFailure
from sap.platform.abap.localrepository import CheckinContext, ObjectCheckinResult, RepoObject, RepoPackage, Repository
from sap.platform.abap.ddic import DEVC

from mock import PatcherTestCase, ConsoleOutputTestCase
from infra import generate_parse_args


parse_args = generate_parse_args(sap.cli.checkin.CommandGroup())


def new_object(code, name, package, handler=None, files=None):
    """Returns a repository object stored in the directory of the package"""

    return RepoObject(code, name, f'{package.dir_path}/{name}.{code}.xml', files or [], package, handler)


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


class TestActivationOrder(unittest.TestCase):

    def test_every_handler_has_activation_order(self):
        file_types = {handler.FILE_TYPE for handler in sap.platform.abap.abapgit.handlers.HANDLERS}

        self.assertEqual(file_types - set(sap.cli.checkin.ACTIVATION_ORDER), set())

    def test_resolve_dependencies(self):
        package = RepoPackage('./src', './src/package.devc.xml', None)

        clas = new_object('clas', 'cl_ass', package)
        intf = new_object('intf', 'if_ace', package)
        prog = new_object('prog', 'program', package)
        fugr = new_object('fugr', 'function_group', package)
        ttyp = new_object('ttyp', 'table_type', package)
        ddls = new_object('ddls', 'cds_view', package)
        dcls = new_object('dcls', 'cds_role', package)
        ddlx = new_object('ddlx', 'cds_ext', package)
        bdef = new_object('bdef', 'cds_bo', package)
        tabl = new_object('tabl', 'structure', package)
        doma = new_object('doma', 'domain', package)
        dtel = new_object('dtel', 'data_element', package)

        objects = [clas, dcls, ddls, ddlx, prog, intf, fugr, ttyp, bdef, tabl, dtel, doma]

        deps = sap.cli.checkin._resolve_dependencies(objects)

        self.assertEqual(deps, [[doma, dtel, tabl, ddls, ttyp], [bdef, clas, intf], [prog], [dcls, ddlx, fugr]])

    def test_resolve_dependencies_nothing(self):
        self.assertEqual(sap.cli.checkin._resolve_dependencies([]), [[], [], [], []])


class TestCheckinGroup(unittest.TestCase):

    def setUp(self):
        self.root = RepoPackage('./src', './src/package.devc.xml', None)
        self.sub = RepoPackage('./src/sub', './src/sub/package.devc.xml', self.root)
        self.package_names = {'./src': '$root', './src/sub': '$root_sub'}

        self.clas_handler = Mock()
        self.clas_handler.checkin.return_value = ObjectCheckinResult(['class', 'class texts'], ['./src/sub/used.abap'])
        self.clas = new_object('clas', 'zcl_foo', self.sub, self.clas_handler)

        self.prog_handler = Mock()
        self.prog_handler.checkin.return_value = ObjectCheckinResult(['program'], [])
        self.prog = new_object('prog', 'zfoo', self.root, self.prog_handler)

        self.prepared = {self.clas.path: 'prepared class', self.prog.path: 'prepared program'}
        self.used_files = set()

    def checkin_group(self, group, corrnr=None, check_before_save=False):
        with patch('sap.adt.objects.ADTObjectReferences') as fake_references:
            inactive = sap.cli.checkin._checkin_dependency_group('connection', group, self.package_names,
                                                                 self.used_files, corrnr, check_before_save,
                                                                 self.prepared, 'observer')

        self.assertIs(inactive, fake_references.return_value)

        return inactive

    def test_checkin_group(self):
        inactive = self.checkin_group([self.clas, self.prog])

        self.clas_handler.checkin.assert_called_once_with(CheckinContext('connection', '$root_sub', None, False, 'observer'),
                                                          self.clas, 'prepared class')
        self.prog_handler.checkin.assert_called_once_with(CheckinContext('connection', '$root', None, False, 'observer'),
                                                          self.prog, 'prepared program')
        self.assertEqual(inactive.add_object.call_args_list, [call('class'), call('class texts'), call('program')])
        self.assertEqual(self.used_files, {'./src/sub/used.abap'})

    def test_checkin_group_passes_options(self):
        self.checkin_group([self.prog], corrnr='420', check_before_save=True)

        self.prog_handler.checkin.assert_called_once_with(CheckinContext('connection', '$root', '420', True, 'observer'),
                                                          self.prog, 'prepared program')

    def test_checkin_group_failure_stops_checkin(self):
        self.clas_handler.checkin.side_effect = ExceptionCheckinFailure('Checkin of adt object failed')

        with self.assertRaises(ExceptionCheckinFailure) as caught:
            self.checkin_group([self.clas, self.prog])

        self.assertEqual(str(caught.exception), 'Checkin of adt object failed')
        self.prog_handler.checkin.assert_not_called()
        self.assertEqual(self.used_files, set())


class TestPrepareRepository(ConsoleOutputTestCase, PatcherTestCase):

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

        self.fake_layout = self.patch('sap.cli.checkin.REPOSITORY_LAYOUT')
        self.fake_layout.prepare_package.return_value = 'prepared package'

        self.intf_handler = Mock()
        self.intf_handler.prepare.return_value = 'prepared intf'
        self.clas_handler = Mock()
        self.clas_handler.prepare.return_value = 'prepared clas'
        self.tabl_handler = Mock()
        self.tabl_handler.prepare.return_value = 'prepared tabl'

        self.package = RepoPackage('./src', './src/package.devc.xml', None)
        self.intf = new_object('intf', 'zif_good', self.package, self.intf_handler)
        self.clas = new_object('clas', 'zcl_bad', self.package, self.clas_handler)
        self.tabl = new_object('tabl', 'zbad', self.package, self.tabl_handler)
        self.repo = Repository([self.package], [self.intf, self.clas, self.tabl], [], None, '/src/')

    def test_prepare_repository(self):
        prepared = sap.cli.checkin._prepare_repository(self.repo, self.console, 'observer')

        self.fake_layout.prepare_package.assert_called_once_with(self.package)
        self.intf_handler.prepare.assert_called_once_with(self.intf, 'observer')
        self.clas_handler.prepare.assert_called_once_with(self.clas, 'observer')
        self.tabl_handler.prepare.assert_called_once_with(self.tabl, 'observer')
        self.assertEqual(prepared, {
            './src/package.devc.xml': 'prepared package',
            './src/zif_good.intf.xml': 'prepared intf',
            './src/zcl_bad.clas.xml': 'prepared clas',
            './src/zbad.tabl.xml': 'prepared tabl',
        })
        self.assertEmptyConsole(self.console)

    def test_prepare_repository_reports_all_problems(self):
        self.fake_layout.prepare_package.side_effect = SAPCliError('DEVC does not have the member FOO')
        self.clas_handler.prepare.side_effect = ExceptionCheckinFailure('No source file for class zcl_bad')
        self.tabl_handler.prepare.side_effect = sap.errors.InputError('Invalid XML for DD02V: syntax error')

        with self.assertRaises(SAPCliError) as caught:
            sap.cli.checkin._prepare_repository(self.repo, self.console, 'observer')

        self.assertEqual(str(caught.exception), 'Cannot check in 3 files - nothing has been changed')
        self.intf_handler.prepare.assert_called_once_with(self.intf, 'observer')
        self.assertConsoleContents(self.console, stderr='''./src/package.devc.xml: DEVC does not have the member FOO
./src/zcl_bad.clas.xml: No source file for class zcl_bad
./src/zbad.tabl.xml: Invalid XML for DD02V: syntax error
''')


class TestCheckIn(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def new_handler(self, code):
        def checkin(context, repo_obj, prepared):
            return ObjectCheckinResult([SimpleNamespace(full_adt_uri=repo_obj.path, name=repo_obj.name)],
                                       list(repo_obj.files))

        handler = Mock()
        handler.prepare.return_value = f'prepared {code}'
        handler.checkin.side_effect = checkin

        return handler

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

        self.root = RepoPackage('./src/', './src/package.devc.xml', None)
        self.sub = RepoPackage('./src/sub', './src/sub/package.devc.xml', self.root)

        self.prog = new_object('prog', 'run_report', self.sub, self.new_handler('prog'),
                               ['./src/sub/run_report.prog.abap'])
        self.fugr = new_object('fugr', 'test_fugr', self.root, self.new_handler('fugr'),
                               ['./src/test_fugr.fugr.module.abap', './src/test_fugr.fugr.include.abap'])
        self.intf = new_object('intf', 'if_strategy', self.sub, self.new_handler('intf'),
                               ['./src/sub/if_strategy.intf.abap'])
        self.doma = new_object('doma', 'zdomain', self.root, self.new_handler('doma'))

        files = ['./src/package.devc.xml', './src/sub/package.devc.xml', './src/README.md',
                 './src/test_fugr.fugr.include.xml', self.prog.path, self.fugr.path, self.intf.path, self.doma.path]
        files += self.prog.files + self.fugr.files + self.intf.files

        self.repo = Repository([self.root, self.sub], [self.prog, self.fugr, self.intf, self.doma], files, 'settings',
                               '/src/')

        self.package_names = {'./src/': '$foo', './src/sub': '$foo_sub'}
        self.devc = DEVC(CTEXT='Test Package')

        self.fake_layout = self.patch('sap.cli.checkin.REPOSITORY_LAYOUT')
        self.fake_layout.load_repository.return_value = self.repo
        self.fake_layout.package_name.side_effect = lambda repo, package, name: self.package_names[package.dir_path]
        self.fake_layout.prepare_package.return_value = self.devc

        self.fake_observer_class = self.patch('sap.cli.checkin.ConsoleObserver')
        self.observer = self.fake_observer_class.return_value

        self.fake_checkin_package = self.patch('sap.cli.checkin.checkin_package')
        self.fake_activate = self.patch('sap.adt.wb.try_mass_activate')
        self.fake_activate.return_value = []

    def test_do_checkin(self):
        args = parse_args('package', '$foo')
        exit_code = args.execute('connection', args)

        self.assertEqual(exit_code, 0)

        self.fake_layout.load_repository.assert_called_once_with(None, sap.cli.checkin.OBJECT_HANDLERS)
        self.assertEqual(self.fake_layout.package_name.call_args_list, [call(self.repo, self.root, '$foo'),
                                                                        call(self.repo, self.sub, '$foo')])

        self.assertEqual(self.fake_checkin_package.call_args_list, [
            call('connection', '$foo', None, self.devc, args),
            call('connection', '$foo_sub', '$foo', self.devc, args),
        ])

        self.fake_observer_class.assert_called_once_with(self.console)

        self.prog.handler.prepare.assert_called_once_with(self.prog, self.observer)
        self.prog.handler.checkin.assert_called_once_with(CheckinContext('connection', '$foo_sub', None, False, self.observer),
                                                          self.prog, 'prepared prog')
        self.fugr.handler.checkin.assert_called_once_with(CheckinContext('connection', '$foo', None, False, self.observer),
                                                          self.fugr, 'prepared fugr')
        self.intf.handler.checkin.assert_called_once_with(CheckinContext('connection', '$foo_sub', None, False, self.observer),
                                                          self.intf, 'prepared intf')
        self.doma.handler.checkin.assert_called_once_with(CheckinContext('connection', '$foo', None, False, self.observer),
                                                          self.doma, 'prepared doma')

        self.assertEqual(self.fake_activate.call_count, 4)

        self.assertConsoleContents(self.console,
                                   stdout='''Checking files ...
Creating packages ...
Creating objects ...
Activating objects ...
Creating objects ...
Activating objects ...
Creating objects ...
Activating objects ...
Creating objects ...
Activating objects ...
''',
                                   stderr='''Using starting-folder: /src/
Unused file: ./src/README.md
Unused file: ./src/test_fugr.fugr.include.xml
''')

    def test_do_checkin_options(self):
        args = parse_args('package', '$foo', 'K900001', '--starting-folder', 'backend', '--check')

        with patch('sap.cli.checkin.os.path.isdir', return_value=True) as fake_isdir:
            exit_code = args.execute('connection', args)

        self.assertEqual(exit_code, 0)
        fake_isdir.assert_called_once_with('./backend/')
        self.fake_layout.load_repository.assert_called_once_with('/backend/', sap.cli.checkin.OBJECT_HANDLERS)
        self.doma.handler.checkin.assert_called_once_with(CheckinContext('connection', '$foo', 'K900001', True, self.observer),
                                                          self.doma, 'prepared doma')

    def test_do_checkin_requested_starting_folder_used(self):
        args = parse_args('package', '$foo', '--starting-folder', '/src/')

        with patch('sap.cli.checkin.os.path.isdir', return_value=True) as fake_isdir:
            exit_code = args.execute('connection', args)

        self.assertEqual(exit_code, 0)
        fake_isdir.assert_called_once_with('./src/')
        self.fake_layout.load_repository.assert_called_once_with('/src/', sap.cli.checkin.OBJECT_HANDLERS)
        self.assertEqual(self.console.caperr, '''Unused file: ./src/README.md
Unused file: ./src/test_fugr.fugr.include.xml
''')

    def test_do_checkin_starting_folder_without_slashes(self):
        args = parse_args('package', '$foo', '--starting-folder', 'src')

        with patch('sap.cli.checkin.os.path.isdir', return_value=True) as fake_isdir:
            exit_code = args.execute('connection', args)

        self.assertEqual(exit_code, 0)
        fake_isdir.assert_called_once_with('./src/')
        self.fake_layout.load_repository.assert_called_once_with('/src/', sap.cli.checkin.OBJECT_HANDLERS)
        self.assertEqual(self.console.caperr, '''Unused file: ./src/README.md
Unused file: ./src/test_fugr.fugr.include.xml
''')

    def test_do_checkin_starting_folder_trailing_slash(self):
        args = parse_args('package', '$foo', '--starting-folder', 'src/')

        with patch('sap.cli.checkin.os.path.isdir', return_value=True) as fake_isdir:
            exit_code = args.execute('connection', args)

        self.assertEqual(exit_code, 0)
        fake_isdir.assert_called_once_with('./src/')
        self.fake_layout.load_repository.assert_called_once_with('/src/', sap.cli.checkin.OBJECT_HANDLERS)

    def test_do_checkin_starting_folder_nested(self):
        args = parse_args('package', '$foo', '--starting-folder', 'abap/src')

        with patch('sap.cli.checkin.os.path.isdir', return_value=True) as fake_isdir:
            exit_code = args.execute('connection', args)

        self.assertEqual(exit_code, 0)
        fake_isdir.assert_called_once_with('./abap/src/')
        self.fake_layout.load_repository.assert_called_once_with('/abap/src/', sap.cli.checkin.OBJECT_HANDLERS)

    def test_do_checkin_starting_folder_root(self):
        args = parse_args('package', '$foo', '--starting-folder', '/')

        with patch('sap.cli.checkin.os.path.isdir', return_value=True) as fake_isdir:
            exit_code = args.execute('connection', args)

        self.assertEqual(exit_code, 0)
        fake_isdir.assert_called_once_with('./')
        self.fake_layout.load_repository.assert_called_once_with('/', sap.cli.checkin.OBJECT_HANDLERS)

    def test_do_checkin_starting_folder_not_folder(self):
        args = parse_args('package', '$foo', '--starting-folder', 'FILE')

        with patch('sap.cli.checkin.os.path.isdir', return_value=False):
            exit_code = args.execute(None, args)

        self.assertEqual(exit_code, 1)
        self.fake_layout.load_repository.assert_not_called()
        self.assertConsoleContents(self.console, stderr='Cannot check-in ABAP objects from "./FILE/": not a directory\n')

    def test_do_checkin_error(self):
        self.fake_layout.load_repository.side_effect = sap.errors.SAPCliError('Load failed.')

        args = parse_args('package', '$foo')
        exit_code = args.execute(None, args)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='Checkin failed: Load failed.\n')

    def test_do_checkin_preparation_fails(self):
        self.intf.handler.prepare.side_effect = ExceptionCheckinFailure('No source file for interface if_strategy')

        args = parse_args('package', '$foo')
        exit_code = args.execute(None, args)

        self.assertEqual(exit_code, 1)
        self.fake_checkin_package.assert_not_called()
        self.doma.handler.checkin.assert_not_called()
        self.assertConsoleContents(self.console, stdout='Checking files ...\n',
                                   stderr='''Using starting-folder: /src/
./src/sub/if_strategy.intf.xml: No source file for interface if_strategy
Checkin failed: Cannot check in 1 files - nothing has been changed
''')

    def test_do_checkin_check_findings(self):
        message = Mock()
        result = Mock(messages=[message, message])
        self.doma.handler.checkin.side_effect = sap.adt.checks.ObjectCheckFindings(Mock(), result)

        args = parse_args('package', '$foo')
        with patch('sap.adt.checks.format_check_message', return_value='zdomain: syntax error') as fake_format:
            exit_code = args.execute(None, args)

        self.assertEqual(exit_code, 1)
        fake_format.assert_called_with(message, None)
        self.fugr.handler.checkin.assert_not_called()
        self.assertConsoleContents(self.console,
                                   stdout='''Checking files ...
Creating packages ...
Creating objects ...
''',
                                   stderr='''Using starting-folder: /src/
zdomain: syntax error
zdomain: syntax error
''')

    def test_do_checkin_nothing_to_activate(self):
        self.repo.objects.clear()

        args = parse_args('package', '$foo')
        exit_code = args.execute(None, args)

        self.assertEqual(exit_code, 0)
        self.fake_activate.assert_not_called()
        self.assertEqual(self.console.capout, '''Checking files ...
Creating packages ...
Creating objects ...
Creating objects ...
Creating objects ...
Creating objects ...
''')

    def test_do_checkin_with_activate(self):
        self.repo.objects[:] = [self.doma]

        args = parse_args('package', '$foo')
        with patch('sap.cli.checkin._activate') as fake_activate:
            exit_code = args.execute('connection', args)

        self.assertEqual(exit_code, 0)
        fake_activate.assert_called_once()
        connection, inactive_objects, console = fake_activate.call_args.args
        self.assertEqual(connection, 'connection')
        self.assertEqual([reference.name for reference in inactive_objects.references], ['ZDOMAIN'])
        self.assertIs(console, self.console)

    def _resolved_check_before_save(self, *cli_args, env_value=None):
        """Run do_checkin_directory with the given CLI args and return
        the ``check_before_save`` value passed to the object handlers.
        """

        env = {} if env_value is None else {'SAPCLI_CHECK_BEFORE_SAVE': env_value}

        with patch('os.environ', env):
            args = parse_args('package', '$foo', *cli_args)
            args.execute(None, args)

        return self.doma.handler.checkin.call_args.args[0].check_before_save

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
        self.connection.user = 'fake_user'
        self.devc = DEVC(CTEXT='Test Package')
        self.fake_args = Mock(software_component='LOCAL', app_component=None, transport_layer=None, corrnr=None)

    @patch('sap.adt.package.Package.create')
    def test_package_already_exists(self, fake_package_create):
        fake_package_create.side_effect = ExceptionResourceAlreadyExists(message='Package already exists.')

        with self.assertLogs(sap.get_logger(), 'INFO') as logs:
            sap.cli.checkin.checkin_package(self.connection, 'checkin-test', None, self.devc, self.fake_args)

        self.assertEqual([record.getMessage() for record in logs.records], ['Package already exists.'])

    @patch('sap.adt.package.Package.create')
    def test_package_create_raises_error(self, fake_package_create):
        fake_package_create.side_effect = SAPCliError('Create error.')

        with self.assertRaises(SAPCliError) as cm:
            sap.cli.checkin.checkin_package(self.connection, 'checkin-test', None, self.devc, self.fake_args)

        self.assertEqual(str(cm.exception), 'Create error.')

    @patch('sap.adt.Package')
    @patch('sap.adt.ADTCoreData')
    def test_checkin_successful(self, fake_core_data, fake_package):
        metadata = Mock()
        fake_core_data.return_value = metadata
        package = Mock()
        package.super_package.name = None
        fake_package.return_value = package

        sap.cli.checkin.checkin_package(self.connection, 'checkin-test', None, self.devc, self.fake_args)

        self.assertConsoleContents(self.console, stdout='Creating Package: checkin-test Test Package\n')
        fake_core_data.assert_called_once_with(language='EN', master_language='EN', responsible='FAKE_USER',
                                               description='Test Package')
        fake_package.assert_called_once_with(self.connection, 'CHECKIN-TEST', metadata=metadata)
        package.set_package_type.assert_called_once_with('development')
        self.assertIsNone(package.super_package.name)
        package.set_software_component.assert_called_once_with('LOCAL')
        package.set_app_component.assert_not_called()
        package.set_transport_layer.assert_not_called()
        package.create.assert_called_once_with(None)

    @patch('sap.adt.Package')
    @patch('sap.adt.ADTCoreData')
    def test_checkin_successful_full(self, _, fake_package):
        package = Mock()
        package.super_package.name = None
        fake_package.return_value = package
        full_fake_args = Mock(software_component='local', app_component='app', transport_layer='trans', corrnr='corrnr')

        sap.cli.checkin.checkin_package(self.connection, 'checkin-test_sub', 'checkin-test', self.devc, full_fake_args)

        self.assertConsoleContents(self.console, stdout='Creating Package: checkin-test_sub Test Package\n')
        self.assertEqual(package.super_package.name, 'CHECKIN-TEST')
        package.set_software_component.assert_called_once_with('LOCAL')
        package.set_app_component.assert_called_once_with('APP')
        package.set_transport_layer.assert_called_once_with('TRANS')
        package.create.assert_called_once_with('corrnr')


if __name__ == '__main__':
    unittest.main()
