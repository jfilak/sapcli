# Author: Jakub Filak <jakub@thefilaks.net>
"""SAP Command Line tool entry point"""

import os
import os.path
import sys
import logging
from argparse import ArgumentParser
import getpass
import warnings
from importlib.metadata import version, PackageNotFoundError

import sap
import sap.cli
import sap.adt
import sap.rfc
from sap.config import ConfigFile
from sap.http import TimedOutRequestError as HttpTimedOutRequestError
from sap.http.truststore_support import enable_system_cert_store, TruststoreNotAvailableError
import sap.http.oauth
from sap.odata.errors import TimedOutRequestError as ODataTimedOutRequestError

# pylint: disable=invalid-name
log = sap.get_logger()


# pylint: disable=too-few-public-methods
class ExitCodes:
    """sys.exit() codes"""

    SUCCESS = 0
    # Do not use Shell Reserved Exit Codes
    SHELL_RESERVED_1 = 1
    SHELL_RESERVED_2 = 2
    # Use the first available Exit code
    INVALID_CONFIGURATION = 3


def report_args_error_and_exit(args, error):
    """Prints error to stderr and exits with coder reporting invalid
       paramters.
    """

    print(error, file=sys.stderr)
    args.print_help(sys.stderr)
    sys.exit(ExitCodes.INVALID_CONFIGURATION)


def _system_cert_store_applies(args):
    """Whether the operating system trust store should back TLS verification.

    True only when sapcli actually verifies a server certificate over TLS and no
    explicit CA bundle was supplied - otherwise enabling the OS trust store is
    either a no-op (plain HTTP or validation disabled) or would override the
    user's explicit --ssl-server-cert choice.
    """

    return bool(
        args.ssl_use_system_certs
        and args.ssl
        and args.verify
        and not args.ssl_server_cert
    )


def _report_auth_cert_cli_conflicts(arg_parser, args):
    """Reject contradictory authentication modes given on the command line.

    Must run before resolve_default_connection_values merges in env/config
    values - after that the sources are indistinguishable and e.g. an
    exported SAP_PASSWORD must not trip the check.
    """

    if args.auth_cert and args.password:
        report_args_error_and_exit(
            arg_parser,
            '--auth-cert and --password are mutually exclusive'
            ': the client certificate replaces the password')


def _report_auth_cert_resolved_conflicts(arg_parser, args):
    """Reject broken client certificate setups after defaults resolution."""

    if args.auth_key and not args.auth_cert:
        report_args_error_and_exit(
            arg_parser,
            '--auth-key requires --auth-cert'
            ' (or auth_cert in the configuration file)')

    if args.auth_cert and not args.ssl:
        report_args_error_and_exit(
            arg_parser,
            '--auth-cert cannot be used with --no-ssl'
            ': a client certificate requires TLS')


# pylint: disable=too-many-statements
def parse_command_line(argv):
    """Parses command line arguments"""

    arg_parser = ArgumentParser(os.path.basename(argv[0]))
    try:
        sapcli_version = version('sapcli')
    except PackageNotFoundError:
        sapcli_version = 'unknown version'

    arg_parser.add_argument('--version', action='version', version=f'%(prog)s {sapcli_version}')
    arg_parser.add_argument(
        '-v', '--verbose', dest='verbose_count', action='count', default=0,
        help='make verbose output')
    arg_parser.add_argument(
        '--config', dest='config', type=str, default=None,
        help='Path to configuration file (default: ~/.sapcli/config.yml)')
    arg_parser.add_argument(
        '--context', dest='context', type=str, default=None,
        help='Configuration context to use (overrides current-context in config file)')
    arg_parser.add_argument(
        '--auth-plugin-invalidate-cache', dest='auth_plugin_invalidate_cache',
        default=False, action='store_true',
        help='Drop the cached auth-plugin response before authenticating')
    arg_parser.add_argument(
        '--auth-plugin-disable-cache', dest='auth_plugin_disable_cache',
        default=None, action='store_true',
        help='Do not read or write the auth-plugin response cache on disk '
             '(also drops any pre-existing entry). '
             'Env: SAPCLI_AUTH_PLUGIN_DISABLE_CACHE')
    arg_parser.add_argument(
        '--auth-cert', dest='auth_cert', type=str, default=None,
        help='Path to a PEM client certificate for TLS client certificate '
             'authentication; may contain the private key too. '
             'Env: SAP_AUTH_CERT')
    arg_parser.add_argument(
        '--auth-key', dest='auth_key', type=str, default=None,
        help='Path to the unencrypted PEM private key for --auth-cert. '
             'Env: SAP_AUTH_KEY')
    arg_parser.add_argument(
        '--ashost', dest='ashost', type=str, default=None,
        help='Application Server address (DNS or IP)')
    arg_parser.add_argument(
        '--sysnr', dest='sysnr', type=str, default=None,
        help='ABAP instance system number for RFC (default 00 (i.e. port 3200))')
    arg_parser.add_argument(
        '--client', dest='client', type=str, default=None,
        help='Client (MANDT)')
    arg_parser.add_argument(
        '--no-ssl', dest='ssl', default=None, action='store_false',
        help='Switch from HTTPS to HTTP')
    arg_parser.add_argument(
        '--skip-ssl-validation', dest='verify', default=None, action='store_false',
        help='Skip validation of SSL server certificates')
    arg_parser.add_argument(
        '--ssl-server-cert', dest='ssl_server_cert', type=str, default=None,
        help='Path to a custom CA certificate file for SSL verification')
    arg_parser.add_argument(
        '--ssl-no-system-certs', dest='ssl_use_system_certs', default=None, action='store_false',
        help='Verify SSL server certificates against the bundled certifi CA list instead '
             'of the operating system trust store (used by default). Env: SAP_SSL_USE_SYSTEM_CERTS')
    arg_parser.add_argument(
        '--port', dest='port', type=int, default=None,
        help='ADT HTTP port; default = 443')
    arg_parser.add_argument(
        '--user', dest='user', type=str, default=None,
        help='Logon user')
    arg_parser.add_argument(
        '--password', dest='password', type=str, default=None,
        help='Password')

    arg_parser.add_argument("--mshost", default=os.getenv("SAP_MSHOST"), help="Message server address (if connecting "
                                                                              "via a load balancer)")
    arg_parser.add_argument("--msserv", default=os.getenv("SAP_MSSERV"), help="Message server port")
    arg_parser.add_argument("--sysid", default=os.getenv("SAP_SYSID"), help="System ID (use if connecting via a "
                                                                            "message server")
    arg_parser.add_argument("--group", default=os.getenv("SAP_GROUP"), help="Group (use if connecting via a message "
                                                                            "server")
    arg_parser.add_argument("--snc_qop", default=os.getenv("SNC_QOP"), help="SAP Secure Login Client QOP")
    arg_parser.add_argument("--snc_myname", default=os.getenv("SNC_MYNAME"), help="SAP Secure Login Client MyName")
    arg_parser.add_argument("--snc_partnername",
                            default=os.getenv("SNC_PARTNERNAME"), help="SAP Secure Login Client Partner name")
    arg_parser.add_argument("--snc_lib", default=os.getenv("SNC_LIB"),
                            help="SAP Secure Login Client library (e.g. "
                                 "/Applications/Secure Login Client.app/Contents/MacOS/lib/libsapcrypto.dylib")

    subparsers = arg_parser.add_subparsers()
    # pylint: disable=not-an-iterable
    for connection, cmd in sap.cli.get_commands():
        cmd_args = subparsers.add_parser(cmd.name, help=cmd.description)
        cmd_args.set_defaults(command=cmd)
        cmd_args.set_defaults(connection_factory=connection)

        cmd.install_parser(cmd_args)

    args = arg_parser.parse_args(argv[1:])

    loglevel = max(3 - args.verbose_count, 0) * 10
    log.setLevel(loglevel)
    logging.debug('Logging level: %i', loglevel)

    if not hasattr(args, 'execute'):
        report_args_error_and_exit(
            arg_parser,
            'No command specified - please consult the help and specify a command to execute')

    # Load config file and attach to args for use by resolve_default_connection_values
    args.config_file = ConfigFile.load(args.config)

    # Commands that don't need a connection (e.g. config) skip connection validation
    connection_factory = getattr(args, 'connection_factory', None)
    if connection_factory is sap.cli.no_connection:
        return args

    _report_auth_cert_cli_conflicts(arg_parser, args)

    sap.cli.resolve_default_connection_values(args)

    if _system_cert_store_applies(args):
        try:
            enable_system_cert_store()
        except TruststoreNotAvailableError as ex:
            # truststore is a regular sapcli dependency, so a failed import means
            # a broken installation. The operating system trust store is the
            # default, so do not fail every connection over it - warn and fall
            # back to the bundled certifi CA list.
            log.warning('%s', ex)

    if not args.ashost and not args.mshost:
        report_args_error_and_exit(
            arg_parser, ': '.join((
                'No SAP Application Server Host name provided',
                'use the option --ashost or the environment variable SAP_ASHOST in case of direct connection via HTTP '
                'or RFC',
                'and use the option --mshost or the variable SAP_MSHOST in case of RFC or a load balancer'
            )))

    if not args.client:
        report_args_error_and_exit(
            arg_parser, ': '.join((
                'No SAP Client provided',
                'use the option --client or the environment variable SAP_CLIENT'
            )))

    _report_auth_cert_resolved_conflicts(arg_parser, args)

    if not (args.snc_qop or args.snc_myname or args.snc_partnername):
        # auth_plugin owns credential acquisition and the server derives
        # the user from a client certificate - do not prompt for either
        # user or password in these modes.
        if not args.auth_plugin and not args.auth_cert:
            if not args.user:
                args.user = input('Login:')

            oauth_needs_password = sap.http.oauth.password_required(args.token_url, args.client_id)

            if not args.password and oauth_needs_password:
                args.password = getpass.getpass()

    return args


def init_deprecation_warnings():
    """Register default filter for deprecation warning."""

    warnings.filterwarnings('default', category=DeprecationWarning, module='sap.cli')


def main(argv=None):
    """Main function"""

    if argv is None:
        argv = sys.argv

    retval = 1
    init_deprecation_warnings()
    try:
        args = parse_command_line(argv)
        connection = args.connection_factory(args)
        retval = args.execute(connection, args)
    except KeyboardInterrupt:
        log.error('Program interrupted!')
    except (HttpTimedOutRequestError, ODataTimedOutRequestError) as ex:
        print(f'Exception ({type(ex).__name__}):', file=sys.stderr)
        print(' ', str(ex), file=sys.stderr)
        print('  You can increase the timeout with the environment variable SAPCLI_HTTP_TIMEOUT (in seconds).', file=sys.stderr)
        log.debug('Execution of program has been terminated due to an error', exc_info=True)
    except sap.errors.SAPCliError as ex:
        print(f'Exception ({type(ex).__name__}):', file=sys.stderr)
        print(' ', str(ex), file=sys.stderr)
        log.debug('Execution of program has been terminated due to an error', exc_info=True)
    finally:
        logging.shutdown()

    return retval
