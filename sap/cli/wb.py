"""ADT Object CLI templates"""

import sap.adt.wb

from sap.errors import SAPCliError
from sap.cli.core import printout


# pylint: disable=too-few-public-methods
class ObjectActivationStats:
    """Sequential mass activation statistics"""

    def __init__(self):
        self.errors = 0
        self.warnings = 0
        self.active_objects = []
        self.inactive_objects = []


class StopObjectActivation(SAPCliError):
    """Represents a stopped sequential mass activation"""

    def __init__(self, message, stats, name, obj):
        super(StopObjectActivation, self).__init__(message)

        self.stats = stats
        self.name = name
        self.obj = obj


class ObjectActivationWorker:
    """A helper function for consistent handling of object activation.
    By default it stops on errors and continues on warnings.
    """

    def __init__(self):
        self._continue_on_errors = False
        self._warnings_as_errors = False

    @property
    def continue_on_errors(self):
        """If true, the activation will continue in despite receiving
        activation errors.
        """

        return self._continue_on_errors

    @continue_on_errors.setter
    def continue_on_errors(self, value):
        """If true, the activation will continue in despite receiving
        activation errors.
        """

        self._continue_on_errors = value

    @property
    def warnings_as_errors(self):
        """If true, the activation will treat warnings as errors.
        """

        return self._warnings_as_errors

    @warnings_as_errors.setter
    def warnings_as_errors(self, value):
        """If true, the activation will treat warnings as errors.
        """

        self._warnings_as_errors = value

    # pylint: disable=no-self-use
    def begin(self, count):
        """Reports start of activation"""

        if count is None or count == 1:
            printout('Activating:')
        else:
            printout(f'Activating {count} objects:')

    # pylint: disable=no-self-use
    def start_object(self, name, index, count):
        """Reports start of object activation"""

        progress = f'({index}'

        if count is None or count == 1:
            progress += ')'
        else:
            progress += f'/{count})'

        printout('*', name, progress)

    # pylint: disable=no-self-use
    def handle_message(self, msg):
        """Reports an activation message"""

        printout(f'-- {msg.obj_descr}')
        printout(f'   {msg.typ}: {msg.short_text}')

    def handle_results(self, name, obj, results, stats):
        """Processes activation results for a single object"""

        error = False

        if results.generated:
            stats.active_objects.append(obj)
        else:
            stats.inactive_objects.append(obj)

        for msg in results.messages:
            if msg.is_error:
                error = True

            if msg.is_warning:
                stats.warnings += 1
                error = self.warnings_as_errors

            if error:
                stats.errors += 1

            self.handle_message(msg)

        if (error and not self.continue_on_errors):
            raise StopObjectActivation('Stopped activation because of errors', stats, name, obj)

    def activate_sequentially(self, name_and_obj_tuples, count=None):
        """Sequentially goes from the enumerable name_and_obj_tuples and tries
        to activate each object.
        """

        stats = ObjectActivationStats()
        self.begin(count)
        for index, item in enumerate(name_and_obj_tuples, start=1):
            name, obj = item

            self.start_object(name, index, count)
            results, _ = sap.adt.wb.try_activate(obj)
            self.handle_results(name, obj, results, stats)

        return stats
