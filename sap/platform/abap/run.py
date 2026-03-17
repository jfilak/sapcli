"""ABAP Adhoc Code Execution"""

import secrets
import string

import sap.adt
import sap.adt.wb
from sap.errors import SAPCliError


DEFAULT_PREFIX = 'zcl_sapcli_run'
DEFAULT_PACKAGE = '$tmp'

_CLASS_DESCRIPTION = 'Temporary class created by sapcli for adhoc ABAP execution'

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

        with clas.open_editor() as editor:
            editor.write(class_code)

        sap.adt.wb.activate(clas)

        result = clas.execute()
    finally:
        clas.delete()

    return result
