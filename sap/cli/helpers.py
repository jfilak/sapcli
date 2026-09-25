"""Auxiliary functionality"""

from enum import Enum, auto
import time
import threading

from sap.errors import SAPCliError


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
        """An attempt to offer an elegant way of defining table columns.
           The goal was to save typing method name to have more legible
           code where reader can focus on the essential part which
           is the definitions.

           The parameter 'default' was introduced to provide default value if a
           list of dictionaries contains a dictionary where a key is missing ->
           that sometimes happen when you recieve a list of JSON objects
           (especially gCTS does that - the list items are not uniform).

           The parameter 'attr' can be a dot separated path to a nested
           attribute or dictionary key (e.g. 'owner.name'). Dots are always
           treated as separators, so dictionary keys containing dots cannot
           be used. The 'default' value is used when any part of the path is
           missing; if an intermediate part is None, the next part is treated
           as missing too.

           Example:
             columns = TableWriter.Columns() \
                           ('field_one', 'Header One', formatter=lambda x: str(x), default='...') \
                           ('field_two', 'Header Two') \
                           .done()

             tw = TableWriter(my_data, columns)
        """

        ATTR = 0
        HEADER = 1
        FORMATTER = 2
        DEFAULT = 3
        SENTINEL = object()

        def __init__(self):
            self._columns = []

        def __call__(self, attr, header, formatter=None, default=SENTINEL):
            self._columns.append((attr, header, formatter, default))
            return self

        def done(self):
            """Returns the gathered column definitions.
            """

            return self._columns

    @staticmethod
    def _resolve_attribute(obj: object, attribute: str, default: object):
        """Resolves value of the given attribute of the given object.
           The attribute can be a path consisting of several parts joined by dots.
           The function will iteratively resolve each part of the attribute, each time
           using the object retrieved by the previous part.

           If the object is a dictionary, the key is retrieved instead.

           Dots are always treated as path separators, hence dictionary keys
           containing dots (e.g. {'a.b': 1}) cannot be addressed.

           If an intermediate part resolves to None, the next part is looked up
           on None and ends up with the default value - i.e. the error
           'Missing column' is raised for columns without default even though
           the data is empty rather than missing.
        """

        val = obj
        for part in attribute.split('.'):
            if isinstance(val, dict):
                val = val.get(part, default)
            else:
                val = getattr(val, part, default)

            if val is TableWriter.Columns.SENTINEL:
                raise SAPCliError(f'Missing column in table data: {attribute}')

        return val

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

        self._data = data
        self._lines = []

        for item in data:
            line = []

            for i, c in enumerate(self._columns):
                val = TableWriter._resolve_attribute(item, c[TableWriter.Columns.ATTR], c[TableWriter.Columns.DEFAULT])

                if c[TableWriter.Columns.FORMATTER] is not None:
                    val = c[TableWriter.Columns.FORMATTER](val)
                else:
                    val = str(val)

                if self._widths[i] < len(val):
                    self._widths[i] = len(val)

                line.append(val)

            self._lines.append(line)

    def printout(self, console, separator=" | ", line_callback=None):
        """Prints out the content

        Args:
            console: Console object for output
            separator: Column separator string
            line_callback: Optional callback function called after each data line.
                          Receives (console, data_item) as arguments where data_item
                          is the original data object for that row.
        """

        fmt = separator.join((f'{{:<{w}}}' for w in self._widths))
        if self._display_header:
            console.printout(fmt.format(*[c[TableWriter.Columns.HEADER] for c in self._columns]))
            console.printout('-' * (sum(self._widths) + len(separator) * (len(self._columns) - 1)))

        for i, line in enumerate(self._lines):
            console.printout(fmt.format(*line))
            if line_callback is not None:
                line_callback(console, self._data[i])


def abapstamp_to_isodate(abapstamp: 'int') -> 'str':
    """Formats ABAP timestamp to ISO8061 date string with space instead of T"""

    abapstamp_str = str(abapstamp)

    if len(abapstamp_str) != 14:
        raise SAPCliError(f'Not ABAP time stamp: {abapstamp}')

    year = abapstamp_str[0:4]
    month = abapstamp_str[4:6]
    day = abapstamp_str[6:8]
    hour = abapstamp_str[8:10]
    minute = abapstamp_str[10:12]
    second = abapstamp_str[12:14]

    return f'{year}-{month}-{day} {hour}:{minute}:{second}'


def raise_if_object_name_is_not_supported(object_type_name, supported_object_type_names):
    """Check that the given object type name is supported, and raise an exception if not."""

    if object_type_name not in supported_object_type_names:
        supported = ', '.join(sorted(supported_object_type_names))
        raise SAPCliError(
            f"Unsupported object type: '{object_type_name}'. Supported types: {supported}.")
