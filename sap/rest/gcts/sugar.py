"""Python Sugar for gCTS operations"""

import abc
from contextlib import contextmanager

from sap import get_logger


def _mod_log():
    return get_logger()


class SugarOperationProgress(metaclass=abc.ABCMeta):

    def __init__(self, progress=None):
        self._progress = progress
        self.recover_message = None

    def update(self, message, recover_message=None):
        self.recover_message = recover_message
        self._handle_updated(message, recover_message)


    @abc.abstractmethod
    def _handle_updated(self, message, recover_message):
        raise NotImplementedError()


class LogSugarOperationProgress(SugarOperationProgress):

    def _handle_updated(self, message, recover_message):
        _mod_log().info(message)


@contextmanager
def abap_modifications_disabled(repo, progress=None):
    """Temporarily disable ABAP modifications upon gCTS operations (perform
       operations only in filesystem git repository).
    """

    if progress is None:
        progress = LogSugarOperationProgress()

    def _reset(previous):
        progress.update(f'Resetting the config VCS_NO_IMPORT = "{previous}" ...',
            recover_message=f'Please set the configuration option VCS_NO_IMPORT = "{old_vcs_no_import}" manually'
        )
        repo.set_config('VCS_NO_IMPORT', previous)
        progress.update(f'Successfully reset the config VCS_NO_IMPORT = "{previous}"')

    def _delete(_):
        progress.update(
            'Removing the config VCS_NO_IMPORT ...',
            recover_message="Please delete the configuration option VCS_NO_IMPORT manually"
        )
        repo.delete_config('VCS_NO_IMPORT')
        progress.update('Successfully removed the config VCS_NO_IMPORT')

    def _donothing(_):
        progress.update('The config VCS_NO_IMPORT has not beed changed')

    tmp_vcs_no_import = 'true'

    progress.update(f'Disabling imports by setting the config VCS_NO_IMPORT = "{tmp_vcs_no_import}" ...')
    # Let's pray for no raceconditions.
    old_vcs_no_import = repo.get_config('VCS_NO_IMPORT')
    repo.set_config('VCS_NO_IMPORT', tmp_vcs_no_import)

    if old_vcs_no_import is None:
        revert_action = _delete
        progress.update(
            f'Successfully added the config VCS_NO_IMPORT = "{tmp_vcs_no_import}"',
            recover_message=f'Please delete the configuration option VCS_NO_IMPORT manually'
        )
    elif old_vcs_no_import != tmp_vcs_no_import:
        revert_action = _reset
        progress.update(
            f'Successfully changed the config VCS_NO_IMPORT = "{old_vcs_no_import}" -> "{tmp_vcs_no_import}"',
            recover_message=f'Please set the configuration option VCS_NO_IMPORT = "{old_vcs_no_import}" manually'
        )
    else:
        revert_action = _donothing
        progress.update(f'The config VCS_NO_IMPORT was already set to "{tmp_vcs_no_import}"')

    try:
        yield
    finally:
        revert_action(old_vcs_no_import)


@contextmanager
def temporary_switched_branch(repo, branch, progress=None):
    """Temporarily checkout the requested branch.
    """

    if progress is None:
        progress = LogSugarOperationProgress()

    def _checkout(revert_branch):
        progress.update(
            f'Restoring the previously active branch {revert_branch} ...',
            recover_message=f'Please double check if the original branch {revert_branch} is active'
        )
        repo.checkout(revert_branch)
        progress.update(f'Successfully restored the previously active branch {revert_branch}')

    def _donothing(revert_branch):
        progress.update(f'The updated branch {revert_branch} remains active')

    old_branch = repo.branch

    if old_branch != branch:
        revert_action = _checkout
        progress.update(f'Temporary switching to the updated branch {branch} ...',
                        recover_message=f'Please double check if the originl branch {old_branch} is active')
        repo.checkout(branch)
        progress.update(f'Successfully switched to the updated branch {branch}',
                        recover_message=f'Please switch if the branch {old_branch} manually')
    else:
        revert_action = _donothing
        progress.update(f'The updated branch {branch} is already active')

    try:
        yield
    finally:
        revert_action(old_branch)
