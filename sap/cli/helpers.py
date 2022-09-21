"""Auxiliary functionality"""

from enum import Enum, auto
import time
import threading

from sap.rest.gcts.errors import SAPCliError


class TaskStates(Enum):
    """Background task states"""

    STOPPED = auto()
    RUNNING = auto()
    TERMINATING = auto()


class ConsoleHeartBeat:
    """A context manager starting a heart beater printing dots to the given
       console in a thread."""

    def __init__(self, console, sleep_period_s):
        self._console = console
        self._sleep_period_s = sleep_period_s
        self._state = TaskStates.STOPPED
        self._state_lock = threading.Lock()
        self._thread = None

    def _set_state(self, new_state: TaskStates) -> TaskStates:
        with self._state_lock:
            old_state = self._state
            self._state = new_state

        return old_state

    def _run(self):
        """Starts beating"""

        old_state = self._set_state(TaskStates.RUNNING)

        if old_state != TaskStates.STOPPED:
            return

        if self._sleep_period_s <= 0:
            self._set_state(TaskStates.STOPPED)
            return

        count = 0
        dot_period = 10 * self._sleep_period_s
        line_length = 0
        elapsed = 0
        end = ''
        while self._state == TaskStates.RUNNING:
            time.sleep(self._sleep_period_s)
            end = ''

            if count == 9:
                if line_length == 7:
                    end = '\n'
                    line_length = 0
                else:
                    line_length += 1

                elapsed += dot_period
                self._console.printout(f'{elapsed}s', end=end)
                count = 0
            else:
                count += 1
                self._console.printout('.', end=end)

            self._console.flush()

        if end != '\n':
            self._console.printout('')

        self._set_state(TaskStates.STOPPED)

    def _stop(self):
        """Stops beating"""

        self._set_state(TaskStates.TERMINATING)

    def __enter__(self):
        if self._sleep_period_s > 0:
            self._thread = threading.Thread(target=self._run)
            self._thread.start()

        return self

    def __exit__(self, *exc):
        if self._thread is not None:
            self._stop()
            self._thread.join()
            self._thread = None

        return False




class TableWriter:
    """A helper class for formatting a list of objects into a table"""

    class Columns:

        ATTR = 0
        HEADER = 1
        FORMATTER = 2
        DEFAULT = 3

        def __init__(self):
            self._columns = []

        def __call__(self, attr, header, formatter=None, default=None):
            self._columns.append((attr, header, formatter, default))
            return self

        def done(self):
            return self._columns


    def __init__(self, data, columns, display_header=True, visible_columns=None):
        if visible_columns is None:
            self._columns = columns
        else:
            self._columns = [c for c in columns if c[TableWriter.Columns.ATTR] in visible_columns]

        self._display_header = display_header
        if display_header:
            self._widths = [len(c[TableWriter.Columns.HEADER]) for c in self._columns]
        else:
            self._widths = [0] * len(self._columns)

        self._lines = []

        for item in data:
            line = []

            for i, c in enumerate(self._columns):
                if isinstance(item, dict):
                    val = item.get(c[TableWriter.Columns.ATTR], c[TableWriter.Columns.DEFAULT])
                    if val is None:
                        raise SAPCliError(f'Missing column in table data: {c[TableWriter.Columns.ATTR]}')
                    val = str(val)
                else:
                    val = str(getattr(item, c[TableWriter.Columns.ATTR]))

                if c[TableWriter.Columns.FORMATTER] is not None:
                    val = c[TableWriter.Columns.FORMATTER](val)

                if self._widths[i] < len(val):
                    self._widths[i] = len(val)

                line.append(val)

            self._lines.append(line)

    def printout(self, console, separator=" | "):
        """Prints out the content"""

        fmt = separator.join((f'{{:<{w}}}' for w in self._widths))
        if self._display_header:
            console.printout(fmt.format(*[c[TableWriter.Columns.HEADER] for c in self._columns]))
            console.printout('-' * (sum(self._widths) + len(separator) * (len(self._columns) - 1)))

        for line in self._lines:
            console.printout(fmt.format(*line))
