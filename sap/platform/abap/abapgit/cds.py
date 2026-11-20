"""Common parts of the handlers of CDS source code objects in the abapGit
   serialization: <name>.<type>.xml and <name>.<type>.<source suffix>
"""

from types import SimpleNamespace

import sap.adt
import sap.adt.checkin
import sap.adt.errors
import sap.adt.checks
import sap.platform.abap.abapgit


def prepare_cds_source(repo_obj, abap_type, get_description, source_suffix, label):
    """Reads and checks the abapGit XML file of the given type and the source
       code file of the CDS source object without accessing the system
    """

    source_file = repo_obj.path[:-4] + source_suffix
    if source_file not in repo_obj.files:
        raise sap.adt.errors.ExceptionCheckinFailure(f'No source file for {label.lower()} {repo_obj.name}')

    with open(repo_obj.path, encoding='utf-8') as abap_data_file:
        abap_data = sap.platform.abap.abapgit.from_xml([abap_type], abap_data_file.read())[abap_type.__name__]

    with open(source_file, 'r', encoding='utf-8') as source:
        source_code = source.read()

    return SimpleNamespace(description=get_description(abap_data), source_file=source_file, source_code=source_code)


def checkin_cds_source(context, repo_obj, prepared, adt_type, label):
    """Creates the CDS source object and writes its source code. Returns
       the ADT object and the path of the source code file.
    """

    context.observer.creating(label, repo_obj.name)

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=context.connection.user.upper(),
                                   description=prepared.description)
    adt_object = adt_type(context.connection, repo_obj.name.upper(), package=context.package_name, metadata=metadata)

    sap.adt.checkin.create_in_package(adt_object, context.corrnr, context.package_name, label.lower())

    context.observer.writing(label, repo_obj.name)
    sap.adt.checks.write_source(prepared.source_code, adt_object, corrnr=context.corrnr,
                                source_label=prepared.source_file,
                                check_before_save=context.check_before_save)

    return (adt_object, prepared.source_file)
