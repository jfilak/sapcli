#!/usr/bin/env python3

import base64
import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

import sap
import sap.adt
import sap.adt.checks
import sap.adt.errors
import sap.errors
from sap.adt.marshalling import Marshal

from mock import Connection, Response, Request
from fixtures_adt_checks import (
    ADT_XML_CHECK_REPORTERS,
    ADT_XML_RUN_CHECK_2_REPORTERS,
    ADT_XML_RUN_OBJECT_CHECK_RESPONSE_ERRORS,
    ADT_XML_RUN_OBJECT_CHECK_RESPONSE_WARNINGS_ONLY,
    ADT_XML_RUN_OBJECT_CHECK_RESPONSE_CLEAN,
    ADT_XML_RUN_CLASS_PARTS_CHECK_RESPONSE_ERRORS,
)


FIXTURE_TWO_CLASSES_REQUEST = '''<?xml version="1.0" encoding="UTF-8"?>
<chkrun:checkObjectList xmlns:chkrun="http://www.sap.com/adt/checkrun" xmlns:adtcore="http://www.sap.com/adt/core">
<chkrun:checkObject adtcore:uri="/sap/bc/adt/oo/classes/cl_first" chkrun:version="active"/>
<chkrun:checkObject adtcore:uri="/sap/bc/adt/oo/classes/cl_second" chkrun:version="active"/>
</chkrun:checkObjectList>'''


class TestFetchReporters(unittest.TestCase):

    def test_fech_reporters_ok(self):
        connection = Connection([Response(status_code=200,
                                          headers={'Content-Type': 'application/vnd.sap.adt.reporters+xml'},
                                          text=ADT_XML_CHECK_REPORTERS)])

        result = sap.adt.checks.fetch_reporters(connection)

        self.assertIsInstance(result, list)
        self.assertEqual(3, len(result))

        self.assertEqual(result[0].name, 'abapCheckRun')
        self.assertEqual(result[1].name, 'abapPackageCheck')
        self.assertEqual(result[2].name, 'tableStatusCheck')

        self.assertEqual(result[0].supported_types, ['WDYN*', 'CLAS*', 'WGRP'])
        self.assertEqual(result[1].supported_types, ['PROG*', 'INTF*', 'HTTP'])
        self.assertEqual(result[2].supported_types, ['TABL/DT'])


class TestReporter(unittest.TestCase):

    def test_supports_type_and_obj(self):
        reporter = sap.adt.checks.Reporter()
        reporter.name = 'mock'
        reporter.supported_types = 'CLAS*'
        reporter.supported_types = 'TABL/DB'

        self.assertTrue(reporter.supports_type('CLAS'))
        self.assertTrue(reporter.supports_type('CLAS/OO'))
        self.assertTrue(reporter.supports_type('TABL/DB'))

        self.assertFalse(reporter.supports_type('TABL'))
        self.assertFalse(reporter.supports_type('TABL/VW'))

        connection = Mock()
        self.assertTrue(reporter.supports_object(sap.adt.Class(connection, 'CL_FOO')))


class TestCheckObjectLiss(unittest.TestCase):

    def test_serialize(self):
        connection = Connection()

        obj_list = sap.adt.checks.CheckObjectList()
        obj_list.add_object(sap.adt.Class(connection, 'CL_FIRST'))
        obj_list.add_object(sap.adt.Class(connection, 'CL_SECOND'))

        xml_obj_list = Marshal().serialize(obj_list)

        self.maxDiff = None
        self.assertEqual(xml_obj_list, FIXTURE_TWO_CLASSES_REQUEST)

    def test_object_list_add_uri(self):
        connection = Connection()

        obj_list = sap.adt.checks.CheckObjectList()
        obj_list.add_uri(sap.adt.Class(connection, 'CL_FIRST').full_adt_uri)
        obj_list.add_uri(sap.adt.Class(connection, 'CL_SECOND').full_adt_uri)

        xml_obj_list = Marshal().serialize(obj_list)

        self.maxDiff = None
        self.assertEqual(xml_obj_list, FIXTURE_TWO_CLASSES_REQUEST)

    def test_object_list_iter(self):
        obj_list = sap.adt.checks.CheckObjectList()
        obj_list.add_uri('/1/uri')
        obj_list.add_uri('/2/uri')

        self.assertEqual(['/1/uri', '/2/uri'], [obj.uri for obj in obj_list])


class TestRunForObjects(unittest.TestCase):

    def test_2_reportes_2_classes(self):
        connection = Connection([Response(status_code=200,
                                          content_type='application/vnd.sap.adt.checkmessages+xml; charset=utf-8',
                                          text=ADT_XML_RUN_CHECK_2_REPORTERS)])

        reporter = sap.adt.checks.Reporter('abapCheckRun')
        reporter.supported_types = '*'

        reports = sap.adt.checks.run_for_supported_objects(connection, reporter,
                                                           [sap.adt.Class(connection, 'CL_FIRST'),
                                                            sap.adt.Class(connection, 'CL_SECOND')])

        self.assertEqual(connection.mock_methods(), [('POST', '/sap/bc/adt/checkruns')])
        self.assertEqual(connection.execs[0].body, FIXTURE_TWO_CLASSES_REQUEST)

        self.assertEqual(['abapCheckRun', 'tableStatusCheck'], [report.reporter for report in reports])
        self.assertEqual(['First', 'Second'], [msg.short_text for msg in reports[0].messages])
        self.assertEqual(['Third', 'Fourth'], [msg.short_text for msg in reports[1].messages])


class TestCheckObjectWithArtifacts(unittest.TestCase):

    def test_add_object_with_source_strips_trailing_newline_and_base64_encodes(self):
        connection = Connection()
        source = 'CLASS cl_foo DEFINITION PUBLIC.\nENDCLASS.\n'

        obj_list = sap.adt.checks.CheckObjectList()
        obj_list.add_object_with_source(sap.adt.Class(connection, 'CL_FOO'), source)

        self.assertEqual(len(obj_list.objects), 1)
        check_object = obj_list.objects[0]

        self.assertEqual(check_object.uri, '/sap/bc/adt/oo/classes/cl_foo')
        self.assertEqual(check_object.chkrun_version, 'active')
        self.assertIsNotNone(check_object.artifacts)
        self.assertEqual(len(check_object.artifacts.items), 1)

        artifact = check_object.artifacts.items[0]
        self.assertEqual(artifact.uri, '/sap/bc/adt/oo/classes/cl_foo/source/main')
        self.assertEqual(artifact.content_type, 'text/plain; charset=utf-8')

        expected_b64 = base64.b64encode(
            b'CLASS cl_foo DEFINITION PUBLIC.\nENDCLASS.'
        ).decode('ascii')
        self.assertEqual(artifact.content, expected_b64)

    def test_add_object_with_source_of_include_with_master(self):
        connection = Connection()

        obj_list = sap.adt.checks.CheckObjectList()
        obj_list.add_object_with_source(sap.adt.Include(connection, 'ZHELLO_INCLUDE', master='ZHELLO_WORLD'),
                                        'WRITE 1.')

        check_object = obj_list.objects[0]
        self.assertEqual(check_object.uri, '/sap/bc/adt/programs/includes/zhello_include'
                                           '?context=%2Fsap%2Fbc%2Fadt%2Fprograms%2Fprograms%2Fzhello_world')

        artifact = check_object.artifacts.items[0]
        self.assertEqual(artifact.uri, '/sap/bc/adt/programs/includes/zhello_include/source/main'
                                       '?context=%2Fsap%2Fbc%2Fadt%2Fprograms%2Fprograms%2Fzhello_world')

    def test_add_object_with_source_serializes_with_artifacts_block(self):
        connection = Connection()

        obj_list = sap.adt.checks.CheckObjectList()
        obj_list.add_object_with_source(sap.adt.Class(connection, 'CL_FOO'), 'REPORT zfoo.')

        xml = Marshal().serialize(obj_list)

        self.assertIn('<chkrun:artifacts>', xml)
        self.assertIn('<chkrun:artifact ', xml)
        self.assertIn('chkrun:uri="/sap/bc/adt/oo/classes/cl_foo/source/main"', xml)
        self.assertIn('<chkrun:content>UkVQT1JUIHpmb28u</chkrun:content>', xml)

    def test_add_object_with_sources_of_class_parts(self):
        connection = Connection()
        clas = sap.adt.Class(connection, 'CL_FOO')

        obj_list = sap.adt.checks.CheckObjectList()
        obj_list.add_object_with_sources(clas, [(clas, 'REPORT zfoo.\n'),
                                                (clas.definitions, 'DEFS.'),
                                                (clas.test_classes, '')])

        self.assertEqual(Marshal().serialize(obj_list), '''<?xml version="1.0" encoding="UTF-8"?>
<chkrun:checkObjectList xmlns:chkrun="http://www.sap.com/adt/checkrun" xmlns:adtcore="http://www.sap.com/adt/core">
<chkrun:checkObject adtcore:uri="/sap/bc/adt/oo/classes/cl_foo" chkrun:version="active">
<chkrun:artifacts>
<chkrun:artifact chkrun:contentType="text/plain; charset=utf-8" chkrun:uri="/sap/bc/adt/oo/classes/cl_foo/source/main">
<chkrun:content>UkVQT1JUIHpmb28u</chkrun:content>
</chkrun:artifact>
<chkrun:artifact chkrun:contentType="text/plain; charset=utf-8" chkrun:uri="/sap/bc/adt/oo/classes/cl_foo/includes/definitions">
<chkrun:content>REVGUy4=</chkrun:content>
</chkrun:artifact>
<chkrun:artifact chkrun:contentType="text/plain; charset=utf-8" chkrun:uri="/sap/bc/adt/oo/classes/cl_foo/includes/testclasses">
<chkrun:content></chkrun:content>
</chkrun:artifact>
</chkrun:artifacts>
</chkrun:checkObject>
</chkrun:checkObjectList>''')

    def test_add_object_with_sources_version(self):
        connection = Connection()
        clas = sap.adt.Class(connection, 'CL_FOO')

        obj_list = sap.adt.checks.CheckObjectList()
        check_object = obj_list.add_object_with_sources(clas, [(clas, 'REPORT zfoo.')], version='inactive')

        self.assertIs(obj_list.objects[0], check_object)
        self.assertEqual(check_object.chkrun_version, 'inactive')

    def test_source_artifact_uri_of_class_include(self):
        clas = sap.adt.Class(Connection(), 'CL_FOO')

        self.assertEqual(sap.adt.checks.source_artifact_uri(clas.test_classes),
                         '/sap/bc/adt/oo/classes/cl_foo/includes/testclasses')

    def test_source_artifact_uri_of_class_macros(self):
        clas = sap.adt.Class(Connection(), 'CL_FOO')

        self.assertEqual(sap.adt.checks.source_artifact_uri(clas.macros),
                         '/sap/bc/adt/oo/classes/cl_foo/includes/macros')

    def test_source_artifact_uri_of_include_with_master(self):
        include = sap.adt.Include(Connection(), 'ZHELLO_INCLUDE', master='ZHELLO_WORLD')

        self.assertEqual(sap.adt.checks.source_artifact_uri(include),
                         '/sap/bc/adt/programs/includes/zhello_include/source/main'
                         '?context=%2Fsap%2Fbc%2Fadt%2Fprograms%2Fprograms%2Fzhello_world')

    def test_plain_add_object_does_not_emit_artifacts_node(self):
        connection = Connection()

        obj_list = sap.adt.checks.CheckObjectList()
        obj_list.add_object(sap.adt.Class(connection, 'CL_FOO'))

        xml = Marshal().serialize(obj_list)

        self.assertNotIn('<chkrun:artifacts', xml)


class TestCheckMessageCodeDeserialisation(unittest.TestCase):

    def test_code_attribute_is_parsed(self):
        # pylint: disable=no-value-for-parameter
        reports = sap.adt.checks.CheckReportList()
        Marshal.deserialize(ADT_XML_RUN_OBJECT_CHECK_RESPONSE_ERRORS, reports)

        messages = reports.items[0].messages.items
        self.assertEqual([m.code for m in messages], ['SYNTAX(001)', 'DEPRECATION(002)'])


class TestFormatCheckMessage(unittest.TestCase):

    def _make_message(self, uri, typ, code, text):
        msg = sap.adt.checks.CheckMessage()
        msg.uri = uri
        msg.typ = typ
        msg.code = code
        msg.short_text = text
        return msg

    def test_with_source_label(self):
        msg = self._make_message(
            '/sap/bc/adt/oo/classes/cl_foo/source/main#start=27,2;end=27,15',
            'E', 'SYNTAX(001)', 'Bad variable',
        )
        self.assertEqual(
            sap.adt.checks.format_check_message(msg, source_label='src/cl_foo.clas.abap'),
            'src/cl_foo.clas.abap:27:2: E SYNTAX(001): Bad variable',
        )

    def test_without_source_label(self):
        msg = self._make_message(
            '/sap/bc/adt/oo/classes/cl_foo/source/main#start=27,2;end=27,15',
            'E', 'SYNTAX(001)', 'Bad variable',
        )
        self.assertEqual(
            sap.adt.checks.format_check_message(msg),
            'cl_foo:27:2: E SYNTAX(001): Bad variable',
        )

    def test_start_without_end(self):
        msg = self._make_message(
            '/sap/bc/adt/oo/classes/zcl_victorious_macros/includes/macros#start=2,2',
            'E', 'DEFINE(004)',
            'Open macro definition at end of source code: DEFINE VICTORIOUS was not closed with END-OF-DEFINITION.',
        )
        self.assertEqual(
            sap.adt.checks.format_check_message(msg),
            'zcl_victorious_macros/includes/macros:2:2: E DEFINE(004): '
            'Open macro definition at end of source code: DEFINE VICTORIOUS was not closed with END-OF-DEFINITION.',
        )

    def test_missing_code_omits_code_segment(self):
        msg = self._make_message(
            '/sap/bc/adt/oo/classes/cl_foo/source/main#start=5,1;end=5,3',
            'W', None, 'Unused',
        )
        self.assertEqual(
            sap.adt.checks.format_check_message(msg),
            'cl_foo:5:1: W: Unused',
        )


class TestRunObjectCheck(unittest.TestCase):

    def _make_connection(self, response_text):
        return Connection([Response(status_code=200,
                                    content_type='application/vnd.sap.adt.checkmessages+xml; charset=utf-8',
                                    text=response_text)])

    def test_errors_present(self):
        connection = self._make_connection(ADT_XML_RUN_OBJECT_CHECK_RESPONSE_ERRORS)
        clas = sap.adt.Class(connection, 'CL_FOO')

        result = sap.adt.checks.run_object_check(clas, 'CLASS cl_foo DEFINITION.\nENDCLASS.\n')

        self.assertTrue(result.has_errors)
        self.assertTrue(result.has_warnings)
        messages = list(result.messages)
        self.assertEqual([m.typ for m in messages], ['E', 'W'])
        self.assertEqual([m.code for m in messages], ['SYNTAX(001)', 'DEPRECATION(002)'])

        self.assertEqual(connection.mock_methods(), [('POST', '/sap/bc/adt/checkruns')])
        self.assertEqual(connection.execs[0].params, {'reporters': 'abapCheckRun'})

    def test_warnings_only(self):
        connection = self._make_connection(ADT_XML_RUN_OBJECT_CHECK_RESPONSE_WARNINGS_ONLY)
        clas = sap.adt.Class(connection, 'CL_FOO')

        result = sap.adt.checks.run_object_check(clas, 'REPORT zfoo.')

        self.assertFalse(result.has_errors)
        self.assertTrue(result.has_warnings)

    def test_clean(self):
        connection = self._make_connection(ADT_XML_RUN_OBJECT_CHECK_RESPONSE_CLEAN)
        clas = sap.adt.Class(connection, 'CL_FOO')

        result = sap.adt.checks.run_object_check(clas, 'REPORT zfoo.')

        self.assertFalse(result.has_errors)
        self.assertFalse(result.has_warnings)
        self.assertEqual(list(result.messages), [])


class TestRunObjectPartsCheck(unittest.TestCase):

    def test_one_request_with_all_parts(self):
        connection = Connection([Response(status_code=200,
                                          content_type='application/vnd.sap.adt.checkmessages+xml; charset=utf-8',
                                          text=ADT_XML_RUN_CLASS_PARTS_CHECK_RESPONSE_ERRORS)])
        clas = sap.adt.Class(connection, 'CL_FOO')

        result = sap.adt.checks.run_object_parts_check(clas, [(clas, 'REPORT zfoo.'), (clas.test_classes, '')])

        self.assertTrue(result.has_errors)
        self.assertEqual(connection.mock_methods(), [('POST', '/sap/bc/adt/checkruns')])
        self.assertEqual(connection.execs[0].params, {'reporters': 'abapCheckRun'})
        self.assertIn('adtcore:uri="/sap/bc/adt/oo/classes/cl_foo" chkrun:version="active"', connection.execs[0].body)
        self.assertIn('chkrun:uri="/sap/bc/adt/oo/classes/cl_foo/source/main"', connection.execs[0].body)
        self.assertIn('chkrun:uri="/sap/bc/adt/oo/classes/cl_foo/includes/testclasses"', connection.execs[0].body)


class TestObjectCheckFindings(unittest.TestCase):

    def _make_connection(self, response_text):
        return Connection([Response(status_code=200,
                                    content_type='application/vnd.sap.adt.checkmessages+xml; charset=utf-8',
                                    text=response_text)])

    def test_str_renders_messages_without_raw_uri(self):
        connection = self._make_connection(ADT_XML_RUN_OBJECT_CHECK_RESPONSE_ERRORS)
        clas = sap.adt.Class(connection, 'CL_FOO')
        result = sap.adt.checks.run_object_check(clas, 'foo')

        exc = sap.adt.checks.ObjectCheckFindings(clas, result)
        rendered = str(exc)

        # The rendered string is a sequence of compiler-style finding
        # lines with no header prefix - the entry-point handler already
        # prints "Exception (ObjectCheckFindings):", and the object name
        # is already part of every location label.
        self.assertNotIn('Object check failed', rendered)
        self.assertIn('cl_foo:27:2: E SYNTAX(001): Variable "FOO" is not type-compatible', rendered)
        self.assertIn('cl_foo:45:1: W DEPRECATION(002): Statement is deprecated', rendered)
        self.assertNotIn('/sap/bc/adt/', rendered)
        self.assertNotIn('#start=', rendered)

    def test_str_uses_source_label_when_provided(self):
        connection = self._make_connection(ADT_XML_RUN_OBJECT_CHECK_RESPONSE_ERRORS)
        clas = sap.adt.Class(connection, 'CL_FOO')
        result = sap.adt.checks.run_object_check(clas, 'foo')

        exc = sap.adt.checks.ObjectCheckFindings(clas, result, source_label='src/cl_foo.clas.abap')
        rendered = str(exc)

        self.assertIn('src/cl_foo.clas.abap:27:2: E SYNTAX(001)', rendered)
        self.assertNotIn('cl_foo:27:2:', rendered)

    def test_str_uses_source_labels_of_parts(self):
        connection = self._make_connection(ADT_XML_RUN_CLASS_PARTS_CHECK_RESPONSE_ERRORS)
        clas = sap.adt.Class(connection, 'CL_FOO')
        result = sap.adt.checks.run_object_parts_check(clas, [(clas, 'foo')])

        exc = sap.adt.checks.ObjectCheckFindings(clas, result, source_labels={
            '/sap/bc/adt/oo/classes/cl_foo/source/main': 'src/cl_foo.clas.abap',
            '/sap/bc/adt/oo/classes/cl_foo/includes/testclasses': 'src/cl_foo.clas.testclasses.abap',
        })

        self.assertEqual(str(exc), 'src/cl_foo.clas.testclasses.abap:8:72: E MESSAGE(G$S): Method "GET_VALUX" does not exist.\n'
                                   'src/cl_foo.clas.abap:3:1: W OBSOLETE(001): Obsolete syntax\n'
                                   'cl_foo/includes/definitions:1:7: E SYNTAX(002): Unknown type')

    def test_str_uses_source_label_for_parts_without_label(self):
        connection = self._make_connection(ADT_XML_RUN_CLASS_PARTS_CHECK_RESPONSE_ERRORS)
        clas = sap.adt.Class(connection, 'CL_FOO')
        result = sap.adt.checks.run_object_parts_check(clas, [(clas, 'foo')])

        exc = sap.adt.checks.ObjectCheckFindings(clas, result, source_label='src/cl_foo', source_labels={
            '/sap/bc/adt/oo/classes/cl_foo/includes/testclasses': 'src/cl_foo.clas.testclasses.abap',
        })

        self.assertEqual(str(exc), 'src/cl_foo.clas.testclasses.abap:8:72: E MESSAGE(G$S): Method "GET_VALUX" does not exist.\n'
                                   'src/cl_foo:3:1: W OBSOLETE(001): Obsolete syntax\n'
                                   'src/cl_foo:1:7: E SYNTAX(002): Unknown type')

    def test_str_source_labels_ignore_query_and_case(self):
        connection = self._make_connection(ADT_XML_RUN_CLASS_PARTS_CHECK_RESPONSE_ERRORS)
        clas = sap.adt.Class(connection, 'CL_FOO')
        result = sap.adt.checks.run_object_parts_check(clas, [(clas, 'foo')])

        exc = sap.adt.checks.ObjectCheckFindings(clas, result, source_labels={
            '/sap/bc/adt/oo/classes/CL_FOO/includes/testclasses?context=foo': 'src/cl_foo.clas.testclasses.abap',
        })

        self.assertIn('src/cl_foo.clas.testclasses.abap:8:72: E MESSAGE(G$S)', str(exc))

    def test_source_labels_are_normalized(self):
        exc = sap.adt.checks.ObjectCheckFindings(Mock(), Mock(), source_labels={
            '/sap/bc/adt/oo/classes/CL_FOO/source/main?context=foo': 'src/cl_foo.clas.abap',
        })

        self.assertEqual(exc.source_labels, {'/sap/bc/adt/oo/classes/cl_foo/source/main': 'src/cl_foo.clas.abap'})


def new_adt_object():
    adt_object = MagicMock()
    editor = MagicMock()
    editor.__enter__.return_value = editor
    adt_object.open_editor.return_value = editor

    return (adt_object, editor)


class TestWriteSource(unittest.TestCase):

    def test_default_skips_pre_check(self):
        adt_object, editor = new_adt_object()

        with patch('sap.adt.checks.run_object_check') as fake_check:
            sap.adt.checks.write_source('CODE', adt_object)

        fake_check.assert_not_called()
        adt_object.open_editor.assert_called_once_with(corrnr=None)
        editor.write.assert_called_once_with('CODE')

    def test_corrnr(self):
        adt_object, editor = new_adt_object()

        sap.adt.checks.write_source('CODE', adt_object, corrnr='K900001')

        adt_object.open_editor.assert_called_once_with(corrnr='K900001')
        editor.write.assert_called_once_with('CODE')

    def test_check_before_save_true_runs_pre_check(self):
        adt_object, editor = new_adt_object()

        bad_result = SimpleNamespace(has_errors=True, messages=iter([]))

        with patch('sap.adt.checks.run_object_check', return_value=bad_result):
            with self.assertRaises(sap.adt.checks.ObjectCheckFindings) as cm:
                sap.adt.checks.write_source('CODE', adt_object,
                                           source_label='src/foo.clas.abap',
                                                check_before_save=True)

        self.assertEqual(cm.exception.source_label, 'src/foo.clas.abap')
        editor.write.assert_not_called()

    def test_check_before_save_without_errors_writes(self):
        adt_object, editor = new_adt_object()

        clean_result = SimpleNamespace(has_errors=False, messages=iter([]))

        with patch('sap.adt.checks.run_object_check', return_value=clean_result) as fake_check:
            sap.adt.checks.write_source('CODE', adt_object, check_before_save=True)

        fake_check.assert_called_once_with(adt_object, 'CODE')
        editor.write.assert_called_once_with('CODE')

    def test_failed_put_runs_check_and_raises_findings(self):
        adt_object, editor = new_adt_object()
        editor.write.side_effect = sap.adt.errors.ExceptionResourceSaveFailure('PUT failed')

        bad_result = SimpleNamespace(has_errors=True, messages=iter([]))

        with patch('sap.adt.checks.run_object_check', return_value=bad_result) as fake_check:
            with self.assertRaises(sap.adt.checks.ObjectCheckFindings) as cm:
                sap.adt.checks.write_source('CODE', adt_object,
                                           source_label='src/foo.clas.abap')

        # Pre-check is off (default), so the only invocation is the
        # post-PUT recheck triggered by ExceptionResourceSaveFailure.
        fake_check.assert_called_once()
        self.assertEqual(cm.exception.source_label, 'src/foo.clas.abap')

    def test_failed_put_with_clean_check_reraises_original(self):
        adt_object, editor = new_adt_object()
        editor.write.side_effect = sap.adt.errors.ExceptionResourceSaveFailure('locked')

        clean_result = SimpleNamespace(has_errors=False, messages=iter([]))

        with patch('sap.adt.checks.run_object_check', return_value=clean_result) as fake_check:
            with self.assertRaises(sap.adt.errors.ExceptionResourceSaveFailure):
                sap.adt.checks.write_source('CODE', adt_object)

        fake_check.assert_called_once()

    def test_failed_put_with_failed_check_reraises_original(self):
        adt_object, editor = new_adt_object()
        save_failure = sap.adt.errors.ExceptionResourceSaveFailure('locked')
        editor.write.side_effect = save_failure

        check_failure = sap.errors.SAPCliError('check run failed')

        with patch('sap.adt.checks.run_object_check', side_effect=check_failure) as fake_check:
            with self.assertRaises(sap.adt.errors.ExceptionResourceSaveFailure) as cm:
                sap.adt.checks.write_source('CODE', adt_object)

        fake_check.assert_called_once()
        self.assertIs(cm.exception, save_failure)

    def test_failed_put_without_check_after_failed_save_reraises_original(self):
        adt_object, editor = new_adt_object()
        save_failure = sap.adt.errors.ExceptionResourceSaveFailure('locked')
        editor.write.side_effect = save_failure

        with patch('sap.adt.checks.run_object_check') as fake_check:
            with self.assertRaises(sap.adt.errors.ExceptionResourceSaveFailure) as cm:
                sap.adt.checks.write_source('CODE', adt_object, check_after_failed_save=False)

        fake_check.assert_not_called()
        self.assertIs(cm.exception, save_failure)


if __name__ == '__main__':
    unittest.main(verbosity=100)
