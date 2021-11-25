"""Simple API for gCTS operations"""

from sap import get_logger
from sap.rest.errors import HTTPRequestError
from sap.rest.gcts.remote_repo import Repository
from sap.rest.gcts.errors import (
    exception_from_http_error,
    GCTSRepoAlreadyExistsError
)


def _mod_log():
    return get_logger()


def fetch_repos(connection):
    """Returns list of repositories in the target systems defined by the given
       connection.
    """

    try:
        response = connection.get_json('repository')
    except HTTPRequestError as ex:
        raise exception_from_http_error(ex) from ex

    result = response.get('result', [])
    return [Repository(connection, repo['name'], data=repo) for repo in result]


# pylint: disable=too-many-arguments
def clone(connection, url, name, vsid='6IT', start_dir='src/', vcs_token=None, error_exists=True,
          role='SOURCE', typ='GITHUB'):
    """Creates and clones the repository in the target systems"""

    config = {}

    if start_dir:
        config['VCS_TARGET_DIR'] = start_dir

    if vcs_token:
        config['CLIENT_VCS_AUTH_TOKEN'] = vcs_token

    repo = Repository(connection, name)

    try:
        repo.create(url, vsid, config=config, role=role, typ=typ)
    except GCTSRepoAlreadyExistsError as ex:
        if error_exists:
            raise ex

        _mod_log().debug(ex)
        _mod_log().info(str(ex))

        repo.wipe_data()

    if not repo.is_cloned:
        repo.clone()
    else:
        _mod_log().info('Not cloning the repository "%s": already performed')

    return repo


def checkout(connection, branch, name=None, repo=None):
    """Checks out the given branch in the given repository on the give system"""

    if repo is None:
        repo = Repository(connection, name)

    return repo.checkout(branch)


def log(connection, name=None, repo=None):
    """Returns log history of the given repository on the give system"""

    if repo is None:
        repo = Repository(connection, name)

    return repo.log()


def pull(connection, name=None, repo=None):
    """Pulls the given repository on the give system"""

    if repo is None:
        repo = Repository(connection, name)

    return repo.pull()


def delete(connection, name):
    """Deletes the given repository on the give system"""

    return Repository(connection, name).delete()


def set_user_api_token(connection, api_url, token):
    """Set Token for the currently logged in user"""

    body = {
        'endpoint': api_url,
        'user': '',
        'password': '',
        'token': token,
        'type': 'token'
    }

    connection.post_obj_as_json('user/credentials', body)
