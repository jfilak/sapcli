"""ADT URI parsing utilities"""
from typing import NamedTuple, Optional

from sap.adt.errors import InvalidURIError


class StatementPosition(NamedTuple):
    """Parsed ADT statement URI with object location and source range"""

    object_name: str
    object_part: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    # ADT object type code (e.g. CLAS/OC) or None if the URI is not known
    adt_type: Optional[str]


# ADT object type codes by the parts of URI paths; the more specific
# patterns go first and * stands for a name
URI_PATH_ADT_TYPES = (
    (('oo', 'classes', '*'), 'CLAS/OC'),
    (('oo', 'interfaces', '*'), 'INTF/OI'),
    (('programs', 'programs', '*'), 'PROG/P'),
    (('programs', 'includes', '*'), 'PROG/I'),
    (('functions', 'groups', '*', 'fmodules', '*'), 'FUGR/FF'),
    (('functions', 'groups', '*', 'includes', '*'), 'FUGR/I'),
)

ADT_URI_ROOT = ['sap', 'bc', 'adt']


def _adt_type_of_path_parts(parts):
    """Returns the ADT object type code of the URI path split to parts or
       None if the path is not known.
    """

    if parts[:len(ADT_URI_ROOT)] == ADT_URI_ROOT:
        parts = parts[len(ADT_URI_ROOT):]

    for pattern, adt_type in URI_PATH_ADT_TYPES:
        candidate = parts[:len(pattern)]
        if len(candidate) != len(pattern):
            continue

        if all(expected in ('*', actual) for expected, actual in zip(pattern, candidate)):
            return adt_type

    return None


def _parse_fragment_tokens(fragment: str) -> dict:
    """Split a URI fragment into a mapping of token name to (line, column).

    Handles any number of semicolon-separated key=L,C tokens without
    validating which keys are present. Column defaults to 0 when absent.

      'start=52,9;end=53,1' -> {'start': (52, 9), 'end': (53, 1)}
      'start=52'            -> {'start': (52, 0)}
      ''                    -> {}
    """

    result = {}
    for token in (fragment or '').split(';'):
        name, sep, coords = token.partition('=')
        if sep:
            parts = coords.split(',', 1)
            result[name] = (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
    return result


def _object_name_and_part(parts):
    """Returns (object name, object part) of the source URI path split to
       parts, e.g. ('zcx_foo', 'includes/definitions') of
       /sap/bc/adt/oo/classes/zcx_foo/includes/definitions. The part is
       empty if the path has no source part.
    """

    for marker in ('source', 'includes'):
        if marker in parts:
            idx = parts.index(marker)
            return parts[idx - 1], '/'.join(parts[idx:])

    return parts[-1], ''


def parse_statement_uri(uri: str) -> StatementPosition:
    """Parse an ADT statement URI into a StatementPosition.

    Statement URIs always contain both start and end:
      /sap/bc/adt/oo/classes/zcx_foo/source/main#start=183,1;end=183,20
        -> StatementPosition('zcx_foo', 'source/main', 183, 1, 183, 20, 'CLAS/OC')
    """

    path, _, fragment = uri.partition('#')
    if not fragment:
        raise InvalidURIError(f'URI has no fragment: {uri!r}')

    try:
        tokens = _parse_fragment_tokens(fragment)
    except ValueError as ex:
        raise InvalidURIError(f'Fragment invalid start+end: {fragment!r}') from ex

    if 'start' not in tokens or 'end' not in tokens:
        raise InvalidURIError(f'Fragment missing start+end: {fragment!r}')

    parts = path.strip('/').split('/')
    object_name, object_part = _object_name_and_part(parts)

    return StatementPosition(
        object_name=object_name,
        object_part=object_part,
        start_line=tokens['start'][0],
        start_column=tokens['start'][1],
        end_line=tokens['end'][0],
        end_column=tokens['end'][1],
        adt_type=_adt_type_of_path_parts(parts),
    )


def format_check_location(uri: str, source_label: Optional[str] = None) -> str:
    """Render a checkrun URI as ``<label>:<line>:<column>``.

    ``source_label``, when given, replaces the object-name derived from
    the URI path - used by checkin to show the on-disk file path. Only the
    start position is needed because ADT reports some findings without
    the end, e.g. an open macro definition (``#start=2,2``). If the URI
    has no start position (no fragment / malformed), the label is returned
    so the output still points at *something* meaningful.
    """

    path, _, fragment = (uri or '').partition('#')

    try:
        start = _parse_fragment_tokens(fragment).get('start')
    except ValueError:
        # A malformed fragment has no position to show - the label or
        # the path returned below still points at the source.
        start = None

    if start is None:
        return source_label or path or '<unknown>'

    if source_label is not None:
        label = source_label
    else:
        object_name, object_part = _object_name_and_part(path.strip('/').split('/'))
        if object_part in ('', 'source/main'):
            label = object_name
        else:
            label = f'{object_name}/{object_part}'

    return f'{label}:{start[0]}:{start[1]}'


def parse_object_implementation_start_uri(location: str) -> tuple:
    """Parse the start position from an object implementation URI fragment.

    Object implementation URIs carry only a start position:
      '/sap/bc/adt/oo/classes/foo/source/main#start=52,9' -> (52, 9)
      '/sap/bc/adt/oo/classes/foo/source/main#start=199,1' -> (199, 1)
      '' or None -> (0, 0)
    """

    _, _, fragment = (location or '').partition('#')
    tokens = _parse_fragment_tokens(fragment)
    return tokens.get('start', (0, 0))
