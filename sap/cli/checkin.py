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
    parent: str


class Repository:
    """Repository information"""

    def __init__(self, name, config):
        self._name = name
        self._full_fmt = '$%s' if name[0] == '$' else '%s'
        self._pfx_fmt = f'{name}_%s'
        self._config = config

        self._dir_prefix = config.STARTING_FOLDER.split('/')
        del self._dir_prefix[0]
        del self._dir_prefix[-1]

        self._packages = dict()

        self._pkg_name_bldr = {
            sap.platform.abap.abapgit.FOLDER_LOGIC_FULL: lambda parts: self._full_fmt % (parts[-1]),
            # pylint: disable=unnecessary-lambda
            sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX: lambda parts: self._pfx_fmt % ('_'.join(parts)),
        }[config.FOLDER_LOGIC]

    @property
    def config(self):
        return self._config

    @property
    def packages(self):
        """List of packages"""

        return self._packages.values()

    def find_package_by_path(self, dir_path):
        return self._packages[dir_path]

    def add_package_dir(self, dir_path, parent=None):
        """add new directory package"""

        pkg_file = os.path.join(dir_path, 'package.devc.xml', )
        if not os.path.isfile(pkg_file):
            raise sap.errors.SAPCliError('Not a package directory: {full_path}'.format(full_path=root))

        mod_log().debug('Adding new package dir: %s' % (dir_path))

        # Skip the first to ignore ./
        parts = dir_path.split('/')[1:]
        if len(parts) < len(self._dir_prefix):
            raise sap.errors.SAPCliError(f'Sub-package dir {dir_path} not in starting folder {self._config.STARTING_FOLDER}')

        for prefix in self._dir_prefix:
            if parts[0] != prefix:
                raise sap.errors.SAPCliError(f'Sub-package dir {dir_path} not in starting folder {self._config.STARTING_FOLDER}')

            del parts[0]

        if parts and parts[0]:
            pkg_name = self._pkg_name_bldr(parts)
        else:
            pkg_name = self._name

        pkg = RepoPackage(pkg_name, pkg_file, parent)
        self._packages[dir_path] = pkg

        return pkg




def _load_objects(repo):
    # packages
    # ddic
    # interfaces
    # classes
    # programs + includes

    abap_dir = f'.{repo.config.STARTING_FOLDER}'

    mod_log().debug('Loading ABAP dir: %s' % (abap_dir))

    repo.add_package_dir(abap_dir)

    for root, dirs, files in os.walk(abap_dir):
        parent = repo.find_package_by_path(root)

        for sub_dir in dirs:
            sub_pkg_dir = os.path.join(root, sub_dir)
            repo.add_package_dir(sub_pkg_dir, parent=parent)


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


def print_package(package):
    pfx = ''

    if package.parent:
        pfx = print_package(package.parent)

    sap.cli.core.printout(f'{pfx}{package.name}')
    return f'{pfx}  '


def do_checkin(_, args):
    """Synchronize directory structure with ABAP package structure"""

    top_dir = '.'
    if args.starting_folder:
        top_dir = os.path.join(top_dir, args.starting_folder)

    config = _get_config(args.starting_folder)
    repo = Repository(args.name, config)

    _load_objects(repo)

    for package in repo.packages:
        print_package(package)


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
