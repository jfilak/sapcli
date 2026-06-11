"""ADT error types"""

import re

from sap.errors import SAPCliError


ADT_EXCEPTION_XML_FRAGMENT = '''<?xml version="1.0" encoding="utf-8"?>\
<exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework">'''


class ADTError(SAPCliError):
    """Errors reported by ADT tools"""

    def __init__(self, namespace, typ, message):
        super().__init__()

        self.namespace = namespace
        self.type = typ
        self.message = message

    def __repr__(self):
        return f'{self.namespace}.{self.type}'

    def __str__(self):
        return f'{self.type}: {self.message}'


class ExceptionResourceAlreadyExists(ADTError):
    """Thin wrapper for the class type of ADTErrors"""

    def __init__(self, message):
        super().__init__('com.sap.adt', self.__class__.__name__, message)

    def __str__(self):
        return f'{self.message}'


class ExceptionResourceNotFound(ADTError):
    """Thin wrapper for the class type of ADTErrors"""

    def __init__(self, message):
        super().__init__('com.sap.adt', self.__class__.__name__, message)

    def __str__(self):
        return f'{self.message}'


class ExceptionResourceCreationFailure(ADTError):
    """Thin wrapper for the class type of ADTErrors"""

    def __init__(self, message):
        super().__init__('com.sap.adt', self.__class__.__name__, message)

    def __str__(self):
        return f'{self.message}'


class ExceptionResourceLockConflict(ADTError):
    """Raised when an ADT resource cannot be modified because the
       lock state of the resource (or a parent like a software
       component / package) does not permit it.

       Common message text is
         'No suitable software component is modifiable; cannot create object'
       seen on package or DDIC create calls under a parent that is
       not modifiable for the current user.
    """

    def __init__(self, message):
        super().__init__('com.sap.adt', self.__class__.__name__, message)

    def __str__(self):
        return f'{self.message}'


class ExceptionResourceNoAccess(ADTError):
    """Raised when the calling user has no access to the addressed
       resource or transport request.

       Common message text on gCTS-managed systems is
         'Request <T> cannot be used since it is not assigned to repository <R>'
       which means the object's gCTS repository binding rejects the
       transport the caller picked (or the implicit one).
    """

    def __init__(self, message):
        super().__init__('com.sap.adt', self.__class__.__name__, message)

    def __str__(self):
        return f'{self.message}'


class ExceptionCheckinFailure(SAPCliError):
    """Wrapper for checkin errors"""

    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return f'{self.message}'


class ADTConnectionError(SAPCliError):
    """Wrapper for ADT connection errors"""

    def __init__(self, host, port, ssl, message):
        super().__init__()
        msg = f'[HOST:"{host}", PORT:"{port}", SSL:"{ssl}"] Error: '
        if 'Errno -5' in message:
            msg += 'Name resolution error. Check the HOST configuration.'
        elif 'Errno 111' in message:
            msg += 'Cannot connect to the system. Check the HOST and PORT configuration.'
        else:
            msg += message
        self.message = msg

    def __str__(self):
        return f'ADT Connection error: {self.message}'


class ExceptionResourceSaveFailure(ADTError):
    """Thin wrapper for the class type of ADTErrors"""

    def __init__(self, message):
        super().__init__('com.sap.adt', self.__class__.__name__, message)

    def __str__(self):
        return f'{self.message}'


class ExceptionDeletionFailure(SAPCliError):
    """Wrapper for ADT deletion errors"""

    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return f'{self.message}'


class InvalidURIError(SAPCliError):
    """Raised when an ADT URI cannot be parsed"""

    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return f'{self.message}'


def new_adt_error_from_xml(xmldata):
    """Parses the xml data and create the correct instance.

       Returns None, if the given xmldata does not represent an ADT Exception.
    """

    if not xmldata.startswith(ADT_EXCEPTION_XML_FRAGMENT):
        return None

    namespace = re.match('.*<namespace id="([^"]*)"/>.*', xmldata)[1]
    typ = re.match('.*<type id="([^"]*)"/>.*', xmldata)[1]
    message = re.match('.*<message lang="..">([^<]*)</message>.*', xmldata)[1]

    for subclass in ADTError.__subclasses__():
        if subclass.__name__ == typ:
            return subclass(message)

    return ADTError(namespace, typ, message)
