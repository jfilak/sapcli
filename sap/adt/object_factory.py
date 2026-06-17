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

        return ctor(self._connection, name)

    def get_supported_names(self) -> List[str]:
        """List of known object type names"""

        return cast(List[str], self._builders.keys())


def human_names_factory(connection: sap.adt.core.Connection) -> ADTObjectFactory:
    """Returns an instance of factory making ADT object proxies
       based on human readable ADT object types.

       The catalogue exposes both canonical, dash-separated names
       (``program``, ``function-group`` ...) and the corresponding
       ABAP-style 4-char aliases (``prog``, ``fugr`` ...) so that the
       same factory can serve every ``sap.cli`` consumer that needs to
       map a user-facing name to an ADT object proxy.
    """

    canonical: ADTObjectBuilderDictType = cast(ADTObjectBuilderDictType, {
        'program': sap.adt.Program,
        'include': sap.adt.Include,
        'program-include': sap.adt.programs.make_program_include_object,
        'class': sap.adt.Class,
        'interface': sap.adt.Interface,
        'function-group': sap.adt.FunctionGroup,
        'function-module': sap.adt.function.make_function_module_object,
        'function-include': sap.adt.function.make_function_include_object,
        'data-element': sap.adt.DataElement,
        'domain': sap.adt.Domain,
        'table': sap.adt.Table,
        'structure': sap.adt.Structure,
        'behavior-definition': sap.adt.BehaviorDefinition,
        'message-class': sap.adt.MessageClass,
        'transaction': sap.adt.Transaction,
        'package': sap.adt.Package,
        'cds-view': sap.adt.DataDefinition,
    })

    # Each alias must reuse the very same builder as its canonical
    # counterpart so callers can rely on alias-vs-canonical equivalence.
    aliases = {
        'prog': 'program',
        'incl': 'include',
        'clas': 'class',
        'intf': 'interface',
        'fugr': 'function-group',
        'fm': 'function-module',
        'dtel': 'data-element',
        'doma': 'domain',
        'tabl': 'table',
        'stru': 'structure',
        'bdef': 'behavior-definition',
        'msag': 'message-class',
        'tran': 'transaction',
        'ddls': 'cds-view',
    }

    types: ADTObjectBuilderDictType = dict(canonical)
    for alias, target in aliases.items():
        types[alias] = canonical[target]

    return ADTObjectFactory(connection, types)
