#!/usr/bin/env python3

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import sap.adt.checks
import sap.adt.errors
import sap.fileformat.adt


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
            sap.fileformat.adt.write_source('CODE', adt_object)

        fake_check.assert_not_called()
        adt_object.open_editor.assert_called_once_with(corrnr=None)
        editor.write.assert_called_once_with('CODE')

    def test_corrnr(self):
        adt_object, editor = new_adt_object()

        sap.fileformat.adt.write_source('CODE', adt_object, corrnr='K900001')

        adt_object.open_editor.assert_called_once_with(corrnr='K900001')
        editor.write.assert_called_once_with('CODE')

    def test_check_before_save_true_runs_pre_check(self):
        adt_object, editor = new_adt_object()

        bad_result = SimpleNamespace(has_errors=True, messages=iter([]))

        with patch('sap.adt.checks.run_object_check', return_value=bad_result):
            with self.assertRaises(sap.adt.checks.ObjectCheckFindings) as cm:
                sap.fileformat.adt.write_source('CODE', adt_object,
                                                source_label='src/foo.clas.abap',
                                                check_before_save=True)

        self.assertEqual(cm.exception.source_label, 'src/foo.clas.abap')
        editor.write.assert_not_called()

    def test_check_before_save_without_errors_writes(self):
        adt_object, editor = new_adt_object()

        clean_result = SimpleNamespace(has_errors=False, messages=iter([]))

        with patch('sap.adt.checks.run_object_check', return_value=clean_result) as fake_check:
            sap.fileformat.adt.write_source('CODE', adt_object, check_before_save=True)

        fake_check.assert_called_once_with(adt_object, 'CODE')
        editor.write.assert_called_once_with('CODE')

    def test_failed_put_runs_check_and_raises_findings(self):
        adt_object, editor = new_adt_object()
        editor.write.side_effect = sap.adt.errors.ExceptionResourceSaveFailure('PUT failed')

        bad_result = SimpleNamespace(has_errors=True, messages=iter([]))

        with patch('sap.adt.checks.run_object_check', return_value=bad_result) as fake_check:
            with self.assertRaises(sap.adt.checks.ObjectCheckFindings) as cm:
                sap.fileformat.adt.write_source('CODE', adt_object,
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
                sap.fileformat.adt.write_source('CODE', adt_object)

        fake_check.assert_called_once()


if __name__ == '__main__':
    unittest.main()
