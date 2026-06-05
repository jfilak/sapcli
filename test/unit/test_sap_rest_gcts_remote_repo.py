"""Test sap.rest.gcts.remote_repo module - RepositoryLayout"""

import unittest

from sap.rest.gcts.remote_repo import RepositoryLayout


class TestRepositoryLayout(unittest.TestCase):

    def test_to_json_returns_layout_data(self):
        layout_data = {'subdirectory': 'src'}
        layout = RepositoryLayout(layout_data)

        self.assertEqual(layout.to_json(), {'subdirectory': 'src'})

    def test_items_returns_data_items(self):
        layout_data = {'subdirectory': 'src', 'objectStorage': 'plain'}
        layout = RepositoryLayout(layout_data)

        self.assertEqual(dict(layout.items()), {'subdirectory': 'src', 'objectStorage': 'plain'})

    def test_starting_folder_returns_subdirectory(self):
        layout_data = {'subdirectory': 'src/abap'}
        layout = RepositoryLayout(layout_data)

        self.assertEqual(layout.starting_folder, 'src/abap')

    def test_starting_folder_returns_none_when_not_set(self):
        layout_data = {}
        layout = RepositoryLayout(layout_data)

        self.assertIsNone(layout.starting_folder)

    def test_starting_folder_setter_sets_subdirectory(self):
        layout_data = {}
        layout = RepositoryLayout(layout_data)

        layout.starting_folder = 'src'

        self.assertEqual(layout.starting_folder, 'src')
        self.assertEqual(layout.to_json()['subdirectory'], 'src')

    def test_starting_folder_setter_overwrites_existing_value(self):
        layout_data = {'subdirectory': 'old'}
        layout = RepositoryLayout(layout_data)

        layout.starting_folder = 'new'

        self.assertEqual(layout.starting_folder, 'new')

    def test_starting_folder_setter_none_removes_subdirectory(self):
        layout_data = {'subdirectory': 'src'}
        layout = RepositoryLayout(layout_data)

        layout.starting_folder = None

        self.assertIsNone(layout.starting_folder)
        self.assertNotIn('subdirectory', layout.to_json())

    def test_starting_folder_setter_none_when_no_subdirectory_does_not_fail(self):
        layout_data = {'objectStorage': 'plain'}
        layout = RepositoryLayout(layout_data)

        layout.starting_folder = None

        self.assertIsNone(layout.starting_folder)


if __name__ == '__main__':
    unittest.main()
