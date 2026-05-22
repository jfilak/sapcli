"""ABAP Message Class ADT functionality module.

Worth mentioning:
- deletion of a message is done by sending am XML element deletedmessages for
  each deleted message

- any modified/deleted message must be locked separately and the lock handle
  must be included in the message element as an attribute

- use MessageLockManager as a context manager for locking/unlocking messages in
  a message class
"""

import contextlib

from sap.adt.objects import (
    ADTObject,
    ADTObjectType,
    ADTObjectPropertyEditor,
    XMLNS_ADTCORE,
    XMLNamespace,
    lock_params,
    unlock_params,
    adt_object_lock,
    adt_object_unlock,
    LOCK_ACCESS_MODE_MODIFY,
    LOCK_ACTION_LOCK_MSG,
    UNLOCK_ACTION_UNLOCK_ALL,
)
from sap.adt.annotations import (
    OrderedClassMembers,
    XmlNodeAttributeProperty,
    XmlListNodeProperty,
)
from sap import get_logger
from sap.errors import SAPCliError


XMLNS_MC = XMLNamespace('mc', 'http://www.sap.com/adt/MessageClass', parents=[XMLNS_ADTCORE])


def mod_log():
    """Returns module logger"""
    return get_logger()


# pylint: disable=too-many-instance-attributes,too-few-public-methods
class Message(metaclass=OrderedClassMembers):
    """A single message in a message class"""

    msgno = XmlNodeAttributeProperty('mc:msgno')
    msgtext = XmlNodeAttributeProperty('mc:msgtext')
    selfexplainatory = XmlNodeAttributeProperty('mc:selfexplainatory', value='false')
    lockhandle = XmlNodeAttributeProperty('mc:lockhandle')
    documented = XmlNodeAttributeProperty('mc:documented')
    lastchangedby = XmlNodeAttributeProperty('mc:lastchangedby')
    lastmodified = XmlNodeAttributeProperty('mc:lastmodified')
    name = XmlNodeAttributeProperty('adtcore:name')


class MessageLockManager(contextlib.AbstractContextManager):
    """Context manager for locking/unlocking messages in a message class"""

    def __init__(self, connection, message_class, messages: list):
        self.connection = connection
        self.message_class = message_class
        self.messages = messages
        self.locked_msgnos: list[str] = []

    def __enter__(self):
        try:
            self._lock()
        except Exception:
            self._unlock()
            raise

        self.message_class.message_context = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._unlock()
        self.message_class.message_context = None

    def _lock(self):
        """Lock messages and store lock handles"""
        if self.locked_msgnos:
            mod_log().warning("Messages %s are already locked for message class %s. Skipping locking.",
                              self.locked_msgnos, self.message_class.name)
            return

        for message in self.messages:
            uri = f'{self.message_class.uri}/messages/{message.msgno}'
            parameters = lock_params(LOCK_ACCESS_MODE_MODIFY, action=LOCK_ACTION_LOCK_MSG)
            lock_handle = adt_object_lock(self.connection, uri, parameters)
            message.lockhandle = lock_handle
            self.locked_msgnos.append(message.msgno)

    def _unlock(self):
        """Unlock messages with UNLOCK_ALL"""
        if not self.locked_msgnos:
            mod_log().info("Nothing to unlock for message class %s", self.message_class.name)
            return

        body = '[' + ', '.join(self.locked_msgnos) + ']'

        url_msgno = self.locked_msgnos[-1]
        uri = f'{self.message_class.uri}/messages/{url_msgno}'

        # UNLOCK_ALL is used to unlock all messages in one call.
        # The first parameter is lockhandle which is not used with UNLOCK_ALL, so we pass None.
        parameters = unlock_params(None, action=UNLOCK_ACTION_UNLOCK_ALL)

        adt_object_unlock(self.connection, uri, parameters, content_type='text/plain', body=body)

        for message in self.messages:
            message.lockhandle = None

        self.locked_msgnos.clear()


class MessageClass(ADTObject):
    """Public wrapper for message class ADT object"""

    OBJTYPE = ADTObjectType(
        'MSAG/N',
        'messageclass',
        XMLNS_MC,
        'application/vnd.sap.adt.mc.messageclass+xml',
        None,
        'messageClass',
        editor_factory=ADTObjectPropertyEditor
    )

    messages = XmlListNodeProperty('mc:messages', factory=Message, value=[])
    # Any deleted message must be sent to ADT backed in mc:deletedmessages to be processed.
    deleted_messages = XmlListNodeProperty('mc:deletedmessages', factory=Message, value=[])

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name.upper(), metadata)

        self._metadata.package_reference.name = package
        self.message_context: MessageLockManager | None = None

    def _build_lock_params(self, access_mode):
        """Extend base lock params with message-specific ones"""

        base_lock_params = super()._build_lock_params(access_mode)

        if self.message_context is not None and self.message_context.locked_msgnos:
            base_lock_params['msgNo'] = self.message_context.locked_msgnos[-1]
            base_lock_params['onSave'] = 'X'
        else:
            mod_log().debug("No locked messages to include in lock params for message class %s", self.name)

        return base_lock_params

    def set_message(self, connection, msgno, msgtext, selfexplainatory='false', corrnr=None):  # pylint: disable=unused-argument
        """Add or update a message: read -> lock msg -> lock class -> PUT -> unlock"""
        self.fetch()

        # Find or create the message
        existing = None
        for msg in self.messages:
            if msg.msgno == msgno:
                existing = msg
                break

        if existing is None:
            existing = Message()
            existing.msgno = msgno
            self.messages.append(existing)

        existing.msgtext = msgtext
        existing.selfexplainatory = selfexplainatory

        with MessageLockManager(connection, self, [existing]):
            with self.open_editor(corrnr=corrnr) as editor:
                editor.push()

    def delete_message(self, connection, msgno, corrnr=None):  # pylint: disable=unused-argument
        """Delete a message: read -> lock msg -> lock class -> PUT with deletedmessages -> unlock"""
        self.fetch()

        # Find and move the message to deleted
        target = None
        for msg in self.messages:
            if msg.msgno == msgno:
                target = msg
                break

        if target is None:
            raise SAPCliError(f'Message {msgno} not found in message class {self.name}')

        with MessageLockManager(connection, self, [target]):
            try:
                self.messages.remove(target)
                target.documented = None
                target.lastchangedby = None
                target.lastmodified = None
                target.name = None

                # The XmlListNodeProperty has weir behaviour and its setter actually appends the value.
                self.deleted_messages.append(target)

                with self.open_editor(corrnr=corrnr) as editor:
                    editor.push()
            finally:
                self.deleted_messages.remove(target)
