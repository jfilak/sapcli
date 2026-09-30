"""ABAP runtime short dumps"""

import sap.adt.feeds
import sap.errors


def list_dumps(connection):
    """Returns the ABAP runtime short dumps as a list of feed-entry dicts"""

    return sap.adt.feeds.parse_feed(connection.execute('GET', 'runtime/dumps').text)


def read_dump(connection, dump_id):
    """Returns a single short dump, formatted by the system, by its ID"""

    dump_id = dump_id.strip()
    if not dump_id:
        raise sap.errors.SAPCliError('No dump ID provided')

    return connection.execute('GET', f'runtime/dump/{dump_id}/formatted').text
