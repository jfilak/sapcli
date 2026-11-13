"""Writing files of the abapGit serialization"""

import os

import sap.adt.errors
import sap.cli.core
from sap.platform.abap.abapgit import XMLWriter


def build_filename(object_name, typsfx, fileext, destdir=None):
    """Creates file name"""

    filename = f'{object_name}{typsfx}.{fileext}'.lower()

    if destdir is not None:
        filename = os.path.join(destdir, filename)

    return filename


def dump_attributes_to_file(object_name, abap_attributes, typsfx, ag_serializer, destdir=None):
    """Writes ABAP attributes to a file"""

    filename = build_filename(object_name, typsfx, 'xml', destdir=destdir)
    sap.cli.core.printout(f'- {os.path.basename(filename)}')
    with open(filename, 'w', encoding='utf8') as dest:
        writer = XMLWriter(ag_serializer, dest)

        for attributes in abap_attributes:
            writer.add(attributes)

        writer.close()


def write_source(source, object_name, typsfx, destdir=None, fileext='abap'):
    """Write source code to file"""

    filename = build_filename(object_name, typsfx, fileext, destdir=destdir)
    sap.cli.core.printout(f'- {os.path.basename(filename)}')
    with open(filename, 'w', encoding='utf8') as dest:
        dest.write(source)


def download_abap_source(object_name, source_object, typsfx, destdir=None):
    """Reads the text and saves it in the corresponding file"""

    try:
        text = source_object.text
    except sap.adt.errors.ADTError as err:
        sap.cli.core.printerr(f'Download of ABAP source code failed: {err}')
    else:
        write_source(text, object_name, typsfx, destdir)
