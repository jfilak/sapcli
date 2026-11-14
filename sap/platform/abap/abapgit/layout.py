"""Directory structure of abapGit repositories

   .abapgit.xml             the repository settings
   <starting folder>/       the root package
   .../<sub directory>/     a sub-package
   .../package.devc.xml     the package of the directory
   .../<name>.<type>.*      the files of an object of the package
"""

import errno
import os

from sap import get_logger

import sap.adt
import sap.cli.core
import sap.errors
import sap.platform.abap
from sap.platform.abap.localrepository import RepositoryLayout, RepoPackage, RepoObject, Repository
from sap.platform.abap.abapgit.files import dump_attributes_to_file
from sap.platform.abap.abapgit import DOT_ABAP_GIT, FOLDER_LOGIC_FULL, FOLDER_LOGIC_PREFIX
from sap.platform.abap.ddic import DEVC

SETTINGS_FILE_NAME = '.abapgit.xml'
PACKAGE_FILE_NAME = 'package.devc.xml'


def mod_log():
    """Module logger"""

    return get_logger()


def load_settings(starting_folder):
    """Reads .abapgit.xml of the current directory. If the file does not
       exist, returns the settings of a new repository with the given
       starting folder.
    """

    try:
        with open(SETTINGS_FILE_NAME, 'r', encoding='utf-8') as settings_file:
            settings = DOT_ABAP_GIT.from_xml(settings_file.read())
    except OSError as ex:
        if ex.errno != errno.ENOENT:
            raise

        if starting_folder is None:
            return DOT_ABAP_GIT.for_new_repo()

        return DOT_ABAP_GIT.for_new_repo(STARTING_FOLDER=starting_folder)

    if settings.STARTING_FOLDER != starting_folder:
        # stdout belongs to the results of commands (e.g. XML reports)
        sap.cli.core.printerr(f'Using starting-folder from {SETTINGS_FILE_NAME}: {settings.STARTING_FOLDER}')

    return settings


def _new_package(dir_path, parent):
    package_file = os.path.join(dir_path, PACKAGE_FILE_NAME)
    if not os.path.isfile(package_file):
        raise sap.errors.SAPCliError(f'Not a package directory: {dir_path}')

    mod_log().debug('Adding new package dir: %s', dir_path)

    return RepoPackage(dir_path, package_file, parent)


def _new_object(file_name, dir_file_names, package, registry):
    """Returns the object of the metadata file or None if no handler claims
       the file.
    """

    parts = file_name.split('.')
    if len(parts) < 2:
        return None

    handler = registry.for_metadata_file(parts[-2], parts[-1])
    if handler is None:
        return None

    if len(parts) != 3 or not parts[0]:
        raise sap.errors.SAPCliError(f'Invalid ABAP file name: {file_name}')

    name, code, metadata_ext = parts
    mod_log().debug('Handling object code: %s (%s)', code, file_name)

    # The files with the extension of the metadata file are not handed over
    # to keep the handlers simple
    files = [os.path.join(package.dir_path, other_name) for other_name in dir_file_names
             if other_name.startswith(f'{name}.{code}.') and not other_name.endswith(f'.{metadata_ext}')]

    return RepoObject(code, name, os.path.join(package.dir_path, file_name), files, package, handler)


def _find_objects(dir_file_names, package, registry):
    """Returns the objects of the metadata files of the package directory"""

    objects = []

    for file_name in dir_file_names:
        repo_obj = _new_object(file_name, dir_file_names, package, registry)
        if repo_obj is not None:
            objects.append(repo_obj)

    return objects


def _path_parts(path):
    return [part for part in path.split('/') if part]


class AbapGitLayout(RepositoryLayout):
    """abapGit repository in the current directory"""

    def load_repository(self, starting_folder, registry):
        settings = load_settings(starting_folder)

        abap_dir = f'.{settings.STARTING_FOLDER}'
        if not abap_dir.startswith('./'):
            raise sap.errors.SAPCliError(f'Package dirs must start with "./": {abap_dir}')

        mod_log().debug('Loading ABAP dir: %s', abap_dir)

        packages = {abap_dir: _new_package(abap_dir, None)}
        objects = []
        files = []

        for root, dirs, file_names in os.walk(abap_dir):
            mod_log().debug('Analyzing package dir: %s', root)

            package = packages[root]

            files += [os.path.join(root, file_name) for file_name in file_names]
            objects += _find_objects(file_names, package, registry)

            for sub_dir in dirs:
                dir_path = os.path.join(root, sub_dir)
                packages[dir_path] = _new_package(dir_path, package)

        return Repository(list(packages.values()), objects, files, settings)

    def package_name(self, repository, repo_package, root_package_name):
        settings = repository.settings

        starting_parts = _path_parts(settings.STARTING_FOLDER)
        # Skip the first path part to ignore .
        dir_parts = _path_parts(repo_package.dir_path)[1:]

        if dir_parts[:len(starting_parts)] != starting_parts:
            raise sap.errors.SAPCliError(f'Sub-package dir {repo_package.dir_path} not in starting folder'
                                         f' {settings.STARTING_FOLDER}')

        sub_parts = dir_parts[len(starting_parts):]
        if not sub_parts:
            return root_package_name

        if settings.FOLDER_LOGIC == FOLDER_LOGIC_FULL:
            return ('$' if root_package_name[0] == '$' else '') + sub_parts[-1]

        if settings.FOLDER_LOGIC == FOLDER_LOGIC_PREFIX:
            return f'{root_package_name}_' + '_'.join(sub_parts)

        raise sap.errors.SAPCliError(f'Unsupported folder logic: {settings.FOLDER_LOGIC}')

    def prepare_package(self, repo_package):
        devc = DEVC()
        with open(repo_package.path, encoding='utf-8') as devc_file:
            sap.platform.abap.from_xml(devc, devc_file.read())

        return devc

    def init_repository(self, repo_dir, starting_folder):
        dot_abapgit = DOT_ABAP_GIT.for_new_repo(STARTING_FOLDER='/' + starting_folder + '/')

        with open(os.path.join(repo_dir, SETTINGS_FILE_NAME), 'w', encoding='utf8') as dest:
            sap.platform.abap.to_xml(dot_abapgit, dest=dest, top_element='DATA')

    def checkout_package(self, connection, name, destdir):
        adt_package = sap.adt.Package(connection, name)
        adt_package.fetch()

        devc = DEVC(CTEXT=adt_package.description)
        dump_attributes_to_file('package', (devc,), '.devc', 'LCL_OBJECT_DEVC', destdir=destdir)
