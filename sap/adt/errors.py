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
