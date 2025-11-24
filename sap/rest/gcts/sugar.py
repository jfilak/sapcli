"""Python Sugar for gCTS operations"""

import abc
import uuid
from contextlib import contextmanager
from sap.rest.gcts.errors import GCTSRequestError
from sap import get_logger


def _mod_log():
    return get_logger()


class SugarOperationProgress(metaclass=abc.ABCMeta):
    """Abstract class for recording progress of sugar operations."""

    def __init__(self):
        self.recover_messages = {}

    def update(self, message, recover_message=None, pid=None):
        """Update progress of operation."""
        if recover_message and pid:
            self.recover_messages[pid] = recover_message
        self._handle_updated(message, recover_message, pid)

    def recover_notification(self, pid):
        """Send a notification about the recover error."""
        self._handle_recover(pid)
        self.clear_recover_message(pid)

    def clear_recover_message(self, pid):
        """Clear the recover message for the given PID."""
        self.recover_messages.pop(pid, None)

    def get_recover_message(self, pid):
        """Get the recover message for the given PID."""
        return self.recover_messages.get(pid, None)

    @abc.abstractmethod
    def _handle_updated(self, message, recover_message, pid):
        raise NotImplementedError()

    @abc.abstractmethod
    def _handle_recover(self, pid):
        raise NotImplementedError()


class LogSugarOperationProgress(SugarOperationProgress):
    """Recording progress of sugar operations as logs."""

    def _handle_updated(self, message, recover_message, pid):
        _mod_log().info(message)

    def _handle_recover(self, pid):
        _mod_log().error(self.get_recover_message(pid))


@contextmanager
def abap_modifications_disabled(repo, progress=None):
    """Temporarily disable ABAP modifications upon gCTS operations (perform
       operations only in filesystem git repository).
    """

    if progress is None:
        progress = LogSugarOperationProgress()

    context_id = uuid.uuid4().hex

    def _reset(previous):
        progress.update(
            f'Resetting the config VCS_NO_IMPORT = "{previous}" ...',
            recover_message=f'Please set the configuration option VCS_NO_IMPORT = "{old_vcs_no_import}" manually',
            pid=context_id
        )
        repo.set_config('VCS_NO_IMPORT', previous)
        progress.update(f'Successfully reset the config VCS_NO_IMPORT = "{previous}"')

    def _delete(_):
        progress.update(
            'Removing the config VCS_NO_IMPORT ...',
            recover_message="Please delete the configuration option VCS_NO_IMPORT manually",
            pid=context_id
        )
        repo.delete_config('VCS_NO_IMPORT')
        progress.update('Successfully removed the config VCS_NO_IMPORT')

    def _donothing(_):
        progress.update('The config VCS_NO_IMPORT has not been changed')

    tmp_vcs_no_import = 'X'

    # Let's pray for no raceconditions.
    try:
        progress.update(
            'Retrieving the config VCS_NO_IMPORT ...',
            recover_message='Attempt to retrieve the config VCS_NO_IMPORT failed',
            pid=context_id
        )
        old_vcs_no_import = repo.get_config('VCS_NO_IMPORT')
    except GCTSRequestError as ex:
        progress.recover_notification(context_id)
        raise ex

    if old_vcs_no_import != tmp_vcs_no_import:
        try:
            progress.update(
                f'Disabling imports by setting the config VCS_NO_IMPORT = "{tmp_vcs_no_import}" ...',
                recover_message='Attempt to change the config VCS_NO_IMPORT failed',
                pid=context_id
            )
            repo.set_config('VCS_NO_IMPORT', tmp_vcs_no_import)
        except GCTSRequestError as ex:
            progress.recover_notification(context_id)
            raise ex from ex

    if old_vcs_no_import is None:
        revert_action = _delete
        progress.update(
            f'Successfully added the config VCS_NO_IMPORT = "{tmp_vcs_no_import}"',
            recover_message='Please delete the configuration option VCS_NO_IMPORT manually',
            pid=context_id
        )
    elif old_vcs_no_import != tmp_vcs_no_import:
        revert_action = _reset
        progress.update(
            f'Successfully changed the config VCS_NO_IMPORT = "{old_vcs_no_import}" -> "{tmp_vcs_no_import}"',
            recover_message=f'Please set the configuration option VCS_NO_IMPORT = "{old_vcs_no_import}" manually',
            pid=context_id,
        )
    else:
        revert_action = _donothing
        progress.update(f'The config VCS_NO_IMPORT was already set to "{tmp_vcs_no_import}"')

    try:
        yield
    finally:
        try:
            revert_action(old_vcs_no_import)
        except GCTSRequestError as ex:
            progress.recover_notification(context_id)
            raise ex
        finally:
            progress.clear_recover_message(context_id)


@contextmanager
def temporary_switched_branch(repo, branch, progress=None):
    """Temporarily checkout the requested branch.
    """

    if progress is None:
        progress = LogSugarOperationProgress()

    context_id = uuid.uuid4().hex

    def _checkout(revert_branch):
        progress.update(
            f'Restoring the previously active branch {revert_branch} ...',
            recover_message=f'Please double check if the original branch {revert_branch} is active',
            pid=context_id
        )
        repo.checkout(revert_branch)
        progress.update(f'Successfully restored the previously active branch {revert_branch}')

    def _donothing(revert_branch):
        progress.update(f'The updated branch {revert_branch} remains active')

    old_branch = repo.branch

    if old_branch != branch:
        revert_action = _checkout
        progress.update(f'Temporary switching to the updated branch {branch} ...',
                        recover_message=f'Please double check if the original branch {old_branch} is active',
                        pid=context_id)
        try:
            repo.checkout(branch)
        except GCTSRequestError as ex:
            progress.recover_notification(context_id)
            raise ex
        progress.update(f'Successfully switched to the updated branch {branch}',
                        recover_message=f'Please switch to the branch {old_branch} manually',
                        pid=context_id)
    else:
        revert_action = _donothing
        progress.update(f'The updated branch {branch} is already active')

    try:
        yield
    finally:
        try:
            revert_action(old_branch)
        except GCTSRequestError as ex:
            progress.recover_notification(context_id)
            raise ex
        finally:
            progress.clear_recover_message(context_id)
