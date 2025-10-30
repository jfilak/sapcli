"""gCTS CLI utilities"""

import sap.cli.core
from sap.rest.gcts.errors import GCTSRequestError, SAPCliError

def gcts_exception_handler(func):
    """Exception handler for gcts commands"""
    def _handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GCTSRequestError as ex:
            # Use the console from sap.cli.core
            from sap.cli.gcts import dump_gcts_messages
            dump_gcts_messages(sap.cli.core.get_console(), ex.messages)
            return 1
        except SAPCliError as ex:
            sap.cli.core.get_console().printerr(str(ex))
            return 1
    return _handler
