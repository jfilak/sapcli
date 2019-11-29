"""ADT Object import"""

import os
import errno
import typing

from sap import get_logger

import sap.errors
import sap.cli.core
import sap.platform.abap.abapgit


def mod_log():
    """ADT Module logger"""

    return get_logger()


class RepoPackage(typing.NamedTuple):
    """Package on file system"""

    name: str
    source: str


class Repository:
    """Repository information"""

    def __init__(self, name, config):
        self._name = name
        self._full_fmt = '$%s' if name[0] == '$' else '%s'
        self._pfx_fmt = f'{name}_%s'
        self._config = config
        self._packages = list()

        self._pkg_name_bldr = {
            sap.platform.abap.abapgit.FOLDER_LOGIC_FULL: lambda parts: self._full_fmt % (parts[-1]),
            # pylint: disable=unnecessary-lambda
            sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX: lambda parts: self._pfx_fmt % ('_'.join(parts)),
        }[config.FOLDER_LOGIC]

    @property
    def packages(self):
        """List of packages"""

        return self._packages

    def add_package_dir(self, dir_path):
        """add new directory package"""

        mod_log().debug('Adding new package dir: %s' % (dir_path))

        # Skip the first to ignore ./
        parts = dir_path.split('/')[1:]
        if parts:
            pkg_name = self._pkg_name_bldr(parts)
        else:
            pkg_name = self._name

        self._packages.append(RepoPackage(pkg_name, os.path.join(dir_path, 'package.devc')))


def _load_objects(repo, directory):
    # packages
    # ddic
    # interfaces
    # classes
    # programs + includes

    for root, _, files in os.walk(directory):
        if 'package.devc' not in files:
            raise sap.errors.SAPCliError('Not a package directory: {full_path}'.format(full_path=root))

        repo.add_package_dir(root)


def _get_config(starting_folder):
    config = None

    conf_file_contents = None
    conf_file_path = '.abapgit.xml'

    try:
        with open(conf_file_path) as conf_file:
            conf_file_contents = conf_file.read()
    except OSError as ex:
        if ex.errno != errno.ENOENT:
            raise

        config = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(STARTING_FOLDER=starting_folder)
    else:
        config = sap.platform.abap.abapgit.DOT_ABAP_GIT.from_xml(conf_file_contents)

    return config


def do_checkin(_, args):
    """Synchronize directory structure with ABAP package structure"""

    top_dir = '.'
    if args.starting_folder:
        top_dir = os.path.join(top_dir, args.starting_folder)

    config = _get_config(args.starting_folder)
    repo = Repository(args.name, config)
    _load_objects(repo, top_dir)

    for package in repo.packages:
        sap.cli.core.printout(package[0])


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for importing ADT objects"""

    def __init__(self):
        super(CommandGroup, self).__init__('checkin')

    # pylint: disable=arguments-differ
    def install_parser(self, arg_parser):
        arg_parser.add_argument('--starting-folder', default=None)
        arg_parser.add_argument('name')
        arg_parser.set_defaults(execute=do_checkin)

        return arg_parser
