"""SAP CLI error types"""


class FatalError(Exception):
    """Common base exception type for """

    # pylint: disable=unnecessary-pass
    pass


class SAPCliError(FatalError):
    """Common base exception type for runtime errors"""

    # pylint: disable=unnecessary-pass
    pass


class ResourceAlreadyExistsError(SAPCliError):
    """Exception for existing resources - e.g. item to be created"""

    # pylint: disable=unnecessary-pass
    pass

    def __repr__(self):
        return 'Resource already exists'

    def __str__(self):
        return repr(self)
