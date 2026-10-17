#!/usr/bin/env python3

import unittest
from unittest.mock import patch, Mock

from sap.errors import SAPCliError
from sap.rfc.bapi import BAPIError
from sap.platform.abap.abapgit_rfc import (
    abap_string_literal,
    build_link_code,
    build_pull_code,
    parse_return,
    link,
    pull,
)

from fixtures_sap_platform_abap_abapgit_rfc import (
    LINK_ABAP_CODE,
    LINK_OUTPUT_OK,
    LINK_OUTPUT_ERROR,
    LINK_OUTPUT_NOISE,
    LINK_OUTPUT_TRUNCATED,
    PULL_ABAP_CODE,
    PULL_OUTPUT_OK,
    PULL_OUTPUT_ERROR,
)


class TestAbapStringLiteral(unittest.TestCase):

    def test_plain(self):
        self.assertEqual(abap_string_literal('foo'), '`foo`')

    def test_empty(self):
        self.assertEqual(abap_string_literal(''), '``')

    def test_backtick_doubled(self):
        self.assertEqual(abap_string_literal('a`b'), '`a``b`')

    def test_template_characters_kept(self):
        self.assertEqual(abap_string_literal("|{x}'\\"), "`|{x}'\\`")

    def test_long_value_split(self):
        value = 'a' * 100 + 'b' * 100 + 'c'
        expected = '`' + 'a' * 100 + '`\n  && `' + 'b' * 100 + '`\n  && `c`'

        self.assertEqual(abap_string_literal(value), expected)

    def test_long_value_split_before_escaping(self):
        value = '`' * 101
        expected = '`' + '``' * 100 + '`\n  && ````'

        self.assertEqual(abap_string_literal(value), expected)

    def test_newline_rejected(self):
        with self.assertRaises(SAPCliError) as caught:
            abap_string_literal('a\nb')

        self.assertEqual(str(caught.exception), 'Line breaks are not supported in values passed to ABAP')

    def test_carriage_return_rejected(self):
        with self.assertRaises(SAPCliError):
            abap_string_literal('a\rb')


class TestBuildLinkCode(unittest.TestCase):

    def test_all_parameters(self):
        code = build_link_code(
            package='$PKG',
            url='https://github.com/jfilak/sapcli.git',
            user='user',
            password='pass`word',
            branch='refs/heads/main',
            folder_logic='FULL',
            starting_folder='/abap/',
            ignore_subpackages=True,
            main_lang_only=False)

        self.assertEqual(code, LINK_ABAP_CODE)


class TestBuildPullCode(unittest.TestCase):

    def test_all_parameters(self):
        code = build_pull_code(
            package='$PKG',
            user='user',
            password='pass`word',
            corrnr='C50K000001')

        self.assertEqual(code, PULL_ABAP_CODE)


class TestParseReturn(unittest.TestCase):

    def test_ok(self):
        bapiret = parse_return(LINK_OUTPUT_OK)

        self.assertFalse(bapiret.is_error)
        self.assertEqual(bapiret.message_lines(), [
            'Info: Running migrations',
            'Info: Linking https://github.com/jfilak/sapcli.git with $PKG',
            'Info: Done',
        ])

    def test_error_message_with_separator(self):
        bapiret = parse_return(LINK_OUTPUT_ERROR)

        self.assertTrue(bapiret.is_error)
        self.assertEqual(bapiret.error_message, 'Error: Repository already exists | in package $PKG')

    def test_noise_ignored(self):
        bapiret = parse_return(LINK_OUTPUT_NOISE)

        self.assertEqual(bapiret.message_lines(), ['Warning(ZMSG|042): Careful'])

    def test_missing_end_marker(self):
        with self.assertRaises(SAPCliError) as caught:
            parse_return(LINK_OUTPUT_TRUNCATED)

        self.assertEqual(str(caught.exception),
                         'Incomplete output of the abapGit API call:\n' + LINK_OUTPUT_TRUNCATED)


class TestLink(unittest.TestCase):

    def call_link(self, connection):
        return link(connection,
                    package='$PKG',
                    url='https://github.com/jfilak/sapcli.git',
                    user='user',
                    password='pass`word',
                    branch='refs/heads/main',
                    folder_logic='FULL',
                    starting_folder='/abap/',
                    ignore_subpackages=True,
                    main_lang_only=False)

    @patch('sap.platform.abap.run.execute_abap')
    def test_link_ok(self, fake_execute):
        fake_execute.return_value = LINK_OUTPUT_OK
        connection = Mock()

        bapiret = self.call_link(connection)

        fake_execute.assert_called_once_with(connection, LINK_ABAP_CODE)
        self.assertEqual(bapiret.message_lines()[-1], 'Info: Done')

    @patch('sap.platform.abap.run.execute_abap')
    def test_link_error(self, fake_execute):
        fake_execute.return_value = LINK_OUTPUT_ERROR

        with self.assertRaises(BAPIError) as caught:
            self.call_link(Mock())

        self.assertEqual(str(caught.exception),
                         'Info: Running migrations\nError: Repository already exists | in package $PKG')
        self.assertEqual(caught.exception.response, LINK_OUTPUT_ERROR)


class TestPull(unittest.TestCase):

    def call_pull(self, connection):
        return pull(connection,
                    package='$PKG',
                    user='user',
                    password='pass`word',
                    corrnr='C50K000001')

    @patch('sap.platform.abap.run.execute_abap')
    def test_pull_ok(self, fake_execute):
        fake_execute.return_value = PULL_OUTPUT_OK
        connection = Mock()

        bapiret = self.call_pull(connection)

        fake_execute.assert_called_once_with(connection, PULL_ABAP_CODE)
        self.assertEqual(bapiret.message_lines()[-1], 'Info: Finished')

    @patch('sap.platform.abap.run.execute_abap')
    def test_pull_error(self, fake_execute):
        fake_execute.return_value = PULL_OUTPUT_ERROR

        with self.assertRaises(BAPIError) as caught:
            self.call_pull(Mock())

        self.assertEqual(str(caught.exception),
                         'Info: Run migration\nError: Unable to find repo for package $PKG!')
        self.assertEqual(caught.exception.response, PULL_OUTPUT_ERROR)


if __name__ == '__main__':
    unittest.main()
