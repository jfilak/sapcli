"""gCTS Repo activities utilities"""

from collections.abc import Callable
from typing import Union

from sap.rest.errors import HTTPRequestError
from sap.rest.gcts.errors import SAPCliError
from sap.rest.gcts.remote_repo import Repository, RepoActivitiesQueryParams


def get_activity_rc(repo: Repository, operation: RepoActivitiesQueryParams.Operation) -> int:
    """Get the return code of the operation"""

    activities_params = RepoActivitiesQueryParams().set_operation(operation.value)
    try:
        activities_list = repo.activities(activities_params)
    except HTTPRequestError as exc:
        raise SAPCliError(f'Unable to obtain activities of repository: "{repo.rid}"\n{exc}') from exc

    if not activities_list or activities_list[0]['rc'] is None:
        raise SAPCliError(f'Expected {operation.value} activity not found! Repository: "{repo.rid}"')

    return int(activities_list[0]['rc'])


def is_clone_activity_success(repo: Repository, rc_cb: Union[Callable[[int], None], None] = None) -> bool:
    """Check if the cloned activity is successful
    Args:
        repo (Repository): The repository to check
        rc_cb (Callable, optional): Callback function to log the activity Return Code (rc).
            It receives the return code as an argument.
    """

    rc = get_activity_rc(repo, RepoActivitiesQueryParams.Operation.CLONE)

    if rc_cb is not None:
        rc_cb(rc)

    return rc <= Repository.ActivityReturnCode.CLONE_SUCCESS.value


def is_checkout_activity_success(repo: Repository, rc_cb: Union[Callable[[int], None], None] = None) -> bool:
    """Check if the checkout activity is successful
    Args:
        repo (Repository): The repository to check
        rc_cb (Callable, optional): Callback function to log the activity Return Code (rc).
            It receives the return code as an argument.
    """

    rc = get_activity_rc(repo, RepoActivitiesQueryParams.Operation.BRANCH_SW)

    if rc_cb is not None:
        rc_cb(rc)

    return rc <= Repository.ActivityReturnCode.BRANCH_SW_SUCCES.value
