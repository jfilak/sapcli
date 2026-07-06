"""ABAP Adhoc Code Execution"""

import re
import secrets
import string
import warnings

import sap.adt
import sap.adt.checks
import sap.adt.wb
from sap.config import config_get
from sap.errors import SAPCliError


DEFAULT_PREFIX = 'zcl_sapcli_run'
DEFAULT_PACKAGE = '$tmp'

_CLASS_DESCRIPTION = 'Temporary class created by sapcli for adhoc ABAP execution'

# Preprocessor token: anything between {{ and }} on a single line. The match is
# deliberately broader than the supported content so that future syntax (defaults,
# filters, functions) fails loudly today instead of being passed to the ABAP system.
_TOKEN_RE = re.compile(r'{{(.*?)}}')

# Grammar of token names - shared with the --define argument parsing so that every
# definable name is also matchable. Future token syntax will use the characters
# excluded here (e.g. '|', '()') as operators.
TOKEN_NAME_RE = re.compile(r'[A-Za-z_]\w*', re.ASCII)

# Jinja2 statement and comment delimiters - reserved for future template features.
# Their mere presence is an error (paired or not, Jinja2 comments may span lines),
# so a future upgrade to full Jinja2 templating cannot silently change the meaning
# of sources which work today.
_RESERVED_DELIMITERS = ('{%', '{#')

_CLASS_TEMPLATE = '''"! This is a temporary class created by sapcli for execution
"! of an adhoc ABAP statements.
CLASS {class_name} DEFINITION
  PUBLIC FINAL CREATE PUBLIC .

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

ENDCLASS.

CLASS {class_name} IMPLEMENTATION.
    METHOD if_oo_adt_classrun~main.

{user_code}

    ENDMETHOD.
ENDCLASS.
'''


def generate_class_name(prefix, username):
    """Generates a class name with exactly 30 characters following the pattern
       <prefix>_<username>_<random>
    """

    prefix_lower = prefix.lower()
    username_lower = username.lower()

    random_len = 30 - len(prefix_lower) - 1 - len(username_lower) - 1
    if random_len < 1:
        raise SAPCliError(
            f'The prefix "{prefix}" and username "{username}" are too long to fit in a 30-char class name'
        )

    random_chars = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(random_len))
    return f'{prefix_lower}_{username_lower}_{random_chars}'


def preprocess(user_code, definitions):
    """Replaces every {{NAME}} token in user_code with definitions[NAME].

    Raises SAPCliError if the code contains a token without a matching definition,
    so a forgotten substitution fails loudly instead of reaching the ABAP system,
    and also if a token holds anything but a plain name - the content between the
    braces is reserved for future syntax. The Jinja2 delimiters '{%' and '{#' are
    reserved too and must not appear in the code at all. Only the original code is
    checked - substituted values are inserted literally and never re-scanned.
    """

    reserved = [delimiter for delimiter in _RESERVED_DELIMITERS if delimiter in user_code]
    if reserved:
        names = ', '.join(reserved)
        raise SAPCliError(f'Reserved preprocessor delimiter(s): {names}')

    undefined = set()

    def _replace(match):
        name = match.group(1).strip()
        if not TOKEN_NAME_RE.fullmatch(name):
            raise SAPCliError(f'Unsupported preprocessor expression: {match.group(0)}')

        if name not in definitions:
            undefined.add(name)
            return match.group(0)

        return definitions[name]

    result = _TOKEN_RE.sub(_replace, user_code)

    if undefined:
        names = ', '.join(sorted(undefined))
        raise SAPCliError(f'Undefined preprocessor token(s): {names}')

    return result


def build_class_code(class_name, user_code):
    """Assembles the ABAP class source code wrapping user_code in if_oo_adt_classrun~main"""

    indented_code = '\n'.join(f'        {line}' for line in user_code.splitlines())
    return _CLASS_TEMPLATE.format(
        class_name=class_name.upper(),
        user_code=indented_code
    )


def execute_abap(connection, user_code, prefix=DEFAULT_PREFIX, package=DEFAULT_PACKAGE):
    """Creates a temporary ABAP class, executes it, then unconditionally deletes it.

    Returns the output of the execution.
    """

    class_name = generate_class_name(prefix, connection.user)
    class_code = build_class_code(class_name, user_code)

    clas = sap.adt.Class(connection, class_name.upper(), package=package)
    clas.description = _CLASS_DESCRIPTION

    try:
        clas.create()

        if config_get('check_before_save', True):
            check_result = sap.adt.checks.run_object_check(clas, class_code)
            if check_result.has_errors:
                raise sap.adt.checks.ObjectCheckFindings(clas, check_result)

        with clas.open_editor() as editor:
            editor.write(class_code)

        sap.adt.wb.activate(clas)

        connection.new_session()  # avoid "Class does not implement if_oo_adt_classrun~main method!"

        result = clas.execute()
    finally:
        try:
            clas.delete()
        except SAPCliError as delete_exception:
            warn_message = f'Warning: failed to delete temporary class {class_name}: {str(delete_exception)}'
            warnings.warn(warn_message, stacklevel=2)

    return result
