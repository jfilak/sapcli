#!/usr/bin/env python3

from types import SimpleNamespace
import unittest
from unittest.mock import patch, Mock

import sap.cli.helpers

from mock import (
    ConsoleOutputTestCase
)

class TestConsoleHeartBeat(ConsoleOutputTestCase, unittest.TestCase):

    def getBeater(self, period):
        return sap.cli.helpers.ConsoleHeartBeat(self.console, period)

    def test_heart_beat_not_start(self):
        beater = self.getBeater(0)
        beater._run()

        self.assertConsoleContents(console=self.console)

    @patch('sap.cli.helpers.time.sleep')
    def test_heart_beat_line_break(self, fake_sleep):
        beater = self.getBeater(5)

        self.remaining_beats = 199
        def stop_at_zero(timeout):
            self.remaining_beats -= 1

            if self.remaining_beats == 0:
                beater._stop()

        fake_sleep.side_effect = stop_at_zero

        beater._run()

        self.maxDiff = None
        self.assertConsoleContents(console=self.console, stdout=
'''.........50s.........100s.........150s.........200s.........250s.........300s.........350s.........400s
.........450s.........500s.........550s.........600s.........650s.........700s.........750s.........800s
.........850s.........900s.........950s.........
''')

    @patch('sap.cli.helpers.time.sleep')
    def test_heart_beat_line_break_no_empty_line(self, fake_sleep):
        beater = self.getBeater(5)

        self.remaining_beats = 80
        def stop_at_zero(timeout):
            self.remaining_beats -= 1

            if self.remaining_beats == 0:
                beater._stop()

        fake_sleep.side_effect = stop_at_zero

        beater._run()

        self.maxDiff = None
        self.assertConsoleContents(console=self.console, stdout=
'''.........50s.........100s.........150s.........200s.........250s.........300s.........350s.........400s
''')

    @patch('sap.cli.helpers.time.sleep')
    def test_heart_beat_line_break_with_elapsed(self, fake_sleep):
        beater = self.getBeater(5)

        self.remaining_beats = 85
        def stop_at_zero(timeout):
            self.remaining_beats -= 1

            if self.remaining_beats == 0:
                beater._stop()

        fake_sleep.side_effect = stop_at_zero

        beater._run()

        self.maxDiff = None
        self.assertConsoleContents(console=self.console, stdout=
'''.........50s.........100s.........150s.........200s.........250s.........300s.........350s.........400s
.....
''')

    @patch('sap.cli.helpers.time.sleep')
    def test_heart_beat_line_break(self, fake_sleep):
        fake_sleep.side_effect = Exception()
        beater = self.getBeater(1)
        # HACK!!!
        beater._state = sap.cli.helpers.TaskStates.RUNNING

        beater._run()
        self.assertEqual(beater._state, sap.cli.helpers.TaskStates.RUNNING)


    @patch('sap.cli.helpers.threading.Thread')
    def test_heart_beat_context_start_thread(self, fake_thread):
        fake_instance = Mock()
        fake_thread.return_value = fake_instance

        with sap.cli.helpers.ConsoleHeartBeat(self.console, 3) as beater:
            self.assertIsNotNone(beater._thread)
            self.assertEqual(beater._sleep_period_s, 3)
            self.assertEqual(beater._console, self.console)
            fake_thread.assert_called_once_with(target=beater._run)
            beater._state = sap.cli.helpers.TaskStates.RUNNING

        fake_instance.start.assert_called_once_with()
        fake_instance.join.assert_called_once_with()
        self.assertIsNone(beater._thread)
        self.assertEqual(beater._state, sap.cli.helpers.TaskStates.TERMINATING)


class TestTableWriter(ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()

        self.columns = sap.cli.helpers.TableWriter.Columns()('col1', 'Col1')('col2', 'Col2')('col3', 'Col3')\
            ('col4', 'Col4', default='').done()
        self.data = Mock(col1='col1', col2='col2', col3='col3', col4=None)

    def test_table_writer(self):
        sap.cli.helpers.TableWriter([self.data], self.columns).printout(self.console)

        self.assertConsoleContents(self.console, stdout=
'''Col1 | Col2 | Col3 | Col4
-------------------------
col1 | col2 | col3 | None
''')

    def test_table_writer_without_header(self):
        sap.cli.helpers.TableWriter([self.data], self.columns, display_header=False).printout(self.console)

        self.assertConsoleContents(self.console, stdout=
'''col1 | col2 | col3 | None
''')

    def test_table_writer_with_visible_columns(self):
        sap.cli.helpers.TableWriter([self.data], self.columns, visible_columns=['col1', 'col2']).printout(self.console)

        self.assertConsoleContents(self.console, stdout=
'''Col1 | Col2
-----------
col1 | col2
''')

    def test_table_writer_missing_column_in_data(self):
        data = Mock(spec=['col1'], col1='col1')

        with self.assertRaises(sap.cli.helpers.SAPCliError) as cm:
            sap.cli.helpers.TableWriter([data], self.columns).printout(self.console)

        self.assertEqual(str(cm.exception), 'Missing column in table data: col2')

    def test_table_writer_missing_column_in_dict_data(self):
        data_dict = {'col1': 'col1'}

        with self.assertRaises(sap.cli.helpers.SAPCliError) as cm:
            sap.cli.helpers.TableWriter([data_dict], self.columns).printout(self.console)

        self.assertEqual(str(cm.exception), 'Missing column in table data: col2')

    def test_table_writer_with_formatter(self):
        def formatter(value: str):
            return value.upper()

        columns = sap.cli.helpers.TableWriter.Columns()('col1', 'Col1', formatter=formatter)\
            ('col2', 'Col2', formatter=formatter)('col3', 'Col3', formatter=formatter).done()

        sap.cli.helpers.TableWriter([self.data], columns).printout(self.console)

        self.assertConsoleContents(self.console, stdout=
'''Col1 | Col2 | Col3
------------------
COL1 | COL2 | COL3
''')

    def test_table_writer_custom_separator(self):
        sap.cli.helpers.TableWriter([self.data], self.columns).printout(self.console, separator=" ! ")

        self.assertConsoleContents(self.console, stdout=
'''Col1 ! Col2 ! Col3 ! Col4
-------------------------
col1 ! col2 ! col3 ! None
''')

    def test_table_writer_dict_containing_none(self):
        def formatter(value: str):
            if value is None:
                return '(..)'

            return 'BANG'

        columns = (sap.cli.helpers.TableWriter.Columns()
            ('col1', 'Col1', formatter=formatter)
            ('col2', 'Col2', formatter=formatter, default=None)
            .done()
        )

        sap.cli.helpers.TableWriter([{'col1': None}], columns).printout(self.console)

        self.assertConsoleContents(self.console, stdout=
'''Col1 | Col2
-----------
(..) | (..)
''')

    def test_table_writer_attr_containing_none(self):
        def formatter(value: str):
            if value is None:
                return '(..)'

            return 'BANG'


        columns = (sap.cli.helpers.TableWriter.Columns()
            ('col1', 'Col1', formatter=formatter)
            ('col2', 'Col2', formatter=formatter, default=None)
            .done()
        )

        sap.cli.helpers.TableWriter([SimpleNamespace(col1=None)], columns).printout(self.console)

        self.assertConsoleContents(self.console, stdout=
'''Col1 | Col2
-----------
(..) | (..)
''')
