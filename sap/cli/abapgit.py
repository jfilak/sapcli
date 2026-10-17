"""
ADT proxy for ababgit commands
"""

import time

import sap.adt.abapgit
import sap.cli.core
import sap.cli.helpers
import sap.config
import sap.platform.abap.abapgit_rfc
from sap.errors import SAPCliError
from sap.platform.abap.abapgit import FOLDER_LOGIC_FULL, FOLDER_LOGIC_PREFIX


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for ababgit"""

    def __init__(self):
        super().__init__('abapgit')


API_STEAMPUNK = 'steampunk'
API_RFC_VIA_CLASSRUN = 'rfc-via-classrun'
APIS = [API_STEAMPUNK, API_RFC_VIA_CLASSRUN]


def _get_api(args):
    api = args.api or sap.config.config_get('abapgit_api', API_STEAMPUNK)
    if api not in APIS:
        raise SAPCliError(f'Unknown abapGit API "{api}" (SAPCLI_ABAPGIT_API) - use one of: {", ".join(APIS)}')

    return api


def _link_steampunk(connection, args):
    for param, value in (('--folder-logic', args.folder_logic),
                         ('--starting-folder', args.starting_folder),
                         ('--ignore-subpackages', args.ignore_subpackages),
                         ('--main-lang-only', args.main_lang_only)):
        if value:
            raise SAPCliError(f'The parameter {param} is supported only by the API {API_RFC_VIA_CLASSRUN}')

    resp = sap.adt.abapgit.Repository.link(connection, {
        'package': args.package.upper(),
        'url': args.url,
        'branchName': args.branch or 'refs/heads/master',
        'remoteUser': args.remote_user,
        'remotePassword': args.remote_password,
        'transportRequest': args.corrnr
    })

    console = args.console_factory()
    if resp.status_code == 200:
        console.printout('Repository was linked.')
    else:
        console.printerr(f'Failed to link repository: {args.package}', resp)


def _link_rfc_via_classrun(connection, args):
    if args.corrnr:
        raise SAPCliError(f'The parameter --corrnr is not supported by the API {API_RFC_VIA_CLASSRUN}')

    bapiret = sap.platform.abap.abapgit_rfc.link(
        connection,
        package=args.package.upper(),
        url=args.url,
        user=args.remote_user or '',
        password=args.remote_password or '',
        branch=args.branch or '',
        folder_logic=args.folder_logic or FOLDER_LOGIC_PREFIX,
        starting_folder=args.starting_folder or '/src/',
        ignore_subpackages=args.ignore_subpackages,
        main_lang_only=args.main_lang_only)

    console = args.console_factory()
    for line in bapiret.message_lines():
        console.printout(line)


@CommandGroup.argument('--api', type=str, choices=APIS, default=None,
                       help=f'abapGit API (default: SAPCLI_ABAPGIT_API or {API_STEAMPUNK})')
@CommandGroup.argument('--main-lang-only', action='store_true', default=False,
                       help=f'Serialize main language only ({API_RFC_VIA_CLASSRUN} only)')
@CommandGroup.argument('--ignore-subpackages', action='store_true', default=False,
                       help=f'Ignore subpackages ({API_RFC_VIA_CLASSRUN} only)')
@CommandGroup.argument('--starting-folder', type=str, default=None,
                       help=f'Repository folder with sources (default: /src/; {API_RFC_VIA_CLASSRUN} only)')
@CommandGroup.argument('--folder-logic', type=str, choices=[FOLDER_LOGIC_PREFIX, FOLDER_LOGIC_FULL], default=None,
                       help=f'Folder logic (default: {FOLDER_LOGIC_PREFIX}; {API_RFC_VIA_CLASSRUN} only)')
@CommandGroup.argument('--corrnr', type=str, nargs='?')
@CommandGroup.argument('--remote-user', type=str, nargs='?')
@CommandGroup.argument('--remote-password', type=str, nargs='?')
@CommandGroup.argument('--branch', type=str, nargs='?', default=None,
                       help=f'Branch (default: refs/heads/master for {API_STEAMPUNK}, '
                            f'remote HEAD for {API_RFC_VIA_CLASSRUN})')
@CommandGroup.argument('url')
@CommandGroup.argument('package')
@CommandGroup.command()
def link(connection, args):
    """ link git repository to ABAP package
    """

    if _get_api(args) == API_RFC_VIA_CLASSRUN:
        _link_rfc_via_classrun(connection, args)
    else:
        _link_steampunk(connection, args)


@CommandGroup.argument('--corrnr', type=str, nargs='?')
@CommandGroup.argument('--branch', type=str, nargs='?', default=None)
@CommandGroup.argument('--remote-user', type=str, nargs='?')
@CommandGroup.argument('--remote-password', type=str, nargs='?')
@CommandGroup.argument('package')
@CommandGroup.command()
def pull(connection, args):
    """ pull git repository branch to linked ABAP package
    """

    repository = sap.adt.abapgit.Repository(connection, args.package.upper())
    repository.fetch()
    repository.pull({
        'branchName': args.branch,
        'remoteUser': args.remote_user,
        'remotePassword': args.remote_password,
        'transportRequest': args.corrnr
    })

    repository.fetch()
    console = args.console_factory()
    with sap.cli.helpers.ConsoleHeartBeat(console, 1):
        while repository.get_status() == 'R':
            time.sleep(1)
            repository.fetch()

    if repository.get_status() == 'E' or repository.get_status() == 'A':
        console.printerr(repository.get_status_text())
        console.printerr(repository.get_error_log())
    else:
        console.printout(repository.get_status_text())
