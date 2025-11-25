"""Python Sugar for gCTS operations"""

import abc
import uuid
import functools
from contextlib import contextmanager
from sap import get_logger


def _mod_log():
    return get_logger()


class SugarOperationProgress(metaclass=abc.ABCMeta):
    """Abstract class for recording progress of sugar operations."""

    def __init__(self):
        self._recover_messages = {}

    def update(self, message, recover_message=None, pid=None):
        """Update progress of operation.

        Args:
            message (str): Progress message.
            recover_message (str): Recover message to be printed in the case
                the temporary configuration change could not be reverted.
            pid (str): Process ID to identify the operation for future clearing
                of the corresponding recover_message - meaning the temporary
                configuration change was successfully reverted.
        """

        # It is OK to pass pid=None for simple cases.
        self._recover_messages[pid] = recover_message
        self._handle_updated(message, recover_message, pid)

    def process_recover_notification(self):
        """Process recover messages for the temporary configuration changes
        that could not be reverted. In case of no recover messages, nothing
        happens.
        """
        if self._recover_messages:
            for recover_message in self._recover_messages.values():
                if recover_message is not None:
                    self._handle_recover(recover_message)

    @abc.abstractmethod
    def _handle_updated(self, message, recover_message, pid):
        raise NotImplementedError()

    @abc.abstractmethod
    def _handle_recover(self, message: str):
        raise NotImplementedError()


class LogSugarOperationProgress(SugarOperationProgress):
    """Recording progress of sugar operations as logs."""

    def _handle_updated(self, message, recover_message, pid):
        _mod_log().info(message)

    def _handle_recover(self, message):
        _mod_log().error(message)


@contextmanager
def abap_modifications_disabled(repo, progress=None):
    """Temporarily disable ABAP modifications upon gCTS operations (perform
       operations only in filesystem git repository).
    """

    if progress is None:
        progress = LogSugarOperationProgress()

    context_id = uuid.uuid4().hex
    _do_progress_update = functools.partial(progress.update, pid=context_id)

    def _reset(previous):
        _do_progress_update(
            f'Resetting the config VCS_NO_IMPORT = "{previous}" ...',
            recover_message=f'Please set the configuration option VCS_NO_IMPORT = "{old_vcs_no_import}" manually'
        )
        repo.set_config('VCS_NO_IMPORT', previous)
        _do_progress_update(f'Successfully reset the config VCS_NO_IMPORT = "{previous}"')

    def _delete(_):
        _do_progress_update(
            'Removing the config VCS_NO_IMPORT ...',
            recover_message="Please delete the configuration option VCS_NO_IMPORT manually"
        )
        repo.delete_config('VCS_NO_IMPORT')
        _do_progress_update('Successfully removed the config VCS_NO_IMPORT')

    def _donothing(_):
        _do_progress_update('The config VCS_NO_IMPORT has not been changed')

    tmp_vcs_no_import = 'X'

    # Let's pray for no raceconditions.
    _do_progress_update('Retrieving the config VCS_NO_IMPORT ...')
    old_vcs_no_import = repo.get_config('VCS_NO_IMPORT')
    _do_progress_update(f'Disabling imports by setting the config VCS_NO_IMPORT = "{tmp_vcs_no_import}" ...')
    repo.set_config('VCS_NO_IMPORT', tmp_vcs_no_import)

    if old_vcs_no_import is None:
        revert_action = _delete
        _do_progress_update(
            f'Successfully added the config VCS_NO_IMPORT = "{tmp_vcs_no_import}"',
            recover_message='Please delete the configuration option VCS_NO_IMPORT manually',
        )
    elif old_vcs_no_import != tmp_vcs_no_import:
        revert_action = _reset
        _do_progress_update(
            f'Successfully changed the config VCS_NO_IMPORT = "{old_vcs_no_import}" -> "{tmp_vcs_no_import}"',
            recover_message=f'Please set the configuration option VCS_NO_IMPORT = "{old_vcs_no_import}" manually',
        )
    else:
        revert_action = _donothing
        _do_progress_update(f'The config VCS_NO_IMPORT was already set to "{tmp_vcs_no_import}"')

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

    context_id = uuid.uuid4().hex
    _do_progress_update = functools.partial(progress.update, pid=context_id)

    def _checkout(revert_branch):
        _do_progress_update(
            f'Restoring the previously active branch {revert_branch} ...',
            recover_message=f'Please double check if the original branch {revert_branch} is active',
        )
        repo.checkout(revert_branch)
        _do_progress_update(f'Successfully restored the previously active branch {revert_branch}')

    def _donothing(revert_branch):
        _do_progress_update(f'The updated branch {revert_branch} remains active')

    old_branch = repo.branch

    if old_branch != branch:
        revert_action = _checkout
        _do_progress_update(
            f'Temporary switching to the updated branch {branch} ...',
            recover_message=f'Please double check if the original branch {old_branch} is active',
        )
        repo.checkout(branch)

        _do_progress_update(
            f'Successfully switched to the updated branch {branch}',
            recover_message=f'Please switch to the branch {old_branch} manually',
        )
    else:
        revert_action = _donothing
        _do_progress_update(f'The updated branch {branch} is already active')

    try:
        yield
    finally:
        revert_action(old_branch)
