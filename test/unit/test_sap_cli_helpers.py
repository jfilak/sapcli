#!/usr/bin/env python3

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

