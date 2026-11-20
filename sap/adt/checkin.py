"""ADT steps shared by the checkin of objects of all serializations"""

from sap import get_logger
from sap.adt.errors import ExceptionCheckinFailure, ExceptionResourceAlreadyExists


def mod_log():
    """Module logger"""

    return get_logger()


def check_package(adt_object, package_name, label):
    """Fetches the existing object and raises ExceptionCheckinFailure if the
       object is not in the package.
    """

    adt_object.fetch()

    existing_package = adt_object.reference.name
    # ADT returns upper case names but the package name comes from the command
    # line or a directory name and checkin creates packages in upper case
    if existing_package.upper() != package_name.upper():
        raise ExceptionCheckinFailure(f'Cannot checkin {label} {adt_object.name} into package {package_name}.'
                                      f' It already exists in package {existing_package}.')


def create_in_package(adt_object, corrnr, package_name, label):
    """Creates the object. If the object already exists, checks that it is in
       the package. Returns True if the object was created and False if it
       already existed.
    """

    try:
        adt_object.create(corrnr)
    except ExceptionResourceAlreadyExists as err:
        mod_log().info(err.message)
        check_package(adt_object, package_name, label)
        return False

    return True
