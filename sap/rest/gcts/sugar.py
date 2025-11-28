"""Python Sugar for gCTS operations"""

import abc
import uuid
import functools
from typing import Optional, ContextManager
from contextlib import contextmanager, nullcontext as nc
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


def abap_modifications_disabled(repo, progress=None) -> ContextManager[None]:
    """Temporarily disable ABAP modifications upon gCTS operations (perform
       operations only in filesystem git repository).
    """
    return temporary_config(repo, config_name='VCS_NO_IMPORT', tmp_config_value='X', progress=progress)


def abap_modifications_added_only_to_buffer(repo, progress=None) -> ContextManager[None]:
    """Temporarily disable ABAP modifications upon gCTS operations (perform
       operations in filesystem git repository and a transport request
       is generated and added to the buffer).
    """
    return temporary_config(repo, config_name='VCS_BUFFER_ONLY', tmp_config_value='X', progress=progress)


@contextmanager
def temporary_config(repo, config_name, tmp_config_value, progress=None):
    """Temporarily disable a configuration option.
    """

    if progress is None:
        progress = LogSugarOperationProgress()

    context_id = uuid.uuid4().hex
    _do_progress_update = functools.partial(progress.update, pid=context_id)

    def _reset(previous):
        _do_progress_update(
            f'Resetting the config {config_name} = "{previous}" ...',
            recover_message=f'Please set the configuration option {config_name} = "{previous}" manually'
        )
        repo.set_config(config_name, previous)
        _do_progress_update(f'Successfully reset the config {config_name} = "{previous}"')

    def _delete(_):
        _do_progress_update(
            f'Removing the config {config_name} ...',
            recover_message=f"Please delete the configuration option {config_name} manually"
        )
        repo.delete_config(config_name)
        _do_progress_update(f'Successfully removed the config {config_name}')

    def _donothing(_):
        _do_progress_update(f'The config {config_name} has not been changed')

    # Let's pray for no raceconditions.
    _do_progress_update(f'Retrieving the config {config_name} ...')
    old_config_value = repo.get_config(config_name)
    _do_progress_update(f'Setting the config {config_name} = "{tmp_config_value}" ...')
    repo.set_config(config_name, tmp_config_value)

    if old_config_value is None:
        revert_action = _delete
        _do_progress_update(
            f'Successfully added the config {config_name} = "{tmp_config_value}"',
            recover_message=f'Please delete the configuration option {config_name} manually',
        )
    elif old_config_value != tmp_config_value:
        revert_action = _reset
        _do_progress_update(
            f'Successfully changed the config {config_name} = "{old_config_value}" -> "{tmp_config_value}"',
            recover_message=f'Please set the configuration option {config_name} = "{old_config_value}" manually',
        )
    else:
        revert_action = _donothing
        _do_progress_update(f'The config {config_name} was already set to "{tmp_config_value}"')

    try:
        yield
    finally:
        revert_action(old_config_value)


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


def context_stub():
    '''Stub context manager that does nothing'''
    return nc()
