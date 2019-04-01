"""ABAP Workbench functionality"""

from sap.errors import SAPCliError


def activation_params():
    """Returns parameters for Activation of object"""

    return {'method': 'activate', 'preauditRequested': 'true'}


def build_activation_request(adt_object_full_uri, adt_object_name):
    """Creates the XML ADT activation request"""

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="{adt_object_full_uri}" adtcore:name="{adt_object_name}"/>
</adtcore:objectReferences>'''


def activate(adt_object):
    """Activates the given object"""

    request = build_activation_request(adt_object.full_adt_uri, adt_object.name.upper())

    resp = adt_object.connection.execute(
        'POST',
        'activation',
        params=activation_params(),
        headers={
            'Accept': 'application/xml',
            'Content-Type': 'application/xml'
        },
        body=request
    )

    if resp.text:
        raise SAPCliError(f'Could not activate the object {adt_object.name}: {resp.text}')
