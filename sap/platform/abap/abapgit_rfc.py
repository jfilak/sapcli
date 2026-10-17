"""abapGit API based on RFC function modules called from adhoc ABAP code

The function modules ZABAPGIT_API_RFC_* are not called over RFC but from
a temporary class executed via ADT (sap.platform.abap.run), so no RFC
library is needed on the client side. The class writes the BAPIRET2 lines
and the rows of output tables of the function module to its output and
sapcli parses them back.
"""

import sap.platform.abap.run
from sap.errors import SAPCliError
from sap.rfc.bapi import BAPIReturn, BAPIError


FUNCTION_LINK = 'ZABAPGIT_API_RFC_LINK'
FUNCTION_PULL = 'ZABAPGIT_API_RFC_PULL'
FUNCTION_LIST = 'ZABAPGIT_API_RFC_LIST'
FUNCTION_COMMITPUSH = 'ZABAPGIT_API_RFC_COMMITPUSH'

# Fields of ZABAPGIT_API_RFC_REPO returned by list_repositories
REPOSITORY_FIELDS = ['REPO_KEY', 'NAME', 'ABAP_PACKAGE', 'URL', 'BRANCH_NAME', 'DESERIALIZED_AT']

_RETURN_PREFIX = 'SAPCLI-BAPIRET|'
_ROW_PREFIX = 'SAPCLI-ROW|'
_FIELD_PREFIX = 'SAPCLI-FIELD|'
_END_MARKER = 'SAPCLI-END'

# Raw characters per literal chunk - even if every character is a backtick
# (doubled when escaped), the chunk stays far below the ABAP line length limit.
_LITERAL_CHUNK = 100

_RETURN_CODE = '''LOOP AT lt_return INTO DATA(ls_return).
  out->write( |SAPCLI-BAPIRET\\|{ ls_return-type }\\|{ ls_return-id }\\|{ ls_return-number }\\|{ ls_return-message }| ).
ENDLOOP.
out->write( `SAPCLI-END` ).'''


def _abap_line_literal(line):
    chunks = [line[i:i + _LITERAL_CHUNK] for i in range(0, len(line), _LITERAL_CHUNK)] or ['']
    return '\n  && '.join('`' + chunk.replace('`', '``') + '`' for chunk in chunks)


def abap_string_literal(value):
    """Returns ABAP code of a string literal holding the value.

    Long values are split into several literals concatenated with &&
    to avoid exceeding the maximum length of an ABAP source line.
    Line breaks are concatenated as cl_abap_char_utilities=>newline.
    """

    if '\r' in value:
        raise SAPCliError('Carriage returns are not supported in values passed to ABAP')

    return '\n  && cl_abap_char_utilities=>newline\n  && '.join(
        _abap_line_literal(line) for line in value.split('\n'))


def _abap_bool(value):
    return 'X' if value else ''


def build_function_call_code(function, parameters, tables=()):
    """Returns ABAP code calling the function module with the parameters
       given as the list of tuples (name, ABAP type, value) and writing
       the output tables given as the list of tuples (name, ABAP table type,
       list of fields) and the TABLES parameter RETURN to the output.

       Each row of an output table is written as the line SAPCLI-ROW|<TABLE>
       followed by the lines SAPCLI-FIELD|<FIELD>|<value>.
    """

    lines = ['DATA lt_return TYPE bapiret2_t.']
    for name, abap_type, value in parameters:
        lines.append(f'DATA lv_{name} TYPE {abap_type}.')
        lines.append(f'lv_{name} = {abap_string_literal(value)}.')

    for name, abap_type, _ in tables:
        lines.append(f'DATA lt_{name} TYPE {abap_type}.')

    lines.append(f"CALL FUNCTION '{function}'")
    if parameters:
        lines.append('  EXPORTING')
        for name, _, _ in parameters:
            lines.append(f'    {name} = lv_{name}')
    lines.append('  TABLES')
    for name, _, _ in tables:
        lines.append(f'    {name} = lt_{name}')
    lines.append('    return = lt_return.')

    for name, _, fields in tables:
        lines.append(f'LOOP AT lt_{name} INTO DATA(ls_{name}).')
        lines.append(f'  out->write( `{_ROW_PREFIX}{name.upper()}` ).')
        for field in fields:
            lines.append(f'  out->write( |SAPCLI-FIELD\\|{field}\\|{{ ls_{name}-{field.lower()} }}| ).')
        lines.append('ENDLOOP.')

    lines.append(_RETURN_CODE)

    return '\n'.join(lines)


# pylint: disable=too-many-arguments
def build_link_code(package, url, user, password, branch, folder_logic, starting_folder,
                    ignore_subpackages, main_lang_only):
    """Returns ABAP code calling the function module ZABAPGIT_API_RFC_LINK"""

    return build_function_call_code(FUNCTION_LINK, [
        ('abap_package', 'devclass', package),
        ('git_repo_url', 'string', url),
        ('git_user', 'string', user),
        ('git_password', 'string', password),
        ('branch', 'string', branch),
        ('folder_logic', 'string', folder_logic),
        ('ignore_subpackages', 'xfeld', _abap_bool(ignore_subpackages)),
        ('main_lang_only', 'xfeld', _abap_bool(main_lang_only)),
        ('starting_folder', 'string', starting_folder),
    ])


def build_pull_code(package, user, password, corrnr):
    """Returns ABAP code calling the function module ZABAPGIT_API_RFC_PULL"""

    return build_function_call_code(FUNCTION_PULL, [
        ('abap_package', 'devclass', package),
        ('git_user', 'string', user),
        ('git_password', 'string', password),
        ('corrnr', 'trkorr', corrnr),
    ])


def build_list_code():
    """Returns ABAP code calling the function module ZABAPGIT_API_RFC_LIST"""

    return build_function_call_code(FUNCTION_LIST, [], [
        ('repositories', 'zabapgit_api_rfc_repo_t', REPOSITORY_FIELDS),
    ])


# pylint: disable=too-many-arguments
def build_commit_code(package, user, password, comment, body, committer_name, committer_email,
                      author_name, author_email):
    """Returns ABAP code calling the function module ZABAPGIT_API_RFC_COMMITPUSH
       committing and pushing all changes
    """

    return build_function_call_code(FUNCTION_COMMITPUSH, [
        ('abap_package', 'devclass', package),
        ('git_user', 'string', user),
        ('git_password', 'string', password),
        ('comment', 'string', comment),
        ('body', 'string', body),
        ('all', 'xfeld', _abap_bool(True)),
        ('committer_name', 'string', committer_name),
        ('committer_email', 'string', committer_email),
        ('author_name', 'string', author_name),
        ('author_email', 'string', author_email),
    ])


def parse_rows(output, table):
    """Returns the list of rows (dictionaries) of the output table written
       by the code generated by build_function_call_code.
    """

    rows = []
    in_table = False

    for line in output.splitlines():
        line = line.strip()

        if line.startswith(_ROW_PREFIX):
            in_table = line[len(_ROW_PREFIX):] == table
            if in_table:
                rows.append({})
        elif line.startswith(_FIELD_PREFIX) and in_table:
            field, value = line[len(_FIELD_PREFIX):].split('|', 1)
            rows[-1][field] = value

    return rows


def parse_return(output):
    """Returns BAPIReturn built from the output of the code generated by
       build_function_call_code.
    """

    messages = []
    completed = False

    for line in output.splitlines():
        line = line.strip()

        if line == _END_MARKER:
            completed = True
        elif line.startswith(_RETURN_PREFIX):
            msg_type, msg_id, msg_number, msg_message = line[len(_RETURN_PREFIX):].split('|', 3)
            messages.append({'TYPE': msg_type, 'ID': msg_id, 'NUMBER': msg_number, 'MESSAGE': msg_message})

    if not completed:
        raise SAPCliError(f'Incomplete output of the abapGit API call:\n{output}')

    return BAPIReturn(messages)


def _call(connection, code):
    output = sap.platform.abap.run.execute_abap(connection, code)

    bapiret = parse_return(output)
    if bapiret.is_error:
        raise BAPIError(bapiret, output)

    return bapiret, output


# pylint: disable=too-many-arguments
def link(connection, package, url, user, password, branch, folder_logic, starting_folder,
         ignore_subpackages, main_lang_only):
    """Links the git repository to the ABAP package and returns BAPIReturn"""

    bapiret, _ = _call(connection, build_link_code(package, url, user, password, branch, folder_logic,
                                                   starting_folder, ignore_subpackages, main_lang_only))
    return bapiret


def pull(connection, package, user, password, corrnr):
    """Pulls the git repository linked to the ABAP package and returns BAPIReturn"""

    bapiret, _ = _call(connection, build_pull_code(package, user, password, corrnr))
    return bapiret


def list_repositories(connection):
    """Returns the list of linked repositories (dictionaries with the keys
       REPOSITORY_FIELDS)
    """

    _, output = _call(connection, build_list_code())
    return parse_rows(output, 'REPOSITORIES')


# pylint: disable=too-many-arguments
def commit(connection, package, user, password, comment, body, committer_name, committer_email,
           author_name, author_email):
    """Commits all changes of the ABAP package, pushes them to the linked git
       repository, and returns BAPIReturn
    """

    bapiret, _ = _call(connection, build_commit_code(package, user, password, comment, body, committer_name,
                                                     committer_email, author_name, author_email))
    return bapiret
