"""Local repository of ABAP objects - the file formats used by commands"""

import os

from sap import get_logger

import sap.platform.abap.abapgit.handlers
from sap.errors import FatalError
from sap.platform.abap.localrepository import HandlerRegistry
from sap.platform.abap.abapgit.layout import AbapGitLayout

# Handlers of object files in the priority order
OBJECT_HANDLERS = HandlerRegistry(sap.platform.abap.abapgit.handlers.HANDLERS)

# Directory structure of the repository
REPOSITORY_LAYOUT = AbapGitLayout()


def mod_log():
    """Module logger"""

    return get_logger()


def load_local_objects():
    """Returns the objects of the repository in the current directory by
       (ADT object type, upper case name) or None if the current directory
       is not a repository.
    """

    try:
        repo = REPOSITORY_LAYOUT.load_repository(None, OBJECT_HANDLERS)
    except (FatalError, OSError) as ex:
        # ABAP Unit can be run anywhere, so results are just not mapped to
        # local files when the current directory is not a repository
        mod_log().debug('No local repository: %s', ex)
        return None

    local_objects = {}
    for repo_obj in repo.objects:
        for adt_type in repo_obj.handler.ADT_TYPES:
            local_objects[(adt_type, repo_obj.name.upper())] = repo_obj

    return local_objects


def locate_source(local_objects, adt_type, object_name, part, line):
    """Returns (file path, line) of the line of the ADT source part of
       the object in the local repository or None.
    """

    if not local_objects:
        return None

    repo_obj = local_objects.get((adt_type, object_name.upper()))
    if repo_obj is None:
        return None

    located = repo_obj.handler.locate(repo_obj, part, line)
    if located is None:
        return None

    return (os.path.normpath(located[0]), located[1])
