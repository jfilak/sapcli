#!/usr/bin/env python3

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, call, patch

import sap
import sap.adt
import sap.adt.errors
import sap.platform.abap.abapgit.fugr
from sap.adt.errors import ExceptionCheckinFailure, ExceptionResourceAlreadyExists, ExceptionResourceCreationFailure
from sap.errors import SAPCliError
from sap.platform.abap.localrepository import CheckinContext, ObjectHandler, RepoObject, RepoPackage, RepositoryObserver
from sap.platform.abap.abapgit.fugr import FunctionGroupHandler, SourceCodeFormat

from mock import Connection, PatcherTestCase, StringIOFile
from fixtures_sap_platform_abap_abapgit_fugr import FUNCTION_GROUP_XML, FUNCTION_GROUP_XML_NO_RFC, \
    FUNCTION_MODULE_CODE_ABAPGIT, FUNCTION_MODULE_CODE_ADT, FUNCTION_MODULE_CODE_NO_PARAMS_ABAPGIT, \
    FUNCTION_MODULE_CODE_NO_PARAMS_ADT, FUNCTION_MODULE_CODE_ALL_PARAMS_ABAPGIT, FUNCTION_MODULE_CODE_ALL_PARAMS_ADT, \
    CHECKOUT_FUNCTION_GROUP_XML, CHECKOUT_FUNCTION_INCLUDE_1_XML, CHECKOUT_FUNCTION_INCLUDE_2_XML, \
    CHECKOUT_FUNCTION_MODULE_1_CODE, CHECKOUT_FUNCTION_MODULE_2_CODE, CHECKOUT_FUNCTION_MODULE_1_CODE_ABAPGIT, \
    CHECKOUT_FUNCTION_MODULE_2_CODE_ABAPGIT


class TestFunctionGroupHandlerIdentity(unittest.TestCase):

    def test_identity(self):
        handler = FunctionGroupHandler()

        self.assertIsInstance(handler, ObjectHandler)
        self.assertEqual(handler.FILE_TYPE, 'fugr')
        self.assertEqual(handler.METADATA_EXT, 'xml')
        self.assertEqual(handler.ADT_TYPES, (sap.adt.FunctionGroup.OBJTYPE.code,))


class TestDownloadAbapGitSource(unittest.TestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def setUp(self):
        super().setUp()
        self.observer = Mock(spec=RepositoryObserver)
        self.fake_write_source = self.patch('sap.platform.abap.abapgit.fugr.write_source')

    def tearDown(self):
        try:
            self.unpatch_all()
        finally:
            super().tearDown()

    def test_download(self):
        translate = Mock(return_value='FUNCTION zfoo.')

        sap.platform.abap.abapgit.fugr.download_abapgit_source(self.observer, 'ZFUGR', 'function module',
                                                               '.fugr.ZFOO', translate, destdir='/repo')

        translate.assert_called_once_with('function module')
        self.fake_write_source.assert_called_once_with(self.observer, 'FUNCTION zfoo.', 'ZFUGR', '.fugr.ZFOO', '/repo')
        self.assertEqual(self.observer.mock_calls, [])

    def test_download_error(self):
        translate = Mock(side_effect=sap.adt.errors.ExceptionResourceNotFound('No such function'))

        sap.platform.abap.abapgit.fugr.download_abapgit_source(self.observer, 'ZFUGR', 'function module',
                                                               '.fugr.ZFOO', translate)

        self.fake_write_source.assert_not_called()
        self.assertEqual(self.observer.mock_calls, [
            call.warning('Download of AbapGit source code failed: No such function'),
        ])


class TestFunctionGroupHandlerCheckout(unittest.TestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    class MockOpenWrite:
        def __init__(self):
            self.content = ''

        def write(self, *args, **kwargs):
            self.content += args[0]

    def mock_function_module(self, conn, name, args):
        return {fn_module.name: fn_module for fn_module in self.fn_modules}[name]

    def mock_include(self, conn, name, args):
        return {include.name: include for include in self.includes}[name]

    def set_up_fixture_objects(self):
        self.fake_include_1 = sap.adt.FunctionInclude(Connection(), 'TEST_INCLUDE_1TOP', self.fake_funcgrp.name)
        self.fake_include_1.connection.get_text = Mock(return_value='Include 1 source code.')
        self.fake_include_1.description = 'Test include 1 description.'
        self.fake_include_2 = sap.adt.FunctionInclude(Connection(), 'TEST_INCLUDE_2', self.fake_funcgrp.name)
        self.fake_include_2.connection.get_text = Mock(return_value='Include 2 source code.')
        self.fake_include_2.description = 'Test include 2 description.'
        self.includes = [self.fake_include_1, self.fake_include_2]

        includeObjtype = sap.adt.FunctionInclude.OBJTYPE
        fake_fun_include_class = self.patch('sap.adt.FunctionInclude')
        fake_fun_include_class.OBJTYPE = includeObjtype
        fake_fun_include_class.side_effect = self.mock_include

        # Fake function modules must correspond to XMLs in fixtures
        self.fake_func_module_1 = sap.adt.FunctionModule(Connection([]), 'TEST_FUNCTION_1', self.fake_funcgrp.name,
                                                         metadata=SimpleNamespace(
                                                             description='Test function 1 description.'))
        self.fake_func_module_1.connection.get_text = Mock(return_value=CHECKOUT_FUNCTION_MODULE_1_CODE)
        self.fake_func_module_2 = sap.adt.FunctionModule(Connection([]), 'TEST_FUNCTION_2', self.fake_funcgrp.name,
                                                         metadata=SimpleNamespace(
                                                             description='Test function 2 description.'))
        self.fake_func_module_2.connection.get_text = Mock(return_value=CHECKOUT_FUNCTION_MODULE_2_CODE)
        self.fake_func_module_2.processing_type = 'rfc'
        self.fn_modules = [self.fake_func_module_1, self.fake_func_module_2]

        moduleObjtype = sap.adt.FunctionModule.OBJTYPE
        fake_func_module_class = self.patch('sap.adt.FunctionModule')
        fake_func_module_class.OBJTYPE = moduleObjtype
        fake_func_module_class.side_effect = self.mock_function_module

        fake_walk = MagicMock(return_value=[('path', 'subpackages', [SimpleNamespace(typ='FUGR/I', name=include.name) for include in self.includes]
                                             + [SimpleNamespace(typ='FUGR/FF', name=fn_module.name) for fn_module in self.fn_modules])])
        self.fake_funcgrp.walk = fake_walk

    def setUp(self) -> None:
        super().setUp()
        self.conn = Connection([])
        self.observer = Mock(spec=RepositoryObserver)
        self.handler = FunctionGroupHandler()

        self.fake_metadata = SimpleNamespace(description='TEST FUNCTION GROUP',
                                             package_reference=SimpleNamespace(name='TEST_PACKAGE'))
        self.fake_funcgrp = sap.adt.FunctionGroup(self.conn, 'TEST_FUNCGRP', metadata=self.fake_metadata)
        self.fake_funcgrp.fix_point_arithmetic = 'true'
        self.fake_funcgrp.active_unicode_check = 'true'
        fake_funcgrp_class = self.patch('sap.adt.FunctionGroup')
        fake_funcgrp_class.return_value = self.fake_funcgrp

    @patch('sap.platform.abap.abapgit.files.open')
    def test_checkout_function_group(self, fake_open):
        self.set_up_fixture_objects()
        fake_write = self.MockOpenWrite()
        fake_open.return_value.__enter__.return_value = fake_write

        fake_download_abap_source = self.patch('sap.platform.abap.abapgit.fugr.download_abap_source')

        self.handler.checkout(self.conn, 'FUGR/F', 'TEST_FUNCGRP', None, self.observer)

        expected_content = CHECKOUT_FUNCTION_INCLUDE_1_XML + CHECKOUT_FUNCTION_INCLUDE_2_XML + CHECKOUT_FUNCTION_MODULE_1_CODE_ABAPGIT + CHECKOUT_FUNCTION_MODULE_2_CODE_ABAPGIT + CHECKOUT_FUNCTION_GROUP_XML
        self.assertEqual(fake_write.content, expected_content)
        fake_download_abap_source.assert_has_calls(
            [call(self.observer, self.fake_funcgrp.name, fn_include, f'.fugr.{fn_include.name}', destdir=None)
             for fn_include in self.includes]
        )

    @patch('sap.platform.abap.abapgit.files.open')
    def test_checkout_function_group_abap(self, fake_open):
        self.set_up_fixture_objects()
        fake_write = self.MockOpenWrite()
        fake_open.return_value.__enter__.return_value = fake_write

        sap.platform.abap.abapgit.fugr.checkout_function_group(self.conn, 'TEST_FUNCGRP', self.observer,
                                                               source_format=SourceCodeFormat.ABAP)

        expected_content = (CHECKOUT_FUNCTION_INCLUDE_1_XML + 'Include 1 source code.' + CHECKOUT_FUNCTION_INCLUDE_2_XML + 'Include 2 source code.' +
                            CHECKOUT_FUNCTION_MODULE_1_CODE + CHECKOUT_FUNCTION_MODULE_2_CODE + CHECKOUT_FUNCTION_GROUP_XML)
        self.assertEqual(fake_write.content, expected_content)

    def test_checkout_function_group_unsupported_type(self):
        self.fake_funcgrp.walk = Mock(return_value=[('path', 'subpackages', [SimpleNamespace(typ='UNSUPPORTED/THIS', name='TEST')])])

        with self.assertRaises(SAPCliError) as cm:
            self.handler.checkout(self.conn, 'FUGR/F', 'TEST_FUNCGRP', None, self.observer)

        self.assertEqual(str(cm.exception), 'Unsupported function group object: UNSUPPORTED/THIS TEST')
        self.assertEqual(self.observer.mock_calls, [call.checking_out('TEST_FUNCGRP')])

    @patch('sap.platform.abap.abapgit.fugr.build_function_group_abap_attributes')
    @patch('sap.platform.abap.abapgit.fugr.build_system_fn_include_abap_attributes')
    @patch('sap.platform.abap.abapgit.fugr.dump_attributes_to_file')
    @patch('sap.platform.abap.abapgit.fugr.download_abap_source')
    def test_checkout_function_group_px_include(self, fake_download, fake_dump, fake_build_include, fake_build_funcgrp):
        self.fake_funcgrp.walk = Mock(return_value=[('path', 'subpackages', [SimpleNamespace(typ='FUGR/PX', name='TESTTOP')])])
        fake_build_include.return_value = 'FAKE_INCLUDE_PARAMS'
        fake_build_funcgrp.return_value = 'FAKE_FUNCGRP_PARAMS'

        self.handler.checkout(self.conn, 'FUGR/F', 'TEST_FUNCGRP', None, self.observer)

        fake_download.assert_called_once()
        fake_dump.assert_has_calls([
            call(self.observer, self.fake_funcgrp.name, 'FAKE_INCLUDE_PARAMS', '.fugr.TESTTOP', '', destdir=None),
            call(self.observer, self.fake_funcgrp.name, 'FAKE_FUNCGRP_PARAMS', '.fugr', 'LCL_OBJECT_FUGR', destdir=None)
        ])

    @patch('sap.platform.abap.abapgit.fugr.build_function_group_abap_attributes')
    @patch('sap.platform.abap.abapgit.fugr.dump_attributes_to_file')
    @patch('sap.platform.abap.abapgit.fugr.download_abap_source')
    def test_checkout_function_group_skip_uxx(self, fake_download, fake_dump, fake_build_funcgrp):
        self.fake_funcgrp.walk = Mock(return_value=[('path', 'subpackages', [SimpleNamespace(typ='FUGR/I', name='TESTUXX')])])

        self.handler.checkout(self.conn, 'FUGR/F', 'TEST_FUNCGRP', None, self.observer)

        fake_download.assert_not_called()
        fake_build_funcgrp.assert_called_once()
        fake_dump.assert_called_once()
        self.assertEqual(self.observer.mock_calls, [
            call.checking_out('TEST_FUNCGRP'),
            call.warning('Skipping system generated "UXX" function group include: TESTUXX.'),
        ])


class TestFunctionGroupHandlerCheckin(unittest.TestCase, PatcherTestCase):

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
        self.observer = Mock(spec=RepositoryObserver)
        self.handler = FunctionGroupHandler()

        self.connection = Mock()
        self.connection.user = 'test_user'


        self.fake_open = self.patch('sap.platform.abap.abapgit.fugr.open')
        self.fake_open.side_effect = [StringIOFile(FUNCTION_GROUP_XML)]

        self.fake_core_data = self.patch('sap.adt.ADTCoreData')

        self.function_group = MagicMock()
        self.fake_function_group = self.patch('sap.adt.FunctionGroup')
        self.fake_function_group.return_value = self.function_group

        self.function_module = MagicMock()
        self.function_module.name = 'TEST_FUNCTION_MODULE'
        self.function_module.lock.return_value = 'lock_handle'
        self.function_module_editor = MagicMock()
        self.function_module_editor.__enter__.return_value = self.function_module_editor
        self.fake_function_module = self.patch('sap.adt.FunctionModule')
        self.fake_function_module.return_value = self.function_module
        self.function_module.open_editor.return_value = self.function_module_editor

        self.function_include = MagicMock()
        self.function_include.name = 'TEST_INCLUDE'
        self.function_include_editor = MagicMock()
        self.function_include_editor.__enter__.return_value = self.function_include_editor
        self.fake_function_include = self.patch('sap.adt.FunctionInclude')
        self.fake_function_include.return_value = self.function_include
        self.function_include.open_editor.return_value = self.function_include_editor

        self.metadata = Mock()
        self.fake_core_data.return_value = self.metadata

        self.package = RepoPackage('/src', '/src/package.devc.xml', None)

        self.fugr_object = RepoObject('fugr', 'test_fugr', '/src/test_fugr.xml',
                                      ['/src/test_fugr.test_function_module.abap', '/src/test_fugr.test_include.abap'],
                                      self.package, self.handler)

    def checkin(self, repo_obj, corrnr=None, check_before_save=False):
        prepared = self.handler.prepare(repo_obj, self.observer)

        context = CheckinContext(self.connection, 'test_package', corrnr, check_before_save, self.observer)
        return self.handler.checkin(context, repo_obj, prepared)

    def test_checkin_fugr_no_files(self):
        fugr_object = RepoObject('fugr', 'test_fugr', '/src/test_fugr.xml', [], self.package, self.handler)

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            self.checkin(fugr_object)

        self.assertEqual(str(cm.exception), 'No source file for function test_function_module')
        self.fake_core_data.assert_not_called()
        self.fake_function_group.assert_not_called()
        self.fake_function_module.assert_not_called()
        self.fake_function_include.assert_not_called()

    def test_checkin_fugr_no_function_module_files(self):
        fugr_object = RepoObject('fugr', 'test_fugr', '/src/test_fugr.xml', ['/src/test_fugr.test_include.abap'], self.package, self.handler)

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            self.checkin(fugr_object)

        self.assertEqual(str(cm.exception), 'No source file for function test_function_module')
        self.fake_core_data.assert_not_called()
        self.fake_function_group.assert_not_called()
        self.fake_function_module.assert_not_called()
        self.fake_function_include.assert_not_called()

    def test_checkin_fugr_no_function_include_files(self):
        fugr_object = RepoObject('fugr', 'test_fugr', '/src/test_fugr.xml', ['/src/test_fugr.test_function_module.abap'], self.package, self.handler)

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            self.checkin(fugr_object)

        self.assertEqual(str(cm.exception), 'No source file for include test_include')
        self.fake_core_data.assert_not_called()
        self.fake_function_group.assert_not_called()
        self.fake_function_module.assert_not_called()
        self.fake_function_include.assert_not_called()

    def test_checkin_fugr_create_error(self):
        # the source files are read before creating the function group
        self.fake_open.side_effect = list(self.fake_open.side_effect) + [StringIOFile('Test include body'),
                                                                         StringIOFile(FUNCTION_MODULE_CODE_ADT)]
        self.function_group.create.side_effect = SAPCliError('Failed to create function group')

        with self.assertRaises(SAPCliError) as cm:
            self.checkin(self.fugr_object)

        self.assertEqual(str(cm.exception), 'Failed to create function group')
        self.function_module.create.assert_not_called()
        self.function_include.create.assert_not_called()

    def test_checkin_fugr_include_create_error(self):
        # the source files are read before creating the function group
        self.fake_open.side_effect = list(self.fake_open.side_effect) + [StringIOFile('Test include body'),
                                                                         StringIOFile(FUNCTION_MODULE_CODE_ADT)]
        self.function_include.create.side_effect = ExceptionResourceCreationFailure('Failed to create function include')

        with self.assertRaises(SAPCliError) as cm:
            self.checkin(self.fugr_object)

        self.assertEqual(str(cm.exception), 'Failed to create function include')
        self.function_module.create.assert_not_called()

    def test_checkin_fugr_module_create_error(self):
        self.fake_open.side_effect = list(self.fake_open.side_effect) + [StringIOFile('Test include body'),
                                                                         StringIOFile(FUNCTION_MODULE_CODE_ADT)]
        self.function_module.create.side_effect = SAPCliError('Failed to create function module')

        with self.assertRaises(SAPCliError) as cm:
            self.checkin(self.fugr_object)

        self.assertEqual(str(cm.exception), 'Failed to create function module')

    def test_checkin_fugr(self):
        self.fake_open.side_effect = list(self.fake_open.side_effect) + [StringIOFile('Test include body'),
                                                                         StringIOFile(FUNCTION_MODULE_CODE_ADT)]

        result = self.checkin(self.fugr_object)

        self.assertEqual(result.abap_objects, [self.function_group, self.function_include, self.function_module])
        self.assertEqual(result.used_files, ['/src/test_fugr.test_include.abap',
                                             '/src/test_fugr.test_function_module.abap'])

        self.fake_core_data.assert_called_once_with(language='EN', master_language='EN', responsible=self.connection.user.upper())
        self.fake_function_group.assert_called_once_with(self.connection, 'TEST_FUGR', package='test_package',
                                                         metadata=self.metadata)
        self.fake_function_module.assert_called_once_with(self.connection, 'TEST_FUNCTION_MODULE', self.function_group.name,
                                                          metadata=self.metadata)
        self.fake_function_include.assert_called_once_with(self.connection, 'TEST_INCLUDE', self.function_group.name,
                                                           metadata=self.metadata)

        self.function_group.create.assert_called_once_with(None)
        self.assertEqual(self.function_group.description, 'Test function group')
        self.function_module.create.assert_called_once_with(None)
        self.assertEqual(self.function_module.description, 'Test function module')
        self.function_include.create.assert_called_once_with(None)

        self.assertEqual(self.function_module.processing_type, 'rfc')

        self.function_module.open_editor.assert_any_call('lock_handle', None)
        self.function_module.open_editor.assert_any_call(corrnr=None)
        self.assertEqual(self.function_module.open_editor.call_count, 2)
        self.function_module_editor.write.assert_called_once_with(FUNCTION_MODULE_CODE_ADT)
        self.function_include.open_editor.assert_called_once_with(corrnr=None)
        self.function_include_editor.write.assert_called_once_with('Test include body')

        self.assertEqual(self.observer.mock_calls, [
            call.creating('Function Group', self.fugr_object.name),
            call.creating('Function Group Include', self.function_include.name),
            call.writing('Function Group Include', self.function_include.name),
            call.creating('Function Module', self.function_module.name),
            call.writing('Function Module', self.function_module.name),
        ])

    def test_checkin_fugr_with_corrnr(self):
        corrnr = '123456'
        self.fake_open.side_effect = list(self.fake_open.side_effect) + [StringIOFile('Test include body'),
                                                                         StringIOFile('Test module body')]

        result = self.checkin(self.fugr_object, corrnr=corrnr)

        self.assertEqual(result.abap_objects, [self.function_group, self.function_include, self.function_module])
        self.function_group.create.assert_called_once_with(corrnr)
        self.function_module.create.assert_called_once_with(corrnr)
        self.function_include.create.assert_called_once_with(corrnr)

        self.function_include.open_editor.assert_called_once_with(corrnr=corrnr)
        self.function_module.open_editor.assert_any_call('lock_handle', corrnr)
        self.function_module.open_editor.assert_any_call(corrnr=corrnr)
        self.assertEqual(self.function_module.open_editor.call_count, 2)

    def test_checkin_fugr_no_rfc(self):
        self.fake_open.side_effect = [StringIOFile(FUNCTION_GROUP_XML_NO_RFC), StringIOFile('Test include'),
                                      StringIOFile('Test function module')]

        result = self.checkin(self.fugr_object)
        self.assertEqual(result.abap_objects, [self.function_group, self.function_include, self.function_module])
        self.assertTrue(isinstance(self.function_module.processing_type, MagicMock))  # processing_type is MagicMock => is not defined

    def test_checkin_fugr_already_created(self):
        self.fake_open.side_effect = list(self.fake_open.side_effect) + [StringIOFile('Test include body'),
                                                                         StringIOFile('Test module body')]
        self.function_group.create.side_effect = ExceptionResourceAlreadyExists('Function group already exists')
        self.function_include.create.side_effect = ExceptionResourceCreationFailure('Function include already exists')
        self.function_module.create.side_effect = ExceptionResourceAlreadyExists('Function module already exists')

        with self.assertLogs(sap.get_logger(), 'INFO') as logs:
            result = self.checkin(self.fugr_object)

        self.assertEqual(result.abap_objects, [self.function_group, self.function_include, self.function_module])
        self.assertEqual([record.getMessage() for record in logs.records],
                         ['Function group already exists',
                          'Function include already exists',
                          'Function module already exists'])

    def test_checkin_fugr_check_before_save(self):
        self.fake_open.side_effect = list(self.fake_open.side_effect) + [StringIOFile('Test include body'),
                                                                         StringIOFile(FUNCTION_MODULE_CODE_ADT)]
        fake_write_source = self.patch('sap.adt.checks.write_source')

        self.checkin(self.fugr_object, check_before_save=True)

        self.assertEqual(fake_write_source.call_args_list, [
            call('Test include body', self.function_include, None,
                 source_label='/src/test_fugr.test_include.abap', check_before_save=True),
            call(FUNCTION_MODULE_CODE_ADT, self.function_module, None,
                 source_label='/src/test_fugr.test_function_module.abap', check_before_save=True),
        ])

    def test_checkin_fugr_abapgit_format(self):
        self.fake_open.side_effect = list(self.fake_open.side_effect) + [StringIOFile('Test include body'),
                                                                         StringIOFile(FUNCTION_MODULE_CODE_ABAPGIT)]
        result = self.checkin(self.fugr_object)

        self.assertEqual(result.abap_objects, [self.function_group, self.function_include, self.function_module])
        self.function_module_editor.write.assert_called_once_with(FUNCTION_MODULE_CODE_ADT)

    def test_checkin_fugr_abapgit_no_parameters(self):
        self.fake_open.side_effect = list(self.fake_open.side_effect) + [StringIOFile('Test include body'),
                                                                         StringIOFile(
                                                                             FUNCTION_MODULE_CODE_NO_PARAMS_ABAPGIT)]
        result = self.checkin(self.fugr_object)

        self.assertEqual(result.abap_objects, [self.function_group, self.function_include, self.function_module])
        self.function_module_editor.write.assert_called_once_with(FUNCTION_MODULE_CODE_NO_PARAMS_ADT)

    def test_checkin_fugr_abapgit_all_parameters(self):
        self.fake_open.side_effect = list(self.fake_open.side_effect) + [StringIOFile('Test include body'),
                                                                         StringIOFile(FUNCTION_MODULE_CODE_ALL_PARAMS_ABAPGIT)]
        result = self.checkin(self.fugr_object)

        self.assertEqual(result.abap_objects, [self.function_group, self.function_include, self.function_module])
        self.function_module_editor.write.assert_called_once_with(FUNCTION_MODULE_CODE_ALL_PARAMS_ADT)

    def test_checkin_fugr_surplus_file_not_used(self):
        fugr_object = RepoObject('fugr', 'test_fugr', '/src/test_fugr.xml', ['/src/test_fugr.test_function_module.abap',
                                                  '/src/test_fugr.test_include.abap',
                                                  '/src/test_fugr.leftover.abap'], self.package, self.handler)
        self.fake_open.side_effect = list(self.fake_open.side_effect) + [StringIOFile('Test include body'),
                                                                         StringIOFile(FUNCTION_MODULE_CODE_ADT)]

        result = self.checkin(fugr_object)

        self.assertEqual(result.used_files, ['/src/test_fugr.test_include.abap',
                                             '/src/test_fugr.test_function_module.abap'])


class TestFunctionGroupHandlerLocate(unittest.TestCase):

    def test_not_supported(self):
        handler = FunctionGroupHandler()
        fugr_object = RepoObject('fugr', 'zfugr', './src/zfugr.fugr.xml', ['./src/zfugr.fugr.zfunction.abap'],
                                 RepoPackage('./src', './src/package.devc.xml', None), handler)

        self.assertIsNone(handler.locate(fugr_object, 'source/main', 1))


if __name__ == '__main__':
    unittest.main()
