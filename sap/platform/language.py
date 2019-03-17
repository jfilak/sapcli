"""ABAP Platform helpers and utilities"""

from sap.errors import SAPCliError

# Supported Languages and Code Pages (Non-Unicode)
# https://help.sap.com/viewer/f3941a838b254ba396a9d92d9dea7294/7.4.19/en-US/c1ae563cd2ad4f0ce10000000a11402f.html

CODE_LIST = [
    ('AF', 'a'),  # Afrikaans
    ('AR', 'A'),  # Arabic
    ('BG', 'W'),  # Bulgarian
    ('CA', 'c'),  # Catalan
    ('ZH', '1'),  # Chinese
    ('ZF', 'M'),  # Chinese-traditional
    ('HR', '6'),  # Croatian
    ('CS', 'C'),  # Czech
    ('DA', 'K'),  # Danish
    ('NL', 'N'),  # Dutch
    ('EN', 'E'),  # English
    ('ET', '9'),  # Estonian
    ('FI', 'U'),  # Finnish
    ('FR', 'F'),  # French
    ('DE', 'D'),  # German
    ('EL', 'G'),  # Greek
    ('HE', 'B'),  # Hebrew
    ('HU', 'H'),  # Hungarian
    ('IS', 'b'),  # Icelandic
    ('ID', 'i'),  # Indonesian
    ('IT', 'I'),  # Italian
    ('JA', 'J'),  # Japanese
    ('KO', '3'),  # Korean
    ('LV', 'Y'),  # Latvian
    ('LT', 'X'),  # Lithuanian
    ('MS', '7'),  # Malay
    ('NO', 'O'),  # Norwegian
    ('PL', 'L'),  # Polish
    ('PT', 'P'),  # Portuguese
    ('Z1', 'Z'),  # Reserved-custt.
    ('RO', '4'),  # Romanian
    ('RU', 'R'),  # Russian
    ('SR', '0'),  # Serbian
    ('SH', 'd'),  # Serbo-Croatian
    ('SK', 'Q'),  # Slovakian
    ('SL', '5'),  # Slovene
    ('ES', 'S'),  # Spanish
    ('SV', 'V'),  # Swedish
    ('TH', '2'),  # Thai
    ('TR', 'T'),  # Turkish
    ('UK', '8')   # Ukrainian
]


def sap_code_to_iso_code(sap_code: str) -> str:
    """Coverts one letter SAP language codes to ISO codes.

       Raises sap.errors.SAPCliError if the give sap_code is not identified.
    """

    try:
        return next((entry[0] for entry in CODE_LIST if entry[1] == sap_code))
    except StopIteration:
        raise SAPCliError(f'Not found SAP Language Code: {sap_code}')


def iso_code_to_sap_code(iso_code: str) -> str:
    """Coverts ISO codes to one letter SAP language codes"""

    try:
        return next((entry[1] for entry in CODE_LIST if entry[0] == iso_code))
    except StopIteration:
        raise SAPCliError(f'Not found ISO Code: {iso_code}')
