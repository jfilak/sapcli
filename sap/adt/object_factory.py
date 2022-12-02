"""Create instances of ADT object proxies by various names"""

from typing import Callable, Dict, List, Optional, cast

import sap.adt
import sap.adt.core
from sap.errors import SAPCliError


ADTObjectBuilderType = Callable[[sap.adt.core.Connection, str], object]
ADTObjectBuilderDictType = Dict[str, ADTObjectBuilderType]


class ADTObjectFactory:
    """Factory producing ADT object Proxies.
    """

    def __init__(self, connection: sap.adt.core.Connection, builders: Optional[ADTObjectBuilderDictType] = None):
        self._connection = connection
        if builders:
            self._builders = builders
        else:
            self._builders = cast(ADTObjectBuilderDictType, {})

    def register(self, typ: str, producer: ADTObjectBuilderType, overwrite: bool = False) -> None:
        """Registers ADT object builder"""

        if not overwrite and typ in self._builders:
            raise SAPCliError(f'Object type builder was already registered: {typ}')

        self._builders[typ] = producer

    def make(self, typ: str, name: str) -> object:
        """Accepts object type name and object name and returns
           instance of ADT Object proxy.
        """

        try:
            ctor = cast(ADTObjectBuilderType, self._builders[typ])
        except KeyError as ex:
            raise SAPCliError(f'Unknown ADT object type: {typ}') from ex
        else:
            return ctor(self._connection, name)

    def get_supported_names(self) -> List[str]:
        """List of known object type names"""

        return cast(List[str], self._builders.keys())


def human_names_factory(connection: sap.adt.core.Connection) -> ADTObjectFactory:
    """Returns an instance of factory making ADT object proxies
       based on human readable ADT object types.
    """

    types = {
        'program': sap.adt.Program,
        'program-include': sap.adt.programs.make_program_include_object,
        'class': sap.adt.Class,
        'package': sap.adt.Package
    }

    return ADTObjectFactory(connection, cast(ADTObjectBuilderDictType, types))
