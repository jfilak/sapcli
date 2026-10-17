#!/usr/bin/env python3

import unittest
from unittest.mock import patch, Mock

from sap.errors import SAPCliError
from sap.rfc.bapi import BAPIError
from sap.platform.abap.abapgit_rfc import (
    abap_string_literal,
    build_link_code,
    build_pull_code,
    build_list_code,
    build_commit_code,
    parse_return,
    parse_rows,
    link,
    pull,
    list_repositories,
    commit,
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
    LIST_ABAP_CODE,
    LIST_OUTPUT_OK,
    LIST_OUTPUT_ERROR,
    COMMIT_ABAP_CODE,
    COMMIT_OUTPUT_OK,
    COMMIT_OUTPUT_ERROR,
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

    def test_newline(self):
        self.assertEqual(abap_string_literal('a\nb'),
                         '`a`\n  && cl_abap_char_utilities=>newline\n  && `b`')

    def test_newline_empty_lines(self):
        self.assertEqual(abap_string_literal('a\n\nb\n'),
                         '`a`\n  && cl_abap_char_utilities=>newline\n  && ``'
                         '\n  && cl_abap_char_utilities=>newline\n  && `b`'
                         '\n  && cl_abap_char_utilities=>newline\n  && ``')

    def test_newline_long_line_split(self):
        self.assertEqual(abap_string_literal('a' * 101 + '\nb'),
                         '`' + 'a' * 100 + '`\n  && `a`\n  && cl_abap_char_utilities=>newline\n  && `b`')

    def test_carriage_return_rejected(self):
        with self.assertRaises(SAPCliError) as caught:
            abap_string_literal('a\r\nb')

        self.assertEqual(str(caught.exception), 'Carriage returns are not supported in values passed to ABAP')


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


class TestBuildListCode(unittest.TestCase):

    def test_list(self):
        self.assertEqual(build_list_code(), LIST_ABAP_CODE)


class TestBuildCommitCode(unittest.TestCase):

    def test_all_parameters(self):
        code = build_commit_code(
            package='$PKG',
            user='user',
            password='pass`word',
            comment='Fix bug',
            body='First line\nSecond line',
            committer_name='Committer',
            committer_email='committer@example.com',
            author_name='Author',
            author_email='author@example.com')

        self.assertEqual(code, COMMIT_ABAP_CODE)


class TestParseRows(unittest.TestCase):

    def test_two_rows(self):
        rows = parse_rows(LIST_OUTPUT_OK, 'REPOSITORIES')

        self.assertEqual(rows, [
            {
                'REPO_KEY': '000000000007',
                'NAME': 'CLAS | test',
                'ABAP_PACKAGE': '$SAPCLI_AGRFC',
                'URL': 'https://github.com/abapGit-tests/CLAS.git',
                'BRANCH_NAME': 'refs/heads/main',
                'DESERIALIZED_AT': '20261017200708.0661700',
            },
            {
                'REPO_KEY': '000000000008',
                'NAME': 'sapcli',
                'ABAP_PACKAGE': '$SAPCLI',
                'URL': 'https://github.com/jfilak/sapcli.git',
                'BRANCH_NAME': 'refs/heads/master',
                'DESERIALIZED_AT': '0.0000000',
            },
        ])

    def test_other_table(self):
        self.assertEqual(parse_rows(LIST_OUTPUT_OK, 'OTHER'), [])

    def test_no_rows(self):
        self.assertEqual(parse_rows(LIST_OUTPUT_ERROR, 'REPOSITORIES'), [])


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


class TestListRepositories(unittest.TestCase):

    @patch('sap.platform.abap.run.execute_abap')
    def test_list_ok(self, fake_execute):
        fake_execute.return_value = LIST_OUTPUT_OK
        connection = Mock()

        repositories = list_repositories(connection)

        fake_execute.assert_called_once_with(connection, LIST_ABAP_CODE)
        self.assertEqual([repo['REPO_KEY'] for repo in repositories], ['000000000007', '000000000008'])

    @patch('sap.platform.abap.run.execute_abap')
    def test_list_error(self, fake_execute):
        fake_execute.return_value = LIST_OUTPUT_ERROR

        with self.assertRaises(BAPIError) as caught:
            list_repositories(Mock())

        self.assertEqual(str(caught.exception), 'Info: Running migrations\nError: Migration failed')


class TestCommit(unittest.TestCase):

    def call_commit(self, connection):
        return commit(connection,
                      package='$PKG',
                      user='user',
                      password='pass`word',
                      comment='Fix bug',
                      body='First line\nSecond line',
                      committer_name='Committer',
                      committer_email='committer@example.com',
                      author_name='Author',
                      author_email='author@example.com')

    @patch('sap.platform.abap.run.execute_abap')
    def test_commit_ok(self, fake_execute):
        fake_execute.return_value = COMMIT_OUTPUT_OK
        connection = Mock()

        bapiret = self.call_commit(connection)

        fake_execute.assert_called_once_with(connection, COMMIT_ABAP_CODE)
        self.assertEqual(bapiret.message_lines()[-3:], [
            'Success: Committed: CLAS ZCL_AG_UNIT_TEST',
            'Info: Pushed 1 objects',
            'Info: Done',
        ])

    @patch('sap.platform.abap.run.execute_abap')
    def test_commit_error(self, fake_execute):
        fake_execute.return_value = COMMIT_OUTPUT_ERROR

        with self.assertRaises(BAPIError) as caught:
            self.call_commit(Mock())

        self.assertEqual(str(caught.exception), 'Error: Cannot push offline repo of the package $PKG')


if __name__ == '__main__':
    unittest.main()
