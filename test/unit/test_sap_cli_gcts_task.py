# --- gcts_task CLI tests ---
from sap.cli import gcts_task

from unittest.mock import Mock

from mock import ConsoleOutputTestCase, PatcherTestCase
from sap.rest.errors import HTTPRequestError


from infra import generate_parse_args
from sap.cli.gcts_task import CommandGroup


parse_args = generate_parse_args(CommandGroup())


class TestgCTSTaskCLI(PatcherTestCase, ConsoleOutputTestCase):
    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        self.patch_console(console=self.console)
        # Patch RepositoryTask at CLI import location
        patcher = self.patch('sap.cli.gcts_task.RepositoryTask', autospec=True)
        self.fake_task_class = patcher
        self.fake_task_instance = patcher.return_value
        self.fake_task_instance.get_by_id.side_effect = None
        self.fake_task_instance.get_list.side_effect = None
        self.fake_task_instance.delete.side_effect = None

    def info(self, package, tid):
        return generate_parse_args(gcts_task.CommandGroup())('info', package, '--tid', tid)

    def print_list(self, package):
        return generate_parse_args(gcts_task.CommandGroup())('print_list', package)

    def delete(self, package, tid):
        return generate_parse_args(gcts_task.CommandGroup())('delete', package, '--tid', tid)

    def test_info_success(self):
        conn = Mock()
        repo_task = Mock()
        repo_task.tid = 'TID123'
        repo_task.status = 'READY'
        repo_task.type = 'CLONE'
        self.fake_task_instance.get_by_id.return_value = repo_task
        args = self.info('PKG', 'TID123')
        exit_code = args.execute(conn, args)
        self.assertEqual(exit_code, 0)
        self.fake_task_instance.get_by_id.assert_called_once_with('TID123')
        self.assertIn('Task ID: TID123', self.console.capout)
        self.assertIn('Task Status: READY', self.console.capout)
        self.assertIn('Task Type: CLONE', self.console.capout)

    def test_info_error(self):
        conn = Mock()
        self.fake_task_instance.get_by_id.side_effect = HTTPRequestError(None, Mock(text='fail', status_code=500))
        args = self.info('PKG', 'TID123')
        exit_code = args.execute(conn, args)
        self.assertEqual(exit_code, 1)
        self.assertIn('500', self.console.caperr)
        self.assertIn('fail', self.console.caperr)

    def test_info_missing_params(self):
        args = self.info('', '')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='Invalid command line options\nRun: sapcli gcts_task info --help\n')

    def test_print_list_success(self):
        conn = Mock()
        fake_task1 = {'tid': 'TID1', 'status': 'READY', 'type': 'CLONE'}
        fake_task2 = {'tid': 'TID2', 'status': 'DONE', 'type': 'DELETE'}
        self.fake_task_instance.get_list.return_value = [fake_task1, fake_task2]
        args = self.print_list('PKG')
        exit_code = args.execute(conn, args)
        self.assertEqual(exit_code, 0)
        self.fake_task_instance.get_list.assert_called_once_with()
        self.assertIn('TID1', self.console.capout)
        self.assertIn('TID2', self.console.capout)

    def test_print_list_empty(self):
        conn = Mock()
        self.fake_task_instance.get_list.return_value = []
        args = self.print_list('PKG')
        exit_code = args.execute(conn, args)
        self.assertEqual(exit_code, 0)
        self.assertIn('No tasks found for repository: PKG', self.console.capout)

    def test_print_list_error(self):
        conn = Mock()
        self.fake_task_instance.get_list.side_effect = HTTPRequestError(None, Mock(text='fail', status_code=500))
        args = self.print_list('PKG')
        exit_code = args.execute(conn, args)
        self.assertEqual(exit_code, 1)
        self.assertIn('500', self.console.caperr)
        self.assertIn('fail', self.console.caperr)

    def test_print_list_missing_params(self):
        args = self.print_list('')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)
        self.assertIn('Invalid command line options', self.console.caperr)

    def test_delete_success(self):
        conn = Mock()
        self.fake_task_instance.delete.side_effect = None
        self.fake_task_instance.delete.return_value = None
        args = self.delete('PKG', 'TID123')
        exit_code = args.execute(conn, args)
        self.assertEqual(exit_code, 0)
        self.fake_task_instance.delete.assert_called_once_with()
        self.assertIn('Task deleted successfully', self.console.capout)

    def test_delete_repo_not_exists(self):
        conn = Mock()
        from sap.rest.gcts.repo_task import GCTSRepoNotExistsError
        self.fake_task_instance.delete.side_effect = GCTSRepoNotExistsError({'exception': 'no repo'})
        args = self.delete('PKG', 'TID123')
        exit_code = args.execute(conn, args)
        self.assertEqual(exit_code, 1)
        self.fake_task_instance.delete.assert_called_once_with()
        self.assertIn('Repository PKG does not exist:', self.console.caperr)

    def test_delete_request_error(self):
        conn = Mock()
        self.fake_task_instance.delete.side_effect = HTTPRequestError(None, Mock(text='fail', status_code=500))
        args = self.delete('PKG', 'TID123')
        exit_code = args.execute(conn, args)
        self.assertEqual(exit_code, 1)
        self.fake_task_instance.delete.assert_called_once_with()
        self.assertIn('500', self.console.caperr)
        self.assertIn('fail', self.console.caperr)
