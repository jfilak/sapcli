"""ADT proxy for Object Activation routines"""

import sap
import sap.cli.core
from sap.adt.wb import fetch_inactive_objects
from sap.cli.core import printout


class InactiveObjectsGroup(sap.cli.core.CommandGroup):
    """Container for inactive objects commands."""

    def __init__(self):
        super().__init__('inactiveobjects')


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.wb.*
       methods calls.
    """

    def __init__(self):
        super().__init__('activation')

        self.inactive_objects_grp = InactiveObjectsGroup()

    def install_parser(self, arg_parser):
        activation_group = super().install_parser(arg_parser)

        inobj_parser = activation_group.add_parser(self.inactive_objects_grp.name)

        self.inactive_objects_grp.install_parser(inobj_parser)


@InactiveObjectsGroup.command('list')
# pylint: disable=unused-argument
def inactiveobjects_list(connection, args):
    """Print out all inactive objects"""

    def print_entry(entry, prefix=''):
        printout(f'{prefix}{entry.object.name} ({entry.object.typ})')

    inactive_results = fetch_inactive_objects(connection)

    handled = set()

    for root_entry in inactive_results.entries:
        if root_entry.object.parent_uri:
            continue

        root_entry_uri = root_entry.object.uri
        if root_entry_uri in handled:
            continue

        print_entry(root_entry)

        handled.add(root_entry_uri)

        for child_entry in inactive_results.entries:
            if root_entry_uri != child_entry.object.parent_uri:
                continue

            child_uri = child_entry.object.uri
            if child_uri in handled:
                continue

            handled.add(child_uri)
            print_entry(child_entry, prefix=' + ')

    for leftover_entry in inactive_results.entries:
        leftover_uri = leftover_entry.object.uri
        if leftover_uri in handled:
            continue

        print_entry(leftover_entry)
