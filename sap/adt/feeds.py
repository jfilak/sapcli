"""ADT ATOM feeds"""

from xml.etree import ElementTree


XMLNS_ATOM = '{http://www.w3.org/2005/Atom}'


def parse_feed(feed_xml):
    """Parses an ATOM feed into a list of dicts.

    Each dict carries the entry's title, updated timestamp and id; the author
    key is only present when the entry declares one.
    """

    root = ElementTree.fromstring(feed_xml)

    entries = []
    for entry in root.findall(f'{XMLNS_ATOM}entry'):
        title = entry.findtext(f'{XMLNS_ATOM}title', default='')
        updated = entry.findtext(f'{XMLNS_ATOM}updated', default='')
        entry_id = entry.findtext(f'{XMLNS_ATOM}id', default='')

        item = {'title': title, 'updated': updated, 'id': entry_id}

        author = entry.findtext(f'{XMLNS_ATOM}author/{XMLNS_ATOM}name')
        if author is not None:
            item['author'] = author

        entries.append(item)

    return entries


def list_feeds(connection):
    """Returns the ATOM feeds available on the system as a list of dicts"""

    return parse_feed(connection.execute('GET', 'feeds').text)


def read_feed(connection, feed_url):
    """Reads a single ATOM feed by its URL and returns its entries as dicts"""

    return parse_feed(connection.execute('GET', feed_url, complete_url=True).text)
