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


def parse_statement_uri(uri: str) -> StatementPosition:
    """Parse an ADT statement URI into a StatementPosition.

    Statement URIs always contain both start and end:
      /sap/bc/adt/oo/classes/zcx_foo/source/main#start=183,1;end=183,20
        -> StatementPosition('zcx_foo', 'source/main', 183, 1, 183, 20)
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
    object_name = parts[-1] if parts else uri
    object_part = ''
    for marker in ('source', 'includes'):
        try:
            idx = parts.index(marker)
        except ValueError:
            pass
        else:
            object_name = parts[idx - 1]
            object_part = '/'.join(parts[idx:])
            break

    return StatementPosition(
        object_name=object_name,
        object_part=object_part,
        start_line=tokens['start'][0],
        start_column=tokens['start'][1],
        end_line=tokens['end'][0],
        end_column=tokens['end'][1],
    )


def format_check_location(uri: str, source_label: Optional[str] = None) -> str:
    """Render a checkrun URI as ``<label>:<line>:<column>``.

    ``source_label``, when given, replaces the object-name derived from
    the URI path - used by checkin to show the on-disk file path. If the
    URI cannot be parsed (no fragment / malformed), the label is returned
    so the output still points at *something* meaningful.
    """

    try:
        pos = parse_statement_uri(uri)
    except InvalidURIError:
        return source_label or (uri or '').partition('#')[0] or '<unknown>'

    if source_label is not None:
        label = source_label
    elif pos.object_part in ('', 'source/main'):
        label = pos.object_name
    else:
        label = f'{pos.object_name}/{pos.object_part}'

    return f'{label}:{pos.start_line}:{pos.start_column}'


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
