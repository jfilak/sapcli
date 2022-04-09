"""Wraps ADT search functionality"""

from sap.adt.objects import ADTObjectReferences
import sap.adt.marshalling


class ADTSearch:
    """ADT Search functionality"""

    def __init__(self, connection):
        self._connection = connection

    def quick_search(self, term: str, max_results: int = 5) -> ADTObjectReferences:
        """Performs the quick object search"""

        resp = self._connection.execute(
            'GET',
            'repository/informationsystem/search',
            params={
                'operation': 'quickSearch',
                'maxResults': max_results,
                'query': term
            }
        )

        results = ADTObjectReferences()
        marshal = sap.adt.marshalling.Marshal()
        marshal.deserialize(resp.text, results)

        return results
