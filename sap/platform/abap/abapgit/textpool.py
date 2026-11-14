"""Text pools of the abapGit serialization"""

import sap.adt.errors
import sap.adt.textelements
from sap.platform.abap.ddic import TPOOL


def download_text_symbols(observer, text_elements):
    """Returns text symbols of the given text elements"""

    try:
        return sap.adt.textelements.parse_symbols(text_elements.text)
    except sap.adt.errors.ADTError as err:
        observer.warning(f'Download of text elements failed: {err}')
        return []


def build_text_pool(text_symbols):
    """Returns TPOOL populated with the given text symbols"""

    tpool = TPOOL()
    for symbol in text_symbols:
        tpool.append(ID='I', KEY=symbol.id, ENTRY=symbol.text, LENGTH=symbol.max_length)

    return tpool


def text_symbols_from_tpool(observer, tpool, object_name, known_ids=(), supported_ids=('I',)):
    """Returns text symbols (TPOOL entries with ID I) and reports the other
       entries not handled by the caller (known_ids) as skipped.
    """

    text_symbols = []

    for text in tpool:
        if text.ID in supported_ids:
            text_symbols.append(sap.adt.textelements.TextSymbol(text.KEY, text.ENTRY, int(text.LENGTH)))
        elif text.ID not in known_ids:
            entry = f'{text.ID} {text.KEY}' if text.KEY else text.ID
            observer.warning(f'Skipping unsupported text pool entry {entry} of {object_name}')

    return text_symbols


def write_text_symbols(text_elements, text_symbols, corrnr):
    """Replaces text symbols of the given text elements"""

    with text_elements.open_editor(corrnr=corrnr) as editor:
        editor.write(sap.adt.textelements.serialize_symbols(text_symbols))
