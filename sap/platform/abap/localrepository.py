"""Contracts of file formats of ABAP objects used by checkin and checkout.

A RepositoryLayout knows directories: where packages and object files are.
An ObjectHandler knows one object type in one serialization: its files and
how to move the object between the files and the system. A HandlerRegistry
is a plain lookup of handlers. A RepositoryObserver is told what layouts and
handlers do because they never print anything.

Nothing in this module knows any particular format.
"""

import abc
import typing

import sap.errors


class UnsupportedContent(sap.errors.SAPCliError):
    """The object contains something the handler cannot serialize yet.
       Handlers raise it before they write any file of the object.
    """


class RepoPackage(typing.NamedTuple):
    """Package directory of a repository"""

    dir_path: str
    # The package metadata file
    path: str
    # None only for the root package
    parent: typing.Any


class RepoObject(typing.NamedTuple):
    """ABAP object stored in files of a repository"""

    # File type, e.g. clas
    code: str
    name: str
    # The metadata file, e.g. zcl_foo.clas.xml
    path: str
    # All files <name>.<code>.*
    files: list
    package: RepoPackage
    # The ObjectHandler which claimed the metadata file
    handler: typing.Any


class Repository(typing.NamedTuple):
    """Packages and objects found by a RepositoryLayout"""

    # Parents first
    packages: list
    objects: list
    # Every file found
    files: list
    # Owned by the layout
    settings: typing.Any
    # The folder of the root package the layout really used
    starting_folder: str


class CheckinContext(typing.NamedTuple):
    """Where and how an object is checked in"""

    connection: typing.Any
    # The ABAP package the object goes to
    package_name: str
    corrnr: typing.Optional[str]
    check_before_save: bool
    # RepositoryObserver
    observer: typing.Any


class ObjectCheckinResult(typing.NamedTuple):
    """Result of a checkin of a single object"""

    # ADT objects to be activated
    abap_objects: list
    used_files: list


class RepositoryObserver(abc.ABC):
    """Observer of the progress of checkin and checkout"""

    @abc.abstractmethod
    def checking_out(self, name):
        """The object is going to be read from the system"""

    @abc.abstractmethod
    def file_written(self, path):
        """The file has been written"""

    @abc.abstractmethod
    def creating(self, kind, name):
        """The object of the kind (e.g. Class) is going to be created in
           the system
        """

    @abc.abstractmethod
    def writing(self, kind, name, part=None):
        """The object of the kind (e.g. Class) or only its part (e.g.
           definitions) is going to be written to the system
        """

    @abc.abstractmethod
    def warning(self, message):
        """Something was skipped or could not be done but the operation
           continues
        """


class ObjectHandler(abc.ABC):
    """One ABAP object type in one serialization"""

    # ABAP object type in file names, e.g. clas
    FILE_TYPE: str
    # Extension of the metadata file which tells the serialization, e.g. xml
    METADATA_EXT: str
    # ADT object type codes, e.g. ('CLAS/OC',)
    ADT_TYPES: tuple

    def __init__(self):
        self._require_attribute('FILE_TYPE')
        self._require_attribute('METADATA_EXT')
        self._require_attribute('ADT_TYPES')

    def _require_attribute(self, name):
        if not getattr(self, name, None):
            raise TypeError(f'{type(self).__name__} does not define {name}')

    @abc.abstractmethod
    def checkout(self, connection, adt_type, name, destdir, observer):
        """Reads the object of the ADT object type (one of ADT_TYPES) from
           the system and writes its files. Reports to the observer.
        """

    @abc.abstractmethod
    def prepare(self, repo_obj, observer):
        """Reads and checks the files without accessing the system.
           Returns the data for checkin(). Reports to the observer.
        """

    @abc.abstractmethod
    def checkin(self, context, repo_obj, prepared):
        """Writes the object to the system. Returns ObjectCheckinResult.
           Reports to the observer of the context.
        """

    @abc.abstractmethod
    def locate(self, repo_obj, part, line):
        """Returns (file_path, line) of the line of the ADT source part
           (e.g. main, testclasses) or None if the object has no such source.
        """


class RepositoryLayout(abc.ABC):
    """Directory structure of a repository"""

    @abc.abstractmethod
    def load_repository(self, starting_folder, registry):
        """Finds packages and objects on disk. Returns Repository."""

    @abc.abstractmethod
    def package_name(self, repository, repo_package, root_package_name):
        """Returns the name of the ABAP package of the directory"""

    @abc.abstractmethod
    def prepare_package(self, repo_package):
        """Reads and checks the package file without accessing the system"""

    @abc.abstractmethod
    def init_repository(self, repo_dir, starting_folder):
        """Creates the repository files"""

    @abc.abstractmethod
    def checkout_package(self, connection, name, destdir, observer):
        """Writes the package file. Reports to the observer."""


class HandlerRegistry:
    """Lookup of object handlers given in the priority order"""

    def __init__(self, handlers):
        self._by_metadata_file = {}
        self._by_adt_type = {}

        for handler in handlers:
            key = (handler.FILE_TYPE, handler.METADATA_EXT)

            other = self._by_metadata_file.get(key)
            if other is not None:
                raise sap.errors.SAPCliError(
                    f'Duplicate object handlers of the files *.{handler.FILE_TYPE}.{handler.METADATA_EXT}:'
                    f' {type(other).__name__} and {type(handler).__name__}')

            self._by_metadata_file[key] = handler

            for adt_type in handler.ADT_TYPES:
                self._by_adt_type.setdefault(adt_type, handler)

    def for_metadata_file(self, file_type, ext):
        """Returns the handler of the file <name>.<file_type>.<ext> or None"""

        return self._by_metadata_file.get((file_type, ext))

    def for_adt_type(self, code):
        """Returns the first handler of the ADT object type or None"""

        return self._by_adt_type.get(code)
