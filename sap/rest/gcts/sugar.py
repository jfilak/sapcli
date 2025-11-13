"""Python Sugar for gCTS operations"""

import abc
from contextlib import contextmanager, nullcontext as nc
from typing import Optional

from sap import get_logger


def _mod_log():
    return get_logger()


class SugarOperationProgress(metaclass=abc.ABCMeta):
    """Abstract class for recording progress of sugar operations."""

    def __init__(self):
        self.recover_message = None

    def update(self, message, recover_message=None):
        """Update progress of operation."""

        self.recover_message = recover_message
        self._handle_updated(message, recover_message)

    @abc.abstractmethod
    def _handle_updated(self, message, recover_message):
        raise NotImplementedError()


class LogSugarOperationProgress(SugarOperationProgress):
    """Recording progress of sugar operations as logs."""

    def _handle_updated(self, message, recover_message):
        _mod_log().info(message)


class LogTaskOperationProgress(SugarOperationProgress, metaclass=abc.ABCMeta):
    """Recording progress of task operations as logs."""

    @abc.abstractmethod
    def update_task(self, error_msg: Optional[str], task: Optional[dict]):
        """Update progress of task operation."""
        raise NotImplementedError()

    @abc.abstractmethod
    def progress_message(self, message: str):
        """Print progress message."""
        raise NotImplementedError()

    @abc.abstractmethod
    def progress_error(self, message: str):
        """Print  message."""
        raise NotImplementedError()


@contextmanager
def abap_modifications_disabled(repo, progress=None):
    """Temporarily disable ABAP modifications upon gCTS operations (perform
       operations only in filesystem git repository).
    """

    if progress is None:
        progress = LogSugarOperationProgress()

    def _reset(previous):
        progress.update(
            f'Resetting the config VCS_NO_IMPORT = "{previous}" ...',
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

    tmp_vcs_no_import = 'X'

    progress.update(f'Disabling imports by setting the config VCS_NO_IMPORT = "{tmp_vcs_no_import}" ...')
    # Let's pray for no raceconditions.
    old_vcs_no_import = repo.get_config('VCS_NO_IMPORT')
    repo.set_config('VCS_NO_IMPORT', tmp_vcs_no_import)

    if old_vcs_no_import is None:
        revert_action = _delete
        progress.update(
            f'Successfully added the config VCS_NO_IMPORT = "{tmp_vcs_no_import}"',
            recover_message='Please delete the configuration option VCS_NO_IMPORT manually'
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
def buffer_only_enabled(repo, progress=None):
    """Temporarily enable buffer only upon gCTS operations.
    """

    if progress is None:
        progress = LogSugarOperationProgress()

    def _reset(previous):
        progress.update(
            f'Resetting the config VCS_BUFFER_ONLY = "{previous}" ...',
            recover_message=f'Please set the configuration option VCS_BUFFER_ONLY = "{old_buffer_only}" manually'
        )
        repo.set_config('VCS_BUFFER_ONLY', previous)
        progress.update(f'Successfully reset the config VCS_BUFFER_ONLY = "{previous}"')

    def _delete(_):
        progress.update(
            'Removing the config VCS_BUFFER_ONLY ...',
            recover_message="Please delete the configuration option VCS_BUFFER_ONLY manually"
        )
        repo.delete_config('VCS_BUFFER_ONLY')
        progress.update('Successfully removed the config VCS_BUFFER_ONLY')

    def _donothing(_):
        progress.update('The config VCS_BUFFER_ONLY has not beed changed')

    tmp_vcs_buffer_only = 'X'

    progress.update(f'Enabling buffer only by setting the config VCS_BUFFER_ONLY = "{tmp_vcs_buffer_only}" ...')

    old_buffer_only = repo.get_config('VCS_BUFFER_ONLY')
    repo.set_config('VCS_BUFFER_ONLY', tmp_vcs_buffer_only)

    if old_buffer_only is None:
        revert_action = _delete
        progress.update(
            f'Successfully added the config VCS_BUFFER_ONLY = "{tmp_vcs_buffer_only}"',
            recover_message='Please delete the configuration option VCS_BUFFER_ONLY manually'
        )
    elif old_buffer_only != tmp_vcs_buffer_only:
        revert_action = _reset
        progress.update(
            f'Successfully changed the config VCS_BUFFER_ONLY = "{old_buffer_only}" -> "{tmp_vcs_buffer_only}"',
            recover_message=f'Please set the configuration option VCS_BUFFER_ONLY = "{old_buffer_only}" manually'
        )
    else:
        revert_action = _donothing
        progress.update(f'The config VCS_BUFFER_ONLY was already set to "{tmp_vcs_buffer_only}"')

    try:
        yield
    finally:
        revert_action(old_buffer_only)


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
                        recover_message=f'Please double check if the original branch {old_branch} is active')
        repo.checkout(branch)
        progress.update(f'Successfully switched to the updated branch {branch}',
                        recover_message=f'Please switch to the branch {old_branch} manually')
    else:
        revert_action = _donothing
        progress.update(f'The updated branch {branch} is already active')

    try:
        yield
    finally:
        revert_action(old_branch)


def context_stub():
    '''Stub context manager that does nothing'''
    return nc()
