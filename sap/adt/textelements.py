"""ABAP Text Elements (text pool) - text symbols"""

from typing import NamedTuple

from sap.errors import SAPCliError
from sap.adt.errors import ExceptionResourceNotFound, ExceptionResourceSaveFailure
from sap.adt.objects import (
    ADTObject,
    ADTObjectType,
    ADTObjectSourceEditor,
    modify_object_params,
    xmlns_adtcore_ancestor,
)


MAX_LENGTH_PREFIX = '@MaxLength:'

TEXT_ELEMENTS_MIMETYPE = 'application/vnd.sap.adt.textelements.v1+xml'
SYMBOLS_MIMETYPE = 'application/vnd.sap.adt.textelements.symbols.v1'

XMLNS_REPT = xmlns_adtcore_ancestor('rept', 'http://www.sap.com/adt/textelements')


class TextSymbol(NamedTuple):
    """ABAP Text Symbol (TEXT-001)"""

    id: str
    text: str
    max_length: int


def parse_symbols(payload):
    """Parses ADT text symbols format into a list of TextSymbol:
         @MaxLength:20
         001=Hello, world!
    """

    symbols = []
    max_length = None

    for line in payload.splitlines():
        if not line:
            continue

        if line.startswith(MAX_LENGTH_PREFIX):
            try:
                max_length = int(line[len(MAX_LENGTH_PREFIX):])
            except ValueError as ex:
                raise SAPCliError(f'Invalid text symbol line: {line}') from ex

            continue

        if '=' not in line:
            raise SAPCliError(f'Invalid text symbol line: {line}')

        if max_length is None:
            raise SAPCliError(f'Text symbol without @MaxLength: {line}')

        symbol_id, text = line.split('=', 1)
        symbols.append(TextSymbol(symbol_id, text, max_length))
        max_length = None

    return symbols


def serialize_symbols(symbols):
    """Serializes the list of TextSymbol into ADT text symbols format"""

    return ''.join(f'{MAX_LENGTH_PREFIX}{symbol.max_length}\r\n{symbol.id}={symbol.text}\r\n'
                   for symbol in symbols)


class TextElementsEditor(ADTObjectSourceEditor):
    """Text Symbols editor"""

    def __init__(self, instance, lock_handle=None, corrnr=None):
        super().__init__(instance, lock_handle, corrnr, content_type=SYMBOLS_MIMETYPE)

    def get_headers(self):
        """The resource accepts and returns only the symbols MIME type"""

        return {'Content-Type': SYMBOLS_MIMETYPE, 'Accept': SYMBOLS_MIMETYPE}

    def write(self, content):
        """Validates the given text symbols and writes them in ADT format"""

        data = bytes(serialize_symbols(parse_symbols(content)), 'utf-8')

        try:
            self.connection.execute(
                'PUT',
                self.uri + self.get_uri_for_type(SYMBOLS_MIMETYPE),
                params=modify_object_params(self.lock_handle, self.corrnr),
                headers=self.get_headers(),
                body=data)
        except ExceptionResourceSaveFailure as save_exc:
            # ADT allows locking text elements of a non-existing object and
            # the PUT then fails with a misleading message about missing
            # package - check the object exists to report the real cause.
            try:
                self._obj.fetch()
            except ExceptionResourceNotFound as not_found:
                raise not_found from save_exc

            raise


class TextElements(ADTObject):
    """Text Elements (text pool) of an ABAP object - children must define
       OBJTYPE and OWNER_LABEL which is used in error messages.
    """

    OWNER_LABEL = 'object'

    def _not_found_error(self):
        return ExceptionResourceNotFound(f'Cannot access text elements: {self.OWNER_LABEL} {self.name} does not exist')

    @property
    def text(self):
        """Downloads text symbols"""

        try:
            return super().text
        except ExceptionResourceNotFound as ex:
            raise self._not_found_error() from ex

    def fetch(self):
        """Retrieve data from ADT"""

        try:
            super().fetch()
        except ExceptionResourceNotFound as ex:
            raise self._not_found_error() from ex


class ClassTextElements(TextElements):
    """Text Elements (text pool) of ABAP OO Class"""

    OBJTYPE = ADTObjectType(
        'CLAS/OCX',
        'textelements/classes',
        XMLNS_REPT,
        TEXT_ELEMENTS_MIMETYPE,
        {SYMBOLS_MIMETYPE: 'source/symbols'},
        'textElement',
        editor_factory=TextElementsEditor,
        source_mimetype=SYMBOLS_MIMETYPE
    )

    OWNER_LABEL = 'class'


class ProgramTextElements(TextElements):
    """Text Elements (text pool) of ABAP Program (Report)"""

    OBJTYPE = ADTObjectType(
        'PROG/PX',
        'textelements/programs',
        XMLNS_REPT,
        TEXT_ELEMENTS_MIMETYPE,
        {SYMBOLS_MIMETYPE: 'source/symbols'},
        'textElement',
        editor_factory=TextElementsEditor,
        source_mimetype=SYMBOLS_MIMETYPE
    )

    OWNER_LABEL = 'program'
