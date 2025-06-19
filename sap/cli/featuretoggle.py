"""Feature Toggle Command Line Interface"""

import sap.cli.core
import sap.cli.helpers
import sap.adt.featuretoggle


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.rfc.user
       methods calls.
    """

    def __init__(self):
        super().__init__('featuretoggle')


@CommandGroup.argument('id')
@CommandGroup.command()
def state(connection, args):
    """Dump Feature Toggle Status"""

    manager = sap.adt.featuretoggle.FeatureToggleManager(connection)
    states = manager.fetch_feature_toggle_state(args.id.lower())

    console = sap.cli.core.get_console()
    console.printout(f"Client {args.client}: {states.client_state.value}")
    console.printout(f"User {args.user}: {states.user_state.value}")
    return 0


@CommandGroup.argument('--corrnr', type=str, required=True,
                       help='Transport Request to capture Feature Toggle changes')
@CommandGroup.argument('id')
@CommandGroup.command()
def on(connection, args):
    """Enable Feature Toggle"""

    manager = sap.adt.featuretoggle.FeatureToggleManager(connection)
    manager.switch_feature_toggle_on(args.id.lower(), corrnr=args.corrnr)
    return 0


@CommandGroup.argument('--corrnr', type=str, required=True,
                       help='Transport Request to capture Feature Toggle changes')
@CommandGroup.argument('id')
@CommandGroup.command()
def off(connection, args):
    """Disable Feature Toggle"""

    manager = sap.adt.featuretoggle.FeatureToggleManager(connection)
    manager.switch_feature_toggle_off(args.id.lower(), corrnr=args.corrnr)
    return 0
